from flask import Blueprint, render_template,session

library = Blueprint('library', __name__)

@library.route('/library')
def library_page():
    return render_template('library.html') 