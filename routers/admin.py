from datetime import date
from typing import List, Annotated
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from authentication.oauth2 import get_current_user, oauth2_scheme
from authentication.role_checker import pre_authorize
from core.constant import ADMIN_ROLE
from core.database import get_db
from schemas.admin_schemas import GameSchema, UpdateGameSchema, IdInputSchema, RevenueResponse, ShowTurfBooking
from schemas.user_schemas import TokenData
from services.admin_service import AdminService

router = APIRouter(
    tags = ["admin"],
    prefix = "/api/v1/admin"
)

@router.post("/add-game")
@pre_authorize(authorized_roles=[ADMIN_ROLE])
async def add_game(request_data: GameSchema,
             db: Session = Depends(get_db),
             current_user: TokenData = Depends(get_current_user)):
    """ API end point to add game."""

    admin_service = AdminService(db)
    return await admin_service.add_games(request_data, current_user)

@router.patch("/game/{game_id}")
@pre_authorize(authorized_roles=[ADMIN_ROLE])
async def update_games(
                game_id: UUID,
                request_data: UpdateGameSchema,
                db: Session = Depends(get_db),
                current_user: TokenData = Depends(get_current_user)):
    """API end point to update game."""

    admin_service = AdminService(db)
    return await admin_service.update_game(game_id,request_data, current_user)


@router.get("/get-games", response_model=List[GameSchema])
@pre_authorize(authorized_roles=[ADMIN_ROLE])
async def get_games(db: Session = Depends(get_db),
              current_user: TokenData = Depends(get_current_user)):
    """ API end point to get all games."""

    admin_service = AdminService(db)
    return await admin_service.get_all_games()

@router.post("/approve-turf-owner")
@pre_authorize(authorized_roles=[ADMIN_ROLE])
async def approve_turf_owner(
            request_data: IdInputSchema,
            db: Session = Depends(get_db),
            current_user: TokenData = Depends(get_current_user)):
    """ API end point to approve turf owner."""

    admin_service = AdminService(db)
    return await admin_service.activate_deactivate_turf_owner(request_data, current_user, is_active = True)

@router.post("/deactivate-turf-owner")
@pre_authorize(authorized_roles=[ADMIN_ROLE])
async def approve_turf_owner(
            request_data: IdInputSchema,
            db: Session = Depends(get_db),
            current_user: TokenData = Depends(get_current_user)):
    """ API end point to approve turf owner."""

    admin_service = AdminService(db)
    return await admin_service.activate_deactivate_turf_owner(request_data, current_user)


@router.post("/approve-turf")
@pre_authorize(authorized_roles=[ADMIN_ROLE])
async def approve_turf(
            request_data: IdInputSchema,
            db: Session = Depends(get_db),
            current_user: TokenData = Depends(get_current_user)):
    """ API endpoint for approving the turf. """
    admin_service = AdminService(db)
    return await admin_service.activate_deactivate_turf(request_data,current_user, is_active = True)


@router.post("/deactivate-turf")
@pre_authorize(authorized_roles=[ADMIN_ROLE])
async def deactivate_turf(
            request_data: IdInputSchema,
            db: Session = Depends(get_db),
            current_user: TokenData = Depends(get_current_user)):
    """ API endpoint for approving the turf. """
    admin_service = AdminService(db)
    return await admin_service.activate_deactivate_turf(request_data,current_user)

@router.get("/get-revenue-data/{turf_owner_id}", response_model = RevenueResponse)
@pre_authorize(authorized_roles=[ADMIN_ROLE])
async def get_revenue_data(
            turf_owner_id : UUID,
            start_date: Optional[date],
            end_date: Optional[date],
            db: Session = Depends(get_db),
            current_user: TokenData = Depends(get_current_user)
):
    """ API endpoint for approving the turf. """
    admin_service = AdminService(db)
    return await admin_service.get_revenue_data(turf_owner_id,current_user,start_date, end_date)

@router.get("/get-booking-data", response_model = ShowTurfBooking)
@pre_authorize(authorized_roles=[ADMIN_ROLE])
async def get_booking_data(
            turf_id : UUID,
            start_date: Optional[date],
            end_date: Optional[date],
            db: Session = Depends(get_db),
            current_user: TokenData = Depends(get_current_user),
            page: int = 1,
            size: int = 5

):
    admin_service = AdminService(db)
    return await admin_service.get_booking_data(turf_id, current_user, start_date, end_date, page, size)
