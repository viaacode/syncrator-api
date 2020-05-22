#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/syncrator_api.py
#

from app.models import *
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
def destroy_job(job_id):
    try:
        api_job = ApiJob.query.filter_by(id=job_id).first()
        api_job.status = "deleted"
        db.session.commit()

        delete_result = oc_delete_syncrator_pod(
            api_job.env,
            api_job.target,
            api_job.job_type
        )

        logger.info('Delete syncrator pod', data={'result': delete_result})
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
    return run(
        read_params_file(environment, project, 'sync'),
        dryrun=request.method == 'GET'
    )


@app.route("/delta/<string:project>/<string:environment>",
           methods=['GET', 'POST'])
def start_delta_job(project, environment):
    return run(
        read_params_file(environment, project, 'delta'),
        dryrun=request.method == 'GET'
    )


@app.route("/delete/<string:project>/<string:environment>",
           methods=['GET', 'POST'])
def start_delete_job(project, environment):
    return run(
        read_params_file(environment, project, 'delete'),
        dryrun=request.method == 'GET'
    )


@app.route("/diff/<string:project>/<string:environment>",
           methods=['GET', 'POST'])
def start_diff_job(project, environment):
    return run(
        read_params_file(environment, project, 'diff'),
        dryrun=request.method == 'GET'
    )


@app.route("/run", methods=['POST'])
def syncrator_run():
    # POST /run run custom job by passing all template parameters in json
    request_data = request.json
    return run(job_params_from_request())


@app.route("/dryrun", methods=['POST'])
def syncrator_dryrun():
    # POST /dryrun same as run but don't execute only return resulting template
    return run(
        job_params_from_request(),
        dryrun=True
    )


def job_params_from_request():
    request_data = request.json
    return {
        'TARGET': request_data['target'],
        'ENV': request_data['env'],
        'ACTION_NAME': request_data['action_name'],
        'ACTION': request_data['action'],
        'IS_TAG': request_data['is_tag'],
        'OPTIONS': request_data['options']
    }


def create_or_find_job(job_params, dryrun=False):
    if dryrun:
        return 'dryrun'

    # check for existing job
    api_job = ApiJob.query.filter_by(
        target=job_params['TARGET'],
        env=job_params['ENV'],
        job_type=job_params['ACTION']
    ).order_by(
        ApiJob.created_at.desc()
    ).first()

    # return existing running job
    if api_job and (
            api_job.status == 'starting' or api_job.status == 'running'):
        return api_job.id

    # create new one because status is : failed, completed, deleted
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

    return api_job.id


def run(job_params, dryrun=False):
    logger.info('Syncrator run called with parameters', data=job_params)

    # piggy back the job id onto options that are templated as command parameter to syncrator
    # so that syncrator is able to set correct sync_id at startup
    api_job_id = create_or_find_job(job_params, dryrun=dryrun)
    job_params['OPTIONS'] = '{} --api_job_id {}'.format(
        job_params['OPTIONS'],
        api_job_id
    )

    response = job_params.copy()
    if dryrun:
        # run inline and give back dryrun result
        result = oc_create_syncrator_pod(job_params, dryrun=True)
        response['result'] = result
    else:
        syncrator_worker = RunWorker(api_job_id, job_params, logger)
        syncrator_worker.start()
        response['result'] = 'starting'

    response['job_id'] = api_job_id

    return jsonify(response)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Page not found</p>", 404


# if __name__ == "__main__":
#    app.run(debug=True, port=8080)
