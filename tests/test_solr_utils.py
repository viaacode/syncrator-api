# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_solr_utils.py
#

import pytest
from flask_api import status
from app.syncrator_api import *
from app.models import *
from app.openshift_utils import *
from app.solr_utils import sync_to_standby, list_aliases

pytestmark = [pytest.mark.vcr(ignore_localhost=True)]


@pytest.fixture(scope="module")
def vcr_config():
    # return {"record_mode": "all"} #do new record, requires vpn connection
    return {"record_mode": "once"}


def test_solr_preperation(client):
    res = client.get('/sync/metadatacatalogus/qas')
    assert res.status_code == 200

    job_params = res.get_json()
    assert '--switch-solr-alias' in job_params['result']

    res = client.get('/sync/cataloguspro/qas')
    assert res.status_code == 200

    job_params = res.get_json()
    assert '--switch-solr-alias' in job_params['result']

    # test for avo we don't need the solr commands
    res = client.get('/sync/avo/qas')
    assert res.status_code == 200

    job_params = res.get_json()
    assert '--switch-solr-alias' not in job_params['result']


@pytest.mark.vcr
def test_list_aliases(client):
    res = list_aliases(
        'http://solr-qas-catalogi.apps.do-prd-okp-m0.do.viaa.be/solr/')
    assert res == {
        'metadatacatalogus-standby': 'metadatacatalogus-2',
        'cataloguspro-standby': 'cataloguspro-1',
        'metadatacatalogus': 'metadatacatalogus-1',
        'cataloguspro': 'cataloguspro-2',
        'metadatacatalogus-sync': 'metadatacatalogus-1',
        'cataloguspro-sync': 'cataloguspro-1'
    }


# solr_base_url == 'http://solr-qas-catalogi.apps.do-prd-okp-m0.do.viaa.be/solr/'
# standby_alias == 'cataloguspro-standby'
@pytest.mark.vcr
def test_sync_to_standby_calls(client):
    res = sync_to_standby('cataloguspro', 'qas')
    assert res
