from flask import Flask
import os

from app.blueprints.landing import landing
from app.blueprints.dashboard import dashboard

def create_app():
    app = Flask(__name__)

    app.register_blueprint(landing)
    app.register_blueprint(dashboard)

    return app