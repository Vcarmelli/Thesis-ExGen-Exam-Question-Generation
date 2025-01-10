from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .. import db
from ..schema import QuestionSet, Question
import json

library = Blueprint('library', __name__)

@library.route('/library')
def library_page():
    question_sets = QuestionSet.query.all()
    return render_template('library.html', question_sets=question_sets) 


@library.route('/library/<int:setId>', methods=['GET', 'POST'])
def library_questions(setId):
    if request.method == 'GET':
        question_set = QuestionSet.query.get(setId)
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
    
    elif request.method == 'POST':
        # FOR UPDATING QUESTION IN DATABASE
        questionId = request.form.get('question-id')
        question = request.form.get('question')
        answer = request.form.get('answer')
        options = request.form.getlist('option') 
        options_dict = {chr(97 + i): option for i, option in enumerate(options)}
        
        question_data = Question.query.get(questionId)
        if question_data:
            question_data.question_text = question
            question_data.answer = answer
            question_data.options = options_dict
            db.session.commit()
            print('Updated Question:', questionId)
        
        return redirect(url_for('library.library_questions', setId=question_data.question_set_id))


# FOR DELETING QUESTION IN DATABASE
@library.route('/library/delete', methods=['POST'])
def delete_question():
    question = json.loads(request.data)
    questionId = question['questionId']
    question = Question.query.get(questionId)
    if question:
        db.session.delete(question)
        db.session.commit()
        print('Deleted Question:', questionId)
    return jsonify({'setId': question.question_set_id})


# FOR RETRIEVING QUESTION IN DATABASE
@library.route('/library/retrieve', methods=['POST'])
def retrieve_question():
    question = json.loads(request.data)
    questionId = question['questionId']
    question = Question.query.get(questionId)
    if question:
        question_data = {
            'id': question.id,
            'type': question.type,
            'question_text': question.question_text,
            'answer': question.answer,
            'options': question.options
        }
        return jsonify({'question': question_data})
    else:
        return jsonify({'error': 'Question not found'}), 404
    