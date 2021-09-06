from flask import Blueprint

static_routes = Blueprint("static_routes", __name__)


@static_routes.route("/security")
def security():
    return "I'll work on this when I get time :sadcat:", 200


@static_routes.route("/faq")
def faq():
    return "I'll work on this when I get time :sadcat:", 200
