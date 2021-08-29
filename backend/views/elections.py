from backend.middlewares.auth import auth_required
import datetime
import random

from flask import Blueprint, render_template, g
from backend.models.models import Candidates, Election


election_routes = Blueprint("elections", __name__)

@election_routes.route("/")
# @auth_required
def home():    
    return render_template(
        "index.html",
        ongoing_election_list=Election.query.filter(
            Election.nomination_start_date < datetime.datetime.now()
        ).all(),
        upcoming_election_list = Election.query.filter(Election.nomination_start_date > datetime.datetime.now()).all(),
        now=datetime.datetime.now(), 
    )

@election_routes.route("/<int:election_id>")
def election_info(election_id):
    election = Election.query.get_or_404(election_id)
    candidates = list(election.candidates)
    random.shuffle(candidates)
    return render_template("election/election.html", election=Election.query.get(election_id), candidates=candidates)

@election_routes.route("/<int:election_id>/candidate/<int:user_id>")
def candidate_info(election_id, user_id):
    election = Election.query.get_or_404(election_id)
    return render_template("election/candidate.html",election=election,candidate=election.get_candidate(user_id),owner=True)