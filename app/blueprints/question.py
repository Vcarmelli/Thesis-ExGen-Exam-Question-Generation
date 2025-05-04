from flask import Blueprint, render_template, request, jsonify, session
from ..model.llama import exam_generate_questions
from ..model.functions import retrieve_text, retrieve_question_sets, get_bloom_level, exam_abbreviate
import json

from .. import db
from ..schema import QuestionSet, Question


question = Blueprint('question', __name__)


@question.route('/question')
def question_page():
    question = session.get('question', {})
    text = retrieve_text()
    filename = session.get('filename', 'No file selected')
    
    if not text:
        return render_template('404.html', message="Cannot retrieve text from the file."), 404
    # Debugging output
    print(f"Filename: {filename}")
    print(f"Text length: {len(text)} characters")
    print(f"Questions: {question}")
    print(f"Preparing to generate {question['quantity']} {question['type']} in {question['bloom']} bloom's taxonomy level.")
    
    try:
        # Generate questions
        all_generated_questions = exam_generate_questions(question, text)
        
        if not all_generated_questions:
            print("No questions were generated!")
            return render_template('question.html', 
                                filename=filename, 
                                generated_questions=[], 
                                sets_data=retrieve_question_sets(),
                                error="Failed to generate questions. Please try again.")
        
        # Format the questions for the template
        question_type = exam_abbreviate(question['type'])
        bloom_level = get_bloom_level(question['bloom'])
        
        formatted_questions = [{
            'bloom': question['bloom'],
            'type': question_type,
            'questions': all_generated_questions
        }]
        
        session['generated_questions'] = formatted_questions  # this session variable will be saved in db
        print(f"GENERATED {len(all_generated_questions)} questions successfully")
        
        # Get existing question sets for the append option
        sets_data = retrieve_question_sets()
        
        return render_template('question.html', 
                              filename=filename, 
                              generated_questions=formatted_questions, 
                              bloom_level=bloom_level,
                              sets_data=sets_data)
    
    except Exception as e:
        import traceback
        print(f"Error in question_page route: {e}")
        print(traceback.format_exc())
        
        return render_template('question.html', 
                              filename=filename, 
                              generated_questions=[], 
                              sets_data=retrieve_question_sets(),
                              error=f"An error occurred: {str(e)}")


@question.route('/question/save', methods=['POST'])
def save_questions():
    try:
        data = json.loads(request.data)
        title = data.get('title')
        generated_questions = session.get('generated_questions', [])
        file_name = session.get('filename', '')
        file_path = session.get('file_path', '')

        new_set = QuestionSet(title=title, filename=file_name, path=file_path)
        db.session.add(new_set)
        db.session.flush()
        
        print("TO SAVE:", generated_questions)
        for item in generated_questions:
            for q in item["questions"]:
                new_question = Question(
                    bloom=item["bloom"],
                    type=item["type"],
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
        
        print(f"TO APPEND IN ID {setId}: {generated_questions}")
        for item in generated_questions:
            for q in item["questions"]:
                new_question = Question(
                    bloom=item["bloom"],
                    type=item["type"],
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