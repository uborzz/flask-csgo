"""Response builders for integration with the Chrome plugin."""

from flask import Response, current_app, jsonify
import json
from typing import Dict


def success(data: Dict, status_code: int = 200) -> Response:
    data["result"] = "OK"
    response = Response(
        response=json.dumps(data), status=status_code, mimetype="application/json",
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def error(description: str, status_code: int = 400) -> Response:
    response = Response(
        response=json.dumps({"result": "error", "description": description}),
        status=status_code,
        mimetype="application/json",
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
