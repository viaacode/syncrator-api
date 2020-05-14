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
    page += '<li> POST /delete/&lt;project>/&lt;env>             - start a new delete synchronisation job</li>'

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


# GET /sync/avo/qas does dryrun
@app.route("/sync/<string:project>/<string:environment>", methods=['GET'])
def dryrun_sync_job(project, environment):
    return dryrun_job(project, environment, 'sync')

# POST /sync/avo/qas creates openshift pod and executes job
@app.route("/sync/<string:project>/<string:environment>", methods=['POST'])
def start_sync_job(project, environment):
    return start_job(project, environment, 'sync')

# GET /delta/avo/qas does dryrun
@app.route("/delta/<string:project>/<string:environment>", methods=['GET'])
def dryrun_delta_job(project, environment):
    return dryrun_job(project, environment, 'delta')

# POST /delta/avo/qas creates openshift pod and executes job
@app.route("/delta/<string:project>/<string:environment>", methods=['POST'])
def start_delta_job(project, environment):
    return start_job(project, environment, 'delta')

# GET /delete/avo/qas does dryrun
@app.route("/delete/<string:project>/<string:environment>", methods=['GET'])
def dryrun_delete_job(project, environment):
    return dryrun_job(project, environment, 'delete')

# POST /delete/avo/qas creates openshift pod and executes job
@app.route("/delete/<string:project>/<string:environment>", methods=['POST'])
def start_delete_job(project, environment):
    return start_job(project, environment, 'delete')



# run alternate script that echo's all commands that will be run using oc cli
def dryrun_job(project, environment, job_type):
    logger.info( "Dryrun for project={} and env={} job_type={}".format(project, environment, job_type))
    stream = os.popen( "cd syncrator-openshift && ./syncrator_job_dryrun.sh {} {} {}".format(
            project, environment, job_type
        )
    )
    dryrun_result = stream.read()

    return "Dryrun {} job on project={}, environment={}...<br/>\n <pre>{}</pre>".format(
        job_type, project, environment, dryrun_result), status.HTTP_200_OK

# run actual startup script that runs real oc commands to create pod and start a sync, delta or delete job_type
def start_job(project, environment, job_type):
    logger.info("Starting openshift pod for project={} and env={}".format(project, environment))
    stream = os.popen( "cd syncrator-openshift && ./syncrator_job.sh {} {} {}".format(
            project, environment, job_type
        )
    )
    job_result = stream.read()

    return "Starting {} job on project={}, environment={}, result={}...".format(
        job_type, project, environment, job_result), status.HTTP_200_OK


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Page not found</p>", 404


if __name__ == "__main__":
    app.run(debug=True, port=8080)
