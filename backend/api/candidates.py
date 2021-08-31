import os
import re
from datetime import datetime

from backend.middlewares.auth import cec_only, auth_required
from backend.models.models import Candidates, Election, ElectionMethods, User
from backend.models.orm import db
from flask import g, request
from flask_restx import (
    Namespace,
    Resource,
    abort,
    marshal_with,
    reqparse,
    fields,
    marshal,
)
from flask_restx.inputs import datetime_from_iso8601
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/candidates"

api = Namespace("candidates", description="Election portals Election generic frontend")

parser = reqparse.RequestParser()
parser.add_argument(
    "manifesto", type=str, help="Candidate manifesto", location="form", required=True
)
parser.add_argument("photo", type=FileStorage, help="Candidate photo", location="files")


def check_nomination_eligibility(user: User, election: Election) -> bool:
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
            re.search(constituency.candidate_regex, user.__constituency__())
            for constituency in constituencies
        ]
    )


@api.route("/<int:election_id>/candidate/<int:user_id>")
class Nominate(Resource):
    def get(self, election_id, user_id):
        """
        Endpoint to get the details of a candidate
        """
        election = Election.query.get(election_id)
        if not election:
            abort(404, "Election not found")
        candidate = Candidates.query.filter_by(
            user_id=user_id, election_id=election_id
        ).first()
        if not candidate:
            abort(404, "Candidate not found")
        if g.user.id != user_id and not candidate.approval_status:
            abort(403, "Candidate not found")
        return marshal(candidate, candidate.api_model), 200

    @api.expect(parser)
    @api.doc(security="apikey")
    @auth_required
    def post(self, election_id, user_id):

        user = g.user
        assert user

        if user_id != user.id:
            abort(400, "Not authorized")

        election = Election.query.filter_by(id=election_id).first()
        if not election:
            abort(404, "Election not found")

        if not self.changes_allowed(election):
            abort(400, "Nominations are currently closed")

        candidate = election.get_candidate(user_id=user_id)
        if candidate:
            abort(400, "Already a candidate")

        if not check_nomination_eligibility(user, election):
            abort(400, "You are not eligible to be a candidate")

        args = parser.parse_args()
        filename = None
        if args["photo"]:
            _, extension = os.path.splitext(args["photo"].filename)
            filename = "{}{}".format(user_id, extension)
            args["photo"].save(os.path.join(UPLOAD_FOLDER, filename))

        candidate = Candidates(
            user_id=user.id,
            election_id=election_id,
            manifesto=args["manifesto"],
            photo=filename,
        )
        db.session.add(candidate)
        db.session.commit()

        return 200

    @api.expect(parser)
    @api.doc(security="apikey")
    @auth_required
    def put(self, election_id, user_id):

        user = g.user
        assert user

        if user_id != user.id:
            abort(400, "Not authorized")

        election = Election.query.filter_by(id=election_id).first()
        if not election:
            abort(404, "Election not found")

        if not self.changes_allowed(election):
            abort(400, "You cannot update after nominations are closed")

        candidate = election.get_candidate(user_id)
        if not candidate:
            abort(400, "You are not a candidate for this election")

        args = parser.parse_args()
        if args["photo"]:
            _, extension = os.path.splitext(args["photo"].filename)
            filename = "{}{}".format(user_id, extension)
            args["photo"].save(os.path.join(UPLOAD_FOLDER, filename))

        if candidate.approval_status:
            candidate.prev_manifesto = candidate.manifesto
            candidate.approval_status = None

        candidate.manifesto = args["manifesto"]
        db.session.commit()

        return 200

    @auth_required
    @api.doc(security="apikey")
    def delete(self, election_id, user_id):

        # check if current user = user_id

        user = g.user
        assert user

        if user_id != user.id:
            abort(400, "Not authorized")

        election = Election.query.filter_by(id=election_id).first()
        if not election:
            abort(404, "Election not found")

        if not self.withdraw_allowed(election):
            abort(400, "Voting has already started")

        candidate = election.get_candidate(user_id)

        if not candidate:
            abort(400, "You are not a candidate for this election")

        db.session.delete(candidate)
        db.session.commit()

        return 200

    def changes_allowed(self, election):
        """
        Checks if user can nominate or update manifesto
        """
        current_datetime = datetime.now()
        nomination_start_datetime = election.nomination_start_date
        nomination_end_datetime = election.nomination_end_date

        if not (
            nomination_end_datetime >= current_datetime >= nomination_start_datetime
        ):
            return False

        return True

    def withdraw_allowed(self, election):
        """
        Checks if user can withdraw nomination
        """
        current_datetime = datetime.now()
        if current_datetime >= election.voting_start_date:
            return False

        return True


@api.route("/<int:election_id>/candidate/<int:user_id>/status_update")
class CandidateApprovals(Resource):
    @cec_only
    @api.doc(security="apikey")
    def post(self, election_id, user_id):
        election = Election.query.get_or_404(election_id)
        candidate = Candidates.query.filter_by(
            election_id=election_id, user_id=user_id
        ).first()

        if candidate is None:
            abort(404, "Candidate not found")

        current_datetime = datetime.now()
        nomination_end_date = election.nomination_end_date

        if not (current_datetime <= nomination_end_date):
            abort(400, "Nominations are closed")

        candidate.approved = True
        db.session.commit()

        return 200

    @cec_only
    @api.doc(security="apikey")
    def delete(self, election_id, user_id):
        election = Election.query.get_or_404(election_id)
        candidate = Candidates.query.filter_by(
            election_id=election_id, user_id=user_id
        ).first()

        if candidate is None:
            abort(404, "Candidate not found")

        current_datetime = datetime.now()
        nomination_end_date = election.nomination_end_date

        if not (current_datetime <= nomination_end_date):
            abort(400, "Nominations are closed")

        candidate.approved = False
        db.session.commit()

        return 200


# @api.route("/<int:election_id>/results")
# class ElectionResults(Resource):
#     def get(self, election_id):
#         candidates = Election.query.get_or_404(election_id).candidates

#         model = Candidates.__json__()
#         model["pref1_counter"] = fields.Integer
#         model["pref2_counter"] = fields.Integer
#         model["pref3_counter"] = fields.Integer

#         return marshal(candidates, model)
