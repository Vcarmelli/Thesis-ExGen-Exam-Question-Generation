from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
from PIL import Image
from pdf2image import convert_from_path
from langchain_community.document_loaders import PyMuPDFLoader
from ..model.summ import summarize

# Configure the Blueprint
key_preview = Blueprint('key_preview', __name__)

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




@key_preview.route('/key_preview', methods=['GET', 'POST'])
def key_preview_page():
    if request.method == 'GET':
        filename = request.args.get('file_name')
        file_path = session.get('file_path')
        if not file_path:
            return render_template('key_upload.html', error="No file uploaded.")

        thumbnails = convert_file_to_thumbnail(
            file_path, THUMBNAIL_FOLDER, start_page=0, end_page=10
        )
        return render_template('key_preview.html', filename=filename, thumbnails=thumbnails)

    elif request.method == 'POST':
        filename = request.args.get('file_name')
        if filename:
            session['filename'] = filename
            print(f"Filename from GET: {filename}")

        pages_input = request.form.get('pages')
        
        # Function to convert range to list of pages
        def parse_pages(pages_input):
            pages = set()
            page_ranges = pages_input.split(',')

            for range_str in page_ranges:
                if '-' in range_str:
                    start, end = map(int, range_str.split('-'))
                    pages.update(range(start, end + 1))
                elif range_str.isdigit():
                    pages.add(int(range_str))

            return sorted(pages)

        # Parse the pages input
        pages = parse_pages(pages_input)
        # Try to extract text from the selected pages
        try:
            extract = extract_text(session['file_path'], pages)
            text = summarize(extract)
        except KeyError:
            return jsonify({'message': 'Return to Upload Page'}), 400

        session['text'] = text
        session['filename'] = filename
        # return jsonify(session['text'], session['questions'])  # Return text or redirect as needed
        return redirect(url_for('keynotes.keynotes_page'))