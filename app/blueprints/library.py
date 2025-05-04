from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .. import db
from ..schema import QuestionSet, Question, Keynote
from sqlalchemy import func
import json

library = Blueprint('library', __name__)


def get_bloom_counts():
    bloom_data = (db.session.query(Question.bloom, func.count(Question.id)).group_by(Question.bloom).all())
    bloom_levels = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']
    data_dict = dict(bloom_data)
    bloom_counts = {level: data_dict.get(level, 0) for level in bloom_levels}
    print(bloom_counts) 
    return bloom_counts

@library.route('/library')
def library_page():
    question_sets = QuestionSet.query.all()
    keynotes = Keynote.query.all()
    counts = get_bloom_counts()
    return render_template('library.html', question_sets=question_sets, keynotes=keynotes, counts=counts) 


@library.route('/library/<int:setId>', methods=['GET', 'POST'])
def library_questions(setId):
    if request.method == 'GET':
        question_set = QuestionSet.query.get(setId)
        if not question_set:
            return render_template('404.html', message="Question set not found."), 404
        
        questions = [
            {
                'id': question.id,
                'bloom': question.bloom, # for class assigned colors
                'bloom_level': question.get_bloom_level(), # for text display
                'question_text': question.question_text,
                'answer': question.answer,
                'options': question.options
            }
            for question in question_set.questions
        ]
        return render_template('library_questions.html', generated_questions=questions, setId=setId) 
    
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
        
        counts = get_bloom_counts()
        return redirect(url_for('library.library_questions', setId=question_data.question_set_id, counts=counts))


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


# FOR RETRIEVING ONE QUESTION IN DATABASE
@library.route('/library/retrieve', methods=['POST'])
def retrieve_question():
    question = json.loads(request.data)
    questionId = question['questionId']
    question = Question.query.get(questionId)
    if question:
        question_data = {
            'id': question.id,
            'question_text': question.question_text,
            'answer': question.answer,
            'options': question.options
        }
        return jsonify({'question': question_data})
    else:
        return render_template('404.html', message="Question set not found."), 404

# Add new route for viewing keynote content
@library.route('/library/keynote/<int:keynoteId>')
def view_keynote(keynoteId):
    keynote = Keynote.query.get(keynoteId)
    if not keynote:
        return render_template('404.html', message="Keynote not found."), 404
    
    return render_template('keynote_view.html', 
                          keynote=keynote,
                          content=keynote.content,
                          filename=keynote.title)


# Add new route for deleting keynote
@library.route('/library/keynote/delete', methods=['POST'])
def delete_keynote():
    try:
        data = json.loads(request.data)
        keynoteId = data.get('keynoteId')
        
        keynote = Keynote.query.get(keynoteId)
        if keynote:
            db.session.delete(keynote)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Keynote deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Keynote not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500