from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status
from authentication.token_management import verify_access_token
from core.constant import NOT_AUTHORIZED
from core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/user/sing-in")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    """ This function check there is a valid token in request."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = NOT_AUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    return verify_access_token(db, token, credentials_exception)