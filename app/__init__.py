from flask import Flask
import os


from app.blueprints.landing import landing
from app.blueprints.home import home
from app.blueprints.library import library
from app.blueprints.upload import upload
from app.blueprints.preview import preview
from app.blueprints.question import question

def create_app():
    app = Flask(__name__)
    app.secret_key = '123456'

    app.register_blueprint(landing)
    app.register_blueprint(home)
    app.register_blueprint(library)
    app.register_blueprint(upload)
    app.register_blueprint(preview)
    app.register_blueprint(question)

    return app




## TOKEN - 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