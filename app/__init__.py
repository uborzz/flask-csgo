from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

from .auth import auth
from .auth.flask_user import FlaskUser
from .stats import stats
from .competitives import competitive


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
    app.register_blueprint(stats)
    app.register_blueprint(competitive)
    CORS(app, resources={r"/uploadgames": {"origins": ["https://steamcommunity.com"]}})
    return app
