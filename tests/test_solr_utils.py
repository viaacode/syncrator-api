# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_solr_utils.py
#
import pytest
from app.solr_utils import sync_to_standby, list_aliases

pytestmark = [pytest.mark.vcr(ignore_localhost=True)]


@pytest.fixture(scope="module")
def vcr_config():
    # return {"record_mode": "all"} #do new record, requires vpn connection
    return {"record_mode": "once"}


def test_solr_preperation(client):
    res = client.get('/sync/metadatacatalogus')
    assert res.status_code == 200

    job_params = res.get_json()
    assert '--switch_solr_alias' in job_params['result']

    res = client.get('/sync/cataloguspro')
    assert res.status_code == 200

    job_params = res.get_json()
    assert '--switch_solr_alias' in job_params['result']
    assert '--target cataloguspro' in job_params['result']
    assert '--target_env qas' in job_params['result']

    # test for avo we don't need the solr commands
    res = client.get('/sync/avo')
    assert res.status_code == 200

    job_params = res.get_json()
    assert '--switch_solr_alias' not in job_params['result']


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


@pytest.mark.vcr
def test_sync_to_standby_calls(client):
    res = sync_to_standby('cataloguspro', 'qas')
    assert res
