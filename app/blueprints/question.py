from flask import Blueprint, render_template, request, jsonify, session
# from .preview import extract_text
from ..model.llama import exam_generate_questions
from langchain_community.llms import Ollama
from docx import Document
import json

from .. import db
from ..schema import QuestionSet, Question


question = Blueprint('question', __name__)

def retrieve_question_sets():
    question_sets = QuestionSet.query.all()
    sets_title = [qs.get_title() for qs in question_sets]
    return sets_title


@question.route('/question')
def question_page():
    questions = session.get('questions', [])
    text = session.get('text', '')
    filename = session.get('filename', 'No file selected')
    
    # Debugging output
    print(f"Filename: {filename}")
    print(f"Text: {text}")
    
    for question in questions:
        question_type = question.get('type')
        num_questions = question.get('quantity')
        question_difficulty = question.get('difficulty')
        print(f"Preparing to generate {num_questions} {question_difficulty} {question_type} questions.")
    
    generated_questions = exam_generate_questions(questions, text)
    session['generated_questions'] = generated_questions
    print(session['generated_questions'])

    sets_data = retrieve_question_sets()
    return render_template('question.html', filename=filename, generated_questions=generated_questions, sets_data=sets_data)


@question.route('/question/save', methods=['POST'])
def save_questions():
    try:
        data = json.loads(request.data)
        title = data.get('title')
        generated_questions = session.get('generated_questions', [])

        new_set = QuestionSet(title=title)
        db.session.add(new_set)
        db.session.flush()
        
        for item in generated_questions:
            question_type = item["type"]
            for q in item["questions"]:
                new_question = Question(
                    type=question_type,
                    question_text=q["question"],
                    options=q["options"],
                    answer=q["answer"],
                    question_set_id=new_set.id
                )
                db.session.add(new_question)
        db.session.commit()

        return jsonify({'message': 'Questions saved successfully.'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save questions.',
            'details': str(e)
        }), 500


@question.route('/question/append', methods=['POST'])
def append_questions():
    try:
        data = json.loads(request.data)
        setId = data.get('setId')
        generated_questions = session.get('generated_questions', [])
        
        for item in generated_questions:
            question_type = item["type"]
            for q in item["questions"]:
                new_question = Question(
                    type=question_type,
                    question_text=q["question"],
                    options=q["options"],
                    answer=q["answer"],
                    question_set_id=setId
                )
                db.session.add(new_question)
        db.session.commit()

        return jsonify({'message': 'Questions append successfully.'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to save questions.',
            'details': str(e)
        }), 500