from flask import Blueprint

stats = Blueprint("stats", __name__, url_prefix="/stats")

from . import views
