from flask_restx import Namespace, Resource, reqparse, abort
from backend.models.models import Election, ElectionMethods, Candidates, User
from flask_restx import marshal_with

api = Namespace("elections", description="Election portals Election generic frontend")

parser = reqparse.RequestParser()

@api.route("/elections")
class Elections(Resource):
    @marshal_with(Election.__json__())
    @api.expect(parser)
    def get(self):
        return Election.query.all()

@api.route("/<int:election_id>")
class CandidateList(Resource):
    @marshal_with(Candidates.__json__())
    def get(self, election_id):
        
        election = Candidates.query.filter(Candidates.election_id == election_id).all()
        print(election_id,type(election_id))
        return election

