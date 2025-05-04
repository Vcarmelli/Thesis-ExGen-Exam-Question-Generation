from flask import Blueprint, render_template,session
from ..model.keygen import keynote_generation, format_keynotes
from ..model.functions import retrieve_text


keynotes = Blueprint('keynotes', __name__)


@keynotes.route('/keynotes')
def keynotes_page():
    questions = session.get('questions', [])
    text = retrieve_text()
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