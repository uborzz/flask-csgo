from datetime import datetime
from typing import List, Dict, Union

from pymongo import MongoClient
from pymongo.bulk import BulkWriteError

from .models import User, SteamUser, CompetitiveInfo


class DBException(Exception):
    ...


class MongoDB:
    def __init__(self):
        self._db = None
        self._initialized = False

    def init(self, connection):
        client = MongoClient(connection, maxPoolSize=50, wtimeout=2000)
        db = client["steam"]

        # collections
        self._users = db["users"]
        self._raw_stats = db["dofitos"]
        self._general_stats = db["dofitos_general"]
        self._group = db["group_info"]
        self._profiles = db["profile_ids"]
        self._competitives = db["competitives"]
        self._competitives_uploaders = db["competitives_uploaders"]
        self._test_col = db["testdb"]

        self._initialized = True

    @property
    def initialized(self) -> bool:
        return self._initialized

    def get_user(self, username) -> Union[User, None]:
        user = self._users.find_one({"username": username})
        return (
            User(username=user["username"], password=user["password"]) if user else None
        )

    def get_general_stats(self) -> List[Dict]:
        return list(self._general_stats.find())

    def get_player_public_stats(self, member_id):
        return self._raw_stats.find_one({"playerstats.steamID": member_id})

    def get_players_in_competitive(self) -> Union[CompetitiveInfo, None]:
        group_info_query = self._group.find_one({"_id": "members_in_competitives"})

        if group_info_query:
            players: List[SteamUser] = group_info_query["members"]
            maps: List[str] = group_info_query["maps_played"]
            return {"players": players, "maps": maps}

        else:
            return {"players": [], "maps": []}

    def get_all_competitive_matches(self) -> List[Dict]:
        return list(self._competitives.find())

    def get_all_competitive_matches_simplified(self) -> List[Dict]:
        projection = {
            "players_team1.nick": 1,
            "players_team2.nick": 1,
            "players_team1.steam_id": 1,
            "players_team2.steam_id": 1,
            "local_team": 1,
            "map": 1,
        }
        matches = db._competitives.find({}, projection).sort("_id", -1)  # Descending

        result = matches if matches else list()
        return result

    def update_group_competitive_info(self, players, maps: List[str], n_matches: int):
        db._group.replace_one(
            {"_id": "members_in_competitives"},
            {
                "members": players,
                "last_updated": datetime.now(),
                "matches_last_update": n_matches,
                "maps_played": maps,
            },
            upsert=True,
        )

    def get_members_ids(self) -> List[int]:
        ids = self._group.find_one({"_id": "clan_members"}).get("members")
        print("En total", len(ids), "ids:", ids)
        result = ids if ids else list()
        return result

    def update_members_ids(self, ids: List[int]):
        try:
            self._group.replace_one(
                {"_id": "clan_members"}, {"members": ids}, upsert=True
            )
        except Exception as e:
            print(f"upsert failed. Exception:", str(e))

    def update_player_profile_urls(self, steam_id: int, url: str) -> bool:
        try:
            result = self._profiles.update_one(
                {"_id": steam_id}, {"$addToSet": {"profile_names": url}}, upsert=True,
            )
            return True if result.modified_count else False
        except Exception as e:
            print("upsert profiles ha fallado. Exception:", str(e))

    def update_general_stats_view(self, data: Dict) -> bool:
        try:
            result = self._general_stats.replace_one(
                {"steam_id": data["steam_id"]}, data, upsert=True
            )
            return True if result.modified_count else False
        except Exception as e:
            print("view upsert failed. Exception:", str(e))

    def update_general_stats_raw(self, player_id: int, data: Dict):
        try:
            result = self._raw_stats.replace_one(
                {"playerstats.steamID": str(player_id)}, data, upsert=True,
            )
            return True if result.modified_count else False
        except Exception as e:
            print("upsert dofitos ha fallado", str(e))

    def insert_competitive_matches(self, matches: List[Dict]) -> int:
        """Inserts list of competitive matches. Returns number of inserts.
        """
        try:
            result = db._competitives.insert_many(matches, ordered=False)
            return len(result.inserted_ids)
        except BulkWriteError as bwe:
            return bwe.details["nInserted"]
        except Exception as e:
            print(str(e))
            raise DBException("Matches not inserted.")

    # TODO delete this. provisional.
    def _test(self):
        now = datetime.now()
        return self._test_col.update_one(
            {"nombre": "prueba insert"}, {"$set": {"date": now}}, upsert=True
        )


db = MongoDB()
