import os
import re
from datetime import datetime

from flask_restx import Namespace, Resource, reqparse, abort
from flask_restx import marshal_with
from flask_restx.inputs import datetime_from_iso8601
from flask import request, g
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


from backend.middlewares.auth import auth_required, admin_only
from backend.models.models import Election, ElectionMethods, Candidates, User, Votes
from backend.models.orm import db


api = Namespace("votes", description="Votes related operations")
parser = reqparse.RequestParser()
parser.add_argument(
    "pref1",
    type=int,
    help="user id of pref 1 candidate",
    location="form",
    required=True,
)
parser.add_argument(
    "pref2", type=int, help="user id of pref 2 candidate", location="form"
)
parser.add_argument(
    "pref3", type=int, help="user id of pref 3 candidate", location="form"
)


def check_voting_eligibility(user, election):
    """
    checks if user is eligible to stand for candidate
    """
    constituencies = election.constituencies
    if user.email == "ec@iiit.ac.in":
        return False

    if not constituencies:
        return True

    return any(
        [
            re.search(constituency.voter_regex, user.__constituency__())
            for constituency in constituencies
        ]
    )


@api.route("/<int:election_id>/vote")
class Vote(Resource):
    @api.expect(parser)
    @api.doc(security="apikey")
    @auth_required
    def post(self, election_id):

        user = User.query.filter_by(email=g.user).first()
        assert user

        election = Election.query.filter_by(id=election_id).first()
        if not election:
            abort(404, "Election not found")

        current_datetime = datetime.now()
        voting_start_date = election.voting_start_date
        voting_end_date = election.voting_end_date

        if not (
            current_datetime >= voting_start_date
            and current_datetime <= voting_end_date
        ):
            abort(400, "Voting is currently closed")

        if not check_voting_eligibility(user, election):
            abort(400, "You cannot vote in this election")

        vote = Votes.query.filter_by(election_id=election_id, user_id=1).first()
        if vote:
            abort(400, "You have already voted in this election")

        candidate = Candidates.query.filter_by(
            election_id=election_id, user_id=user.id
        ).first()
        if candidate:
            abort(400, "You are a candidate in this election")

        args = parser.parse_args()

        cand1 = Candidates.query.filter_by(
            election_id=election_id, user_id=args["pref1"]
        ).first()
        cand1.pref1_counter += 1

        if args["pref2"]:
            cand2 = Candidates.query.filter_by(
                election_id=election_id, user_id=args["pref2"]
            ).first()
            cand2.pref2_counter += 1

        if args["pref3"]:
            cand3 = Candidates.query.filter_by(
                election_id=election_id, user_id=args["pref3"]
            ).first()
            cand3.pref3_counter += 1

        vote = Votes(election_id=election_id, user_id=1, vote_time=current_datetime)
        db.session.add(vote)
        db.session.commit()

        return 200
