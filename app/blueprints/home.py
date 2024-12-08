from flask import Blueprint, render_template

# Create Blueprint
home = Blueprint('home', __name__)

# Define Route
@home.route('/home')
def home_page():
    return render_template('home.html')
