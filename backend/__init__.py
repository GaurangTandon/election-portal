from flask_restx import Api

from backend.api.elections import api as ns1 


authorizations = {
    "apikey": {"type": "apiKey", "in": "header", "name": "Authorization"},
    "organizer": {"type": "apiKey", "in": "header", "name": "Authorization"},
}

api = Api(
    title="Election Portal",
    version="1.0",
    description="Complete Frontend and Backend",
    authorizations=authorizations,
    # doc="/docs" 
)

api.add_namespace(ns1, path="/backend")
