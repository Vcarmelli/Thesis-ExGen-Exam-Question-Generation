from flask import Blueprint, render_template,session
from .key_preview import extract_text
from ..model.keygen import keynote_generation
from langchain_community.llms import Ollama
from docx import Document


keynotes = Blueprint('keynotes', __name__)

@keynotes.route('/keynotes')
def keynotes_page():

    questions = session.get('questions', [])
    text = session.get('text', '')
    filename = session.get('filename', 'No file selected')
    # Debugging output
    print(f"Filename: {filename}")
    print(f"Text: {text}")
    
    # Generate keynotes
    generated_keynotes = keynote_generation(keynotes, text)

    return render_template('keynotes.html', filename=filename, generated_keynotes=generated_keynotes, questions=questions)