from app import db

class Homework(db.Model):
    __tablename__ = 'homeworks'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    
    task_description = db.Column(db.Text)
    due_date_extracted = db.Column(db.String(128))
    is_completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Homework {self.id}>'
