#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_app.py
#

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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=sa_exc.SAWarning)
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
        yield client


def test_home(client):
    res = client.get('/')
    assert res.status_code == status.HTTP_200_OK
    assert b'Syncrator-API' in res.data


def test_liveness_check(client):
    res = client.get('/health/live')

    assert res.data == b'OK'
    assert res.status_code == status.HTTP_200_OK


def test_dryrun_sync_job(client):
    res = client.get('/sync/avo/qas')
    assert res.status_code == status.HTTP_200_OK

    job = res.get_json()
    assert job['environment'] == 'qas'
    assert job['job_type'] == 'sync'
    assert job['project'] == 'avo'
    assert 'DRYRUN' in job['result']
    assert 'name: syncrator-qas-avo-sync' in job['result']
    assert 'TARGET=avo' in job['result']
    assert 'ACTION=sync' in job['result']
    assert 'syncrator sync -n 1000 -c 1' in job['result']


def test_dryrun_delta_job(client):
    res = client.get('/delta/avo/qas')
    assert res.status_code == status.HTTP_200_OK

    job = res.get_json()
    assert job['environment'] == 'qas'
    assert job['job_type'] == 'delta'
    assert job['project'] == 'avo'
    assert 'DRYRUN' in job['result']
    assert 'name: syncrator-qas-avo-delta' in job['result']
    assert 'TARGET=avo' in job['result']
    assert 'ACTION=delta' in job['result']
    assert 'syncrator delta -n 1000 -c 1' in job['result']


def test_dryrun_delete_job(client):
    res = client.get('/delete/avo/qas')
    assert res.status_code == status.HTTP_200_OK

    job = res.get_json()
    assert job['environment'] == 'qas'
    assert job['job_type'] == 'delete'
    assert job['project'] == 'avo'
    assert 'DRYRUN' in job['result']
    assert 'name: syncrator-qas-avo-delete' in job['result']
    assert 'TARGET=avo' in job['result']
    assert 'ACTION=delete' in job['result']
    assert 'syncrator delete --debug' in job['result']


def test_dryrun_generic_run(client):
    res_generic = client.post('/dryrun',
                              json={
                                  'target': 'avo',
                                  'env': 'qas',
                                  'action_name': 'delta',
                                  'action': 'delta',
                                  'is_tag': 'latest',
                                  'options': '-n 1000 -c 1',
                              })
    assert res_generic.status_code == status.HTTP_200_OK
    generic_data = res_generic.get_json()

    res_delta = client.get('/delta/avo/qas')
    assert res_delta.status_code == status.HTTP_200_OK
    delta_data = res_delta.get_json()

    # test that a generic run call with correct params gives same
    # result as a preconfigred delta run (both dryruns)
    assert generic_data['env'] == delta_data['environment']
    assert generic_data['target'] == delta_data['project']

    # get substring in result with only the template generated from dryruns
    gen_template = generic_data['result'][generic_data['result'].find(
        'parametrised template'):]
    delta_template = delta_data['result'][delta_data['result'].find(
        'parametrised template'):]

    assert gen_template == delta_template


def test_password_filter_api_job_nested(client, setup):
    res = client.get('/jobs/2')
    sjob = res.get_json()

    assert res.status_code == 200
    assert 'dbmaster_pass' not in sjob['sync_job']['target_datastore_url']
    assert 'dbmaster' not in sjob['sync_job']['target_datastore_url']


def test_list_api_jobs(client, setup):
    res = client.get('/jobs')

    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_list_sync_jobs_and_pass_filter(client, setup):
    res = client.get('/sync_jobs')
    sjobs = res.get_json()

    for sjob in sjobs:
        assert 'dbmaster_pass' not in sjob['target_datastore_url']
        assert 'dbmaster' not in sjob['target_datastore_url']

    assert res.status_code == 200
    assert len(sjobs) == 4


def test_get_unknown_job(client, setup):
    res = client.get('/jobs/123')
    assert res.status_code == 404


def test_get_existing_starting_job(client, setup):
    res = client.get('/jobs/1')
    assert res.get_json()['status'] == 'starting'
    assert res.get_json()['sync_id'] is None


def test_get_existing_completed_job(client, setup):
    res = client.get('/jobs/2')
    assert res.get_json()['status'] == 'completed'
    assert res.get_json()['sync_job']['completed']
    assert res.get_json()['sync_job']['data_source'] == 'mam harvester-AvO'


# this will actually fire up a syncrator run now, todo make this also dryrun?
# def test_start_job():
#    assert start_job('avo', 'qas') == ('started job on project=avo, environment=qas...', status.HTTP_200_OK)
