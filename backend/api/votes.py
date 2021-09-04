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
    CumulativeHashes,
    Election,
    ElectionMethods,
    Candidates,
    User,
    Votes,
)
from backend.models.orm import db
from backend.utils.vote import vote


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


@api.route("/<int:election_id>/vote")
class Vote(Resource):
    @api.expect(parser)
    @api.doc(security="apikey")
    @auth_required
    def post(self, election_id):
        args = parser.parse_args()
        return vote(election_id, args.get("votes"))


@api.route("/<int:election_id>/cast")
class Cast(Resource):
    @api.expect(parser)
    @api.doc(security="apikey")
    @auth_required
    def post(self, election_id):
        args = parser.parse_args()
        return vote(election_id, args.get("votes"))


@api.route("/<int:election_id>/audit")
class Audit(Resource):
    @api.expect(parser)
    @api.doc(security="apikey")
    @auth_required
    def post(self, election_id):
        return None
