from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


from app.blueprints.landing import landing
from app.blueprints.upload import upload
from app.blueprints.preview import preview

from app.blueprints.key_preview import key_preview
from app.blueprints.key_upload import key_upload
from app.blueprints.keynotes import keynotes

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    app.secret_key = '123456'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, DB_NAME)}'
    db.init_app(app)

    from app.blueprints.home import home
    from app.blueprints.library import library
    from app.blueprints.question import question
    app.register_blueprint(landing)
    app.register_blueprint(home)
    app.register_blueprint(library)
    app.register_blueprint(upload)
    app.register_blueprint(preview)
    app.register_blueprint(question)
    app.register_blueprint(key_preview)
    app.register_blueprint(key_upload)
    app.register_blueprint(keynotes)

    with app.app_context():
        db.create_all()

    return app
