from flask import Blueprint, render_template, request, jsonify, session
from .key_preview import extract_text
from ..model.keygen import keynote_generation, format_keynotes
from langchain_community.llms import Ollama
from docx import Document
import uuid
import datetime
import json

from .. import db
from ..schema import Keynote

keynotes = Blueprint('keynotes', __name__)

def retrieve_keynotes_sets():
    """Get all keynotes sets from the database"""
    try:
        keynotes = Keynote.query.all()
        sets_data = [{'id': qs.id, 'title': qs.title} for qs in keynotes]
        return sets_data
    except Exception as e:
        print(f"Error retrieving keynotes sets: {e}")
        return []
    
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
    

@keynotes.route('/keynotes/save', methods=['POST'])
def save_keynotes():
    try:
        # Get data from form
        data = json.loads(request.data)
        title = data.get('keynote_title', 'Untitled Keynote')
        content = session.get('generated_keynotes', '')
        file_path = session.get('file_path', '')
        
        # Create a new keynote in the database
        new_keynote = Keynote(
            title=title,
            content=content,
            file_path=file_path
        )
        
        # Add to database
        db.session.add(new_keynote)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Keynotes saved successfully.',
            'keynote_id': new_keynote.id
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error saving keynotes: {e}")
        return jsonify({
            'success': False,
            'message': f'Error saving keynotes: {str(e)}'
        }), 500