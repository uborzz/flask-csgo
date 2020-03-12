from flask_login import UserMixin

from ..db import db
from ..models import User

        
class FlaskUser(UserMixin):
    def __init__(self, user: User):
        self.id = user.username
        self.password = user.password

    @staticmethod
    def get(username):
        user: User = db.get_user(username=username)
        if user:
            return FlaskUser(user)
        else:
            return None