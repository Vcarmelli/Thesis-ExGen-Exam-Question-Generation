from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
from PIL import Image
from pdf2image import convert_from_path
from langchain_community.document_loaders import PyMuPDFLoader

# Configure the Blueprint
preview = Blueprint('preview', __name__)

THUMBNAIL_FOLDER = 'app/static/thumbnails'

# Generate thumbnails from PDF
def convert_file_to_thumbnail(file_path, thumbnail_path, start_page=0, end_page=1, size=(256, 256)):
    images = convert_from_path(file_path, dpi=180)
    end_page = min(end_page, len(images))

    if end_page <= start_page:
        print("No pages to convert.")
        return []

    for count, page in enumerate(images[start_page:end_page], start=start_page):
        print(f"Creating thumbnail for page: {count + 1}")
        page.thumbnail(size)
        thumbnail_file = os.path.join(thumbnail_path, f'thumbnail_{count}.jpg')
        page.save(thumbnail_file, 'JPEG')

    return [f'thumbnail_{i}.jpg' for i in range(start_page, end_page)]


def extract_text(file_path, pages):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    extracted_text = ""

    for page_num in pages:
        if page_num <= len(docs):
            extracted_text += docs[page_num - 1].page_content

    return extracted_text


@preview.route('/preview', methods=['GET', 'POST'])
def preview_page():
    if request.method == 'GET':
        filename = request.args.get('file_name')
        file_path = session.get('file_path')
        if not file_path:
            return render_template('upload.html', error="No file uploaded.")

        thumbnails = convert_file_to_thumbnail(
            file_path, THUMBNAIL_FOLDER, start_page=0, end_page=10
        )
        return render_template('preview.html', filename=filename, thumbnails=thumbnails)

    elif request.method == 'POST':
        filename = request.form.get('filename')
        pages_input = request.form.get('pages')
        pages = [int(num) for part in pages_input.split(',') for num in range(int(part.split('-')[0]), int(part.split('-')[-1]) + 1)]

        question_types = request.form.getlist('ques-type')
        question_quantities = request.form.getlist('ques-num')
        questions = [
            {'type': qt, 'quantity': int(qn)} 
            for qt, qn in zip(question_types, question_quantities) if qn.isdigit()
        ]

        try:
            text = extract_text(session['file_path'], pages)
        except KeyError:
            return jsonify({'message': 'Return to Upload Page'}), 400

        session['questions'] = questions
        session['text'] = text

        return redirect(url_for('upload.questions'))
