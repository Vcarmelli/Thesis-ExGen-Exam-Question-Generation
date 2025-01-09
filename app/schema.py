from . import db

class QuestionSet(db.Model):
    __tablename__ = 'question_set'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    questions = db.relationship('Question')

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    question_text = db.Column(db.String(700))
    answer = db.Column(db.String(500))
    options = db.Column(db.JSON)  
    question_set_id = db.Column(db.Integer, db.ForeignKey('question_set.id'))