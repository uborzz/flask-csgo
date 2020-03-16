# -*- coding: utf-8 -*-
from flask import redirect, url_for

from app import create_app


app = create_app()


@app.route("/")
def index():
    return redirect(url_for("competitive.index"))


if __name__ == "__main__":
    app.run()
    # app.run(ssl_context = 'adhoc')
