import os

from flask import Flask, request, g, session

from backend import api
from backend.models.orm import db
from backend.middlewares.auth import validate_access_token
from backend.middlewares.ratelimit import limiter
from backend.views.auth import auth_routes
from backend.views.elections import election_routes


app = Flask(__name__, static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite:////tmp/test.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "top_secret_key")

app.register_blueprint(auth_routes)
app.register_blueprint(election_routes)

limiter.init_app(app)
api.init_app(app)
db.init_app(app)
db.create_all(app=app)


@app.before_request
def before_request():
    """
    This function is executed before every request.
    """
    access_token = request.headers.get("Authorization")
    if access_token is None:
        try:
            access_token = session["apikey"]
        except KeyError:
            g.user = None
            return

    success, msg_or_user = validate_access_token(access_token)
    g.user = msg_or_user if success else None


if __name__ == "__main__":
    app.run(debug=True, port=5000)
