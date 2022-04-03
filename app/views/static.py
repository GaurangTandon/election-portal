from flask.templating import render_template
from app.middlewares.auth import auth_required
from flask import Blueprint

static_routes = Blueprint("static_routes", __name__)


@static_routes.route("/security")
@auth_required
def security():
    return "I'll work on this when I get time :sadcat:", 200


@static_routes.route("/faq")
@auth_required
def faq():
    return render_template("faq.html")

@static_routes.route("/fingerprint")
@auth_required
def fingerprint():
    return render_template("fingerprint.html")