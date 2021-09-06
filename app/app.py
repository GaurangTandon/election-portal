import os

from flask import Flask, request, g, session, send_from_directory

from app import api
from app.models.orm import db
from app.middlewares.auth import validate_access_token
from app.middlewares.ratelimit import limiter
from app.views.auth import auth_routes
from app.views.elections import election_routes
from app.views.static import static_routes


def create_app(db_path: str = "sqlite:////tmp/test.db"):
    app = Flask(__name__, static_url_path="/static")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI", db_path
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "top_secret_key")

    app.register_blueprint(auth_routes)
    app.register_blueprint(election_routes)
    app.register_blueprint(static_routes)

    limiter.init_app(app)
    api.init_app(app)
    db.init_app(app)
    db.create_all(app=app)
    return app


app = create_app()


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


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
