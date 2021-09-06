from app.middlewares.auth import auth_required
from collections import defaultdict

import datetime
import random

from flask import Blueprint, render_template, g, request, session
from app.models.models import Election, Votes
from app.utils.vote import vote, cast, audit, VOTEID_SESSION_KEY
from app.middlewares.ratelimit import limiter

election_routes = Blueprint("elections", __name__)


@election_routes.route("/")
@limiter.limit("1 per second")
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


def get_details_common_to_renders(election_id):
    election = Election.query.get_or_404(election_id)
    candidates = list(election.candidates.filter_by(approval_status=True))
    # it is possible that even a logged in user may not have a constituency
    # for example, if they are an alumni
    voter_constituency = election.get_constituency(g.user) if g.user else None
    eligible_candidates = (
        [
            candidate
            for candidate in candidates
            if voter_constituency.is_candidate_eligible(candidate.user)
        ]
        if voter_constituency
        else []
    )
    ineligible_candidates = list(set(candidates) - set(eligible_candidates))

    random.shuffle(eligible_candidates)

    constituency_wise_ineligible_cands = defaultdict(list)
    for cand in ineligible_candidates:
        cand_constituency = election.get_candidate_constituency(cand)
        key = cand_constituency.candidate_description
        constituency_wise_ineligible_cands[key].append(cand)

    for key in constituency_wise_ineligible_cands.keys():
        random.shuffle(constituency_wise_ineligible_cands[key])

    prefs = voter_constituency.preferences if voter_constituency else 0

    vote = (
        Votes.query.filter_by(election_id=election_id, user_id=g.user.id).first()
        if g.user
        else None
    )
    has_voted = True if vote else False
    can_vote = (eligible_candidates and not vote) and (
        election.voting_end_date
        >= datetime.datetime.now()
        >= election.voting_start_date
    )

    args = {}
    if voter_constituency:
        args["voter_consti_desc"] = voter_constituency.voter_description
        args["candi_consti_desc"] = voter_constituency.candidate_description
        args["consti_seats_count"] = voter_constituency.open_positions

    args.update(
        {
            "election": election,
            "candidates": candidates,
            "preferences": prefs,
            "eligible_candidates": eligible_candidates,
            "ineligible_candidates": constituency_wise_ineligible_cands,
            "can_vote": can_vote,
            "has_voted": has_voted,
            "consti_compete_count": len(eligible_candidates),
        }
    )
    return args


def vote_handler(election_id: int, display_vote_modal=False):
    message = None

    is_post_request = request.method == "POST"
    args = {}
    if is_post_request:
        message, exit_code = vote(election_id, request.form.getlist("votes"))

        if exit_code == 200:
            args["inter_message"] = message
        else:
            args["error_vote"] = message

    args["display_vote_modal"] = display_vote_modal
    args.update(get_details_common_to_renders(election_id))

    return render_template("election/election.html", **args)


@election_routes.route("/<int:election_id>", methods=["GET", "POST"])
@auth_required
@limiter.limit("2 per minute")
def election_info(election_id):
    return vote_handler(election_id=election_id)


@election_routes.route("/<int:election_id>/vote", methods=["GET"])
@auth_required
@limiter.limit("2 per minute")
def election_vote(election_id):
    return vote_handler(election_id=election_id, display_vote_modal=True)


@election_routes.route("/<int:election_id>/audit", methods=["POST"])
@auth_required
@limiter.limit("2 per minute")
def token_audit(election_id):
    votecamp_id = session[VOTEID_SESSION_KEY]
    file_path, filename = audit(votecamp_id=votecamp_id, return_file=False)

    args = get_details_common_to_renders(election_id)
    return render_template(
        "election/election.html",
        **args,
        filepath=file_path,
        audit_message=True,
        filename=filename
    )


@election_routes.route("/<int:election_id>/cast", methods=["POST"])
@auth_required
@limiter.limit("2 per minute")
def token_cast(election_id):
    votecamp_id = session[VOTEID_SESSION_KEY]
    cast(votecamp_id=votecamp_id)

    args = get_details_common_to_renders(election_id)
    return render_template("election/election.html", **args)


@election_routes.route("/<int:election_id>/candidate/<int:user_id>")
@auth_required
@limiter.limit("12 per minute")
def candidate_info(election_id, user_id):
    election = Election.query.get_or_404(election_id)
    candidates = list(election.candidates.filter_by(approval_status=True))
    candidate = election.get_candidate(user_id)
    constituency = election.get_constituency(g.user) if g.user else None
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
@limiter.limit("20 per minute")
def past_elections():
    return render_template(
        "election/past_elections.html",
        past_election_list=Election.query.filter(
            Election.voting_end_date < datetime.datetime.now()
        ).all(),
    )
