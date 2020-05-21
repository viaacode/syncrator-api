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
from app.openshift_utils import oc_create_syncrator_pod
from app.models import *

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
       
        result = oc_create_syncrator_pod( self.job_params )
        
        # TODO: maybe add some checks in result if something fails 
        # then we set ApiJob.status = failed
        # we can do this conveniently using passed api_job_id here

        # problem, we have no valid db session here!
        #api_job = ApiJob.query.filter_by(id=api_job_id).first()
        #api_job.status = "started"
        #db.session.commit()

        self.logger.info( 'RunWorker for api_job_id={} succesfully started syncrator'.format(self.api_job_id), data=result)


       
