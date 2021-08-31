import os
import re
from datetime import datetime

from flask_restx import Namespace, Resource, reqparse, abort
from flask_restx import marshal_with
from flask_restx.inputs import datetime_from_iso8601
from flask import request, g


from backend.middlewares.auth import auth_required
from backend.models.models import (
    Constituency,
    Election,
    ElectionMethods,
    Candidates,
    User,
    Votes,
)
from backend.models.orm import db


api = Namespace("votes", description="Votes related operations")
parser = reqparse.RequestParser()
parser.add_argument(
    "votes",
    type=int,
    help="List of candidates voted for",
    action="append",
    location="form",
    required=True,
)


def get_constituency(user: User, election: Election) -> Constituency:
    """
    checks if user is eligible to vote for candidate
    """
    constituencies = election.constituencies
    if user.email == "ec@iiit.ac.in":
        return None

    if not constituencies:
        raise ValueError("No constituency")

    for constituency in constituencies:
        if re.search(constituency.voter_regex, user.__constituency__()):
            return constituency

    return None


@api.route("/<int:election_id>/vote")
class Vote(Resource):
    @api.expect(parser)
    @api.doc(security="apikey")
    @auth_required
    def post(self, election_id):

        user = g.user
        assert user

        election = Election.query.filter_by(id=election_id).first()
        if not election:
            abort(404, "Election not found")

        current_datetime = datetime.now()
        voting_start_date = election.voting_start_date
        voting_end_date = election.voting_end_date

        if not (voting_start_date <= current_datetime <= voting_end_date):
            abort(400, "Voting is currently closed")

        vote = Votes.query.filter_by(election_id=election_id, user_id=user.id).first()
        if vote:
            abort(400, "You have already voted in this election")

        constituency = get_constituency(user, election)
        if not constituency:
            abort(400, "You are not eligible to vote in this election")

        args = parser.parse_args()
        votes = args.get("votes")
        if not votes:
            abort(400, "Please provide a list of candidates")

        if election.election_method == ElectionMethods.IRV:
            if len(votes) != constituency.preferences:
                abort(
                    400, "You need to vote for %d candidates" % constituency.preferences
                )

            for candidate_id in votes:
                candidate = election.get_candidate(candidate_id, approval_status=True)
                if not candidate:
                    abort(400, "Candidate not found")
                if len(candidate.votes) == 0:
                    candidate.votes = [1]
                else:
                    candidate_votes = list(candidate.votes)
                    candidate_votes[0] += 1
                    candidate.votes = candidate_votes

        elif election.election_method == ElectionMethods.STV:
            for i, candidate_id in enumerate(votes):
                candidate = election.get_candidate(candidate_id, approval_status=True)
                if not candidate:
                    abort(400, "Candidate not found")
                if len(candidate.votes) == 0:
                    candidate.votes = [0 for _ in range(constituency.preferences)]
                candidate_votes = list(candidate.votes)
                candidate_votes[i] += 1
                candidate.votes = candidate_votes

        vote = Votes(election_id=election_id, user_id=user.id, vote_time=datetime.now())
        db.session.add(vote)
        db.session.commit()
        return 200
