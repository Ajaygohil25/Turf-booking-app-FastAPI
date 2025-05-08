from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile, File
from pydantic import BaseModel, field_serializer, computed_field
from uuid import UUID

from schemas.admin_schemas import RoleSchema


class UserSchema(BaseModel):
    name: str
    contact_no : int
    email: str
    password: str
    role_id: UUID
    city_id: int
    is_active: bool
    is_verified: bool
    lat: Optional[float] = None
    long: Optional[float] = None

class UpdateUserSchema(BaseModel):
    name: Optional[str] = None
    contact_no: Optional[int] = None

class StateSchema(BaseModel):
    state_name : str

class CitySchema(BaseModel):
    city_name : str
    state : StateSchema

class UserResponse(BaseModel):
    name: str
    contact_no: int
    email: str
    is_active: bool
    is_verified: bool
    role : RoleSchema
    city: CitySchema


class UserLoginSchema(BaseModel):
    email: str
    password: str

class TokenData(BaseModel):
    email: str | None = None
    user_id: UUID | None = None
    role: str | None = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    class Config:
        from_attributes = True

class NewToken(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True


class ResetPassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    class Config:
        from_attributes = True

class ForgotPassword(BaseModel):
    new_password: str
    confirm_password: str
    class Config:
        from_attributes = True

class UserMail(BaseModel):
    email: str

class TokenSchema(BaseModel):
    token : str

class LoginSchema(BaseModel):
    username: str
    password: str

class LogoutSchema(BaseModel):
    access_token: str
    refresh_token: str