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
import base64

from functools import wraps
from flask import request, abort

OAS_SERVER = os.environ.get('OAS_SERVER', 'https://oas-qas.hetarchief.be')
OAS_APPNAME = os.environ.get('OAS_APPNAME', 'syncrator')
OAS_JWT_SECRET = os.environ.get('OAS_JWT_SECRET', '')


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


def skip_signature_check():
    return len(OAS_JWT_SECRET) == 0


def verify_token(auth_token):
    try:
        if 'Bearer' not in auth_token:
            return False

        # first strip 'Bearer ' from auth_token string to get jwt token
        jwt_token = auth_token.strip().replace("Bearer ", "")

        # we only validate signature if OAS_JWT_SECRET is supplied
        if skip_signature_check():
            print(
                "WARNING skipping jwt verification, configure OAS_JWT_SECRET!",
                flush=True)
            dt = jwt.decode(jwt_token, verify=False)

            # check allowed apps contains our OAS_APPNAME
            allowed_apps = dt.get('aud')
            return OAS_APPNAME in allowed_apps
        else:
            # jwt_secret we base64 decode as bytes and remove EOF marker
            # and extra padding added in case secret len is not multiple of 4
            jwt_secret = base64.b64decode(
                OAS_JWT_SECRET.encode()+b'===').replace(
                b'\x1a', b'')

            # this not only checks signature but also if audience 'aud'
            # contains syncrator
            dt = jwt.decode(
                jwt_token,
                jwt_secret,
                audience=['syncrator'],
                algorithms=['HS256'])
            return True

    except jwt.exceptions.DecodeError as de:
        print(f"caught decode error de={de}", flush=True)
        return False
    except jwt.exceptions.ExpiredSignatureError:
        print("jwt token is expired", flush=True)
        return False
    except jwt.exceptions.InvalidAudienceError:
        print("invalid audience in jwt token.", flush=True)
        return False


# decorator verifies token authenticity
def requires_authorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        jwt_token = request.headers.get('authorization')

        # for GET requests, no token is required
        if request.method == 'GET':
            return f(*args, **kwargs)

        # for PUT, POST, DELETE require jwt_token as this creates/destroys
        # actual syncrator jobs
        if not jwt_token or not verify_token(jwt_token):
            abort(401)

        return f(*args, **kwargs)
    return decorated
