import datetime
from functools import wraps
import json
import os
from typing import Any, Tuple, Union

import jwt
from app.models.models import Election, User, BlacklistedTokens
from flask import g, request, redirect, url_for, session
from flask_restx import abort
import app

RESTRICTED_IP_ADDRS_RAW = os.getenv("RESTRICTED_IP_ADDRS", "")
RESTRICTED_IP_ADDRS = RESTRICTED_IP_ADDRS_RAW.split(',') if RESTRICTED_IP_ADDRS_RAW else []
RESTRICTED_FINGERPRINTS_RAW = os.getenv("RESTRICTED_FINGERPINTS", "")
RESTRICTED_FINGERPRINTS = RESTRICTED_FINGERPRINTS_RAW.split(',') if RESTRICTED_FINGERPRINTS_RAW else []

def encode_auth_token(email):
    """
    encodes the auth token
    """
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=2),
        "iat": datetime.datetime.utcnow(),
        "sub": email,
    }
    return jwt.encode(payload, app.app.app.config.get("SECRET_KEY"), algorithm="HS256")


def decode_auth_token(auth_token):
    """
    decodes the auth token
    """
    payload = jwt.decode(
        auth_token, app.app.app.config.get("SECRET_KEY"), algorithms=["HS256"]
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
                # TODO: how to make this return differently based on GET/POST requests
                # return "Requires CAS login", 401
                return redirect(url_for("auth_routes.login"))

        success, msg_or_user = validate_access_token(access_token)
        if not success:
            return redirect(url_for("auth_routes.login"))
            # return {"msg": msg_or_user, "url": url_for("auth_routes.login")}, 401
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
        if g.user.email != Election.EC_EMAIL:
            return abort(403, "Forbidden: only EC can create election")

        return f(*args, **kwargs)

    return _admin_only

def polling_booth_only(f):
    """
    decorator to restrict access only to machines on the polling booth
    """

    @wraps(f)
    def _polling_booth_only(*args, **kwargs):
        if RESTRICTED_IP_ADDRS:
            ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip_addr not in RESTRICTED_IP_ADDRS:
                return "Invalid IP: not at polling booth", 403
        if RESTRICTED_FINGERPRINTS:
            fingerprint_data = request.form.get('fingerprinter')
            if fingerprint_data not in RESTRICTED_FINGERPRINTS:
                return "Invalid browser fingerprint: not at polling booth", 403

        return f(*args, **kwargs)

    return _polling_booth_only
