#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_api import status
from app.app import *
import pytest

# have app context available in tests
@pytest.fixture
def app_context():
    with app.app_context():
        yield

def test_home():
    assert home()[1] == status.HTTP_200_OK


def test_liveness_check():
    assert liveness_check() == ('OK', status.HTTP_200_OK)


def test_dryrun_job():
    result = dryrun_job('avo', 'qas')

    assert 'Starting synchronisation job on project=avo, environment=qas...' in result[0]
    assert '>>> DRYRUN used' in result[0]
    assert 'params file result' in result[0]
    assert 'template result' in result[0]
    assert result[1] == status.HTTP_200_OK


def test_list_jobs():
    client = app.test_client()
    res = client.get('/jobs')

    assert res.get_json() == [
                  {
                    "id": 1, 
                    "progress": 30, 
                    "running": True
                  }, 
                  {
                    "id": 2, 
                    "progress": 100, 
                    "running": False
                  }
                ]


def test_get_job():
    client = app.test_client()
    res = client.get('/jobs/22')

    assert res.get_json() == {
                  "id": 22, 
                  "progress": 20, 
                  "running": True
                }

# this will actually fire up a syncrator run now, todo make this also dryrun?
# def test_start_job():
#    assert start_job('avo', 'qas') == ('started job on project=avo, environment=qas...', status.HTTP_200_OK)

