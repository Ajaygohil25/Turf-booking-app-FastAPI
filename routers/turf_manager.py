from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from authentication.oauth2 import get_current_user
from authentication.role_checker import pre_authorize
from core.constant import MANAGER_ROLE
from core.database import get_db
from schemas.admin_schemas import IdInputSchema
from schemas.turf_owner_schema import ShowTurfBooking, CancelBooking
from schemas.user_schemas import TokenData
from services.turf_manager_service import ManagerService

router = APIRouter(
    tags = ["Turf manager"],
    prefix = "/api/v1/manager"
)

@router.get("/get-turf-bookings", response_model = ShowTurfBooking)
@pre_authorize(authorized_roles=[MANAGER_ROLE])
async def get_booking_data(
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user),
        start_date: datetime = datetime.now().date(),
        end_date: datetime =datetime.now().date(),
        page: int = 1,
        size: int = 5
):
    manager_service = ManagerService(db)
    return await manager_service.get_booking_data(current_user, start_date, end_date, page, size)

@router.post("/take-booking-payment")
@pre_authorize(authorized_roles=[MANAGER_ROLE])
async def take_booking(
        booking_data : IdInputSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    manager_service = ManagerService(db)
    return await manager_service.take_payment(booking_data, current_user)

@router.post("/cancel-booking")
@pre_authorize(authorized_roles=[MANAGER_ROLE])
async def cancel_booking(
        cancel_booking_data : CancelBooking,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    manager_service = ManagerService(db)
    return await manager_service.cancel_booking(cancel_booking_data, current_user)

