#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from app.models import *
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
        job_rows = SyncJobs.query.order_by(
            SyncJobs.start_time.desc()
        ).paginate(page, app.config['JOBS_PER_PAGE'], False).items
        jobs = [j.to_dict() for j in job_rows]
        return jsonify(jobs)
    except OperationalError as pg:
        return "database error: {}".format(str(pg)), 400


@app.route("/jobs/<int:job_id>", methods=['GET'])
def get_job(job_id):
    try:
        job = SyncJobs.query.filter_by(id=job_id).first()
        return jsonify(job.to_dict())
    except AttributeError:
        return "not found", 404
    except OperationalError as pg:
        return "database error: {}".format(str(pg)), 400


@app.route("/sync/<string:project>/<string:environment>", methods=['GET'])
def dryrun_sync_job(project, environment):
    # GET /sync/avo/qas does dryrun
    return start_job(project, environment, 'sync', dryrun=True)


@app.route("/sync/<string:project>/<string:environment>", methods=['POST'])
def start_sync_job(project, environment):
    # POST /sync/avo/qas creates openshift pod and executes job
    return start_job(project, environment, 'sync')


@app.route("/delta/<string:project>/<string:environment>", methods=['GET'])
def dryrun_delta_job(project, environment):
    # GET /delta/avo/qas does dryrun
    return start_job(project, environment, 'delta', dryrun=True)


@app.route("/delta/<string:project>/<string:environment>", methods=['POST'])
def start_delta_job(project, environment):
    # POST /delta/avo/qas creates openshift pod and executes job
    return start_job(project, environment, 'delta')


@app.route("/delete/<string:project>/<string:environment>", methods=['GET'])
def dryrun_delete_job(project, environment):
    # GET /delete/avo/qas does dryrun
    return start_job(project, environment, 'delete', dryrun=True)


@app.route("/delete/<string:project>/<string:environment>", methods=['POST'])
def start_delete_job(project, environment):
    # POST /delete/avo/qas creates openshift pod and executes job
    return start_job(project, environment, 'delete')


@app.route("/diff/<string:project>/<string:environment>", methods=['GET'])
def dryrun_diff_job(project, environment):
    # GET /diff/avo/qas does dryrun a diff is a delta followed by a delete
    # TODO: possibly implement this in syncrator itself as seperate cli
    # command instead
    res_delta = dryrun_job(project, environment, 'delta')
    res_delete = dryrun_job(project, environment, 'delete')
    res_diff = res_delta[0] + res_delete[0]

    return res_diff, status.HTTP_200_OK


@app.route("/diff/<string:project>/<string:environment>", methods=['POST'])
def start_diff_job(project, environment):
    # POST /delete/avo/qas creates openshift pod and executes job
    # TODO: either poll here or probably better just make syncrator have a diff command
    # res_delta = start_job(project, environment, 'delta')
    # somehow poll here or alternative make a seperate syncrator cli command for this
    # res_delete = start_job(project, environment, 'delete')

    return "This is work in progress", status.HTTP_200_OK


@app.route("/run", methods=['POST'])
def syncrator_run():
    # POST /run instead of only giving project and environment we pass the
    # complete params
    return run()

# uses alternate script to print template and oc commands


@app.route("/dryrun", methods=['POST'])
def syncrator_dryrun():
    # POST /dryrun same as run but don't execute only return resulting template
    return run(dryrun=True)


def run(dryrun=False):
    if dryrun:
        openshift_script = 'syncrator_dryrun.sh'
    else:
        openshift_script = 'syncrator_run.sh'

    request_data = request.json
    if not request_data:
        request_data = {}
    request_data['dryrun'] = dryrun
    request_data['openshift_script'] = openshift_script

    target = request_data['target']
    env = request_data['env']
    action_name = request_data['action_name']
    action = request_data['action']
    is_tag = request_data['is_tag']
    options = request_data['options']

    logger.info('Syncrator run called with parameters', data=request_data)

    stream = os.popen(
        "cd syncrator-openshift && ./{} '{}' '{}' '{}' '{}' '{}' '{}'".format(
            openshift_script, target, env, action_name, action, is_tag, options
        )
    )
    job_result = stream.read()

    return jsonify({
        'openshift_script': openshift_script,
        'target': target,
        'env': env,
        'action_name': action_name,
        'action': action,
        'is_tag': is_tag,
        'options': options,
        'result': job_result
    })


# if openshift_script is syncrator_job.sh that runs an actual job using the paramter
# files defined in syncrator-openshift/job_params
# if openshift script is syncrator_job_dryrun.sh we do a dryrun and return the resulting
# template as specified by the parameter files
def start_job(project, environment, job_type, dryrun=False):
    if dryrun:
        openshift_script = 'syncrator_job_dryrun.sh'
    else:
        openshift_script = 'syncrator_job.sh'

    logger.info(
        "Starting {} job={} for project={} and env={}".format(
            openshift_script, job_type, project, environment))
    stream = os.popen(
        "cd syncrator-openshift && ./{} '{}' '{}' '{}'".format(
            openshift_script, project, environment, job_type))

    job_result = stream.read()

    return jsonify({
        'openshift_script': openshift_script,
        'job_type': job_type,
        'project': project,
        'environment': environment,
        'result': job_result
    })


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Page not found</p>", 404


if __name__ == "__main__":
    app.run(debug=True, port=8080)
