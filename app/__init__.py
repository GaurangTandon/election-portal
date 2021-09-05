from flask_restx import Api

from app.api.elections import api as ns1
from app.api.candidates import api as ns2
from app.api.votes import api as ns3
from app.api.constituencies import api as ns4

authorizations = {
    "apikey": {"type": "apiKey", "in": "header", "name": "Authorization"},
}

api = Api(
    title="Election Portal",
    version="1.0",
    description="Complete Frontend and Backend",
    authorizations=authorizations,
    doc="/docs",
)

api.add_namespace(ns1, path="/backend")
api.add_namespace(ns2, path="/backend")
api.add_namespace(ns3, path="/backend")
api.add_namespace(ns4, path="/backend")
