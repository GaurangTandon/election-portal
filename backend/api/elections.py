from flask_restx import Namespace, Resource, reqparse
from backend.models.models import Election, ElectionMethods
from flask_restx import marshal_with

api = Namespace("elections", description="Election portals Election generic frontend")

parser = reqparse.RequestParser()
parser.add_argument("type", type=str, help="Filter on election type")

@api.route("/elections")
class Elections(Resource):
    @marshal_with(Election.__json__())
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        election_type = args.get("type")
        election_type_valid = election_type and election_type in ElectionMethods.__members__

        # didnt even ask for type
        if not election_type:
            return Election.query.all()

        # asked for a type
        if election_type_valid:
            return Election.query.filter(Election.type == election_type).all()

        # matched nothing
        return []
