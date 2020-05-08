#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_api import status
from app.app import *


def test_home():
    assert home()[1] == status.HTTP_200_OK


def test_liveness_check():
    assert liveness_check() == ('OK', status.HTTP_200_OK)

# this will actually fire up a syncrator run now, todo make this also dryrun?
# def test_start_job():
#    assert start_job('avo', 'qas') == ('started job on project=avo, environment=qas...', status.HTTP_200_OK)


def test_dryrun_job():
    result = dryrun_job('avo', 'qas')

    assert 'started job on project=avo, environment=qas...' in result[0]
    assert '>>> DRYRUN used' in result[0]
    assert 'params file result' in result[0]
    assert 'template result' in result[0]
    assert result[1] == status.HTTP_200_OK


def test_list_jobs():
    assert list_jobs() == (
        'TODO: hook into syncrator db and show paginated job list here',
        status.HTTP_200_OK)


def test_get_job():
    assert get_job('1234') == (
        'TODO: hook into syncrator db and show specific job with id=1234',
        status.HTTP_200_OK)
