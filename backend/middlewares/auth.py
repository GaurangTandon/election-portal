from functools import wraps
from cas import CASClient

from flask import request, g
from flask_restx import abort

from backend.models.models import User

cas_client = CASClient(
    version = 3,
    service_url="http://localhost:5000/",
    server_url="login.iiit.ac.in/cas"
)

def auth_required(f):
    '''
    decorator for authentication
    '''
    @wraps(f)
    def _auth_required(*args, **kwargs):
        return f(*args, **kwargs)

    return _auth_required

def admin_only(f):
    '''
    decorator to restrict access onlt to admins
    '''
    @wraps(f)
    def _admin_only(*args, **kwargs):
        return f(*args, **kwargs)

    return _admin_only
