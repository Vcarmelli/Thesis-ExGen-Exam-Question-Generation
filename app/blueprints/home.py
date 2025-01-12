from flask import Blueprint, render_template,session
from ..schema import QuestionSet

# Create Blueprint
home = Blueprint('home', __name__)

# Define Route
@home.route('/home')
def home_page():
    session.clear()
    question_sets = QuestionSet.query.all()
    return render_template('home.html', question_sets=question_sets)
