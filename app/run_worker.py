#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  file: app/run_worker.py
#  description: threaded worker to asynchronously create syncrator pod and run
#  some setup solr calls for catalogus and metadatacatalogs.
#

import threading
import os
from datetime import datetime
from app.openshift_utils import oc_create_syncrator_pod
from app.models import *
from app.solr_utils import prepare_solr_standby

class RunWorker(threading.Thread):
    def __init__(self, api_job_id, job_params, logger):
        threading.Thread.__init__(self)
        self.api_job_id = api_job_id
        self.job_params = job_params
        self.logger = logger

    def job_requires_solr(self):
        if self.job_params.get('TARGET') == 'cataloguspro':
            return True

        if self.job_params.get('TARGET') == 'metadatacatalogus':
            return True

        # avo and future projects won't use solr but ES + indexer
        # which already handles alias switching
        return False


    def run(self):
        if self.job_requires_solr():
            prepare_solr_standby(
                self.job_params.get('TARGET'),
                self.job_params.get('ENV')
            )
            print('TODO add cli param to syncrator options to perform switch_aliases_solr.rb')

        self.logger.info('Runworker creating syncrator pod', data={
            'api_job_id': self.api_job_id,
            'job_params': self.job_params
        })
 
        # syncrator pod will update the api_job.status first with "running"
        # later on with "completed" or "failed" etc.
        result = oc_create_syncrator_pod( self.job_params )

        self.logger.info( 'RunWorker for api_job_id={} succesfully started syncrator'.format(
            self.api_job_id), data=result)


       
