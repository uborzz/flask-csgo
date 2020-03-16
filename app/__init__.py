from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

from .auth import auth
from .auth.flask_user import FlaskUser
from .stats import stats
from .competitives import competitive
from .provisional_test import test

from .stats.services import update_database_data
from .competitives.services import update_dofitos_found_in_competitives

update_database_data
update_dofitos_found_in_competitives

from .config import Config
from .db import db
from .scheduler import scheduler


login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(username):
    return FlaskUser.get(username)


def create_app():

    # flask
    app = Flask(__name__)
    app.config.from_object(Config())
    login_manager.init_app(app)
    app.register_blueprint(auth)
    app.register_blueprint(stats)
    app.register_blueprint(competitive)
    app.register_blueprint(test)
    CORS(
        app,
        resources={r"/competitive/upload": {"origins": ["https://steamcommunity.com"]}},
    )
    print("▶ Flask app created and configured")

    # db
    db.init(app.config["MONGO_URI"])
    print("▶ DB initialized")

    def b():
        print("BBB")

    def c(v):
        print("CCCCCCCCC", v)

    # task scheduler
    steam_key = app.config["STEAM_KEY"]
    scheduler.new_job(update_database_data, steam_key, hours=24)
    scheduler.new_job(update_dofitos_found_in_competitives, hours=24)

    scheduler.start()
    print("▶ Scheduler running. Tasks... ▼")
    scheduler.print_jobs()

    if app.config["UPDATE_ON_LAUNCH"]:
        print("▶ Update on launch activated. Running the scheduled tasks...")
        scheduler.run_jobs()

    return app
