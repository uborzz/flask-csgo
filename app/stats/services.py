from datetime import datetime
import requests
import xmltodict
from typing import Dict

from pprint import pprint

from ..db import db


class SteamURLS:
    PLAYER = "http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={}&steamid={}"
    STATUS = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}"
    GROUP = "http://steamcommunity.com/groups/{}/memberslistxml/?xml=1"


def update_general_stats_data(app):
    """Some ETL from steam public api data."""
    steam_key = app.config["STEAM_KEY"]
    time_now = datetime.now()
    members_ids = []
    try:
        group_url = SteamURLS.GROUP.format(app.config["STEAM_GROUP"])
        r = requests.get(group_url)
        if r.status_code == 200:
            data = xmltodict.parse(r.text, dict_constructor=dict)
            pprint(data)
            members_ids = data["memberList"]["members"]["steamID64"]
            print("Members ids:", members_ids)
            db.update_members_ids(members_ids)
        else:
            print("request status not OK")
            raise Exception("call status NOK")
    except:
        print("group call failed, getting previously stored.")
        members_ids = db.get_members_ids()

    # steam identification formula
    # ID - "76" + (parseInt(campo-mini) + 561197960265728)

    for player_steam_id in members_ids:
        statistics_url = SteamURLS.PLAYER.format(steam_key, player_steam_id)
        status_url = SteamURLS.STATUS.format(steam_key, player_steam_id)
        print(f"Getting data for {player_steam_id}")
        try:
            r = requests.get(statistics_url)
            s = requests.get(status_url)

            # check status OK of both requests: r & s
            if r.status_code == 200 and s.status_code == 200:

                player_status = s.json()["response"]["players"][0]

                player_data = r.json()
                player_data["playerstats"].pop("achievements")
                player_data["nick"] = player_status["personaname"]
                player_data["last_updated"] = time_now

                # persist user profile url
                db.update_player_profile_urls(
                    steam_id=player_steam_id, url=player_status["profileurl"]
                )

                result = db.update_general_stats_raw(
                    player_id=player_steam_id, data=player_data
                )
                if result:
                    transform_player_data(player_data)

            else:
                print("status NOK")

        except Exception as e:
            # keep loopin
            print("request failed. Exception:", str(e))


def transform_player_data(data: Dict):
    """Some transforms and calcs."""

    view = dict()
    view["steam_id"] = data["playerstats"]["steamID"]
    view["nick"] = data["nick"]
    view["last_updated"] = data["last_updated"]

    stats = dict()
    for element in data["playerstats"]["stats"]:
        stats[element["name"]] = element["value"]

    view["kd_ratio"] = round(float(stats["total_kills"]) / stats["total_deaths"], 3)
    view["total_win"] = round(
        100 * float(stats["total_matches_won"]) / stats["total_matches_played"], 2
    )
    view["time_played"] = int(stats["total_time_played"] / 3600)
    view["rounds_won"] = round(
        100 * float(stats["total_wins"]) / stats["total_rounds_played"], 2
    )
    view["headshots"] = round(
        100 * float(stats["total_kills_headshot"]) / stats["total_kills"], 2
    )
    view["accuracy"] = round(
        100 * float(stats["total_shots_hit"]) / stats["total_shots_fired"], 2
    )

    db.update_general_stats_view(data=view)
