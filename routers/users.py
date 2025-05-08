from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request
from authentication.oauth2 import get_current_user, oauth2_scheme
from core.constant import SOCIAL_AUTH_REDIRECT_URL, PROMPT, CONSENT, ACCESS_TYPE, OFFLINE
from core.database import get_db
from schemas.user_schemas import UserSchema, TokenData, ResetPassword, ForgotPassword, UserMail, LoginSchema, \
    LogoutSchema, UserResponse, UpdateUserSchema
from services.user_service import UserService
from fastapi_sso.sso.google import GoogleSSO
from  dotenv import load_dotenv
import os

router = APIRouter(
    tags = ["users"],
    prefix = "/api/v1/user"
)


@router.post("/sign-up")
async def create_user(request_data: UserSchema, db: Session = Depends(get_db)):
    """API end point to handle user sign-up."""
    user_service = UserService(db, None)
    return await user_service.add_user(request_data)


@router.post("/sign-in")
async def login_user(
        background_tasks: BackgroundTasks,
        login_data: LoginSchema,
        db: Session = Depends(get_db)
):
    """API end point to handle user login."""
    user_service = UserService(db, background_tasks)
    return await user_service.user_login(login_data)


@router.patch("/reset-password")
async def reset_password(
        token: Annotated[str, Depends(oauth2_scheme)],
        request_data: ResetPassword,
        current_user: TokenData = Depends(get_current_user),
        db: Session = Depends(get_db)):
    """API end point to handle user password reset."""
    user_service = UserService(db, None)
    return await user_service.reset_user_password(token, request_data, current_user.email)


@router.post("/forgot-password")
async def forgot_password(
        request_data: UserMail,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)):
    """ API end point to handle forgot password functionality."""
    user_service = UserService(db, background_tasks)
    return await user_service.forgot_user_password(request_data)


@router.post("/reset-forgot-password")
async def reset_forgot_password(request_data: ForgotPassword, token, db: Session = Depends(get_db)):
    """API end point to handle reset password after forgot password."""
    user_service = UserService(db, None)
    return await user_service.reset_forgot_user_password(request_data, token)


@router.post("/logout")
async def logout_user(
        tokens: LogoutSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)):
    """API end point to handle user logout."""

    user_service = UserService(db, None)
    return await user_service.logout_current_user(tokens)

load_dotenv()
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

google_sso = GoogleSSO(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    SOCIAL_AUTH_REDIRECT_URL,
    allow_insecure_http = True
)

@router.get("/google-login", tags=["Google SSO"])
async def google_login():
    """API end point to initiate Google SSO login."""
    return await google_sso.get_login_redirect(params = {PROMPT: CONSENT, ACCESS_TYPE: OFFLINE})

@router.get("/callback")
async def google_callback(
        request: Request,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """ API end point to handle Google SSO callback."""
    try:
        user = await google_sso.verify_and_process(request)
        user_service = UserService(db, background_tasks)
        return await user_service.google_login(user)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

@router.patch("/update-profile")
async def update_profile(
        update_data: UpdateUserSchema,
        current_user: TokenData = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """ API endpoint for updating a profile."""
    user_service = UserService(db, None)
    return await user_service.update_user_profile(update_data,current_user)

@router.get("/profile", response_model = UserResponse)
async def show_profile(
        current_user: TokenData = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_service = UserService(db, None)
    return await user_service.get_user(current_user.email)
