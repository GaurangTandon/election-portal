from functools import wraps
import datetime

import jwt
from backend.models.models import User, BlacklistedTokens
from flask import g, request, redirect, url_for, session
from flask_restx import abort
import backend


def encode_auth_token(email):
    """
    encodes the auth token
    """
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=2),
        "iat": datetime.datetime.utcnow(),
        "sub": email,
    }
    return jwt.encode(
        payload, backend.app.app.config.get("SECRET_KEY"), algorithm="HS256"
    )


def decode_auth_token(auth_token):
    """
    decodes the auth token
    """
    payload = jwt.decode(
        auth_token, backend.app.app.config.get("SECRET_KEY"), algorithms=["HS256"]
    )
    return payload["sub"]


def auth_required(f):
    """
    decorator for authentication
    """

    @wraps(f)
    def _auth_required(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        if access_token is None:
            try:
                access_token = session["apikey"]
            except KeyError:
                return redirect(url_for("auth_routes.login"))

        blt = BlacklistedTokens.query.filter_by(token=access_token).first()
        if blt:
            return {"msg": "Token expired", "url": url_for("auth_routes.login")}, 401
        try:
            g.user = User.query.filter_by(email = decode_auth_token(access_token)).first()
        except jwt.ExpiredSignatureError or jwt.InvalidTokenError:
            return {"msg": "Token expired", "url": url_for("auth_routes.login")}, 401
        return f(*args, **kwargs)

    return _auth_required


def cec_only(f):
    """
    decorator to restrict access onlt to admins
    """

    @wraps(f)
    def _admin_only(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        if access_token is None:
            if session["apikey"]:
                access_token = session["apikey"]
            else:
                return {"msg": "Login required", "url": url_for("auth_routes.login")}, 401

        blt = BlacklistedTokens.query.filter_by(token=access_token).first()
        if blt:
            return {"msg": "Token expired", "url": url_for("auth_routes.login")}, 401
        try:
            g.user = User.query.filter_by(email = decode_auth_token(access_token)).first()
        except jwt.ExpiredSignatureError or jwt.InvalidTokenError:
            return {"msg": "Token expired", "url": url_for("auth_routes.login")}, 401

        if g.user.email != "ec@iiit.ac.in":
            return abort(403, "Forbidden")

        return f(*args, **kwargs)

    return _admin_only
