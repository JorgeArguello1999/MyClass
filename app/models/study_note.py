from app import db

class StudyNote(db.Model):
    __tablename__ = 'study_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    
    note_text = db.Column(db.Text)
    # Boolean to differentiate between a general note and a "Professor Tip"
    is_professor_tip = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<StudyNote {self.id}>'
