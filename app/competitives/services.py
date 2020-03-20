from ..db import db

from pymongo.errors import BulkWriteError
from datetime import datetime


def update_players_found_in_competitives():
    """
    Exploramos partidas competitivas en el sistema y nos quedamos con el nick más reciente y el id_steam
    de las coincidencias con la lista de miembros del clan de steam, tengan o no abierto el perfil.
    """
    matches = db._competitives.find(
        {},
        {
            "players_team1.nick": 1,
            "players_team2.nick": 1,
            "players_team1.steam_id": 1,
            "players_team2.steam_id": 1,
            "local_team": 1,
            "map": 1,
        },
    ).sort(
        "_id", -1
    )  # Desc.
    matches_counter = matches.count()
    try:
        clan_members_ids = db._group.find_one({"_id": "clan_members"})["members"]
    except (KeyError, TypeError):
        clan_members_ids = list()

    members_in_competitives = list()
    steam_ids_aux = list()
    maps = list()
    for match in matches:
        print(match)
        team_text = "players_team" + str(match["local_team"])
        for player in match[team_text]:
            if player["steam_id"] in clan_members_ids:
                if player["steam_id"] not in steam_ids_aux:  # append only once
                    members_in_competitives.append(player)
                    steam_ids_aux.append(player["steam_id"])
        if match["map"] not in maps:
            maps.append(match["map"])

    db._group.replace_one(
        {"_id": "members_in_competitives"},
        {
            "members": members_in_competitives,
            "last_updated": datetime.now(),
            "matches_last_update": matches_counter,
            "maps_played": maps,
        },
        upsert=True,
    )

    print(members_in_competitives)
