import jwt as JWT
import os
from datetime import timedelta, datetime
from dotenv import load_dotenv

load_dotenv()

def generate_jwt_token(user_id):
    token_expiry_time = int(os.environ['TOKEN_EXPIRY_TIME'])
    payload = {
        'exp' : datetime.utcnow() + timedelta(seconds=token_expiry_time),
        'iat' : datetime.utcnow(),
        'sub' : user_id
    }
    token = JWT.encode(payload, os.environ['SECRET_KEY'], algorithm = 'HS256')
    return token

revoked_tokens = set()
def verification_token(gen_token):
    try:
        payload = JWT.decode(gen_token, os.environ['SECRET_KEY'], algorithms='HS256')
        if gen_token in revoked_tokens:
            return None # Token has been revoked
        return payload
    except JWT.ExpiredSignatureError:
        return None # Token expired
    except JWT.InvalidTokenError:
        return None #Token Invalid




gen_token = generate_jwt_token(1)
ver_token = verification_token(gen_token)
print(gen_token)
print("****************")
print(ver_token)