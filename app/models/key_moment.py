from app import db

class KeyMoment(db.Model):
    __tablename__ = 'key_moments'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    
    timestamp_seconds = db.Column(db.Integer)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<KeyMoment {self.title}>'
