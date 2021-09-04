from collections import defaultdict
from backend.middlewares.auth import auth_required
import datetime
import random

from flask import Blueprint, render_template, g, request
from backend.models.models import Candidates, Election
from backend.utils.vote import vote


election_routes = Blueprint("elections", __name__)


@election_routes.route("/")
def home():
    return render_template(
        "index.html",
        ongoing_election_list=Election.query.filter(
            Election.nomination_start_date <= datetime.datetime.now()
        )
        .filter(datetime.datetime.now() <= Election.voting_end_date)
        .all(),
        upcoming_election_list=Election.query.filter(
            Election.nomination_start_date > datetime.datetime.now()
        ).all(),
        now=datetime.datetime.now(),
    )


@election_routes.route("/<int:election_id>", methods=["GET", "POST"])
def election_info(election_id):
    election = Election.query.get_or_404(election_id)
    candidates = list(election.candidates.filter_by(approval_status=True))
    constituency = election.get_constituency(g.user) if g.user else None
    eligible_candidates = (
        [
            candidate
            for candidate in candidates
            if constituency.is_candidate_eligible(candidate.user)
        ]
        if constituency
        else []
    )
    ineligible_candidates = list(set(candidates) - set(eligible_candidates))
    message = None

    if request.method == "POST":
        message, _ = vote(election_id, request.form.getlist("votes"))

    random.shuffle(eligible_candidates)

    constituency_wise_ineligible_cands = defaultdict(list)
    for cand in ineligible_candidates:
        constituency = election.get_candidate_constituency(cand)
        key = constituency.candidate_description
        constituency_wise_ineligible_cands[key].append(cand)

    for key in constituency_wise_ineligible_cands.keys():
        random.shuffle(constituency_wise_ineligible_cands[key])

    return render_template(
        "election/election.html",
        election=election,
        candidates=candidates,
        preferences=constituency.preferences if constituency else 0,
        eligible_candidates=eligible_candidates,
        ineligible_candidates=constituency_wise_ineligible_cands,
        message=message,
    )


@election_routes.route("/<int:election_id>/candidate/<int:user_id>")
def candidate_info(election_id, user_id):
    election = Election.query.get_or_404(election_id)
    candidates = list(election.candidates.filter_by(approval_status=True))
    candidate = election.get_candidate(user_id)
    if g.user:
        constituency = election.get_constituency(g.user)
    if not candidate or not candidate.approval_status:
        return "Candidate not found", 404
    return render_template(
        "election/candidate.html",
        election=election,
        candidate=candidate,
        editable=user_id == g.user.id
        and election.nomination_end_date > datetime.datetime.now()
        if g.user
        else False,
        preferences=constituency.preferences if constituency else 0,
        eligible_candidates=[
            candidate
            for candidate in candidates
            if constituency.is_candidate_eligible(candidate.user)
        ]
        if constituency
        else [],
    )

@election_routes.route("/past-elections")
def past_elections():
    return render_template("election/past_elections.html",
        past_election_list=Election.query.filter(
            Election.voting_end_date < datetime.datetime.now()
        ).all())