from typing import NamedTuple, List, TypedDict


class SteamUser(TypedDict):
    nick: str
    steam_id: int


class CompetitiveInfo(TypedDict):
    members: List[SteamUser]
    maps: List[str]


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password