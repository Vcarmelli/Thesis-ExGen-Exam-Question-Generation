from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from ..model.rag import get_documents_from_vector_db
from ..model.functions import convert_file_to_thumbnail, retrieve_text_from_pages, parse_pages, save_text

from .. import db
from ..schema import QuestionSet

# Configure the Blueprint
preview = Blueprint('preview', __name__)


@preview.route('/preview', methods=['GET', 'POST'])
def preview_page():
    if request.method == 'GET':
        filename = request.args.get('file_name')
        file_path = session.get('file_path')
        print(f"File path in session: {file_path}")
        if not file_path:
            return render_template('upload.html', error="No file uploaded.")

        thumbnails = convert_file_to_thumbnail(file_path, start_page=0, end_page=10)
        
        # Fetch documents
        documents = get_documents_from_vector_db()

        return render_template(
            'preview.html', 
            filename=filename, 
            thumbnails=thumbnails,
            documents=documents # Pass the documents to the template to display in html
        )

    elif request.method == 'POST':
        filename = request.args.get('file_name')
        if filename:
            session['filename'] = filename

        pages_input = request.form.get('page-num')
        question_type = request.form.get('ques-type')
        question_quantity = request.form.get('ques-num')
        bloom_level = request.form.get('blooms')

        # Parse the pages input
        pages = parse_pages(pages_input)
        print(f"Selected pages: {pages}")

        question = {
            'type': question_type, 
            'quantity': int(question_quantity), 
            'bloom': bloom_level
        } 
        print(f"question: {question}")

        # Now, instead of extracting text, pass the pages to the retriever
        try:
            # Pass the pages directly to the retriever to get the text
            text = retrieve_text_from_pages(session['file_path'], pages)
            print(f"Retrieved text on selected pages:{pages} {text[:100]}...")
        except KeyError:
            return jsonify({'message': 'Return to Upload Page'}), 400

        session['question'] = question
        session['filename'] = filename
        save_text(text)
        return redirect(url_for('question.question_page'))
    

# ROUTES FOR FETCHING DATA 
@preview.route('/selection/<int:page>')
def load_thumbnails(page):
    end = page + 10
    thumbnails = convert_file_to_thumbnail(session['file_path'], start_page=page, end_page=end)
    return jsonify(thumbnails=thumbnails)


@preview.route('/preview/<int:setId>')
def load_file(setId):
    question_set = QuestionSet.query.get(setId)
    session['file_path'] = question_set.path
    return redirect(url_for('preview.preview_page', file_name=question_set.filename))