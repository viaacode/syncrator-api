#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_api import status

from app.app import liveness_check


def test_liveness_check():
    assert liveness_check() == ('OK', status.HTTP_200_OK)
