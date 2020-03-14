from flask import Blueprint

competitive = Blueprint("competitive", __name__, url_prefix="/competitive")

from . import views
