from ..db import db


def update_players_and_maps_found_in_competitives():
    """
    Exploramos partidas competitivas en el sistema y nos quedamos con el nick más
    reciente y el id_steam de las coincidencias con la lista de miembros del clan
    de steam, tengan o no abierto el perfil.
    """
    matches = db.get_all_competitive_matches_simplified()
    matches_count = matches.count()
    clan_members_ids = db.get_members_ids()

    members_in_competitives = list()
    maps = list()
    steam_ids_aux = list()
    for match in matches:
        team_text = "players_team" + str(match["local_team"])
        for player in match[team_text]:
            if player["steam_id"] in clan_members_ids:
                if player["steam_id"] not in steam_ids_aux:  # append only once
                    members_in_competitives.append(player)
                    steam_ids_aux.append(player["steam_id"])
        if match["map"] not in maps:
            maps.append(match["map"])

    db.update_group_competitive_info(
        players=members_in_competitives, maps=maps, n_matches=matches_count
    )

    print(members_in_competitives)
