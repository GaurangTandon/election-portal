from datetime import datetime

from flask_restx import Namespace, Resource, reqparse, abort
from flask_restx import marshal_with
from flask_restx.inputs import datetime_from_iso8601
from flask import request, g


from backend.middlewares.auth import auth_required, admin_only
from backend.models.models import Election, ElectionMethods, Candidates, User
from backend.models.orm import db

api = Namespace("elections", description="Election portals Election generic frontend")

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="Name of the election", location="form", required=True)
parser.add_argument("description", type=str, help="Description of the election", location="form", required=True)
parser.add_argument("open_positions", type=int, help="Open positions", location="form", required=True)
parser.add_argument("nomination_start_date", type=datetime_from_iso8601, help="Start date of the nominations", location="form", required=True)
parser.add_argument("nomination_end_date", type=datetime_from_iso8601, help="End date of the nominations", location="form", required=True)
parser.add_argument("voting_start_date", type=datetime_from_iso8601, help="Start date of the voting", location="form", required=True)
parser.add_argument("voting_end_date", type=datetime_from_iso8601, help="End date of the voting", location="form", required=True)

@api.route("/election/create")
class ElectionCreate(Resource):
    @api.expect(parser)
    @admin_only
    def post(self):
        args = parser.parse_args()
        if not (
            args["nomination_start_date"] < args["nomination_end_date"]
            < args["voting_start_date"] < args["voting_end_date"]
        ):
            abort(400, "Invalid dates")
        election = Election(
            title=args["name"],
            description=args["description"],
            open_positions=args["open_positions"],
            nomination_start_date=args["nomination_start_date"],
            nomination_end_date=args["nomination_end_date"],
            voting_start_date=args["voting_start_date"],
            voting_end_date=args["voting_end_date"]
        )
        db.session.add(election)
        db.session.commit()
        return 200

@api.route("/elections")
class ElectionList(Resource):
    @marshal_with(Election.__json__())
    def get(self):
        return Election.query.all()

@api.route("/<int:election_id>")
class ElectionDetails(Resource):
    @marshal_with(Election.__json__())
    def get(self, election_id):
        return Election.query.get_or_404(election_id)

    @admin_only
    @api.expect(parser)
    def put(self, election_id):
        election = Election.query.get_or_404(election_id)
        args = parser.parse_args()
        if not (
            args["nomination_start_date"] < args["nomination_end_date"]
            < args["voting_start_date"] < args["voting_end_date"]
        ):
            abort(400, "Invalid dates")
        election.title = args["name"]
        election.description = args["description"]
        election.open_positions = args["open_positions"]
        election.nomination_start_date = args["nomination_start_date"]
        election.nomination_end_date = args["nomination_end_date"]
        election.voting_start_date = args["voting_start_date"]
        election.voting_end_date = args["voting_end_date"]
        db.session.commit()
        return 200

    @admin_only
    def delete(self, election_id):
        election = Election.query.get_or_404(election_id)
        db.session.delete(election)
        db.session.commit()
        return 200



    


    

