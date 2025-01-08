from flask import Blueprint, render_template, request, jsonify
from ..schema import QuestionSet
import json

library = Blueprint('library', __name__)

@library.route('/library')
def library_page():
    question_sets = QuestionSet.query.all()
    return render_template('library.html', question_sets=question_sets) 


@library.route('/library/<int:id>')
def library_questions(id):
    question_set = QuestionSet.query.get(id)
    if not question_set:
        return jsonify({'error': 'Question set not found'}), 404
    
    questions = [
        {
            'id': question.id,
            'type': question.type,
            'question_text': question.question_text,
            'answer': question.answer,
            'options': question.options
        }
        for question in question_set.questions
    ]
    return render_template('library_questions.html', generated_questions=questions) 