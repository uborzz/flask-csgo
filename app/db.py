from pymongo import MongoClient
from .models import User

from typing import Dict, Union


class MongoDB:
    def __init__(self):
        self._db = None
        self._initialized = False

    def init(self, connection):
        client = MongoClient(connection, maxPoolSize=50, wtimeout=2000)
        db = client["steam"]

        # collections
        self._users = db["users"]
        self._dofitos = db["dofitos"]
        self._dofitos_general_stats_db = db["dofitos_general"]
        self._group = db["group_info"]
        self._profiles = db["profile_ids"]
        self._competitives = db["competitives"]
        self._competitives_uploaders = db["competitives_uploaders"]

        self._initialized = True

    @property
    def initialized(self):
        return self._initialized

    # direct methods
    def get_user(self, username) -> Union[User, None]:
        user = self._users.find_one({"username": username})
        return User(username=user["username"], password=user["password"]) if user else None


db = MongoDB()
