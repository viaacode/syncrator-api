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
