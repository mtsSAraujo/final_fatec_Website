from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
import mysql.connector
from flask_login import LoginManager
from urllib.parse import quote_plus

db = SQLAlchemy()
DB_NAME = "mateus_trabalho"
password = quote_plus("E$tud@_m@1$")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'uma chave secreta'

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://usr_aluno:{password}@201.23.3.86:5000/aula_fatec'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Professor, Disciplina, Aluno, Curso, Endereco
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        user_type = session.get('user_type')
    
        if user_type == 'professor':
            return Professor.query.get(int(id))
        elif user_type == 'aluno':
            return Aluno.query.get(int(id))
        return None

    return app