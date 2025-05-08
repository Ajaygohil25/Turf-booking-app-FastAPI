from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from schemas.turf_owner_schema import UserSchema


class RoleSchema(BaseModel):
    role_name: str

class GameSchema(BaseModel):
    game_name: str
    is_active: bool

    class Config:
        from_attributes = True

class UpdateGameSchema(BaseModel):
    game_name: str

class IdInputSchema(BaseModel):
    id: UUID

class RevenueDetails(BaseModel):
    turf_id: UUID
    turf_name: str
    revenue_amount: int

class RevenueResponse(BaseModel):
    total_revenue: int
    revenues: List[RevenueDetails]

class TurfDetails(BaseModel):
    turf_name : str

    class Config:
        from_attributes = True

class Booking(BaseModel):
    reservation_date : datetime
    start_time : datetime
    end_time : datetime
    total_amount : int
    payment_status : str
    booking_status : str
    customer : UserSchema
    turf: TurfDetails

class ShowTurfBooking(BaseModel):
    bookings : List[Booking]
    next_page: Optional[str] = None
    previous_page: Optional[str] = None


