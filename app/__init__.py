from flask import Flask
import os


from app.blueprints.landing import landing
from app.blueprints.home import home
from app.blueprints.library import library
from app.blueprints.upload import upload
from app.blueprints.preview import preview
from app.blueprints.question import question
from app.blueprints.export_docs import export_docs

from app.blueprints.key_preview import key_preview
from app.blueprints.key_upload import key_upload
from app.blueprints.keynotes import keynotes


def create_app():
    app = Flask(__name__)
    app.secret_key = '123456'

    app.register_blueprint(landing)
    app.register_blueprint(home)
    app.register_blueprint(library)
    app.register_blueprint(upload)
    app.register_blueprint(preview)
    app.register_blueprint(question)
    app.register_blueprint(key_preview)
    app.register_blueprint(key_upload)
    app.register_blueprint(keynotes)
    app.register_blueprint(export_docs)


    return app
