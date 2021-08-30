from cas import CASClient
from flask import redirect, request, render_template, Blueprint, session
import datetime

from backend.utils.ldap_query import get_ldap_data
from backend.models.models import User, BlacklistedTokens
from backend.models.orm import db
from backend.middlewares import auth

auth_routes = Blueprint("auth_routes", __name__)

cas_client = CASClient(
    version=3,
    service_url="http://localhost:5000/login",
    server_url="https://login.iiit.ac.in/cas/",
)


@auth_routes.route("/login")
def login():
    next = request.args.get("next")
    ticket = request.args.get("ticket")

    if not ticket:
        cas_login_url = cas_client.get_login_url()
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
