from flask import Blueprint, render_template,session
from .key_preview import extract_text
from ..model.keygen import keynote_generation, format_keynotes
from langchain_community.llms import Ollama
from docx import Document


keynotes = Blueprint('keynotes', __name__)

@keynotes.route('/keynotes')
def keynotes_page():
    questions = session.get('questions', [])
    text = session.get('text', '')
    filename = session.get('filename', 'No file selected')
    
    # Generate keynotes
    raw_keynotes = keynote_generation(keynotes, text)
    
    # Format the keynotes
    formatted_keynotes = format_keynotes(raw_keynotes)

    session['generated_keynotes'] = formatted_keynotes
    
    return render_template('keynotes.html', 
                         filename=filename, 
                         generated_keynotes=formatted_keynotes, 
                         questions=questions)