from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import os
from werkzeug.utils import secure_filename
from ..model.rag import loader, split_documents, get_chroma, get_pages_from_vector_db
from ..model.functions import allowed_file, UPLOAD_FOLDER

# Configure the Blueprint
upload = Blueprint('upload', __name__)



@upload.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        if 'input_file' not in request.files:
            return render_template('upload.html', error="No file selected")
        
        file = request.files['input_file']
        
        if file.filename == '':
            return render_template('upload.html', error="File name is empty")
        
        # Additional MIME type check for extra security
        if not file.content_type == 'application/pdf':
            return render_template('upload.html', error="Only PDF files are allowed")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            session['file_path'] = file_path
            documents = loader(file_path)
            chunks = split_documents(documents)
            vector_db = get_chroma(chunks)
            pages = get_pages_from_vector_db()
            
            print(f"Pages: {pages}")
            print(f"Total Documents: {len(documents)}")
            print("Process completed successfully.")
            print(chunks[0:1])
            print(f"Number of chunks: {len(chunks)}")
            
            return redirect(url_for('preview.preview_page', file_name=filename))
        
        return render_template('upload.html', error="Invalid file type. Please upload a PDF file only.")
    
    return render_template('upload.html')