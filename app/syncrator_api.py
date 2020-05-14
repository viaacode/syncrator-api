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
            'database_url': app.config.get('SQLALCHEMY_DATABASE_URI')})
    page = '<html><head><style>body{background-color: #fff; color: #333;}</style></head><body>'
    page += '<h1>Syncrator-API</h1>'
    page += '<ul>'
    page += '<li><a href="/jobs?page=1">     GET /jobs </a>    - paginated list of active jobs </li>'
    page += '<li><a href="/jobs/1"> GET /jobs/&lt;id>  </a>    - get job details and progress </li>'
    page += '<li> POST /sync/&lt;project>/&lt;env>             - start a new synchronisation job</li>'
    page += '<li><a href="/sync/avo/qas">GET /sync/avo/qas</a> - job dryrun with openshift template output as result</li></ul>'
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
def dryrun_job(project, environment):
    # GET with /sync/avo/qas does dryrun
    logger.info(
        "Dryrun for project={} and env={} (use POST method to start real job)".format(
            project, environment))
    stream = os.popen(
        "cd syncrator-openshift && ./syncrator_sync_dryrun.sh {} {}".format(project, environment)
    )
    dryrun_result = stream.read()

    return "Starting synchronisation job on project={}, environment={}...<br/>\n <pre>{}</pre>".format(
        project, environment, dryrun_result), status.HTTP_200_OK


@app.route("/sync/<string:project>/<string:environment>", methods=['POST'])
def start_job(project, environment):
    logger.info(
        "Starting openshift pod for project={} and env={}".format(
            project, environment))
    stream = os.popen(
        "cd syncrator-openshift && ./syncrator_sync.sh {} {}".format(project, environment)
    )
    sync_result = stream.read()

    return "Starting synchronisation job on project={}, environment={}, result={}...".format(
        project, environment, sync_result), status.HTTP_200_OK


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Page not found</p>", 404


if __name__ == "__main__":
    app.run(debug=True, port=8080)
