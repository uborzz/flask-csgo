from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

from .auth import auth
from .auth.flask_user import FlaskUser


login_manager = LoginManager()
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(username):
    return FlaskUser.get(username)

def create_app(secret_key):
    app = Flask(__name__)
    app.secret_key = secret_key
    login_manager.init_app(app)
    app.register_blueprint(auth)
    CORS(app)
    return app
