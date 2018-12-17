from datetime import datetime
from pprint import pprint
import requests
import xmltodict
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, Response
from pymongo import MongoClient
from bson import json_util
import _configs as cfg

app = Flask(__name__)

# db info
client = MongoClient(cfg.mongo_uri, maxPoolSize=50, wtimeout=2000)
db = client['steam']  # database
dofitos = db['dofitos']  # collection
dofitos_general_stats_db = db['dofitos_general']  # collection
group = db['group_info']  # collection
testdb = db['test']  # collection


#############################################################
    # Scheduler routine
#############################################################

scheduler = BackgroundScheduler()
scheduler.start()

def format_data(player_data):
    try:
        vista = dict()
        vista['steam_id'] = player_data['playerstats']['steamID']
        vista['nick'] = player_data['nick']
        vista['last_updated'] = player_data['last_updated']
        stats = dict()
        for element in player_data['playerstats']['stats']:
            stats[element['name']] = element['value']
        vista['kd_ratio'] = round(stats['total_kills'] / stats['total_deaths'], 2)
        vista['total_win'] = round(100 * (stats['total_matches_won']) / (stats['total_matches_played']), 2)
        vista['time_played'] = int(stats['total_time_played'] / 3600)
        vista['rounds_won'] = round(100 * (stats['total_wins']) / (stats['total_rounds_played']), 2)
        vista['headshots'] = round(100 * (stats['total_kills_headshot']) / (stats['total_kills']), 2)
        vista['accuracy'] = round(100 * (stats['total_shots_hit']) / (stats['total_shots_fired']), 2)
        try:
            dofitos_general_stats_db.replace_one({"steam_id": vista['steam_id']}, vista, upsert=True)
            print("OK")
        except:
            print("vista not updated")
    except Exception as e:
        print("something bad happend")
        raise e


def update_database_data():
    time_now = datetime.now()
    player_url = "http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={}&steamid={}"
    status_url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}"
    group_url = "http://steamcommunity.com/groups/dofitosbastardos/memberslistxml/?xml=1"
    members_ids = []
    try:
        r = requests.get(group_url)
        if r.status_code == 200:
            data = xmltodict.parse(r.text, dict_constructor=dict)
            pprint(data)
            members_ids = data["memberList"]["members"]["steamID64"]
            print(members_ids)
            try:
                group.replace_one({}, {"members": members_ids}, upsert=True)
            except:
                print("insert failed")
        else:
            print("request status not OK")
            raise Exception("call status NOK")
    except:
        print("group call failed, tratando de tirar de previo.")
        try:
            members_ids = group.find_one()["members"]
        except:
            print("find failed. members empty.")

    for member in members_ids:
        player_steamid = member
        call_stats = player_url.format(cfg.steam_key, player_steamid)
        call_status = status_url.format(cfg.steam_key, player_steamid)
        print("calling GET statistics", call_stats)
        print("calling GET status", call_status)
        try:
            r = requests.get(call_stats)
            s = requests.get(call_status)
            if r.status_code == 200 and s.status_code == 200:
                player_data = r.json()
                player_data["nick"] = s.json()["response"]["players"][0]["personaname"]
                player_data["last_updated"] = time_now
                try:
                    res = dofitos.replace_one({"playerstats.steamID": str(player_steamid)}, player_data, upsert=True)
                    print(res.raw_result)
                    format_data(player_data)
                except:
                    print("insert ha fallado")
            else:
                print("NOK from get requests")
        except Exception as e:
            print("request ha fallado")


# update_database_data()
scheduler.add_job(update_database_data, "interval", hours=6)


#############################################################
    # Services/DB methods
#############################################################
def get_page(kwargs):
    pass

#############################################################
    # Http API
#############################################################

@app.route('/')
def home_page():
    players = dofitos_general_stats_db.find()
    return render_template('base.html', all_players=players)

@app.route('/raw')
def raw():
    res = dofitos.find_one()
    return Response(
        json_util.dumps(res),
        mimetype='application/json'
    )


# @app.route('/insert')
# def insert_dummy():
#     res = testdb.insert({"nombre": "insertado desde flask"})
#     return "ok"


if __name__ == '__main__':
    app.run()
