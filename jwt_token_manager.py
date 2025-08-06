import jwt
import dotenv
import os

dotenv.load_dotenv()
FLASK_APP_ID = os.environ.get("FLASK_APP_ID", None)

def get_secret_key():

    return FLASK_APP_ID

def create_jwt_access_token(user_login):
    try:
        # token should expire after 24 hrs
        token = jwt.encode(
            {"user_login": user_login},
            get_secret_key(),
            algorithm="HS256"
        )
        return token
    except Exception as e:
        # log some error here
        return None

def decode_jwt_token(token):
    try:
        data = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
        return data

    except Exception as e:
        return None
