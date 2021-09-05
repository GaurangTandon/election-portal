from flask import g
from flask_restx import Namespace, Resource, reqparse, abort
from flask_restx.marshalling import marshal_with


from app.middlewares.auth import auth_required, cec_only
from app.models.models import (
    Constituency,
    Election,
)
from app.models.orm import db

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

        prefs = args["preferences"]
        open_positions = args["open_positions"]

        if open_positions <= 0:
            abort(400, "Number of open positions must be a positive integer")
        if prefs > open_positions:
            abort(400, "Number of preferences cannot exceed number of positions")

        constituency = Constituency(
            name=args["name"],
            election_id=election_id,
            open_positions=open_positions,
            preferences=prefs,
            candidate_regex=args["candidate_regex"],
            candidate_description=args["candidate_description"],
            voter_regex=args["voter_regex"],
            voter_description=args["voter_description"],
        )

        db.session.add(constituency)
        db.session.commit()

        return 200


@api.route("/<int:election_id>/constituency")
class GetConstituency(Resource):
    @marshal_with(Constituency.__json__())
    @api.doc(security="apikey")
    @auth_required
    def get(self, election_id: int):
        user = g.user
        election = Election.query.get_or_404(election_id)

        return election.get_constituency(user)
