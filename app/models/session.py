from app import db
from datetime import datetime, timezone

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    title = db.Column(db.String(255))
    audio_file_path = db.Column(db.String(255))
    duration_seconds = db.Column(db.Integer)
    recorded_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    raw_transcript = db.Column(db.Text)
    translated_transcript = db.Column(db.Text)
    
    # Status can be 'unprocessed', 'processing', or 'ready'
    status = db.Column(db.String(50), default='unprocessed')
    
    # Class summary and study group note
    class_summary = db.Column(db.Text)
    study_group_note = db.Column(db.Text)

    # Relationships
    course = db.relationship('Course', backref=db.backref('sessions', lazy='dynamic', cascade='all, delete-orphan'))
    key_moments = db.relationship('KeyMoment', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    homeworks = db.relationship('Homework', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    study_notes = db.relationship('StudyNote', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    summary_topics = db.relationship('SummaryTopic', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Session {self.title or self.id}>'
