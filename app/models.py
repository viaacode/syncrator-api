from app.syncrator_api import db
from sqlalchemy.dialects.postgresql import JSON


class SyncJobs(db.Model):
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

    def to_dict(self):
        """Export sync job to dictionary for later jsonify to work."""

        return {
            'id': self.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'data_source': self.data_source,
            'type': self.type,
            'total_records': int(self.total_records),
            'completed': self.completed,
            'options': self.options,
            'version': self.version,
            'target_datastore_url': self.target_datastore_url,
        }
