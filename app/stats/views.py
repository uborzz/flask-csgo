from flask import render_template, Response
from bson import json_util

from ..db import db

from . import stats


@stats.route("/", methods=["GET"])
def index():
    players = db.get_general_stats()
    names = sorted([member["nick"] for member in players], key=lambda s: s.lower())

    context = {"all_players": players, "names": names}

    return render_template("stats.html", **context)


@stats.route("/<member_id>", methods=["GET"])
def raw(member_id):
    result = db.get_player_public_stats(member_id)
    print("result", type(result))
    print("jsoned", type(json_util.dumps(result)))
    return Response(json_util.dumps(result), mimetype="application/json")
