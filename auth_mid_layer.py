from functools import wraps
import jwt
from flask import request, abort
import jwt_token_manager

"""
It acts as a middle layer to provide security with token authentication. Use token_required decorator for any api endpoint to make it 
a protected api. 
"""
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data = jwt_token_manager.decode_jwt_token(token)
            if data is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
            current_user = data["user_login"]
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500
        return f(current_user, *args, **kwargs)

    return decorated