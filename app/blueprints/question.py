from flask import Blueprint, render_template,session
# from .preview import extract_text
from ..model.llama import exam_generate_questions
from langchain_community.llms import Ollama
from docx import Document


question = Blueprint('question', __name__)

@question.route('/question')
def question_page():

    questions = session.get('questions', [])
    text = session.get('text', '')
    filename = session.get('filename', 'No file selected')
    # Debugging output
    print(f"Filename: {filename}")
    print(f"Text: {text}")
    # For debugging purpose, making sure correct values are being passed
    for question in questions:
        question_type = question.get('type')
        num_questions = question.get('quantity')
        question_difficulty = question.get('difficulty')
        print(f"Preparing to generate {num_questions} {question_difficulty} {question_type} questions.")

    generated_questions = exam_generate_questions(questions, text)

    return render_template('question.html', filename=filename, generated_questions=generated_questions)