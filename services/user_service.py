import os
from datetime import timedelta, datetime

from dotenv import load_dotenv
from fastapi import BackgroundTasks, HTTPException
from geoalchemy2.shape import from_shape
from shapely.geometry.point import Point
from sqlalchemy import select
from starlette import status
from starlette.responses import JSONResponse
from authentication.hashing import Hash
from authentication.token_management import create_access_token, verify_access_token
from core.constant import (LOGIN_SUB, LOGIN_CONTENT, INVALID_PASSWORD, DETAILS, \
    USER_CREATED, SING_IN, SING_IN_URL, USER_NOT_FOUND, TOKEN_SUB, TOKEN_USER_ID, TOKEN_TYPE, PASSWORD_DOES_NOT_MATCH, \
    PASSWORD_SHOULD_NOT_BE_SAME, PASSWORD_CHANGED, FORGOT_PASSWORD_URL, \
    FORGOT_PASSWORD_SUB, EMAIL_SENT, MESSAGE, TOKEN_EXPIRED, WWW_AUTHENTICATE, NEW_PASSWORD_NOT_SAME, LOGOUT_SUCCESS, \
    INVALID_CURRENT_PASSWORD, ROLE_TYPE, INVALID_USER, INCORRECT_CREDENTIALS, NO_DATA_TO_UPDATE, INVALID_CONTACT, \
    INVALID_NAME, USER_DATA_UPDATED)
from core.validations import validate_input, validate_password, validate_login_input, validate_contact_no, \
    is_valid_string
from mail.mail import send_mail
from models.blacklist_token_model import BlackListToken
from models.roles_model import Roles
from models.user_model import User
from schemas.user_schemas import Token


