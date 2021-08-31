import datetime
from functools import wraps
import json
from typing import Any, Tuple, Union

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


def validate_access_token(access_token: str) -> Tuple[bool, Union[str, Any]]:
    """
    Check if given access token yields valid user or not

    Returns
    =======
    Tuple with first boolean member True iff access token is valid
    Second member is either a
    - User object corresponding to valid access token
    - Message string corresding to invalid access token
    """

    blt = BlacklistedTokens.query.filter_by(token=access_token).first()

    if blt:
        return False, "Token expired"

    try:
        user = User.query.filter_by(email=decode_auth_token(access_token)).first()
    except jwt.ExpiredSignatureError or jwt.InvalidTokenError:
        return False, "Token expired"
    except jwt.exceptions.DecodeError or json.decoder.JSONDecodeError or StopIteration:
        return False, "Invalid token, could not decode"

    return True, user


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

        success, msg_or_user = validate_access_token(access_token)
        if not success:
            return {"msg": msg_or_user, "url": url_for("auth_routes.login")}, 401
        g.user = msg_or_user
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
                return {
                    "msg": "Login required",
                    "url": url_for("auth_routes.login"),
                }, 401

        success, msg_or_user = validate_access_token(access_token)
        if not success:
            return {"msg": msg_or_user, "url": url_for("auth_routes.login")}, 401
        g.user = msg_or_user
        if g.user.email != "ec@iiit.ac.in":
            return abort(403, "Forbidden")

        return f(*args, **kwargs)

    return _admin_only
