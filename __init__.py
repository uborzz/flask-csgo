# -*- coding: utf-8 -*-
import json
import requests
from datetime import datetime
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
from bson import json_util
from flask import Flask, render_template, Response, request, jsonify
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import xmltodict
import _configs as cfg
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
update_on_launch = False


#############################################################
    # DB_INFO
#############################################################

client = MongoClient(cfg.mongo_uri, maxPoolSize=50, wtimeout=2000)
db = client['steam']  # database
dofitos = db['dofitos']  # collection
dofitos_general_stats_db = db['dofitos_general']  # collection
group = db['group_info']  # collection
profiles = db['profile_ids']  # collection
competitives = db['competitives']  # collection
competitives_uploaders = db['competitives_uploaders']  # collection
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
        vista['kd_ratio'] = round(float(stats['total_kills']) / stats['total_deaths'], 3)
        vista['total_win'] = round(100 * float(stats['total_matches_won']) / stats['total_matches_played'], 2)
        vista['time_played'] = int(stats['total_time_played'] / 3600)
        vista['rounds_won'] = round(100 * float(stats['total_wins']) / stats['total_rounds_played'], 2)
        vista['headshots'] = round(100 * float(stats['total_kills_headshot']) / stats['total_kills'], 2)
        vista['accuracy'] = round(100 * float(stats['total_shots_hit']) / stats['total_shots_fired'], 2)
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

    # ID - "76" + (parseInt(campo-mini) + 561197960265728)
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
                player_status = s.json()["response"]["players"][0]
                player_data["nick"] = player_status["personaname"]
                player_data["last_updated"] = time_now
                player_profile_name = player_status["profileurl"]
                try:
                    profiles.update(
                        {"_id": member},  # member es el id de steam.
                        {"$addToSet": {"profile_names": player_profile_name}},
                        upsert=True
                    )
                except:
                    print("upsert profiles ha fallado")
                try:
                    res = dofitos.replace_one({"playerstats.steamID": str(player_steamid)}, player_data, upsert=True)
                    print(res.raw_result)
                    format_data(player_data)
                except:
                    print("upsert dofitos ha fallado")
            else:
                print("NOK from get requests")
        except Exception as e:
            print("request ha fallado")


if update_on_launch:
    worker = Thread(target=update_database_data)
    worker.setDaemon(True)
    worker.start()
scheduler.add_job(update_database_data, "interval", hours=12)


#############################################################
    # Services/DB methods
#############################################################
def get_page(kwargs):
    pass

def insert_competitive_matches(matches_list):
    for match in matches_list:
        match["_id"] = match.pop("datetime")
    matches_count = len(matches_list)
    try:
        result = competitives.insert_many(matches_list, ordered=False)
        return ({"result": "OK", "inserted": len(result.inserted_ids), "total": matches_count})
    except BulkWriteError as bwe:
        nr_inserts = bwe.details["nInserted"]
        return ({"result": "OK", "inserted": nr_inserts, "total": matches_count})
    except Exception as e:
        print(type(e))
        return ({"result": "error", "description": "Insertion failed."})


#############################################################
    # Http API
#############################################################

@app.route('/')
def home_page():
    players = list(dofitos_general_stats_db.find())
    names = sorted([member['nick'] for member in players], key=lambda s: s.lower())
    return render_template('base.html', all_players=players, names=names)

@app.route('/competitive')
def competitive_page():
    total_partidas = competitives.find({}, {"nick": 1, "_id": 0}).count()
    return render_template('competitive.html', total_partidas=total_partidas)

@app.route('/raw/<member_id>')
def raw(member_id):
    res = dofitos.find_one({"playerstats.steamID": member_id})
    return Response(
        json_util.dumps(res),
        mimetype='application/json'
    )

@app.route('/dbtest')
def insert_dummy():
    t = datetime.now()
    res = testdb.update_one({"nombre": "prueba insert"}, {"$set": {"date": t}}, upsert=True)
    return Response(
        json_util.dumps(res.raw_result),
        mimetype='application/json'
    )

@app.route('/gettest')
def get_test():
    return Response(
        json_util.dumps({
            "result": "Ok"
        }),
        mimetype='application/json'
    )


@app.route('/posttest', methods=['POST'])
def post_test():
    return Response(
        json_util.dumps({
            "result": "Ok",
            "echo": request.json,
            "mimetype": request.mimetype
        }),
        mimetype='application/json'
    )

@app.route('/uploadgames', methods=['POST'])
def upload_games():
    try:
        if request.args['password'] == cfg.upload_password:
            # inserta base datos
            data = json.loads(request.data)
            result = insert_competitive_matches(data['matches'])
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            return jsonify({"result": "error", "description": "pass not OK."})

    except Exception as e:
        print(str(e))
        return Response(response=json.dumps({"result": "error", "description": "Shit happend. FU."}), status=400, mimetype='application/json')

@app.route('/match')
def get_raw_competitives_matches():
    matches = list(competitives.find())
    return jsonify(matches)

@app.route('/matchbson')
def get_raw_competitives_matches2():
    matches = list(competitives.find())
    return Response(
        json_util.dumps(matches),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run()
