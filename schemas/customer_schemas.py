from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from schemas.admin_schemas import GameSchema
from schemas.turf_owner_schema import MediaSchema, AddressSchema

class DiscountSchema(BaseModel):
    discount_amount: Optional[int] = 0

    class Config:
        from_attributes = True

class TurfResponse(BaseModel):
    turf_name : str
    description: str
    amenities: List[str]
    booking_price: int
    game : GameSchema
    media : List[MediaSchema]
    addresses : AddressSchema
    discounts: List[DiscountSchema]
    distance_turf: float = Field(default=0.0)

    class Config:
        from_attributes = True


class AvailableTurf(BaseModel):
    turf_data: List[TurfResponse] = Field(default_factory=list)
    next_page: Optional[str] = None
    previous_page: Optional[str] = None

    class Config:
        from_attributes = True

class BookTurfSchema(BaseModel):
    turf_id: UUID
    reservation_date: datetime
    start_time: datetime
    end_time: datetime


class UpdateBookingSchema(BaseModel):
    booking_id: UUID
    reservation_date: datetime
    start_time: datetime
    end_time: datetime

class TurfNameSchema(BaseModel):
    turf_name: str

    class Config:
        from_attributes = True

class BookingSchema(BaseModel):
    reservation_date: datetime
    start_time: datetime
    end_time: datetime
    total_amount: int
    booking_status: str
    turf: TurfNameSchema

    class Config:
        from_attributes = True

class ShowBookingSchema(BaseModel):
    bookings : List[BookingSchema]
    next_page: Optional[str] = None
    previous_page: Optional[str] = None

class ExtendBooking(BaseModel):
    booking_id: UUID
    reservation_date: datetime
    end_time: datetime

class FeedbackSchema(BaseModel):
    turf_booking_id : UUID
    feedback : str
    rating : int
