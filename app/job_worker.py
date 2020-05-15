#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/job_worker.py
#
import threading
import os
from datetime import datetime


class JobWorker(threading.Thread):

    def __init__(self, request_data, api_job_id, logger):
        threading.Thread.__init__(self)
        self.data = request_data
        self.logger = logger
        self.api_job_id = api_job_id

    def run(self):
        self.logger.info( 'JobWorker starting openshift pod api_job_id={}'.format(
            self.api_job_id), data=self.data)

        stream = os.popen(
            "cd syncrator-openshift && ./{} '{}' '{}' '{}'".format(
                # self.data['openshift_script'], 
                'syncrator_job_dryrun.sh', #for testing tempararely hardcoe to dryrun
                self.data['project'], 
                self.data['environment'], 
                self.data['job_type']
        ))
        job_result = stream.read()

        self.logger.info('JobWorker openshift result = {}'.format(job_result))

        # TODO: some checks in result if something fails then we set ApiJob.status = failed
