from flask import Blueprint, render_template
from ..schema import QuestionSet

# Create Blueprint
home = Blueprint('home', __name__)

# Define Route
@home.route('/home')
def home_page():
    question_sets = QuestionSet.query.all()
    return render_template('home.html', question_sets=question_sets)
