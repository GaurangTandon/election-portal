import os
from datetime import datetime

from backend.middlewares.auth import admin_only, auth_required
from backend.models.models import Candidates, Election, ElectionMethods, User
from backend.models.orm import db
from flask import g, request
from flask_restx import Namespace, Resource, abort, marshal_with, reqparse, fields, marshal
from flask_restx.inputs import datetime_from_iso8601
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "media/candidates"

api = Namespace("candidates", description="Election portals Election generic frontend")

parser = reqparse.RequestParser()
parser.add_argument("manifesto", type=str, help="Candidate manifesto", location="form",required=True)
parser.add_argument("photo", type=FileStorage, help="Candidate photo", location="files")


def check_nomination_eligibility(user,election):
    '''
    checks if user is eligible to stand for candidate
    '''
    allowed_groups = election.allowed_groups
    if allowed_groups:
        # deal with the case where the user is not in any of the allowed groups
        return False
        ...

    return True

@api.route("/<int:election_id>/candidate/<int:user_id>")
class Nominate(Resource):
    @api.expect(parser)
    @auth_required
    def post(self,election_id,user_id):

        user = User.query.filter_by(email=g.user).first()
        assert user

        if (user_id != user.id):
            abort(400, "Not authorized")
        
        election = Election.query.filter_by(id=election_id).first()
        if not election:
            abort(404, "Election not found")

        current_datetime = datetime.now()
        nomination_start_datetime = election.nomination_start_date
        nomination_end_datetime = election.nomination_end_date

        if not (current_datetime >= nomination_start_datetime and current_datetime <= nomination_end_datetime):
            abort(400, "Nominations are currently closed")

        candidate = Candidates.query.filter_by(election_id=election_id, user_id = 1).first()
        if candidate:
            abort(400, "Already a candidate")

        if not check_nomination_eligibility(user,election):
            abort(400, "You are not eligible to be a candidate")

        args = parser.parse_args()
        filename = None
        if args["photo"]:
            filename = secure_filename(args["photo"].filename)
            args["photo"].save(os.path.join(UPLOAD_FOLDER, "1" + filename))
        
        candidate = Candidates(
            user_id = 1,
            election_id = election_id,
            manifesto = args["manifesto"],
            photo = filename
        )
        db.session.add(candidate)
        db.session.commit()

        return 200

    @api.expect(parser)
    @auth_required
    def put(self,election_id, user_id):

        user = User.query.filter_by(email=g.user).first()
        assert user

        if (user_id != user.id):
            abort(400, "Not authorized")
        
        election = Election.query.filter_by(id=election_id).first()
        if not election:
            abort(404, "Election not found")

        current_datetime = datetime.now()
        nomination_start_datetime = election.nomination_start_date
        nomination_end_datetime = election.nomination_end_date

        if not (current_datetime >= nomination_start_datetime and current_datetime <= nomination_end_datetime):
            abort(400, "You cannot update after nominations are closed")

        candidate = Candidates.query.filter_by(election_id=election_id, user_id = 1).first()
        if not candidate:
            abort(400, "You are not a candidate for this election")

        args = parser.parse_args()
        filename = secure_filename(args["photo"].filename)
        args["photo"].save(os.path.join(UPLOAD_FOLDER, "1" + filename))

        if candidate.approval_status:
            candidate.prev_manifesto = candidate.manifesto
            candidate.approval_status = False

        candidate.manifesto = args["manifesto"]
        db.session.commit()

        return 200

    @auth_required
    def delete(self,election_id, user_id):

        # check if current user = user_id

        user = User.query.filter_by(email=g.user).first()
        assert user

        if (user_id != user.id):
            abort(400, "Not authorized")

        election = Election.query.filter_by(id=election_id).first()
        if not election:
            abort(404, "Election not found")

        current_datetime = datetime.now()
        voting_start_datetime = election.voting_start_date

        if (current_datetime >= voting_start_datetime):
            abort(400, "Voting has already started")

        candidate = Candidates.query.filter_by(election_id=election_id, user_id = 1).first()

        if not candidate:
            abort(400, "You are not a candidate for this election")

        db.session.delete(candidate)
        db.session.commit()

@api.route("/<int:election_id>/candidate/<int:user_id>/status_update")
class CandidateApprovals(Resource):

    @admin_only
    def post(self, election_id, user_id):
        election = Election.query.get_or_404(election_id)
        candidate = Candidates.query.filter_by(election_id=election_id, user_id=user_id).first()
        
        if candidate is None:
            abort(404, "Candidate not found")

        current_datetime = datetime.now()
        voting_start_date = election.voting_start_date

        if not (current_datetime <= voting_start_date):
            abort(400, "Voting has already started")

        candidate.approved = True
        db.session.commit()

        return 200

    @admin_only
    def delete(self, election_id, user_id):
        election = Election.query.get_or_404(election_id)
        candidate = Candidates.query.filter_by(election_id=election_id, user_id=user_id).first()
        
        if candidate is None:
            abort(404, "Candidate not found")

        current_datetime = datetime.now()
        voting_start_date = election.voting_start_date

        if not (current_datetime <= voting_start_date):
            abort(400, "Voting has already started")

        candidate.approved = False
        db.session.commit()

        return 200

@api.route("/<int:election_id>/results")
class ElectionResults(Resource):
    def get(self,election_id):
        candidates = Election.query.get_or_404(election_id).candidates

        model = Candidates.__json__()
        model["pref1_counter"] = fields.Integer
        model["pref2_counter"] = fields.Integer
        model["pref3_counter"] = fields.Integer

        return marshal(candidates,model)
    

