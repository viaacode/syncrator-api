from app.models import *
import datetime


def jobs_fixture(db):
    db.session.add(
        SyncJobs(
            completed=True,
            start_time=datetime.datetime.utcnow(),
            end_time=datetime.datetime.utcnow(),
            data_source='mam harvester-AvO',
            type='sync',
            options='',
            target_datastore_url='postgres://postgres@localhost:5432/avo_qas',
            total_records='19884',
            version='2.4.0'))

    db.session.add(
        SyncJobs(
            completed=False,
            start_time=datetime.datetime.utcnow(),
            end_time=datetime.datetime.utcnow(),
            data_source='mam harvester-AvO',
            type='sync',
            options='',
            target_datastore_url='postgres://postgres@localhost:5432/avo_qas',
            total_records='19884',
            version='2.4.0'))

    db.session.commit()
