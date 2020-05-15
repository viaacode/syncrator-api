#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/run_worker.py
#
import threading
import os
from datetime import datetime


class RunWorker(threading.Thread):
    def __init__(self, request_data, api_job_id, logger):
        threading.Thread.__init__(self)
        self.data = request_data
        self.logger = logger
        self.api_job_id = api_job_id

    def run(self):
        self.logger.info( 'RunWorker starting openshift pod for api_job_id={}'.format(
            self.api_job_id), data=self.data)

        stream = os.popen(
            "cd syncrator-openshift && ./{} '{}' '{}' '{}' '{}' '{}' '{}'".format(
                # self.data['openshift_script'], 
                'syncrator_dryrun.sh',  #for testing temporarely hard code
                self.data['target'], 
                self.data['env'], 
                self.data['action_name'], 
                self.data['action'], 
                self.data['is_tag'], 
                self.data['options']
            )
        )
        job_result = stream.read()

        self.logger.info('RunWorker openshift result = {}'.format(job_result))

        # TODO: some checks in result if something fails then we set ApiJob.status = failed
