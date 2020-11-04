# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  file: app/authorization.py
# description: methods to get jwt token and validate/authenticate token in
# requests a decorater is also defined called requires_authorization

import os
import requests
import jwt

from functools import wraps
from flask import request, abort

OAS_SERVER = os.environ.get('OAS_SERVER', 'https://oas-qas.hetarchief.be')
OAS_APPNAME = os.environ.get('OAS_APPNAME', 'syncrator')


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


def verify_token(auth_token):
    # future TODO: validate token signature with an extra api call to be
    # provided by Herwig.
    try:
        if 'Bearer' not in auth_token:
            return False

        # first strip 'Bearer ' from auth_token string to get jwt token
        jwt_token = auth_token.strip().replace("Bearer ", "")

        # decode token and check allowed apps contains our OAS_APPNAME
        dt = jwt.decode(jwt_token, verify=False)
        allowed_apps = dt.get('aud')
        return OAS_APPNAME in allowed_apps
    except jwt.exceptions.DecodeError:
        return False


# decorator verifies token authenticity
def requires_authorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        jwt_token = request.headers.get('authorization')

        # for GET requests, no token is required
        if request.method == 'GET':
            return f(*args, **kwargs)

        # for testing environment also disable auth token checking
        # if os.environ.get('FLASK_ENV') == 'TESTING':
        #    return f(*args, **kwargs)

        # for PUT, POST, DELETE require jwt_token as this creates/destroys
        # actual syncrator jobs
        if not jwt_token or not verify_token(jwt_token):
            abort(401)

        return f(*args, **kwargs)
    return decorated
