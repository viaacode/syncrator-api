#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/syncrator_api.py
#

from app.models import *
from app.job_worker import JobWorker
from app.run_worker import RunWorker
from flask import request, url_for, jsonify
from flask_api import FlaskAPI, status, exceptions
from viaa.configuration import ConfigParser
from viaa.observability import logging
from sqlalchemy.exc import OperationalError
from app.config import flask_environment
import os

app = FlaskAPI(__name__)
config = ConfigParser()
logger = logging.get_logger(__name__, config=config)

app.config.from_object(flask_environment())
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route("/")
def home():
    # TODO: add some jinja template here
    logger.info(
        "configuration = ", dictionary={
            'environment': flask_environment()})
    page = '<html><head><style>body{background-color: #fff; color: #333;}</style></head><body>'
    page += '<h1>Syncrator-API</h1>'
    page += '<ul>'
    page += '<li><a href="/jobs?page=1">     GET /jobs </a>    - paginated list of active jobs </li>'
    page += '<li><a href="/jobs/1"> GET /jobs/&lt;id>  </a>    - get job details and progress </li><br/>'

    page += '<li><a href="/sync/avo/qas">GET /sync/avo/qas</a> - full synchronisation job dryrun</li>'
    page += '<li> POST /sync/&lt;project>/&lt;env>             - start a new full synchronisation job</li><br/>'

    page += '<li><a href="/delta/avo/qas">GET /delta/avo/qas</a> - delta synchronisation job dryrun</li>'
    page += '<li> POST /delta/&lt;project>/&lt;env>             - start a new delta synchronisation job</li><br/>'

    page += '<li><a href="/delete/avo/qas">GET /delete/avo/qas</a> - delete synchronisation job dryrun</li>'
    page += '<li> POST /delete/&lt;project>/&lt;env>             - start a new delete synchronisation job</li><br/>'

    page += '<li><a href="/diff/avo/qas">GET /diff/avo/qas</a> - dryrun for delta followed by delete in one go for partial updates</li>'
    page += '<li> POST /diff/&lt;project>/&lt;env>             - start delta job followed by a delete job</li><br/>'

    page += '<li> POST /run             - start custom syncrator job by passing all template parameters (target, env, action_name, action, is_tag, options)</li>'

    page += '<li> POST /dryrun          - dryrun custom job by passing all template parameters (target, env, action_name, action, is_tag, options)</li>'

    page += '</ul>'

    page += '<h2>Health check call</h2>'
    page += '<ul><li> <a href="/health/live"> GET /health/live </a> - healthcheck route for openshift'
    page += '</body></html>'
    return page, status.HTTP_200_OK


@app.route("/health/live")
def liveness_check():
    return "OK", status.HTTP_200_OK


@app.route("/jobs", methods=['GET'])
def list_jobs():
    try:
        page = request.args.get('page', 1, type=int)
        job_rows = SyncJob.query.order_by(
            SyncJob.start_time.desc()
        ).paginate(page, app.config['JOBS_PER_PAGE'], False).items
        jobs = [j.to_dict() for j in job_rows]
        return jsonify(jobs)
    except OperationalError as pg:
        return "database error: {}".format(str(pg)), 400


@app.route("/jobs/<int:job_id>", methods=['GET'])
def get_job(job_id):
    try:
        job = SyncJob.query.filter_by(id=job_id).first()
        return jsonify(job.to_dict())
    except AttributeError:
        return "not found", 404
    except OperationalError as pg:
        return "database error: {}".format(str(pg)), 400


@app.route("/sync/<string:project>/<string:environment>", methods=['GET','POST'])
def start_sync_job(project, environment):
    do_dryrun_only = request.method=='GET'
    return start_job(project, environment, 'sync', dryrun=do_dryrun_only)

@app.route("/delta/<string:project>/<string:environment>", methods=['GET', 'POST'])
def start_delta_job(project, environment):
    do_dryrun_only = request.method=='GET'
    return start_job(project, environment, 'delta', dryrun=do_dryrun_only)

@app.route("/delete/<string:project>/<string:environment>", methods=['GET','POST'])
def start_delete_job(project, environment):
    do_dryrun_only = request.method=='GET'
    return start_job(project, environment, 'delete', dryrun=do_dryrun_only)

