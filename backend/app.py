import datetime
import os

from cas import CASClient
from flask import Flask, redirect, render_template, request

from backend import api
from backend.middlewares import auth
from backend.models.models import BlacklistedTokens, User
from backend.models.orm import db
from backend.middlewares.ratelimit import limiter
from backend.api.auth import auth_routes



app = Flask(__name__, static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite:////tmp/test.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "top_secret_key")

app.register_blueprint(auth_routes)

limiter.init_app(app)
api.init_app(app)
db.init_app(app)
db.create_all(app=app)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
