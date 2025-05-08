from datetime import date, datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from authentication.oauth2 import get_current_user
from authentication.role_checker import pre_authorize
from core.constant import CUSTOMER_ROLE
from core.database import get_db
from schemas.admin_schemas import IdInputSchema
from schemas.customer_schemas import AvailableTurf, BookTurfSchema, UpdateBookingSchema, ShowBookingSchema, \
    ExtendBooking, FeedbackSchema
from schemas.user_schemas import TokenData
from services.customer_service import CustomerService

router = APIRouter(
    tags = ["customer"],
    prefix = "/api/v1/customer"
)


@router.get("/get-turf-data/{game_id}/{booking_date}/{start_time}/{end_time}", response_model=AvailableTurf)
async def show_turf_data(
        game_id : UUID,
        booking_date : date,
        start_time : datetime,
        end_time : datetime,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user),
        page: int = 1,
        size: int = 5
):
    customer_service = CustomerService(db)
    return await customer_service.show_available_turfs(game_id,booking_date,
                                                 start_time,end_time,current_user,page, size)

@router.post("/book-turf")
async def reserve_turf(
        booking_data: BookTurfSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    customer_service = CustomerService(db)
    return await customer_service.book_turf(booking_data, current_user)
@router.put("/update-turf-booking")
async def update_booking(
        update_booking_data: UpdateBookingSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    customer_service = CustomerService(db)
    return await customer_service.update_turf_booking(update_booking_data, current_user)

@router.get("/show-turf-booking", response_model = ShowBookingSchema)
async def show_booking(
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user),
        page: int = 1,
        size: int = 5

):
    customer_service = CustomerService(db)
    return await customer_service.show_turf_booking_history(current_user, page, size)

@router.post("/extend-bookings")
async def extend_booking(
        extend_booking_data: ExtendBooking,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    customer_service = CustomerService(db)
    return await customer_service.extend_turf_booking(extend_booking_data, current_user)

@router.post("/cancel-bookings")
async def cancel_booking(
        turf_booking_data: IdInputSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    customer_service = CustomerService(db)
    return await customer_service.cancel_booking(turf_booking_data, current_user)

@router.post("/add-feedback")
@pre_authorize(authorized_roles=[CUSTOMER_ROLE])
async def add_feedback(
        feedback_data: FeedbackSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    customer_service = CustomerService(db)
    return await customer_service.add_feedback_turf(feedback_data, current_user)