@app.route("/diff/<string:project>/<string:environment>", methods=['GET', 'POST'])
def start_diff_job(project, environment):
    do_dryrun_only = request.method=='GET'
    return start_job(project, environment, 'diff', dryrun = do_dryrun_only)


@app.route("/run", methods=['POST'])
def syncrator_run():
    # POST /run run custom job by passing all template parameters in json
    return run()


@app.route("/dryrun", methods=['POST'])
def syncrator_dryrun():
    # POST /dryrun same as run but don't execute only return resulting template
    return run(dryrun=True)

# generic run method needs all parameters for syncrator as json in post request
# these are target, env, action_name, action, is_tag and options. look in
# syncrator-openshift/job_params for examples
def run(dryrun=False):
    request_data = request.json
    if not request_data:
        request_data = {}
    request_data['dryrun'] = dryrun

    target = request_data['target']
    env = request_data['env']
    action_name = request_data['action_name']
    action = request_data['action']
    is_tag = request_data['is_tag']
    options = request_data['options']


    response = {
        'api_job_id': None,
        'target': target,
        'env': env,
        'action_name': action_name,
        'action': action,
        'is_tag': is_tag,
        'options': options,
    }

    if dryrun:
        openshift_script = 'syncrator_dryrun.sh'
        stream = os.popen(
            "cd syncrator-openshift && ./{} '{}' '{}' '{}' '{}' '{}' '{}'".format(
                openshift_script,
                target,
                env,
                action_name,
                action,
                is_tag,
                options))
        job_result = stream.read()

        response['result'] = job_result
    else:
        openshift_script = 'syncrator_run.sh'
        request_data['openshift_script'] = openshift_script

        #TODO: check if there is a job started or running here before creating new one
        api_job = ApiJob(
            sync_id=None,
            target=target,
            env=env,
            job_type=action,
            job_params={
                'script': openshift_script,
                'target': target,
                'env': env,
                'action_name': action_name,
                'action': action,
                'is_tag': is_tag,
                'options': options
            },
            status='starting'
        )
        db.session.add(api_job)
        db.session.commit()
        response['api_job_id'] = api_job.id
        response['result'] = 'starting'

        # handle execution in a worker thread
        syncrator_worker = RunWorker(request_data, api_job.id, logger)
        syncrator_worker.start()

    logger.info('Syncrator run called with parameters', data=request_data)

    return jsonify(response)


# if openshift_script is syncrator_job.sh that runs an actual job using the 
# parameter files defined in syncrator-openshift/job_params
# if openshift script is syncrator_job_dryrun.sh we do a dryrun and return the resulting
# template as specified by the parameter files
def start_job(project, environment, job_type, dryrun=False):
    request_data = request.json
    if not request_data:
        request_data = {}

    request_data['project'] = project
    request_data['environment'] = environment
    request_data['job_type'] = job_type
    request_data['dryrun'] = dryrun

    
    response = {
        'api_job_id': None,
        'job_type': job_type,
        'project': project,
        'environment': environment,
    }

    if dryrun:
        openshift_script = 'syncrator_job_dryrun.sh'
        stream = os.popen(
            "cd syncrator-openshift && ./{} '{}' '{}' '{}'".format(
                openshift_script, project, environment, job_type))
        job_result = stream.read()

        response['result'] = job_result
    else:
        openshift_script = 'syncrator_job.sh'
        request_data['openshift_script'] = openshift_script

        #TODO: check if there is a job started or running here before creating new one
        api_job = ApiJob(
            sync_id=None,
            target=project,
            env=environment,
            job_type=job_type,
            job_params={
                'script': openshift_script,
                'project': project,
                'environment': environment,
                'job_type': job_type,
            },
            status='starting'
        )
        db.session.add(api_job)
        db.session.commit()
        response['api_job_id'] = api_job.id
        response['result'] = 'starting'

        # handle execution in a worker thread, pass request_data to configure
        # worker 
        syncrator_worker = JobWorker(request_data, api_job.id, logger)
        syncrator_worker.start()

    logger.info(
        "Starting {} job={} for project={} and env={} dryrun={}".format(
            openshift_script, job_type, project, environment, dryrun))


    return jsonify(response)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Page not found</p>", 404


if __name__ == "__main__":
    app.run(debug=True, port=8080)
