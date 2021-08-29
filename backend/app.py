import datetime
import os
import jwt

from cas import CASClient
from flask import Flask, redirect, render_template, request, g, session

from backend import api
from backend.middlewares import auth
from backend.models.models import User, BlacklistedTokens
from backend.models.orm import db
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

    blt = BlacklistedTokens.query.filter_by(token=access_token).first()
    if blt:
        g.user = None
    else:
        try:
            g.user = User.query.filter_by(email = auth.decode_auth_token(access_token)).first()
        except jwt.ExpiredSignatureError or jwt.InvalidTokenError:
            g.user = None





if __name__ == "__main__":
    app.run(debug=True, port=5000)
