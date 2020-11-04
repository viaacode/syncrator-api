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
    jwt_token += "eyJzdWIiOiIzMTU3ZmZlZS0xOWE4LTEwM2EtOGIyMi1jYjA0NDgzM2"
    jwt_token += "E4YTMiLCJtYWlsIjoic2NocmVwcGVyc0BnbWFpbC5jb20iLCJjbiI6"
    jwt_token += "IldhbHRlciBTY2hyZXBwZXJzIiwibyI6IjEwMDE3IiwiYXVkIjpbIm"
    jwt_token += "9yZ2FuaXNhdGlvbl9hcGkiLCJhZG1pbnMiLCJzeW5jcmF0b3IiLCJh"
    jwt_token += "dm8iLCJhY2NvdW50LW1hbmFnZXIiLCJoZXRhcmNoaWVmIiwic3luY3"
    jwt_token += "JhdG9yLWFwaSJdLCJleHAiOjE2MDQ1MDQzODUsImlzcyI6IlZJQUEi"
    jwt_token += "LCJqdGkiOiI3ZGU4MjM1NjM1ZWE0OTA2NTE1ODQxMWE3ZDJiOTk4MC"
    jwt_token += "J9.jCDOO3FxGsrMQxXUcTleIdEt2EvMc4eBRmuSnarTEST"

    assert verify_token('Bearer ' + jwt_token)


def test_wrong_credentials():
    result = get_token("user", "pass")
    assert result == {'error': 'wrong username or password'}


@mark.skip(reason="TODO: turn off testing env + check a call returns 401")
def test_unauthorized_call():
    assert True
