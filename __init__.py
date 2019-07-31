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
                group.replace_one({"_id": "clan_members"}, {"members": members_ids}, upsert=True)
            except:
                print("insert failed")
        else:
            print("request status not OK")
            raise Exception("call status NOK")
    except:
        print("group call failed, tratando de tirar de previo.")
        try:
            members_ids = group.find_one({"_id": "clan_members"})["members"]
        except (KeyError, TypeError):
            members_ids
            print("find failed. members empty.")
            members_ids = list()

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


def update_dofitos_found_in_competitives():
    """
    Exploramos partidas competitivas en el sistema y nos quedamos con el nick más reciente y el id_steam
    de las coincidencias con la lista de miembros del clan de steam, tengan o no abierto el perfil.
    """
    matches = competitives.find({}, {"players_team1.nick": 1, "players_team2.nick": 1, "players_team1.steam_id": 1,
                                     "players_team2.steam_id": 1, "local_team": 1, "map": 1}).sort("_id", -1)  # Desc.
    matches_counter = matches.count()
    try:
        clan_members_ids = group.find_one({"_id": "clan_members"})["members"]
    except (KeyError, TypeError):
        clan_members_ids = list()

    members_in_competitives = list()
    steam_ids_aux = list()
    maps = list()
    for match in matches:
        print(match)
        team_text = "players_team" + str(match['local_team'])
        for player in match[team_text]:
            if player['steam_id'] in clan_members_ids:
                if player['steam_id'] not in steam_ids_aux:  # append only once
                    members_in_competitives.append(player)
                    steam_ids_aux.append(player['steam_id'])
        if match['map'] not in maps:
            maps.append(match['map'])

    group.replace_one({"_id": "members_in_competitives"},
                      {"members": members_in_competitives, "last_updated": datetime.now(),
                       "matches_last_update": matches_counter, "maps_played": maps}, upsert=True)

    print(members_in_competitives)


if update_on_launch:
    worker_data = Thread(target=update_database_data)
    worker_data.setDaemon(True)
    worker_data.start()

    worker_players_competitive = Thread(target=update_dofitos_found_in_competitives)
    worker_players_competitive.setDaemon(True)
    worker_players_competitive.start()

scheduler.add_job(update_database_data, "interval", hours=12)
scheduler.add_job(update_dofitos_found_in_competitives, "interval", hours=24)


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
    # total_partidas = competitives.find({}, {"nick": 1, "_id": 0}).count()
    partidas = competitives.find()
    total_partidas = partidas.count()
    try:
        group_info_query = group.find_one({"_id": "members_in_competitives"})
        players = group_info_query["members"]
        maps = group_info_query["maps_played"]
    except (TypeError, KeyError):
        players = list()
        maps = list()
    return render_template('competitive.html', total_partidas=total_partidas, partidas=json_util.dumps(partidas),
                           players=players, players_jsondump=json_util.dumps(players), maps=maps)


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
        return Response(
            response=json.dumps({"result": "error", "description": "Shit happend. FU.", "back_exception": str(e)}),
            status=400, mimetype='application/json')


@app.route('/match')
def get_raw_competitives_matches():
    matches = list(competitives.find())
    return jsonify(matches)


@app.route('/help_upload')
def help_subir_matches():
    return render_template('subir_matches.html')


@app.route('/matchbson')
def get_raw_competitives_matches2():
    matches = list(competitives.find())
    return Response(
        json_util.dumps(matches),
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run()

# if __name__ == '__main__':
#     app.run(ssl_context = 'adhoc')
