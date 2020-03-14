from pymongo import MongoClient
from .models import User, SteamUser, CompetitiveInfo

from typing import List, Dict, Union


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

    def get_user(self, username) -> Union[User, None]:
        user = self._users.find_one({"username": username})
        return User(username=user["username"], password=user["password"]) if user else None

    def get_general_stats(self) -> List[Dict]:
        return list(self._dofitos_general_stats_db.find())

    def get_player_public_stats(self, member_id):
        return self._dofitos.find_one({"playerstats.steamID": member_id})

    def get_players_in_competitive(self) -> Union [CompetitiveInfo, None]:
        group_info_query = self._group.find_one({"_id": "members_in_competitives"})
        
        if group_info_query:
            players: List[SteamUser] = group_info_query["members"]
            maps: List[str] = group_info_query["maps_played"]
            return {"players": players, "maps": maps}

        else:
            return {"players": [], "maps": []}

    def get_all_competitive_matches(self):
        return self._competitives.find()
        

db = MongoDB()
