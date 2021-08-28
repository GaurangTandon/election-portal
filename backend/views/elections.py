import datetime

from flask import Blueprint, render_template
from backend.models.models import Election


election_routes = Blueprint("elections", __name__)


@election_routes.route("/")
def home():
    return render_template(
        "index.html", election_list=Election.query.all(), now=datetime.datetime.now()
    )

@election_routes.route("/<int:election_id>")
def electionInfo(election_id):
    return render_template("election/election.html", election=Election.query.get(election_id))