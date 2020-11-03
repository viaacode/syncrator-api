# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  file: app/authorization.py
# description: methods to get jwt token and validate/authenticate token in
# requests

import os
import requests
import jwt

OAS_SERVER = os.environ.get('OAS_SERVER', 'https://oas-qas.hetarchief.be')
OAS_APPNAME = os.environ.get('OAS_APPNAME', 'syncrator-api')


def get_token(username, password):
    token_url = "{}/token".format(OAS_SERVER)
    token_params = {
        'grant_type': 'client_credentials',
    }
    result = requests.get(
        token_url, data=token_params, auth=(
            username, password))

    if result.status_code == 401:
        return {'error': 'wrong username or password'}
    else:
        return result.json()


def verify_token(jwt_token):
    # future TODO: validate token signature with call to be provided by Herwig.
    dt = jwt.decode(jwt_token, verify=False)
    allowed_apps = dt.get('aud')
    return OAS_APPNAME in allowed_apps
