from flask import render_template, request, current_app, jsonify
from flask_login import login_required
from bson import json_util
import json
from typing import List, Dict

from ..db import db, DBException

from . import competitive
from .responses import error, success


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

            matches: List[Dict] = data["matches"]
            for match in matches:
                match["_id"] = match.pop("datetime")

            try:
                n_inserted = db.insert_competitive_matches(matches)
                data = {"inserted": n_inserted, "total": len(matches)}
                return success(data=data, status_code=200)

            except DBException:
                return error("Insertion failed.", status_code=200)

        else:
            return error("pass not OK", status_code=200)

    except Exception as e:
        print(str(e))
        return error("Shit happend.", 400)
