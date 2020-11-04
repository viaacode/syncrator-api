# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_authorization.py
#
from app.authorization import get_token, verify_token
from .fixtures import jwt_token


def test_jwt():
    assert verify_token(jwt_token())


def test_wrong_credentials():
    result = get_token("user", "pass")
    assert result == {'error': 'wrong username or password'}

# test_app has tests for with/without authorization token now
