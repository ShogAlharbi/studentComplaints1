from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from os import path

db = SQLAlchemy()
babel = Babel()
DB_NAME = "database.db"

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all()
        print("Created Database")

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = 'My duck and your duck'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'ar']

    db.init_app(app)
    babel.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User, Admin, Complaint

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import views
    from .auth import auth
    from .admin import admin
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        create_database(app)

    @babel.localeselector
    def get_locale():
        return request.args.get('lang') or 'en'

    return app
