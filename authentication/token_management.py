from datetime import datetime, timedelta, timezone
from uuid import UUID
import jwt
from fastapi import HTTPException
from jwt import DecodeError
from starlette import status
from core.constant import EXPIRES, REFRESH_TOKEN_REQUIRED, IS_REFRESH, ACCESS_TOKEN_REQUIRED, TOKEN_EXPIRED
from models.blacklist_token_model import BlackListToken
from schemas.user_schemas import TokenData
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get("HASH_KEY")
ALGORITHM = os.environ.get("HASH_ALGO")


def create_access_token(data: dict, expires_delta: timedelta | None = None, refresh = False):
    """ This function create access token and refresh token for the given data."""

    load_dotenv()
    ACCESS_TOKEN_EXPIRE_TIME = os.environ.get("JWT_ACCESS_TOKEN_TIME")
    REFRESH_TOKEN_EXPIRE_TIME = os.environ.get("JWT_REFRESH_TOKEN_TIME")
    to_encode = data.copy()

    if refresh:
        expire = datetime.now(timezone.utc) + timedelta(hours = int(REFRESH_TOKEN_EXPIRE_TIME))
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = float(ACCESS_TOKEN_EXPIRE_TIME))

    to_encode.update({EXPIRES: expire})
    to_encode.update({IS_REFRESH: refresh})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(db, token, credentials_exception, check_refresh=False):
    """ This function verifies the token, If access token is invalid then raise exception """
    try:
        blacklisted_token = db.query(BlackListToken).filter(BlackListToken.token == token).first()

        if blacklisted_token:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = TOKEN_EXPIRED)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("sub")
        user_id: UUID = payload.get("user_id")
        role: str = payload.get("Role")
        is_refresh = payload.get("is_refresh")

        if email:
            # flag check_refresh true then validate refresh token based on is_refresh flag in token data
            if check_refresh:
                if is_refresh:
                    token_data = TokenData(email= email, user_id = user_id, role= role)
                    return token_data
                else:
                    raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = REFRESH_TOKEN_REQUIRED)

            else:
                if is_refresh:
                    raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = ACCESS_TOKEN_REQUIRED)
                else:
                    token_data = TokenData(email=email, user_id=user_id, role=role)
                    return token_data
        else:
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception

    except DecodeError:
        raise credentials_exception