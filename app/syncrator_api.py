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
from app.openshift_utils import *

from flask import Flask, request, url_for, jsonify, render_template
from flask_api import status, exceptions
from viaa.configuration import ConfigParser
from viaa.observability import logging
from sqlalchemy.exc import OperationalError
from app.config import flask_environment
import os

app = Flask(__name__)
config = ConfigParser()
logger = logging.get_logger(__name__, config=config)

app.config.from_object(flask_environment())
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/', methods=['GET'])
def index():
    logger.info(
        "configuration = ", dictionary={
            'environment': flask_environment()
        })
    return render_template('index.html')


@app.route("/health/live")
def liveness_check():
    return "OK", status.HTTP_200_OK


@app.route("/jobs", methods=['GET'])
def list_api_jobs():
    try:
        page = request.args.get('page', 1, type=int)
        rows = ApiJob.query.order_by(
            ApiJob.created_at.desc()
        ).paginate(page, app.config['JOBS_PER_PAGE'], False).items
        api_jobs = [j.to_dict() for j in rows]
        return jsonify(api_jobs)
    except OperationalError as pg:
        return "database error: {}".format(str(pg)), 400


@app.route("/jobs/<int:job_id>", methods=['GET'])
def get_job(job_id):
    try:
        api_job = ApiJob.query.filter_by(id=job_id).first()
        result = api_job.to_dict()
        if api_job.sync_id:
            sync_job = SyncJob.query.filter_by(id=api_job.sync_id).first()
            result['sync_job'] = sync_job.to_dict(filter_passwords=True)

        return jsonify(result)
    except AttributeError:
        return "not found", 404
    except OperationalError as pg:
        return "database error: {}".format(str(pg)), 400


@app.route("/jobs/<int:job_id>", methods=['DELETE'])
def delete_job(job_id):
    try:
        api_job = ApiJob.query.filter_by(id=job_id).first()
        api_job.status = "deleted"
        db.session.commit()

        oc_login()

        oc_logout()

        # noticed a design flaw, the session can be lost in between commands by
        # chaining it should work again
        cmd = oc_login()
        cmd += " ; " + oc_delete_job(
            "syncrator-{}-{}-{}".format(
                api_job.env,
                api_job.target,
                api_job.job_type
            )
        )
        # watch out use ; here instead of && in case delete does not find a
        # previous pod job
        cmd += " ; " + oc_logout()

        oc_execute(cmd)

        return jsonify(api_job.to_dict())

    except AttributeError:
        return "not found", 404
    except OperationalError as pg:
        return "database error: {}".format(str(pg)), 400


@app.route("/sync_jobs", methods=['GET'])
def list_sync_jobs():
    try:
        page = request.args.get('page', 1, type=int)
        rows = SyncJob.query.order_by(
            SyncJob.start_time.desc()
        ).paginate(page, app.config['JOBS_PER_PAGE'], False).items
        jobs = [j.to_dict(filter_passwords=True) for j in rows]
        return jsonify(jobs)
    except OperationalError as pg:
        return "database error: {}".format(str(pg)), 400


@app.route("/sync/<string:project>/<string:environment>",
           methods=['GET', 'POST'])
def start_sync_job(project, environment):
    do_dryrun_only = request.method == 'GET'
    return start_job(project, environment, 'sync', dryrun=do_dryrun_only)


@app.route("/delta/<string:project>/<string:environment>",
           methods=['GET', 'POST'])
def start_delta_job(project, environment):
    do_dryrun_only = request.method == 'GET'
    return start_job(project, environment, 'delta', dryrun=do_dryrun_only)


@app.route("/delete/<string:project>/<string:environment>",
           methods=['GET', 'POST'])
def start_delete_job(project, environment):
    do_dryrun_only = request.method == 'GET'
    return start_job(project, environment, 'delete', dryrun=do_dryrun_only)


@app.route("/diff/<string:project>/<string:environment>",
           methods=['GET', 'POST'])
def start_diff_job(project, environment):
    do_dryrun_only = request.method == 'GET'
    return start_job(project, environment, 'diff', dryrun=do_dryrun_only)


@app.route("/run", methods=['POST'])
def syncrator_run():
    # POST /run run custom job by passing all template parameters in json
    return run()


@app.route("/dryrun", methods=['POST'])
def syncrator_dryrun():
    # POST /dryrun same as run but don't execute only return resulting template
    return run(dryrun=True)


# test out python version that is shorter and allows elimination of
# the 4 shell scripts
@app.route("/runp", methods=['POST'])
def syncrator_run_python():
    # POST /run run custom job by passing all template parameters in json
    return runp()

# generic run method needs all parameters for syncrator as json in post request
# these are target, env, action_name, action, is_tag and options. look in
# syncrator-openshift/job_params for examples


# this version will replace the next 2 longer existing run functions once we test it works, it uses straight
# python to execute the necessary oc commands
def runp(dryrun=False):
    request_data = request.json

    job_params = {
        'TARGET': request_data['target'],
        'ENV': request_data['env'],
        'ACTION_NAME': request_data['action_name'],
        'ACTION': request_data['action'],
        'IS_TAG': request_data['is_tag'],
        'OPTIONS': request_data['options']
    }

    api_job_id = 'dryrun, no actual id available'
    if not dryrun:
        # TODO: check if there is a job started or running here before creating
        # another
        api_job = ApiJob(
            sync_id=None,
            target=job_params['TARGET'],
            env=job_params['ENV'],
            job_type=job_params['ACTION'],
            job_params=job_params,
            status='starting'
        )
        db.session.add(api_job)
        db.session.commit()
        api_job_id = api_job.id

        # piggy back the job id onto options that are templated as command parameter to syncrator
        # so that syncrator is able to set correct sync_id at startup
        job_params['OPTIONS'] = '{} -api_job_id {}'.format(
            job_params['OPTIONS'],
            api_job_id
        )

    # TODO: move this into a worker once tested and then deprecate
    # other workers
    # handle execution in a worker thread
    # syncrator_worker = RunWorker(request_data, api_job.id, logger)
    # syncrator_worker.start()

    # noticed a design flaw, the session can be lost in between commands by
    # chaining it should work again
    cmd = oc_login()
    cmd += " ; " + oc_delete_job(
        "syncrator-{}-{}-{}".format(
            job_params['ENV'],
            job_params['TARGET'],
            job_params['ACTION']
        )
    )
    # gotcha the delete might fail if not are found!
    cmd += " ; " + oc_create_job(job_params)
    cmd += " ; " + oc_logout()

    logger.info("command to execute=", data={'oc_commands': cmd})

    result = oc_execute(cmd, dryrun=dryrun)

    job_params['result'] = result
    job_params['job_id'] = api_job_id

    logger.info('Syncrator run called with parameters', data=request_data)

    return jsonify(job_params)


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

        # TODO: check if there is a job started or running here before creating
        # new one
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

        # TODO: check if there is a job started or running here before creating
        # new one
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
