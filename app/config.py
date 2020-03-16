import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    DEVELOPMENT = True
    DEBUG = True
    UPDATE_ON_LAUNCH = False

    SECRET_KEY = os.getenv("SECRET_KEY")
    STEAM_KEY = os.getenv("STEAM_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    UPLOAD_PASS = os.getenv("UPLOAD_PASS")
