#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_api import status
from viaa.configuration import ConfigParser
from viaa.observability import logging


app = Flask(__name__)
config = ConfigParser()
log = logging.get_logger(__name__, config=config)


@app.route("/health/live")
def liveness_check() -> str:
    return "OK", status.HTTP_200_OK

@app.route("/sync/jobs", methods=['GET'])
def list_jobs() -> str:
    return "TODO: hook into syncrator db and show paginated job list here", status.HTTP_200_OK

@app.route("/sync/jobs/<string:job_id>", methods=['GET'])
def get_job(job_id) -> str:
    return "TODO: hook into syncrator db and show specific job with id={}".format(job_id), status.HTTP_200_OK

@app.route("/sync/<string:project>/<string:environment>", methods=['POST'])
def start_job(project, environment) -> str:
    #TODO: sh syncrator_sync.sh avo qas
    # and return job_id
    return "starting job on project={}, environment={}...".format(project, environment), status.HTTP_200_OK

