import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY")
    SERVER_NAME = "localhost:5000"

    MONGO_URI = os.getenv("MONGO_URI")
    UPDATE_ON_LAUNCH = False
    STEAM_GROUP = "dofitosbastardos"
    UPLOAD_PASS = os.getenv("UPLOAD_PASS")
    STEAM_KEY = os.getenv("STEAM_KEY")
