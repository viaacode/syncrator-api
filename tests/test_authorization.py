# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_authorization.py
#
from app.authorization import get_token, verify_token
from pytest import mark


def test_jwt():
    jwt_token = "eyJ0eXAiOiJKV1QiLCJraWQiOiIwMDAxIiwiYWxnIjoiSFMyNTYifQ."
    jwt_token += "eyJzdWIiOiIzMTU3ZmZlZS0xOWE4LTEwM2EtOGIyMi1jYjA0NDgzM2E4"
    jwt_token += "YTMiLCJtYWlsIjoic2NocmVwcGVyc0BnbWFpbC5jb20iLCJjbiI6Ildh"
    jwt_token += "bHRlciBTY2hyZXBwZXJzIiwibyI6IjEwMDE3IiwiYXVkIjpbIm9yZ2Fu"
    jwt_token += "aXNhdGlvbl9hcGkiLCJhZG1pbnMiLCJzeW5jcmF0b3ItYXBpIiwiYXZv"
    jwt_token += "IiwiYWNjb3VudC1tYW5hZ2VyIiwiaGV0YXJjaGllZiJdLCJleHAiOjE2"
    jwt_token += "MDQ0MjAxMjIsImlzcyI6IlZJQUEiLCJqdGkiOiJhNTBmMmY4NmFmN2Mw"
    jwt_token += "MjM2YzQ5NjViMmJhM2MzOTNhZiJ9.phTAC1ovxal00tLICK17VxJBXYl"
    jwt_token += "oYVMBgx-qJuh5Ai4"
    assert verify_token('Bearer ' + jwt_token)


def test_wrong_credentials():
    result = get_token("user", "pass")
    assert result == {'error': 'wrong username or password'}


@mark.skip(reason="TODO: turn off testing env + check a call returns 401")
def test_unauthorized_call():
    assert True
