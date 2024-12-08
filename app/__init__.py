from flask import Flask
import os

from app.blueprints.landing import landing
from app.blueprints.home import home
from app.blueprints.library import library

def create_app():
    app = Flask(__name__)

    app.register_blueprint(landing)
    app.register_blueprint(home)
    app.register_blueprint(library)

    return app