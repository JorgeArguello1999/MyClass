from app import db

class SummaryTopic(db.Model):
    __tablename__ = 'summary_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    
    main_topic = db.Column(db.String(255))
    description = db.Column(db.Text)
    # Comma-separated list of tags (e.g. "Quantum Physics,Wave Equation")
    tags = db.Column(db.String(255))

    def __repr__(self):
        return f'<SummaryTopic {self.main_topic}>'
