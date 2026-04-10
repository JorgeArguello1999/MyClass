import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config

# Initialize extensions without binding them to the app yet
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Configure the authentication view to recognize protected routes
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import and register Blueprints (controllers)
    from app.controllers.main_controller import main_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.course_controller import course_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(course_bp, url_prefix='/courses')

    # Import models so they are registered with SQLAlchemy
    from app.models.user import User
    from app.models.course import Course

    return app
