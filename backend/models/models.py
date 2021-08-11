from __future__ import generator_stop
import enum
from os import isatty, rmdir

from flask_restx import fields
from backend.models.orm import db

class Votes(db.Model):
    __tableman__ = "votes"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey("election.id"), primary_key=True)
    vote_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"Vote {self.user_id} {self.election_id} {self.vote_time}"
    
    def __json__():
        return {
            "user_id": fields.Integer,
            "election_id": fields.Integer,
            "vote_time": fields.DateTime
        }

class Candidates(db.Model):
    __tablename__ = "candidates"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey("election.id"), primary_key=True)
    manifesto = db.Column(db.String(1024)) #size defined as 1024 for now
    prev_manifesto = db.Column(db.String(1024), default=0)
    approval_status = db.Column(db.Boolean, default=False)
    pref1_counter = db.Column(db.Integer, default=0)
    pref2_counter = db.Column(db.Integer, default=0)
    pref3_counter = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Candidate {self.user_id} {self.election_id} {self.pref1_counter} {self.pref2_counter} {self.pref3_counter}"

    @staticmethod
    def __json__():
        return {
            "user_id": fields.Integer,
            "election_id": fields.Integer,
            "manifesto": fields.String,
            "prev_manifesto": fields.String,
            "approval_status": fields.String,
        }


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    batch = db.Column(db.String(8), nullable=False)
    gender = db.Column(db.String(8), nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)


    def __repr__(self):
        return f"User {self.id} {self.name} {self.email}"

    @staticmethod
    def __json__():
        return {
            "id": fields.Integer,
            "name": fields.String,
            "email": fields.String,
            "batch" : fields.String,
            "gender" : fields.String,
            "isAdmin" : fields.Boolean           
        }

class ElectionMethods(enum.Enum):
    test = 0

class Election(db.Model):
    __tablename__ = "election"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    instructions = db.Column(db.String(512), default="")
    notice = db.Column(db.String(64), default=None)
    open_positions = db.Column(db.Integer, nullable=False)
    allowed_groups = db.Column(db.String(32), default=None)
    election_method = db.Column(db.Enum(ElectionMethods), default=ElectionMethods.test)
    nomination_start_date = db.Column(db.DateTime, nullable=False)
    nomination_end_date = db.Column(db.DateTime, nullable=False)
    voting_start_date = db.Column(db.DateTime, nullable=False)
    voting_end_date = db.Column(db.DateTime, nullable=False)

    # votes = db.relationship("Vote",
    #     secondary=Votes,
    #     backref=db.backref("election", lazy=True), 
    #     lazy=True
    # )

    # candidates = db.relationship("Candidate",
    #     secondary=Candidates,
    #     backref=db.backref("election", lazy=True),
    #     lazy="subquery"
    # )

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

        # flask restx input parameters
        _json = {
            "id": fields.Integer,
            "title": fields.String,
            "instruction" : fields.String,
            "notice" : fields.String,
            "open_positions" : fields.Integer,
            "allowed_groups" : fields.String,
            "election_method" : ElectionMethodConverter(attribute="election_method"),
            "nomination_start_date" : fields.DateTime,
            "nomination_end_date" : fields.DateTime,
            "voting_start_date" : fields.DateTime,
            "voting_end_date" : fields.DateTime,
        }

        return _json


