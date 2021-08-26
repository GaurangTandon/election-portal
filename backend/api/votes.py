import os
import re
from datetime import datetime

from flask_restx import Namespace, Resource, reqparse, abort
from flask_restx import marshal_with
from flask_restx.inputs import datetime_from_iso8601
from flask import request, g
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


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


def get_constituencies(user: User, election: Election) -> list:
    """
    checks if user is eligible to vote for candidate
    """

    valid_constituencies = []

    constituencies = election.constituencies
    if user.email == "ec@iiit.ac.in":
        return valid_constituencies

    if not constituencies:
        raise ValueError("No constituency")

    for constituency in constituencies:
        if re.search(constituency.voter_regex, user.__constituency__()):
            valid_constituencies.append(constituency)

    return valid_constituencies


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

        if not (voting_start_date <= current_datetime <= voting_end_date):
            abort(400, "Voting is currently closed")

        vote = Votes.query.filter_by(election_id=election_id, user_id=user.id).first()
        if vote:
            abort(400, "You have already voted in this election")

        ...
