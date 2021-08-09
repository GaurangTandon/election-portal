from __future__ import generator_stop
import enum
from os import isatty, rmdir

from flask_restx import fields
from backend.models.orm import db


Votes =  db.Table(
    "votes",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("election_id", db.Integer, db.ForeignKey("poll.id"), primary_key=True),
    db.Column("vote_time", db.DateTime, nullable=False)
)

Candidates = db.Table(
    "candidates",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=False),
    db.Column("election_id", db.Integer, db.ForeignKey("poll.id"), primary_key=False),
    db.Column("manifesto", db.String(1024)),
    db.Column("prev_manifesto", db.String(1024), default=None),
    db.Column("approval_status", db.Boolean, default=False),
    db.Column("pref1_counter", db.Integer, default=0),
    db.Column("pref2_counter", db.Integer, default=0),
    db.Column("pref3_counter", db.Integer, default=0)
)

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

    votes = db.relationship("Vote",
        secondary=Votes,
        backref=db.backref("election", lazy=True), 
        lazy=True
    )

    candidates = db.relationship("Candidate",
        secondary=Candidates,
        backref=db.backref("election", lazy=True),
        lazy="subquery"
    )

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


