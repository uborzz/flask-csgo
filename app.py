from datetime import datetime
from pprint import pprint
import requests
import xmltodict
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from pymongo import MongoClient
import _configs as gb

app = Flask(__name__)

# db info
mongo_uri = "mongodb://127.0.0.1:27017"
client = MongoClient(mongo_uri)
db = client['steam']  # database
dofitos = db['dofitos']  # collection
group = db['group_info']  # collection
testdb = db['test']  # collection

# scheduler api calls
scheduler = BackgroundScheduler()
scheduler.start()


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
        call_stats = player_url.format(gb.steam_key, player_steamid)
        call_status = status_url.format(gb.steam_key, player_steamid)
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
                except:
                    print("insert ha fallado")
            else:
                print("NOK from get requests")
        except Exception as e:
            print("request ha fallado")


update_database_data()
scheduler.add_job(update_database_data, "interval", hours=6)


@app.route('/')
def hello_world():
    return "home"


@app.route('/insert')
def insert_dummy():
    res = testdb.insert({"nombre": "insertado desde flask"})
    return "ok"


if __name__ == '__main__':
    app.run()
