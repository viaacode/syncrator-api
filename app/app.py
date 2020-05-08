#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_api import status
from viaa.configuration import ConfigParser
from viaa.observability import logging
import os


app = Flask(__name__)
config = ConfigParser()
log = logging.get_logger(__name__, config=config)


@app.route("/")
def home():
    # TODO: add some jinja template here
    page = '<h1>Syncrator-API routes</h1>'
    page += '<ul><li>GET /sync/jobs - lists active jobs </li>'
    page += '<li>GET /sync/jobs/&lt;id> - get job details and progress </li>'
    page += '<li>POST /sync/&lt;project>/&lt;env> - start a new job</li>'
    page += '<li><a href="/sync/avo/qas">GET /sync/avo/qas</a> - job dryrun with openshift template output as result</li></ul>'
    page += '<h2>Health check call</h2> GET /health/live'
    return page, status.HTTP_200_OK


@app.route("/health/live")
def liveness_check() -> str:
    return "OK", status.HTTP_200_OK


@app.route("/sync/jobs", methods=['GET'])
def list_jobs() -> str:
    return "TODO: hook into syncrator db and show paginated job list here", status.HTTP_200_OK


@app.route("/sync/jobs/<string:job_id>", methods=['GET'])
def get_job(job_id) -> str:
    return "TODO: hook into syncrator db and show specific job with id={}".format(
        job_id), status.HTTP_200_OK


@app.route("/sync/<string:project>/<string:environment>", methods=['GET'])
def dryrun_job(project, environment) -> str:
    # GET with /sync/avo/qas does dryrun
    stream = os.popen(
        "cd openshift && ./syncrator_sync_dryrun.sh {} {}".format(project, environment))
    dryrun_result = stream.read()

    return "started job on project={}, environment={}...<br/>\n result:<br/> <pre>{}</pre>".format(
        project, environment, dryrun_result), status.HTTP_200_OK


@app.route("/sync/<string:project>/<string:environment>", methods=['POST'])
def start_job(project, environment) -> str:
    # post with /sync/avo/qas does actual job starting!
    stream = os.popen(
        "cd openshift && ./syncrator_sync.sh {} {}".format(project, environment))
    sync_result = stream.read()
    print("result of sync:\n{}".format(sync_result))

    return "started job on project={}, environment={}...".format(
        project,
        environment), status.HTTP_200_OK
