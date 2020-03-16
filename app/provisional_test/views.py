from flask import Response, request
from bson import json_util
from . import test
from ..db import db


@test.route("/get")
def get_test():
    return Response(json_util.dumps({"result": "Ok"}), mimetype="application/json")


@test.route("/post", methods=["POST"])
def post_test():
    return Response(
        json_util.dumps(
            {"result": "Ok", "echo": request.json, "mimetype": request.mimetype}
        ),
        mimetype="application/json",
    )


@test.route("/db")
def insert_dummy():
    res = db._test()
    return Response(json_util.dumps(res.raw_result), mimetype="application/json")
