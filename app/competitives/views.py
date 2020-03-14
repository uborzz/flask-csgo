from flask import render_template, session, redirect, flash, url_for
from bson import json_util

from ..db import db
from ..models import CompetitiveInfo

from . import competitive


@competitive.route("/", methods=["GET"])
def index():
    partidas = db.get_all_competitive_matches()  # mongo Cursor 
    total_partidas = partidas.count()
    
    info = db.get_players_in_competitive()

    context = {
        "total_partidas": total_partidas, 
        "partidas": json_util.dumps(partidas),
        "players": info['players'], 
        "players_jsondump": json_util.dumps(info['players']), 
        "maps": info['maps']
    }

    return render_template('competitive.html', **context)
