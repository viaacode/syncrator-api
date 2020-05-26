# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  file: app/solr_utils.py
#  description: python version of resync_solr.rb in syncrator
#  it methods to make requests to prepare new solr alias before starting a sync job
#
import os
import subprocess

# extra cli command to append for solr sync jobs
SYNCRATOR_SOLR_CLI = '--switch-solr-alias'


#from app.openshift_utils import *

# OS_URL below is OC_URL now
#OC_URL = os.environ.get('OC_URL', 'https://do-prd-okp-m0.do.viaa.be:8443')
#OC_PROJECT_NAME = os.environ.get('OC_PROJECT_NAME', 'shared-components')
#OC_USER = os.environ.get('OC_USER', 'configure_user')
#OC_PASSWORD = os.environ.get('OC_PASSWORD', 'configure_pass')


def job_requires_solr(app):
    if app == 'cataloguspro':
        return True

    if app == 'metadatacatalogus':
        return True

    # avo and future projects won't use solr but ES + indexer
    # which already handles alias switching
    return False


# def modify_alias(name, collections)
#  puts "MODIFY: #{name} #{collections}"
#  uri = URI(
#    SOLR_URL % {
#      command: (COMMAND_TEMPLATE[:modify_alias] % { name: name, collections: collections.join(',') })
#    }
#  )
#  Net::HTTP.get_response(uri)
# end
def modify_alias(name, collections):
    #todo check correctness here for %command
    #SOLR_URL = "{}%{command}&wt=json".format(BASE_SOLR_URL)
    #SOLR_URL = "{}%{}&wt=json".format(BASE_SOLR_URL, command)
    print( "MODIFY: {} {}".format(name,collections))
    # todo: python equivalent from above


def verify_same_collections(alias1, alias2):
    list_collections_of_alias(alias1) == list_collections_of_alias(alias2)

# def list_aliases
#  uri = URI(SOLR_URL % { command: COMMAND_TEMPLATE[:list_aliases] })
#  res = Net::HTTP.get_response(uri)
#  JSON.parse(res.body)['aliases']
# end
def list_aliases():
    #todo check correctness here for %command
    #SOLR_URL = "{}%{command}&wt=json".format(BASE_SOLR_URL)
    #SOLR_URL = "{}%{}&wt=json".format(BASE_SOLR_URL, command)
    print("TODO: translate above...")

    #TODO: translate above request and parse json into res
    res = {
        'aliases':{ 
            'cataloguspro': 'some name1, alias1',
            'cataloguspro-standby': 'standby, alias1',
            'cataloguspro-sync': 'sync, alias1',
        }
    }

    return res['aliases']


# def list_collections_of_alias(name)
#  puts "list collections of alias #{name}"
#  collections = list_aliases[name].split(',')
#  puts "#{collections}"
#  collections
# end
def list_collections_of_alias(name):
    print("list collections of alias {}".format(name))
    collections = list_aliases()[name].split(",")
    print("collections={}", collections)

    return collections


# def delete_standby
#  puts 'Deleting standby Solr before sync'
#  puts '========================'
#  solr_url = BASE_SOLR_URL + STANDBY_ALIAS
#  system "curl #{solr_url}/update --data '<delete><query>*:*</query></delete>' #{CONTENT_TYPE}"
#  system "curl #{solr_url}/update --data '<commit/>' #{CONTENT_TYPE}"
# end

def delete_standby():
    print("TODO translate above")


def sync_to_standby(app, environment):
    print("todo convert below ruby script for app={}, env={}".format(
        app, environment
    ))
    
    #todo most likely move these around into the submethods called...
    CONTENT_TYPE = "-H 'Content-type:text/xml; charset=utf-8'"
    BASE_SOLR_URL = 'http://solr-{}-catalogi.apps.do-prd-okp-m0.do.viaa.be/solr/'.format(environment)


    PRIMARY_ALIAS = "{}".format(app)
    SYNC_ALIAS = "{}-sync".format(app)
    STANDBY_ALIAS = "{}-standby".format(app)

    COMMAND_TEMPLATE = {
        'list_aliases': 'admin/collections?action=LISTALIASES',
        'modify_alias': 'admin/collections?action=CREATEALIAS&name=%{name}&collections=%{collections}'
    }

    # these 2 exceptions will cause sync job not to start
    # which is what we want here, optionally we rescue them later on
    # but don't forget their job is to prevent starting an invalid sync run
    # if solr is not setup right
    if verify_same_collections(PRIMARY_ALIAS, STANDBY_ALIAS):
        #we can add a custom exception class for this later on...
        raise ValueError('Solr standby alias is same as primary alias')

    delete_standby()
    modify_alias(SYNC_ALIAS, list_collections_of_alias(STANDBY_ALIAS))

    # disable until other methods are implemented and stubbed in tests
    #if not verify_same_collections(SYNC_ALIAS, STANDBY_ALIAS):
    #    raise ValueError('-sync tag is still on primary, not on backup')

def prepare_solr_standby(job_params, dryrun=False):
    app = job_params.get('TARGET')
    environment = job_params.get('ENV')

    if job_requires_solr(app):
        job_params['OPTIONS'] = '{} {}'.format( 
            job_params.get('OPTIONS'),
            SYNCRATOR_SOLR_CLI 
        )
        if not dryrun:
            sync_to_standby(app, environment)

    return job_params



