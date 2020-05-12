#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import request, url_for, jsonify
from flask_api import FlaskAPI, status, exceptions
from viaa.configuration import ConfigParser
from viaa.observability import logging
import os


app = FlaskAPI(__name__)
config = ConfigParser()
logger = logging.get_logger(__name__, config=config)

app.config['DATABASE_URL'] = os.environ.get(
    'DATABASE_URL', 'postgres://postgres@localhost:5432/syncrator_dev')
app.config['API_KEY'] = os.environ.get('API_KEY', 'secret123')


@app.route("/")
def home():
    # TODO: add some jinja template here
    logger.info(
        "configuration = ", dictionary={
            'database_url': app.config.get('DATABASE_URL')})
    page = '<html><head><style>body{background-color: #fff; color: #333;}</style></head><body>'
    page += '<h1>Syncrator-API</h1>'
    page += '<ul>'
    page += '<li><a href="/jobs">     GET /jobs         </a>   - lists active jobs </li>'
    page += '<li><a href="/jobs/123"> GET /jobs/&lt;id> </a>   - get job details and progress </li>'
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
    logger.warning(
        "TODO: implement sqlalchemy connect and give back job list table entries")

    jobs = [
        {
            'id': 1,
            'running': True,
            'progress': 30
        },
        {
            'id': 2,
            'running': False,
            'progress': 100
        },

    ]
    return jsonify(jobs)


@app.route("/jobs/<int:job_id>", methods=['GET'])
def get_job(job_id):
    logger.warning("TODO: implement sqlalchemy connect and lookup job entry")
    job = {
        'id': job_id,
        'running': True,
        'progress': 20
    }
    return jsonify(job)


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
