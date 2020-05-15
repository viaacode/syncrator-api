# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/fixtures.py
#
from app.models import *
import datetime


def jobs_fixture(db):

    # sync job completed
    db.session.add(
        SyncJob(
            completed=True,
            start_time=datetime.datetime.utcnow(),
            end_time=datetime.datetime.utcnow(),
            data_source='mam harvester-AvO',
            type='sync',
            options='',
            target_datastore_url='postgres://postgres@localhost:5432/avo_qas',
            total_records='19884',
            version='2.4.0'
        )
    )

    # full sync job in progress
    db.session.add(
        SyncJob(
            completed=False,
            start_time=datetime.datetime.utcnow(),
            end_time=datetime.datetime.utcnow(),
            data_source='mam harvester-AvO',
            type='sync',
            options='',
            target_datastore_url='postgres://postgres@localhost:5432/avo_qas',
            total_records='19884',
            version='2.4.0'
        )
    )

    # delta job completed
    db.session.add(
        SyncJob(
            completed=True,
            data_source='mam harvester-AvO',
            start_time=datetime.datetime.utcnow(),
            end_time=datetime.datetime.utcnow(),
            type='delta',
            options="[\"2020-05-11T00:00:00Z\", \"2020-05-14\"]",
            target_datastore_url='postgres://postgres@localhost:5432/avo_qas',
            total_records='5',
            version='2.4.0'
        )
    )

    # delete job completed
    db.session.add(
        SyncJob(
            completed=True,
            data_source='mam harvester-AvO',
            start_time=datetime.datetime.utcnow(),
            end_time=datetime.datetime.utcnow(),
            type='delete',
            options="[\"2020-05-12\", \"2020-05-14\"]",
            target_datastore_url='postgres://postgres@localhost:5432/avo_qas',
            total_records='1',
            version='2.4.0'
        )
    )
    db.session.commit()

    # api job example of starting job where sync_id is not filled in yet
    db.session.add(
        ApiJob(
            sync_id=None,
            target='avo',
            env='qas',
            job_type='sync',
            job_params={'env': 'qas', 'type': 'sync'},
            status='starting'
        )
    )

    db.session.add(
        ApiJob(
            sync_id=SyncJob.query.filter_by(
                data_source='mam harvester-AvO').first().id,
            target='avo',
            env='qas',
            job_type='sync',
            job_params={'env': 'qas', 'type': 'sync'},
            status='running'))

    db.session.commit()
