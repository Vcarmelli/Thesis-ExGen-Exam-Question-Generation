from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import os
from werkzeug.utils import secure_filename

# Configure the Blueprint
key_upload = Blueprint('key_upload', __name__)

# Define folders and allowed file types
UPLOAD_FOLDER = 'app/static/uploads'
THUMBNAIL_FOLDER = 'app/static/thumbnails'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

# Check if the file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@key_upload.route('/key_upload', methods=['GET', 'POST'])
def key_upload_page():
    if request.method == 'POST':
        if 'input_file' not in request.files:
            return render_template('upload.html', error="No file selected")
        
        file = request.files['input_file']
        
        if file.filename == '':
            return render_template('upload.html', error="File name is empty")
        
        if not file.content_type == 'application/pdf':
            return render_template('upload.html', error="Only PDF files are allowed")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Save the file path in session
            session['file_path'] = file_path

            # Redirect to preview page
            return redirect(url_for('key_preview.key_preview_page', file_name=filename))
        
        return render_template('key_upload.html', error="Invalid file type")
    
    return render_template('key_upload.html')