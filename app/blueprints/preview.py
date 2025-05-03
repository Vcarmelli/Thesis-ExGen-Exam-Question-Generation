from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
from PIL import Image
from pdf2image import convert_from_path
from langchain_community.document_loaders import PyMuPDFLoader
from ..model.rag import get_documents_from_vector_db, loader, create_retriever
from .. import db
from ..schema import QuestionSet, Question

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


# def extract_text(file_path, pages):
#     loader = PyMuPDFLoader(file_path)
#     docs = loader.load()
#     extracted_text = ""

#     for page_num in pages:
#         if page_num <= len(docs):
#             extracted_text += docs[page_num - 1].page_content

#     return extracted_text


# Function to retrieve text from the given pages using the retriever on the RAG.py
def retrieve_text_from_pages(file_path, pages):
    # Use the retriever to get text based on the page numbers
    documents = loader(file_path)  # Load the document using your loader
    retriever = create_retriever(documents, pages)  # Pass pages to the retriever
    return retriever.get_text()  # Assuming retriever has a method to get text



@preview.route('/preview', methods=['GET', 'POST'])
def preview_page():
    if request.method == 'GET':
        filename = request.args.get('file_name')
        file_path = session.get('file_path')
        print(f"File path in session: {file_path}")
        if not file_path:
            return render_template('upload.html', error="No file uploaded.")

        thumbnails = convert_file_to_thumbnail(
            file_path, THUMBNAIL_FOLDER, start_page=0, end_page=10
        )
        
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

        # Function to convert range to list of pages
        def parse_pages(pages_input):
            pages = set()
            page_ranges = pages_input.split(',')
            print("Page ranges:", page_ranges)
            for range_str in page_ranges:
                range_str = range_str.strip()
                if '-' in range_str:
                    start, end = map(int, range_str.split('-'))
                    pages.update(range(start, end + 1))
                elif range_str.isdigit():
                    pages.add(int(range_str))

            return sorted(pages)

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
        session['text'] = text
        session['filename'] = filename
        return redirect(url_for('question.question_page'))
    

# ROUTES FOR FETCHING DATA 
@preview.route('/selection/<int:page>')
def load_thumbnails(page):
    end = page + 10
    thumbnails = convert_file_to_thumbnail(session['file_path'], THUMBNAIL_FOLDER, start_page=page, end_page=end)
    return jsonify(thumbnails=thumbnails)


@preview.route('/preview/<int:setId>')
def load_file(setId):
    question_set = QuestionSet.query.get(setId)
    session['file_path'] = question_set.path
    return redirect(url_for('preview.preview_page', file_name=question_set.filename))