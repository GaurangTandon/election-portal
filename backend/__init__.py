from flask_restx import Api

from backend.api.elections import api as ns1 


authorizations = {
    "apikey": {"type": "apiKey", "in": "header", "name": "Authorization"},
    "organizer": {"type": "apiKey", "in": "header", "name": "Authorization"},
}

api = Api(
    title="Felicity Events",
    version="1.0",
    description="All user frontend and backend",
    authorizations=authorizations,
    # doc="/docs" SET THIS later
)

api.add_namespace(ns1, path="/backend")
