from flask import Blueprint, render_template,session

landing = Blueprint('landing', __name__)

@landing.route('/')
def index():
    return render_template('landing.html')