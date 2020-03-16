from flask import render_template, Response, request, current_app, jsonify
from flask_login import login_required
from bson import json_util
import json

from ..db import db

from . import competitive
from .services import insert_competitive_matches


@competitive.route("/", methods=["GET"])
def index():
    partidas = db.get_all_competitive_matches()
    total_partidas = len(partidas)

    info = db.get_players_in_competitive()

    context = {
        "total_partidas": total_partidas,
        "partidas": json_util.dumps(partidas),
        "players": info["players"],
        "players_jsondump": json_util.dumps(info["players"]),
        "maps": info["maps"],
    }

    return render_template("competitive.html", **context)


@competitive.route("/match")
@login_required
def get_raw_competitives_matches():
    matches = db.get_all_competitive_matches()
    return jsonify(matches)


@competitive.route("/help_upload")
def help_subir_matches():
    return render_template("subir_matches.html")


@competitive.route("/upload", methods=["POST"])
def upload_games():
    try:
        if request.args["password"] == current_app.config["UPLOAD_PASS"]:
            # inserta base datos
            data = json.loads(request.data)
            result = insert_competitive_matches(data["matches"])
            response = jsonify(result)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        else:
            return jsonify({"result": "error", "description": "pass not OK."})

    except Exception as e:
        print(str(e))
        return Response(
            response=json.dumps({"result": "error", "description": "Shit happend."}),
            status=400,
            mimetype="application/json",
        )
