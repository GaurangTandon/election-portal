from datetime import datetime

from flask_restx import Namespace, Resource, reqparse, abort
from flask_restx import marshal_with
from flask_restx.inputs import datetime_from_iso8601
from flask import request, g


from backend.middlewares.auth import auth_required, cec_only
from backend.models.models import (
    Constituency,
    Election,
    ElectionMethods,
    Candidates,
    User,
)
from backend.models.orm import db

api = Namespace("constituency", description="Election Constituency Frontend")

parser = reqparse.RequestParser()
parser.add_argument(
    "name", type=str, required=True, help="Constituency Name", location="form"
)
parser.add_argument(
    "open_positions",
    type=int,
    required=True,
    help="Number of open positions",
    location="form",
)
parser.add_argument(
    "preferences",
    type=int,
    required=True,
    help="Number of preferences per candidate",
    location="form",
)
parser.add_argument(
    "candidate_regex",
    type=str,
    required=True,
    help="Regular expression for eligible candidate",
    location="form",
)
parser.add_argument(
    "candidate_description",
    type=str,
    required=True,
    help="Description of candidate regex",
    location="form",
)
parser.add_argument(
    "voter_regex",
    type=str,
    required=True,
    help="Regular expression for eligible voter",
    location="form",
)
parser.add_argument(
    "voter_description",
    type=str,
    required=True,
    help="Description of voter regex",
    location="form",
)


@api.route("/<int:election_id>/add_constituency")
class AddConstituency(Resource):
    @api.expect(parser)
    @api.doc(security="apikey")
    @cec_only
    def post(self, election_id: int):
        """
        Add a constituency to an election
        """
        # Check election exists
        election = Election.query.get(election_id)
        if not election:
            abort(404, "Election not found")

        args = parser.parse_args()

        constituency = Constituency(
            name=args["name"],
            election_id=election_id,
            open_positions=args["open_positions"],
            preferences=args["preferences"],
            candidate_regex=args["candidate_regex"],
            candidate_description=args["candidate_description"],
            voter_regex=args["voter_regex"],
            voter_description=args["voter_description"],
        )

        db.session.add(constituency)
        db.session.commit()

        return 200