# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  file: app/models.py
#  description: Database models for tables 'syncs' and 'api_jobs'
#  syncrator itself manages syncs table but it can also be views through api here.
#  api_jobs entries are created before starting an actual job and the sync_id is
#  filled in by syncrator when the job starts.
#

from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class SyncJob(db.Model):
    __tablename__ = 'syncs'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())
    data_source = db.Column(db.String())
    type = db.Column(db.String())
    total_records = db.Column(db.Numeric())
    completed = db.Column(db.Boolean())
    options = db.Column(db.String())
    version = db.Column(db.String())
    target_datastore_url = db.Column(db.String())

    def __init__(self, start_time, end_time, data_source, type,
                 total_records, completed, options,
                 version, target_datastore_url):
        self.start_time = start_time
        self.end_time = end_time
        self.data_source = data_source
        self.type = type
        self.total_records = total_records
        self.completed = completed
        self.options = options
        self.version = version
        self.target_datastore_url = target_datastore_url

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_dict(self, filter_passwords=False):
        """Export sync job to dictionary for later jsonify to work."""
        try:
            total_records = int(self.total_records)
        except TypeError:
            total_records = 0

        sync_dict = {
            'id': self.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'data_source': self.data_source,
            'type': self.type,
            'total_records': total_records,
            'completed': self.completed,
            'options': self.options,
            'version': self.version,
            'target_datastore_url': self.target_datastore_url,
        }

        # 'postgres://dbmaster:dbmaster_pass@postgresql-qas.sc-avo2.svc:5432/avo_qas'
        if filter_passwords:
            db_url = sync_dict['target_datastore_url']
            sync_dict['target_datastore_url'] = '{}<FILTERED>{}'.format(
                db_url[:db_url.find('://') + 3],
                db_url[db_url.find('@'):]
            )
        return sync_dict


class ApiJob(db.Model):
    __tablename__ = 'api_jobs'

    id = db.Column(db.Integer, primary_key=True)
    sync_id = db.Column(db.Integer)  # foreign key to SyncJob

    # we keep these handy to reject concurrent jobs running on same
    # environment and target
    target = db.Column(db.String())     # avo, metadata_catalogus, ...
    env = db.Column(db.String())        # qas, prd, ...
    job_type = db.Column(db.String())   # sync, delta, delete, diff
    status = db.Column(db.String())     # starting, running, completed, failed
    job_params = db.Column(db.JSON())   # params passed in api call

    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())

    def __init__(self, sync_id, target, env, job_type, job_params, status):
        self.sync_id = sync_id
        self.target = target
        self.env = env
        self.job_type = job_type
        self.job_params = job_params
        self.status = status
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_dict(self):
        """Export api job to dictionary for later jsonify to work."""
        return {
            'id': self.id,
            'sync_id': self.sync_id,
            'target': self.target,
            'env': self.env,
            'job_type': self.job_type,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
