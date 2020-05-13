#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_api import status
from app.syncrator_api import *
from app.models import *
from .fixtures import *
import tempfile
import pytest
import warnings
from sqlalchemy import exc as sa_exc


@pytest.fixture(scope="module")
def setup():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        jobs_fixture(db)

    yield setup


@pytest.fixture(scope="module")
def teardown():
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


@pytest.fixture
def client():
    with app.test_client() as client:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=sa_exc.SAWarning)
            yield client


def test_home(client):
    assert home()[1] == status.HTTP_200_OK


def test_liveness_check(client):
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


def test_list_jobs(client, setup):
    res = client.get('/jobs')

    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_get_unknown_job(client, setup):
    res = client.get('/jobs/123')
    assert res.status_code == 404


def test_get_existing_job(client, setup):
    res = client.get('/jobs/1')
    assert res.get_json()['completed']
    assert res.get_json()['data_source'] == 'mam harvester-AvO'


# this will actually fire up a syncrator run now, todo make this also dryrun?
# def test_start_job():
#    assert start_job('avo', 'qas') == ('started job on project=avo, environment=qas...', status.HTTP_200_OK)
