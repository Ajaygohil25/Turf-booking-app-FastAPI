from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from authentication.token_management import verify_access_token, create_access_token
from core.constant import INVALID_ACCESS_TOKEN, DETAILS, VALID_ACCESS_TOKEN, REFRESH_TOKEN_INVALID, \
    TOKEN_TYPE, TOKEN_SUB, TOKEN_USER_ID, ROLE_TYPE
from core.database import get_db
from schemas.user_schemas import TokenSchema, Token, NewToken

router = APIRouter(
    tags = ["Token"],
    prefix = "/api/v1/token"
)

@router.post("/verify-access-token")
async def verify_token(
        token_data : TokenSchema,
        db: Session = Depends(get_db)
):
    """ API endpoint for verifying access"""
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = INVALID_ACCESS_TOKEN,
        headers = {"WWW-Authenticate": "Bearer"},
    )
    if verify_access_token(db, token_data.token, credentials_exception):
        return JSONResponse({
            DETAILS: VALID_ACCESS_TOKEN
        })
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = INVALID_ACCESS_TOKEN)


@router.post("/create-access-token")
async def create_token(
    refresh_token_data : TokenSchema,
    db: Session = Depends(get_db)
):
    """ API for creating a new access token."""
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = REFRESH_TOKEN_INVALID,
        headers = {"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(
                                    db,refresh_token_data.token,
                                     credentials_exception,
                                     check_refresh = True
    )

    if token_data:

        data = {
            TOKEN_SUB: token_data.email,
            TOKEN_USER_ID: str(token_data.user_id),
            ROLE_TYPE: token_data.role
        }

        access_token_expires = timedelta(minutes = 30)
        new_access_token = create_access_token(data, access_token_expires)
        return NewToken(access_token = new_access_token, token_type = TOKEN_TYPE)

    else:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = REFRESH_TOKEN_INVALID)



