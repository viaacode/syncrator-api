#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_api import status
from app.app import liveness_check, start_job, list_jobs, get_job, home


def test_home():
    assert home()[1] == status.HTTP_200_OK

def test_liveness_check():
    assert liveness_check() == ('OK', status.HTTP_200_OK)

def test_start_job():
    assert start_job('avo', 'qas') == ('starting job on project=avo, environment=qas...', status.HTTP_200_OK)

def test_list_jobs():
    assert list_jobs() == ('TODO: hook into syncrator db and show paginated job list here', status.HTTP_200_OK)

def test_get_job():
    assert get_job('1234') == ('TODO: hook into syncrator db and show specific job with id=1234', status.HTTP_200_OK)

