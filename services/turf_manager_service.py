import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import select, and_
from starlette import status
from starlette.responses import JSONResponse

from core.constant import OWNER_ROLE, MANAGER_ROLE, ERROR_MESSAGE, NOT_ALLOWED, INVALID_DATES, BOOKINGS, NEXT_PAGE, \
    PREV_PAGE, NO_DATA_FOUND, NO_BOOKING_FOUND, PAYMENT_STATUS_PAID, STATUS_CONFIRM, FIXED_REVENUE, DETAILS, \
    PAYMENT_SUCCESSFUL, BOOKING_ALREADY_CANCELLED, STATUS_CANCELLED, BOOKING_CANCELLED
from core.validations import is_valid_user
from models.admin_revenue_model import AdminRevenue
from models.manage_turf_manager_model import ManageTurfManager
from models.revenue_model import Revenue
from models.turf_booking import TurfBooking


class ManagerService:
    def __init__(self, db):
        self.db = db

    async def get_turf_id(self, current_user):
        """ This method return turf manager's turf data."""
        manager_data = (self.db.query(ManageTurfManager).
                    filter(ManageTurfManager.turf_manager_id == current_user.user_id).first())

        return  manager_data.turf_id


    async def get_booking_data(self,current_user, start_date, end_date, page, size):
        """ This method get turf booking data."""
        try:
            is_valid_user(self.db, current_user.user_id)
            turf_id = await self.get_turf_id(current_user)
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
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                    detail = NO_DATA_FOUND)

            load_dotenv()
            HOST = os.environ.get("HOST")
            PORT = os.environ.get("PORT")

            total_turf_booking = (self.db.query(TurfBooking).
                                  filter(TurfBooking.turf_id == turf_id).all())

            next_page = (f"http://{HOST}:{PORT}/api/v1/manager/get-turf-bookings?{start_date.date()}&{end_date.date()}?"
                         f"page={page + 1}&size={size}") \
                if (page * size) < len(total_turf_booking) else None

            previous_page = (f"http://{HOST}:{PORT}/api/v1/manager/get-turf-bookings?{start_date.date()}&{end_date.date()}"
                             f"page={page - 1}&size={size}") \
                if page > 1 else None

            return {
                BOOKINGS: turf_booking,
                NEXT_PAGE: next_page,
                PREV_PAGE: previous_page
            }

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail = ERROR_MESSAGE.format(str(e)))

    def is_booking_data(self, booking_id):
        try:
            booking_data = self.db.query(TurfBooking).filter(TurfBooking.id == booking_id).first()

            if not booking_data:
                raise HTTPException(status_code=404, detail = NO_BOOKING_FOUND)

            if booking_data.booking_status == STATUS_CANCELLED:
                raise HTTPException(status_code=400, detail=BOOKING_ALREADY_CANCELLED)

            return booking_data

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))


    async def take_payment(self, booking_data, current_user):
        """ this method implements the payment of booking and add revenue to admin."""
        try:
            is_valid_user(self.db, current_user.user_id)
            turf_id =  await self.get_turf_id(current_user)

            turf_booking_data = self.is_booking_data(booking_data.id)

            turf_booking_data.payment_status = PAYMENT_STATUS_PAID
            turf_booking_data.booking_status = STATUS_CONFIRM
            turf_booking_data.update_at = datetime.now()
            turf_booking_data.updated_by = current_user.user_id


            admin_revenue_data = (self.db.query(AdminRevenue).
                                  filter(AdminRevenue.turf_id == turf_id)).first()

            revenue_mode = admin_revenue_data.revenue_mode
            amount = admin_revenue_data.amount

            if revenue_mode == FIXED_REVENUE:
                admin_revenue = amount
            else:
                admin_revenue = (turf_booking_data.total_amount * amount) // 100

            revenue = Revenue(
                turf_booking_id = turf_booking_data.id,
                amount = admin_revenue
            )
            self.db.add(revenue)
            self.db.commit()
            self.db.refresh(turf_booking_data)
            self.db.refresh(revenue)

            return JSONResponse({
                DETAILS: PAYMENT_SUCCESSFUL
            })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def cancel_booking(self, cancel_booking_data, current_user):
        """ This method cancel booking of turf."""
        try:
            is_valid_user(self.db, current_user.user_id)
            turf_booking_data = self.is_booking_data(cancel_booking_data.booking_id)

            turf_booking_data.booking_status = STATUS_CANCELLED
            turf_booking_data.cancelled_by = current_user.user_id
            turf_booking_data.cancel_reason = cancel_booking_data.cancel_reason

            self.db.commit()
            self.db.refresh(turf_booking_data)

            return JSONResponse({
                DETAILS: BOOKING_CANCELLED
            })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

