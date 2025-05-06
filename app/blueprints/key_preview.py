from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from ..model.summ import summarize
from ..model.functions import convert_file_to_thumbnail, retrieve_text_from_pages, parse_pages, save_text


# Configure the Blueprint
key_preview = Blueprint('key_preview', __name__)


@key_preview.route('/key_preview', methods=['GET', 'POST'])
def key_preview_page():
    if request.method == 'GET':
        filename = request.args.get('file_name')
        file_path = session.get('file_path')
        if not file_path:
            return render_template('key_upload.html', error="No file uploaded.")

        thumbnails = convert_file_to_thumbnail(file_path, start_page=0, end_page=10)
        return render_template('key_preview.html', filename=filename, thumbnails=thumbnails)

    elif request.method == 'POST':
        filename = request.args.get('file_name')
        if filename:
            session['filename'] = filename
            print(f"Filename from GET: {filename}")

        pages_input = request.form.get('pages')

        # Parse the pages input
        pages = parse_pages(pages_input)
        # Try to extract text from the selected pages
        try:
            extract = retrieve_text_from_pages(session['file_path'], pages)
            text = summarize(extract)
        except KeyError:
            return jsonify({'message': 'Return to Upload Page'}), 400

        save_text(text)
        session['filename'] = filename
        # return jsonify(session['text'], session['questions'])  # Return text or redirect as needed
        return redirect(url_for('keynotes.keynotes_page'))