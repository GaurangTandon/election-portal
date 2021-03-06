import enum
import re
from typing import Optional

from flask_restx import fields, marshal
from sqlalchemy.orm import relationship

from app.models.orm import db


class Votes(db.Model):
    __tablename__ = "votes"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey("election.id"), primary_key=True)
    vote_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"Vote {self.user_id} {self.election_id} {self.vote_time}"

    @staticmethod
    def __json__():
        return {
            "user_id": fields.Integer,
            "election_id": fields.Integer,
            "vote_time": fields.DateTime,
        }


class Candidates(db.Model):
    __tablename__ = "candidates"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey("election.id"), primary_key=True)
    manifesto = db.Column(db.String(1024))  # size defined as 1024 for now
    manifesto_pdf = db.Column(
        db.String(1024), nullable=False
    )  # Temporary column to support manifestos in pdf format
    prev_manifesto = db.Column(db.String(1024), default=None)
    approval_status = db.Column(db.Boolean, default=None)
    photo = db.Column(db.String(1024), default="default.jpg")
    votes = db.Column(db.ARRAY(db.Integer), default=[])

    user = relationship("User", lazy="subquery")

    def __repr__(self):
        # TODO: integrate votes array here
        return f"Candidate {self.user_id} {self.election_id}"

    @staticmethod
    def __json__():
        return {
            "user": fields.Nested(User.__json__()),
            "election_id": fields.Integer,
            "manifesto": fields.String,
            "photo": fields.String,
            "approval_status": fields.String,
        }

    def get_key(self) -> str:
        """
        Get the key for this record used in generating the cryptographic keys
        """
        return str(self.user.roll_number)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    roll_number = db.Column(db.Integer, nullable=False)
    batch = db.Column(db.String(16), nullable=False)
    programme = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        return f"User {self.id} {self.name} {self.email}"

    @staticmethod
    def __json__():
        return {
            "id": fields.Integer,
            "roll_number": fields.Integer,
            "name": fields.String,
            "email": fields.String,
            "batch": fields.String,
            "programme": fields.String,
            "gender": fields.String,
        }

    def __constituency__(self):
        return f"{self.batch} {self.programme} {self.gender}"


class Constituency(db.Model):
    __tablename__ = "constituency"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    election_id = db.Column(db.Integer, db.ForeignKey("election.id"))
    open_positions = db.Column(db.Integer, nullable=False)
    preferences = db.Column(db.Integer, nullable=False)
    candidate_regex = db.Column(db.String(64), nullable=False)
    candidate_description = db.Column(db.String(64), nullable=False)
    voter_regex = db.Column(db.String(64), nullable=False)
    voter_description = db.Column(db.String(64), nullable=False)

    @staticmethod
    def __json__():
        return {
            "name": fields.String,
            "open_positions": fields.Integer,
            "preferences": fields.Integer,
            "candidate_regex": fields.String,
            "candidate_description": fields.String,
            "voter_regex": fields.String,
            "voter_description": fields.String,
        }

    def is_candidate_eligible(self, user: User):
        return re.search(self.candidate_regex, user.__constituency__()) is not None

    def is_voter_eligible(self, user: User):
        return re.search(self.voter_regex, user.__constituency__()) is not None


class ElectionMethods(enum.Enum):
    STV = 0
    IRV = 1


