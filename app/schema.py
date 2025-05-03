from . import db

class QuestionSet(db.Model):
    __tablename__ = 'question_set'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    path = db.Column(db.String(500))
    filename = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    questions = db.relationship('Question')
    
    def get_title(self):
        return {
            'id': self.id,
            'title': self.title
        }

    def question_count(self):
        return len(self.questions)


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    bloom = db.Column(db.String(20))
    type = db.Column(db.String(20))
    question_text = db.Column(db.String(700))
    answer = db.Column(db.String(500))
    options = db.Column(db.JSON)  
    question_set_id = db.Column(db.Integer, db.ForeignKey('question_set.id'))

    def get_bloom_level(self):
        return {
            'remember': 'Level 1: Remember',
            'understand': 'Level 2: Understand',
            'apply': 'Level 3: Apply',
            'analyze': 'Level 4: Analyze',
            'evaluate': 'Level 5: Evaluate',
            'create': 'Level 6: Create'
        }.get(self.bloom.lower(), 'Level 1: Remember') 