class UserService:
    def __init__(self, db, background_tasks: BackgroundTasks):
        self.db = db
        self.background_tasks = background_tasks

    async def get_user(self, email_id, is_exception=True):
        """ This method check user exist or not. If not exist then raise exception"""

        user_data = self.db.query(User).filter(User.email == email_id).first()

        if not user_data and is_exception:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail = USER_NOT_FOUND)
        else:
            if not user_data.is_verified or not user_data.is_active:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=INVALID_USER)

        return user_data

    async def add_user(self, request_data):
        """This method add a new user to the database."""
        if validate_input(request_data, self.db):
            encrypted_password = Hash.encrypt(request_data.password)
            user_data = User(
                name = request_data.name,
                contact_no = request_data.contact_no,
                email = request_data.email,
                password = encrypted_password,
                role_id = request_data.role_id,
                city_id= request_data.city_id,
                is_active = request_data.is_active,
                is_verified = request_data.is_verified,
                lat = request_data.lat,
                long = request_data.long,
                geom = from_shape(Point(request_data.long, request_data.lat), srid=4326)
            )
            self.db.add(user_data)
            self.db.commit()
            self.db.refresh(user_data)
            return JSONResponse(
                {
                    DETAILS: USER_CREATED,
                    SING_IN : SING_IN_URL
                }
            )

    def get_role(self, user_id):
        """ This method get role type of user. """
        query = (
            select(Roles.role_name)
            .join(User, User.role_id == Roles.id)
            .where(User.id == user_id)
        )
        result = self.db.execute(query).fetchone()
        if result:
            return result[0]

    async def user_login(self, login_data):
        """ This method authenticate a user and generate an access token."""
        input_email = login_data.username
        input_password = login_data.password

        if validate_login_input(input_email, input_password):
            user_data = await self.get_user(input_email)
            role = self.get_role(user_data.id)

            if Hash.verify_password(input_password, user_data.password):

                access_token = create_access_token(
                    data = {
                            TOKEN_SUB: input_email,
                            TOKEN_USER_ID: str(user_data.id),
                            ROLE_TYPE: role
                    }
                )

                refresh_token = create_access_token(
                    data = {
                            TOKEN_SUB: input_email,
                            TOKEN_USER_ID: str(user_data.id), ROLE_TYPE: role
                    },
                    refresh = True
                )

                self.background_tasks.add_task(send_mail, input_email, LOGIN_SUB, LOGIN_CONTENT)
                return Token(access_token = access_token, refresh_token = refresh_token, token_type = TOKEN_TYPE)

            else:
                raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = INCORRECT_CREDENTIALS)
        else:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)

    async def reset_user_password(self, token, request_data, email_id):
        """ This method reset the password of an existing user."""

        user_data = await self.get_user(email_id)

        if (validate_password(request_data.new_password) and
                validate_password(request_data.confirm_password)
                and validate_password(request_data.current_password)):

            if request_data.new_password != request_data.confirm_password:
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                    detail = PASSWORD_DOES_NOT_MATCH)

            if Hash.verify_password(request_data.current_password, user_data.password):

                if request_data.new_password == request_data.current_password:
                    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                        detail = PASSWORD_SHOULD_NOT_BE_SAME)

                self.update_user_password(user_data, request_data.new_password)
                self.blacklist_token(token)

                return JSONResponse(
                    {
                         DETAILS: PASSWORD_CHANGED,
                         SING_IN: SING_IN_URL
                    }
                )
            else:
                raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                                    detail = INVALID_CURRENT_PASSWORD)

        else:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = INVALID_PASSWORD)

    async def forgot_user_password(self, request_data):
        """This method handle the forgot password process."""

        user_data = await self.get_user(request_data.email)
        role = self.get_role(user_data.id)

        access_token_expires = timedelta(minutes = 3)
        access_token = create_access_token(
            data={
                TOKEN_SUB: user_data.email,
                TOKEN_USER_ID: str(user_data.id),
                ROLE_TYPE: role
            },
            expires_delta = access_token_expires
        )

        self.background_tasks.add_task(send_mail, request_data.email,
                                       FORGOT_PASSWORD_SUB,
                                       FORGOT_PASSWORD_URL.format(access_token))

        return JSONResponse(
            content = {
                    MESSAGE: EMAIL_SENT
        })


    def update_user_password(self, user_data, new_password):
        """ This method updates the user password"""
        user_data.password = Hash.encrypt(new_password)
        self.db.commit()
        self.db.refresh(user_data)

    def blacklist_token(self, token):
        """ This method blacklist the token by adding it into the database."""

        access_token = BlackListToken(
            token=token
        )
        self.db.add(access_token)
        self.db.commit()
        self.db.refresh(access_token)



    async def reset_forgot_user_password(self, request_data, token):
        """ This method reset the password with a secret token of forgot password."""

        token_exception = HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = TOKEN_EXPIRED,
            headers = {WWW_AUTHENTICATE : TOKEN_TYPE},
        )

        token_data = verify_access_token(self.db, token, token_exception)

        if validate_password(request_data.new_password) and validate_password(request_data.confirm_password):

            if request_data.new_password == request_data.confirm_password:
                user_data = await self.get_user(token_data.email)

                self.update_user_password(user_data, request_data.new_password)
                self.blacklist_token(token)

                return JSONResponse(
                    {
                        MESSAGE: PASSWORD_CHANGED,
                        SING_IN: SING_IN_URL
                    })
            else:
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                    detail = NEW_PASSWORD_NOT_SAME)
        else:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = INVALID_PASSWORD)

    async def logout_current_user(self, tokens):
        """ This method logout the current user."""
        self.blacklist_token(tokens.access_token)
        self.blacklist_token(tokens.refresh_token)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                     MESSAGE: LOGOUT_SUCCESS,
                     SING_IN: SING_IN_URL
            }
        )

    async def google_login(self, user):
        """ This method authenticate a user with Google and generate an access token."""
        user_data = await self.get_user(user.email)

        if not user_data:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail = USER_NOT_FOUND)

        if not user_data.is_active and user_data.is_verified:
            raise HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, detail=INVALID_USER)

        access_token_expires = timedelta(minutes = 20)

        access_token = create_access_token(
            data={
                    TOKEN_SUB: user_data.email,
                    TOKEN_USER_ID: str(user_data.id),
                    ROLE_TYPE: self.get_role(user_data.id)
            },
            expires_delta=access_token_expires
        )

        refresh_token = create_access_token(
            data={
                TOKEN_SUB: user_data.email,
                TOKEN_USER_ID: str(user_data.id),
                ROLE_TYPE: self.get_role(user_data.id)
            }
        )

        # print("authentication successful with Google")
        self.background_tasks.add_task(send_mail,
                                       user.email,
                                       LOGIN_SUB, LOGIN_CONTENT)

        return Token(access_token = access_token, refresh_token = refresh_token, token_type = TOKEN_TYPE)


    async def update_user_profile(self, update_data, current_user):
        """ This method update the user profile."""
        if update_data:
            user_data = await self.get_user(current_user.email)

            if update_data.name:

                if is_valid_string(update_data.name):
                    user_data.name = update_data.name
                else:
                    raise HTTPException(status_code = 400, detail = INVALID_NAME)

            elif update_data.contact_no:

                if validate_contact_no( update_data.contact_no):
                    user_data.contact_no = update_data.contact_no
                else:
                    raise HTTPException(status_code = 400, detail = INVALID_CONTACT)

            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=NO_DATA_TO_UPDATE)

            user_data.updated_by = current_user.user_id
            user_data.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(user_data)

            return JSONResponse(
                {
                    DETAILS: USER_DATA_UPDATED,
                }
            )

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = NO_DATA_TO_UPDATE)


