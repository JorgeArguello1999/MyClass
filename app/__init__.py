import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config

# Inicializamos las extensiones sin vincular a la app todavía
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Configuramos la vista de autenticación para que reconozca rutas protegidas
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializamos las extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Importamos y registramos los Blueprints (controladores)
    from app.controllers.main_controller import main_bp
    from app.controllers.auth_controller import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
