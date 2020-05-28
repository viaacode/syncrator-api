# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  file: app/solr_utils.py
#  description:
#   python version of resync_solr.rb in syncrator
#   it methods to make requests to prepare new solr alias
#   before starting a sync job
#
import requests

OC_SERVER = 'do-prd-okp-m0.do.viaa.be'
SYNCRATOR_SOLR_FLAG = '--switch_solr_alias'
CONTENT_TYPE = {
    'Content-type': 'text/xml; charset=utf-8'
}


def job_requires_solr(app):
    if app == 'cataloguspro':
        return True

    if app == 'metadatacatalogus':
        return True

    # avo and future projects won't use solr but ES + indexer
    # which already handles alias switching
    return False


def modify_alias(base_solr_url, name, collections):
    modify_alias = '{}?{}&name={}&collections={}'.format(
        'admin/collections',
        'action=CREATEALIAS',
        name,
        ",".join(collections)
    )

    modify_alias_url = '{}{}&wt=json'.format(
        base_solr_url,
        modify_alias
    )

    return requests.get(modify_alias_url).json()


def verify_same_collections(base_solr_url, alias1, alias2):
    return (
        list_collections_of_alias(base_solr_url, alias1) ==
        list_collections_of_alias(base_solr_url, alias2)
    )


def list_aliases(base_solr_url):
    list_aliases_url = '{}{}&wt=json'.format(
        base_solr_url,
        'admin/collections?action=LISTALIASES'
    )
    result = requests.get(list_aliases_url).json()

    return result['aliases']


def list_collections_of_alias(base_solr_url, name):
    print("list collections of base_url={} name={}".format(
        base_solr_url,
        name
    ))
    collections = list_aliases(base_solr_url)[name].split(",")
    print("collections={}", collections)

    return collections


def delete_standby(base_solr_url, standby_alias):
    solr_url = "{}{}/update".format(
        base_solr_url,
        standby_alias
    )

    requests.post(
        solr_url,
        data='<delete><query>*:*</query></delete>',
        headers=CONTENT_TYPE
    )

    requests.post(
        solr_url,
        data='<commit/>',
        headers=CONTENT_TYPE
    )


def sync_to_standby(app, environment):
    base_solr_url = 'http://solr-{}-catalogi.apps.{}/solr/'.format(
        environment,
        OC_SERVER
    )
    primary_alias = "{}".format(app)
    sync_alias = "{}-sync".format(app)
    standby_alias = "{}-standby".format(app)

    # these 2 exceptions will cancel sync job check fails before or after
    # delete and modify commands
    if verify_same_collections(base_solr_url, primary_alias, standby_alias):
        # we can add a custom exception class for this later on...
        raise ValueError('Solr standby alias is same as primary alias')

    delete_standby(base_solr_url, standby_alias)
    result = modify_alias(
        base_solr_url,
        sync_alias,
        list_collections_of_alias(base_solr_url, standby_alias)
    )

    # disable until other methods are implemented and stubbed in tests
    if not verify_same_collections(base_solr_url, sync_alias, standby_alias):
        raise ValueError(
            '-sync tag is still on primary, '
            f'not on backup sync_alias={sync_alias} '
            f'standby_alias={standby_alias}'
        )

    return result


def prepare_solr_standby(job_params, dryrun=False):
    app = job_params.get('TARGET')
    environment = job_params.get('ENV')

    if job_requires_solr(app):
        job_params['OPTIONS'] = '{} {}'.format(
            job_params.get('OPTIONS'),
            SYNCRATOR_SOLR_FLAG
        )
        if not dryrun:
            sync_to_standby(app, environment)

    return job_params
