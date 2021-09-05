from cas import CASClient
from flask import redirect, request, render_template, Blueprint, session
import datetime

from app.utils.ldap_query import get_ldap_data
from app.models.models import User, BlacklistedTokens
from app.models.orm import db
from app.middlewares import auth

auth_routes = Blueprint("auth_routes", __name__)

cas_client = CASClient(
    version=3,
    # TODO: move to http on self-hosted domain
    service_url="http://election.iiit.ac.in/login",
    server_url="https://login.iiit.ac.in/cas/",
)


def store_new_user(email: str):
    """
    Construct a User object from email's LDAP data
    and commit to DB, if it does not already exist
    """

    user = User.query.filter_by(email=email).first()
    if user:
        return

    data = get_ldap_data(email=email)
    roll = data["rollno"]
    if not isinstance(roll, int):
        roll = int(roll)

    user = User(
        name=data["name"],
        email=email,
        roll_number=roll,
        batch=data["batch"],
        programme=data["programme"],
        gender=data["gender"],
    )
    db.session.add(user)
    db.session.commit()


@auth_routes.route("/login")
def login():
    _ = request.args.get("next")
    ticket = request.args.get("ticket")

    if not ticket:
        cas_login_url = cas_client.get_login_url()
        return redirect(cas_login_url)

    email, _, _ = cas_client.verify_ticket(ticket)

    # email is None when the ticket is invalid
    if not email:
        return redirect("/login")
    else:
        store_new_user(email)

        auth_token = auth.encode_auth_token(email)
        session["apikey"] = auth_token
        return render_template("redirect.html", token=auth_token)


@auth_routes.route("/logout")
@auth.auth_required
def logout():
    access_token = request.headers.get("Authorization")
    if not access_token:
        access_token = session["apikey"]
        session.pop("apikey")
    blt = BlacklistedTokens(token=access_token, blacklisted_on=datetime.datetime.now())
    db.session.add(blt)
    db.session.commit()
    return redirect("/")
