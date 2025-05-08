import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import func, select, and_
from starlette import status
from starlette.responses import JSONResponse

from core.constant import (DETAILS, NOT_ALLOWED, GAME_ADDED_SUCCESS, GAME_NAME_UPDATED,
                           ERROR_MESSAGE, GAME_ALREADY_EXISTS, INVALID_TURF_OWNER_ID,
                           INVALID_GAME_ID, INVALID_TURF_ID,
                           TURF_ACTIVATION_UPDATED, TURF_OWNER_ACTIVATION_UPDATED, ADMIN_ROLE, NO_TURF_FOUND, BOOKINGS,
                           NEXT_PAGE, PREV_PAGE, NO_DATA_FOUND, ID)
from core.validations import is_valid_game, is_valid_user, is_turf
from models.game_model import Game
from models.revenue_model import Revenue
from models.turf_booking import TurfBooking
from models.turf_model import Turf
from schemas.admin_schemas import RevenueDetails, RevenueResponse


class AdminService:
    def __init__(self, db):
        self.db = db

    async def add_games(self, request_data, current_user):
        """ This method add games in system."""
        try:
            is_game_exist = (self.db.query(Game).
                             filter(func.lower(Game.game_name) == func.lower(request_data.game_name)).
                             first())

            if not is_game_exist:
                game_data = Game(
                    game_name=request_data.game_name,
                    is_active=request_data.is_active
                )
                game_data.created_by = current_user.user_id
                game_data.created_at = datetime.now()
                self.db.add(game_data)
                self.db.commit()
                self.db.refresh(game_data)
                return JSONResponse(
                    {
                        ID: str(game_data.id),
                        DETAILS: GAME_ADDED_SUCCESS
                    })
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=GAME_ALREADY_EXISTS)

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def update_game(self, game_id, update_data, current_user):
        """ This method update game in system."""
        try:
            game_data = is_valid_game(self.db, game_id)
            if game_data:
                is_game_exist = (self.db.query(Game).
                                 filter(func.lower(Game.game_name) == func.lower(update_data.game_name)).
                                 first())

                if is_game_exist:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=GAME_ALREADY_EXISTS)

                game_data.game_name = update_data.game_name
                game_data.updated_by = current_user.user_id
                game_data.updated_at = datetime.now()
                self.db.commit()
                self.db.refresh(game_data)
                return JSONResponse(
                    {
                        DETAILS: GAME_NAME_UPDATED,
                    }
                )
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=INVALID_GAME_ID)


        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def get_all_games(self):
        """ API end point to get all games."""
        try:
            games = self.db.query(Game).all()
            return games

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def update_activation_data(self, data_model, is_active, user_id):
        """ This method updates the activation of data."""

        # if is_active is true then update data as active otherwise deactivate
        if is_active:
            data_model.is_active = True
            data_model.is_verified = True
        else:
            data_model.is_active = False

        data_model.updated_by = user_id
        data_model.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(data_model)

    async def activate_deactivate_turf_owner(self, request_data, current_user, is_active=False):
        """ This method approve the turf owner. """
        try:
            turf_owner_data = is_valid_user(self.db, request_data.id, is_exception=False)

            if is_active:
                await self.update_activation_data(turf_owner_data, is_active, current_user.user_id)
            else:
                await self.update_activation_data(turf_owner_data, is_active, current_user.user_id)

                # Deactivate all the turf of turf owner after deactivate turf owner
                turf_data = self.db.query(Turf).filter(Turf.turf_owner_id == request_data.id).all()
                for turf in turf_data:
                    await self.update_activation_data(turf, is_active, current_user.user_id)

            return JSONResponse({
                DETAILS: TURF_OWNER_ACTIVATION_UPDATED
            })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def activate_deactivate_turf(self, request_data, current_user, is_active=False):
        """
            This method to activate and deactivate the turf based on the is_active.
            If the is_active is true then activate the turf otherwise deactivate turf.
        """
        try:
            turf_data = is_turf(self.db, request_data.id)
            if turf_data:
                await self.update_activation_data(turf_data, is_active, current_user.user_id)

                return JSONResponse({
                    DETAILS: TURF_ACTIVATION_UPDATED
                })

            else:
                raise HTTPException(status_code=404, detail=INVALID_TURF_ID)

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def get_revenue_data(self, turf_owner_id, current_user, start_date, end_date):
        """ This method get the revenue data."""
        try:

            is_valid_user(self.db, turf_owner_id)

            turfs = self.db.query(Turf).filter(Turf.turf_owner_id == turf_owner_id).all()

            if not turfs:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=NO_TURF_FOUND)
            total_revenue = 0
            revenue_details = []

            turfs_with_revenue = (
                self.db.query(Turf)
                .join(TurfBooking)
                .join(Revenue)
                .filter(
                    Revenue.turf_booking_id == TurfBooking.id,
                    TurfBooking.turf_id == Turf.id,
                    Turf.turf_owner_id == turf_owner_id
                )
                .distinct()
                .all()
            )

            # get revenue of each turf of turf owner
            for turf in turfs_with_revenue:
                bookings = (
                    self.db.query(TurfBooking)
                    .join(Revenue)
                    .filter(
                        Revenue.turf_booking_id == TurfBooking.id,
                        TurfBooking.turf_id == turf.id,
                        TurfBooking.reservation_date >= start_date,
                        TurfBooking.reservation_date <= end_date
                    )
                    .all()
                )

                turf_revenue = sum(
                    sum(rev.amount for rev in booking.revenue) for booking in bookings if booking.revenue)
                total_revenue += turf_revenue

                revenue_details.append(
                    RevenueDetails(
                        turf_id=turf.id,
                        turf_name=turf.turf_name,
                        revenue_amount=turf_revenue
                    )
                )

            return RevenueResponse(
                total_revenue=total_revenue,
                revenues=revenue_details
            )

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def get_booking_data(self, turf_id, current_user, start_date, end_date, page, size):
        """ This method get booking data of particular turf """
        try:
            turf_data = is_turf(self.db, turf_id)
            if turf_data:
                query = (
                    select(
                        TurfBooking
                    )
                    .where(
                        and_(
                            TurfBooking.turf_id == turf_id,
                            TurfBooking.reservation_date >= start_date,
                            TurfBooking.reservation_date <= end_date
                        )
                    )
                    .order_by(TurfBooking.created_at.desc())
                    .offset((page - 1) * size)
                    .limit(size)
                )
                result = self.db.execute(query)
                turf_booking = result.scalars().all()

                if not turf_booking:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=NO_DATA_FOUND)

                total_turf_booking = (
                    self.db.query(TurfBooking)
                    .filter(
                        TurfBooking.turf_id == turf_id,
                        TurfBooking.reservation_date >= start_date,
                        TurfBooking.reservation_date <= end_date
                    )
                    .count()
                )

                # Load environment variables for host/port
                load_dotenv()
                HOST = os.environ.get("HOST")
                PORT = os.environ.get("PORT")

                next_page = (
                    f"http://{HOST}:{PORT}/api/v1/admin/get-booking-data?"
                    f"turf_id={turf_id}&start_date={start_date}&end_date={end_date}"
                    f"&page={page + 1}&size={size}"
                    if (page * size) < total_turf_booking else None
                )

                previous_page = (
                    f"http://{HOST}:{PORT}/api/v1/admin/get-booking-data?"
                    f"turf_id={turf_id}&start_date={start_date}&end_date={end_date}"
                    f"&page={page - 1}&size={size}"
                    if page > 1 else None
                )

                return {
                    BOOKINGS: turf_booking,
                    NEXT_PAGE: next_page,
                    PREV_PAGE: previous_page
                }

            else:
                raise HTTPException(status_code=404, detail=INVALID_TURF_ID)

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))
