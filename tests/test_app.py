#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_api import status
from app.syncrator_api import *
import pytest

# have app context available in tests


@pytest.fixture
def app_context():
    with app.app_context():
        yield


def test_home():
    assert home()[1] == status.HTTP_200_OK


def test_liveness_check():
    client = app.test_client()
    res = client.get('/health/live')

    assert res.data == b'OK'
    assert res.status_code == status.HTTP_200_OK


def test_dryrun_job():
    result = dryrun_job('avo', 'qas')

    assert 'Starting synchronisation job on project=avo, environment=qas...' in result[0]
    assert 'Syncrator DRYRUN' in result[0]
    assert 'TARGET=avo' in result[0]
    assert 'ACTION=sync' in result[0]
    assert 'name: syncrator-qas-avo-sync' in result[0]
    assert result[1] == status.HTTP_200_OK


# todo test db setup here for testing...
def test_list_jobs():
    client = app.test_client()
    res = client.get('/jobs')

    #assert res.get_json() == ''
    assert res.status_code == 400
    

def test_get_job():
    client = app.test_client()
    res = client.get('/jobs/22')
    assert res.status_code == 400 #normal because db does not connect


# this will actually fire up a syncrator run now, todo make this also dryrun?
# def test_start_job():
#    assert start_job('avo', 'qas') == ('started job on project=avo, environment=qas...', status.HTTP_200_OK)
