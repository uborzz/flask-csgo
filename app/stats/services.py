from ..db import db

from datetime import datetime
import xmltodict
from pprint import pprint
import requests


class SteamURLS:
    PLAYER = "http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={}&steamid={}"
    STATUS = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}"
    GROUP = "http://steamcommunity.com/groups/dofitosbastardos/memberslistxml/?xml=1"


def update_database_data(steam_key):

    time_now = datetime.now()
    members_ids = []
    try:
        r = requests.get(SteamURLS.GROUP)
        if r.status_code == 200:
            data = xmltodict.parse(r.text, dict_constructor=dict)
            pprint(data)
            members_ids = data["memberList"]["members"]["steamID64"]
            print(members_ids)
            try:
                db._group.replace_one(
                    {"_id": "clan_members"}, {"members": members_ids}, upsert=True
                )
            except:
                print("insert failed")
        else:
            print("request status not OK")
            raise Exception("call status NOK")
    except:
        print("group call failed, tratando de tirar de previo.")
        try:
            members_ids = db._group.find_one({"_id": "clan_members"})["members"]
        except (KeyError, TypeError):
            members_ids
            print("find failed. members empty.")
            members_ids = list()

    # ID - "76" + (parseInt(campo-mini) + 561197960265728)
    for member in members_ids:
        player_steamid = member
        call_stats = SteamURLS.PLAYER.format(steam_key, player_steamid)
        call_status = SteamURLS.STATUS.format(steam_key, player_steamid)
        print("calling GET statistics", call_stats)
        print("calling GET status", call_status)
        try:
            r = requests.get(call_stats)
            s = requests.get(call_status)
            if r.status_code == 200 and s.status_code == 200:
                player_data = r.json()
                player_status = s.json()["response"]["players"][0]
                player_data["nick"] = player_status["personaname"]
                player_data["last_updated"] = time_now
                player_profile_name = player_status["profileurl"]
                try:
                    db._profiles.update(
                        {"_id": member},  # member es el id de steam.
                        {"$addToSet": {"profile_names": player_profile_name}},
                        upsert=True,
                    )
                except:
                    print("upsert profiles ha fallado")
                try:
                    res = db._dofitos.replace_one(
                        {"playerstats.steamID": str(player_steamid)},
                        player_data,
                        upsert=True,
                    )
                    print(res.raw_result)
                    format_data(player_data)
                except:
                    print("upsert dofitos ha fallado")
            else:
                print("NOK from get requests")
        except:
            print("request ha fallado")


def format_data(player_data):
    try:
        vista = dict()
        vista["steam_id"] = player_data["playerstats"]["steamID"]
        vista["nick"] = player_data["nick"]
        vista["last_updated"] = player_data["last_updated"]
        stats = dict()
        for element in player_data["playerstats"]["stats"]:
            stats[element["name"]] = element["value"]
        vista["kd_ratio"] = round(
            float(stats["total_kills"]) / stats["total_deaths"], 3
        )
        vista["total_win"] = round(
            100 * float(stats["total_matches_won"]) / stats["total_matches_played"], 2
        )
        vista["time_played"] = int(stats["total_time_played"] / 3600)
        vista["rounds_won"] = round(
            100 * float(stats["total_wins"]) / stats["total_rounds_played"], 2
        )
        vista["headshots"] = round(
            100 * float(stats["total_kills_headshot"]) / stats["total_kills"], 2
        )
        vista["accuracy"] = round(
            100 * float(stats["total_shots_hit"]) / stats["total_shots_fired"], 2
        )
        try:
            db._dofitos_general_stats_db.replace_one(
                {"steam_id": vista["steam_id"]}, vista, upsert=True
            )
            print("OK")
        except:
            print("vista not updated")
    except Exception as e:
        print("something bad happend")
        raise e
