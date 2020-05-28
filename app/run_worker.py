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
from app.openshift_utils import oc_create_syncrator_pod

class RunWorker(threading.Thread):
    def __init__(self, api_job_id, job_params, logger):
        threading.Thread.__init__(self)
        self.api_job_id = api_job_id
        self.job_params = job_params
        self.logger = logger

    def run(self):
        self.logger.info('Runworker creating syncrator pod', data={
            'api_job_id': self.api_job_id,
            'job_params': self.job_params
        })

        # syncrator pod will update the api_job.status first with "running"
        # later on with "completed" or "failed" etc.
        result = oc_create_syncrator_pod(self.job_params)

        self.logger.info( 
            'RunWorker for api_job_id={} succesfully started syncrator'.format(
            self.api_job_id), data=result)

