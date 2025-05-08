from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session

from authentication.oauth2 import get_current_user
from authentication.role_checker import pre_authorize
from core.constant import OWNER_ROLE
from core.database import get_db
from schemas.admin_schemas import IdInputSchema
from schemas.turf_owner_schema import TurfSchema, TurfAddressSchema, UpdateTurfDetailsSchema, TurfResponseSchema, \
    TurfDiscountSchema, TurfManagerSchema, FeedbackResponseSchema, AddressSchema, ShowTurfBooking
from schemas.user_schemas import TokenData
from services.turf_owner_services import TurfOwnerService

router = APIRouter(
    tags=["Turf Owner"],
    prefix="/api/v1/turf-owner"
)


@router.post("/add-turf-address")
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def add_turf_address(
        address_data: TurfAddressSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.add_turf_address(address_data, current_user)


@router.post("/add-turf")
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def add_turf(
        game_id: UUID = Form(...),
        turf_name: str = Form(...),
        description: str = Form(...),
        amenities: List[str] = Form(...),
        booking_price: int = Form(...),
        media: List[UploadFile] = File(...),
        revenue_mode: str = Form(...),
        amount: int = Form(...),
        address_id: UUID = Form(...),
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_data = TurfSchema(
        game_id=game_id,
        turf_name=turf_name,
        description=description,
        amenities=amenities,
        booking_price=booking_price,
        media=media,
        revenue_mode=revenue_mode,
        amount=amount,
        address_id=address_id
    )
    turf_service = TurfOwnerService(db)
    return await turf_service.add_turfs(turf_data, current_user)


@router.patch("/update-turf-details/{turf_id}")
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def update_turf(
        turf_id: UUID,
        update_turf_data: UpdateTurfDetailsSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.update_turf_details(turf_id, update_turf_data, current_user)


@router.post("/deactivate-turf")
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def deactivate_turf(
        data: IdInputSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.deactivate_turf(data, current_user)


@router.get("/get-turf-details/{turf_id}", response_model=TurfResponseSchema)
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def get_turf_details(
        turf_id: UUID,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.show_turf_details(turf_id, current_user)


@router.post("/add-turf-discount")
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def add_discount(
        request_data: TurfDiscountSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.add_turf_discount(request_data, current_user)


@router.post("/deactivate-turf-discount")
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def discard_discount(
        request_data: IdInputSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.deactivate_turf_discount(request_data, current_user)


@router.post("/add-turf-manager")
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def add_turf_manager(
        request_data: TurfManagerSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.add_turf_manager(request_data, current_user)


@router.post("/activate-turf-manager")
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def activate_turf_manager(
        request_data: IdInputSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.activate_deactivate_manager(request_data, current_user, is_active=True)


@router.post("/deactivate-turf-manager")
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def deactivate_turf_manager(
        request_data: IdInputSchema,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.activate_deactivate_manager(request_data, current_user)


@router.get("/get-feedback/{turf_id}", response_model=List[FeedbackResponseSchema])
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def get_feedback(
        turf_id: UUID,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.get_turf_feedbacks(turf_id, current_user)


@router.get("/get-all-address", response_model=List[AddressSchema])
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def get_all_address(
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.get_addresses(current_user)


@router.get("/get-all-turfs", response_model=List[TurfResponseSchema])
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def get_all_turf(
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    turf_service = TurfOwnerService(db)
    return await turf_service.get_turfs(current_user)


@router.get("/get-turf-bookings/{turf_id}", response_model=ShowTurfBooking)
@pre_authorize(authorized_roles=[OWNER_ROLE])
async def get_booking_data(
        turf_id: UUID,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user),
        start_date: datetime = datetime.now().date(),
        end_date: datetime = datetime.now().date(),
        page: int = 1,
        size: int = 5
):
    turf_service = TurfOwnerService(db)
    return await turf_service.get_bookings(turf_id, current_user, start_date, end_date, page, size)