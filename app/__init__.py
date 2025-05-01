# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize SQLAlchemy without binding to app
db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    app.secret_key = '123456'
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, DB_NAME)}'
    
    # Initialize db with app
    db.init_app(app)
    
    # Import blueprints here to avoid circular imports
    from app.blueprints.landing import landing
    from app.blueprints.home import home
    from app.blueprints.library import library
    from app.blueprints.upload import upload
    from app.blueprints.preview import preview
    from app.blueprints.question import question
    from app.blueprints.key_export import key_export
    from app.blueprints.key_preview import key_preview
    from app.blueprints.key_upload import key_upload
    from app.blueprints.keynotes import keynotes
    from app.blueprints.export import export
    
    # Register blueprints
    app.register_blueprint(landing)
    app.register_blueprint(home)
    app.register_blueprint(library)
    app.register_blueprint(upload)
    app.register_blueprint(preview)
    app.register_blueprint(question)
    app.register_blueprint(key_preview)
    app.register_blueprint(key_upload)
    app.register_blueprint(keynotes)
    app.register_blueprint(key_export)
    app.register_blueprint(export)
    
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    return app