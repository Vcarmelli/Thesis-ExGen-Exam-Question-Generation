from flask import Blueprint, render_template, session, request

landing = Blueprint('landing', __name__)


@landing.before_request
def before_request():
    if request.path == '/favicon.ico':
        return '', 204


@landing.route('/')
def index():
    return render_template('landing.html')