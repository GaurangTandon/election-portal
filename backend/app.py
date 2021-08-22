import datetime
import os

from cas import CASClient
from flask import Flask, redirect, render_template, request

from backend import api
from backend.middlewares import auth
from backend.models.models import BlacklistedTokens, User
from backend.models.orm import db
from backend.middlewares.ratelimit import limiter
from backend.utils.ldap_query import get_ldap_data

app = Flask(__name__, static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite:////tmp/test.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "top_secret_key")

limiter.init_app(app)
api.init_app(app)
db.init_app(app)
db.create_all(app=app)

cas_client = CASClient(
    version=3,
    service_url="http://localhost:5000/login",
    server_url="https://login.iiit.ac.in/cas/",
)


@app.route("/login")
def login():
    next = request.args.get("next")
    ticket = request.args.get("ticket")

    if not ticket:
        cas_login_url = cas_client.get_login_url()
        app.logger.debug("CAS Login URL: %s", cas_login_url)
        return redirect(cas_login_url)

    email, _, __ = cas_client.verify_ticket(ticket)
    if not email:
        return redirect("/login")
    else:
        user = User.query.filter_by(email=email).first()
        if not user:
            data = get_ldap_data(email=email)
            user = User(
                name=data["name"],
                email=email,
                roll_number=data["rollno"],
                batch=data["batch"],
                programme=data["programme"],
                gender=data["gender"],
            )
            db.session.add(user)
            db.session.commit()

        auth_token = auth.encode_auth_token(email)
        return render_template("redirect.html", token=auth_token)


@app.route("/logout")
@auth.auth_required
def logout():
    access_token = request.headers.get("Authorization")
    blt = BlacklistedTokens(token=access_token, blacklisted_on=datetime.datetime.now())
    db.session.add(blt)
    db.session.commit()
    return "Logout successful", 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
