from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import UploadFile, File, Form

from pydantic import BaseModel


class TurfSchema(BaseModel):
    game_id: UUID = Form(...)
    turf_name: str = Form(...)
    description: str = Form(...)
    amenities: List[str] = Form(...)
    booking_price: int = Form(...)
    media: List[UploadFile] = File(...)
    revenue_mode: str = Form(...)
    amount: int = Form(...)
    address_id: UUID = Form(...)


class TurfAddressSchema(BaseModel):
    street_address: str
    area: str
    city_id: int
    lat: float
    long: float


class UpdateTurfDetailsSchema(BaseModel):
    turf_name: Optional[str] = None
    description: Optional[str] = None
    amenities: Optional[List[str]] = None
    booking_price: Optional[int] = None


class UpdateMediaSchema(BaseModel):
    media: List[UploadFile] = File(...)


class UserSchema(BaseModel):
    name: str
    contact_no: int

    class Config:
        from_attributes = True


class GameSchema(BaseModel):
    game_name: str

    class Config:
        from_attributes = True


class MediaSchema(BaseModel):
    media_url: str

    class Config:
        from_attributes = True


class StateSchema(BaseModel):
    state_name: str

    class Config:
        from_attributes = True


class CitySchema(BaseModel):
    city_name: str
    state: StateSchema

    class Config:
        from_attributes = True


class AddressSchema(BaseModel):
    street_address: str
    area: str
    city: CitySchema
    is_active: bool

    class Config:
        from_attributes = True


class TurfDiscountSchema(BaseModel):
    turf_id: UUID
    discount_amount: int

    class Config:
        from_attributes = True

class TurfResponseSchema(BaseModel):
    turf_name: str
    description: str
    amenities: List[str]
    booking_price: int
    game: GameSchema
    media: List[MediaSchema]
    addresses: AddressSchema
    discounts: List[TurfDiscountSchema]

    class Config:
        from_attributes = True


class TurfManagerSchema(BaseModel):
    name: str
    contact_no: int
    email: str
    password: str
    role_id: UUID
    city_id: int
    is_active: bool
    is_verified: bool
    lat: Optional[float] = None
    long: Optional[float] = None
    turf_id: UUID


class Booking(BaseModel):
    reservation_date: datetime
    start_time: datetime
    end_time: datetime
    total_amount: int
    payment_status: str
    booking_status: str
    customer: UserSchema

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}


class ShowTurfBooking(BaseModel):
    bookings: List[Booking]
    next_page: Optional[str] = None
    previous_page: Optional[str] = None


class CancelBooking(BaseModel):
    booking_id: UUID
    cancel_reason: str


class UserName(BaseModel):
    name: str

    class Config:
        from_attributes = True


class FeedbackResponseSchema(BaseModel):
    customer: UserName
    feedback: str
    rating: int

    class Config:
        from_attributes = True
