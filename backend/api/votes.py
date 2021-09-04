from flask_restx import Namespace, Resource, reqparse


from backend.middlewares.auth import auth_required
from backend.utils.vote import vote, cast, audit


api = Namespace("votes", description="Votes related operations")
voteparser = reqparse.RequestParser()
voteparser.add_argument(
    "votes",
    type=int,
    help="List of candidates voted for",
    action="append",
    location="form",
    required=True,
)
castparser = reqparse.RequestParser()
castparser.add_argument(
    "votecampid",
    type=str,
    help="The vote camp id received on /vote endpoint",
    location="form",
    required=True,
)


@api.route("/<int:election_id>/vote")
class Vote(Resource):
    @api.expect(voteparser)
    @api.doc(security="apikey")
    @auth_required
    def post(self, election_id):
        args = voteparser.parse_args()
        return vote(election_id, args.get("votes"))


@api.route("/<int:election_id>/cast")
class Cast(Resource):
    @api.expect(castparser)
    @api.doc(security="apikey")
    @auth_required
    def post(self, election_id):
        args = castparser.parse_args()
        return cast(election_id, args.get("votecampid"))


@api.route("/<int:election_id>/audit")
class Audit(Resource):
    @api.expect(castparser)
    @api.doc(security="apikey")
    @auth_required
    def post(self, election_id):
        args = castparser.parse_args()
        return audit(args.get("votecampid"))