class Election(db.Model):
    __tablename__ = "election"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(512), default="")
    notice = db.Column(db.String(64), default=None)
    election_method = db.Column(db.Enum(ElectionMethods), nullable=False)
    nomination_start_date = db.Column(db.DateTime, nullable=False)
    nomination_end_date = db.Column(db.DateTime, nullable=False)
    voting_start_date = db.Column(db.DateTime, nullable=False)
    voting_end_date = db.Column(db.DateTime, nullable=False)

    candidates = relationship(Candidates, backref="election", lazy="dynamic")
    votes = relationship(Votes, backref="election", lazy=True)
    constituencies = relationship(Constituency, backref="election", lazy="subquery")

    EC_EMAIL = "ec@students.iiit.ac.in"

    def __repr__(self):
        return f"Election {self.id} {self.title}"

    @staticmethod
    def __json__():
        class ElectionMethodConverter(fields.Raw):
            """
            Converts the integer type in db to human readable string
            """

            def format(self, value):
                return ElectionMethods(value).name

        class ApprovedCandidateConverter(fields.Raw):
            """
            Converts candidates to a list of approved candidates
            """

            def format(self, value):
                return [
                    marshal(candidate, Candidates.__json__())
                    for candidate in value
                    if candidate.approval_status
                ]

        # flask restx input parameters
        _json = {
            "id": fields.Integer,
            "title": fields.String,
            "description": fields.String,
            "notice": fields.String,
            "election_method": ElectionMethodConverter(attribute="election_method"),
            "nomination_start_date": fields.DateTime,
            "nomination_end_date": fields.DateTime,
            "voting_start_date": fields.DateTime,
            "voting_end_date": fields.DateTime,
            "candidates": ApprovedCandidateConverter(attribute="candidates"),
            "constituencies": fields.List(fields.Nested(Constituency.__json__())),
        }
        return _json

    def get_candidate(self, user_id, *args, **kwargs):
        return self.candidates.filter_by(user_id=user_id, *args, **kwargs).first()

    def get_approved_candidates(self):
        return self.candidates.filter_by(approval_status=True)

    def get_constituency(self, user: User) -> Optional[Constituency]:
        """
        Get the constituency in which user is eligible to vote for in the election.
        Returns None if user is ineligible.
        """
        if user.email == Election.EC_EMAIL:
            return None

        if not self.constituencies:
            raise ValueError("No constituency")

        for constituency in self.constituencies:
            if re.search(constituency.voter_regex, user.__constituency__()):
                return constituency

        return None

    def get_candidate_constituency(
        self, candidate: Candidates
    ) -> Optional[Constituency]:
        """
        Get the constituency in which the user eligible to nominate himself in the current election.
        Returns None if user is ineligible.
        """
        if candidate.user.email == Election.EC_EMAIL:
            return None

        if not self.constituencies:
            raise ValueError("No constituency")

        candidate_consti_str = candidate.user.__constituency__()
        for constituency in self.constituencies:
            regex = constituency.candidate_regex
            if re.search(regex, candidate_consti_str):
                return constituency

        return None


class BlacklistedTokens(db.Model):
    __tablename__ = "blacklisted_tokens"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(1024), nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)


class Hashes(db.Model):
    __tablename__ = "hashes"

    HASH_LEN = 256 // 4
    NONCE_LEN = 16
    KEY_LEN = HASH_LEN

    id = db.Column(db.Integer, primary_key=True)
    """
    This user id received the vote and at the given order
    """
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    vote_camp = db.Column(db.ForeignKey("votecamp.id"), nullable=False)
    vote_camp_order = db.Column(db.Integer, nullable=False)
    key = db.Column(db.String(KEY_LEN), nullable=False)
    nonce = db.Column(db.String(NONCE_LEN), nullable=False)

    @staticmethod
    def __json__():
        return {
            "key": fields.String,
            "nonce": fields.String,
        }


class CumulativeHashes(db.Model):
    __tablename__ = "cumhashes"

    MAX_HASH_COUNT = 30
    HASH_LEN = Hashes.HASH_LEN * MAX_HASH_COUNT

    id = db.Column(db.Integer, primary_key=True)
    hash_str = db.Column(db.String(HASH_LEN), nullable=False)
    nonce = db.Column(db.String(Hashes.NONCE_LEN), nullable=False)

    @staticmethod
    def __json__():
        return {
            "hash_str": fields.String,
            "nonce": fields.String,
        }


class VoteCamp(db.Model):
    __tablename__ = "votecamp"

    ID_LEN = 64

    id = db.Column(db.String(ID_LEN), primary_key=True)
    election_id = db.Column(db.ForeignKey("election.id"), nullable=False)
    cumulative_hash = db.Column(db.ForeignKey("cumhashes.id"), nullable=False)
    # property is True when this votecamp has already been used for auditing
    has_audited = db.Column(db.Boolean, nullable=False)
    # property is True when this votecamp has already been cast
    has_cast = db.Column(db.Boolean, nullable=False)
