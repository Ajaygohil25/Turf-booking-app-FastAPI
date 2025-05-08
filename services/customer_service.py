import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import HTTPException
from geoalchemy2.functions import ST_DistanceSphere
from sqlalchemy import select, exists, and_, func
from sqlalchemy.orm import aliased
from starlette import status
from starlette.responses import JSONResponse

from core.constant import CUSTOMER_ROLE, ERROR_MESSAGE, DETAILS, TURF_BOOKED, \
    TURF_SLOT_ALREADY_BOOKED, TURF_UPDATE_SUCCESS, NO_BOOKING_FOUND, \
    PAYMENT_STATUS_UNPAID, STATUS_RESERVED, STATUS_CANCELLED, UPDATE_BEFORE_ONE_HOUR, \
    NOT_ALLOWED_TO_CANCEL, BOOKING_ACTION_NOT_ALLOWED, BOOKING_CANCELLED, BOOKINGS, NEXT_PAGE, PREV_PAGE, NOT_ALLOWED, \
    INVALID_FEEDBACK_INPUT, FEEDBACK_ADDED, STATUS_CONFIRM, FEEDBACK_NOT_ALLOWED, INVALID_GAME_ID, ID
from core.validations import is_valid_turf, validate_reservation, validate_extend_reservation, is_turf_booking, \
    is_valid_string, is_valid_game
from models.address_model import Address
from models.discount_model import Discount
from models.feedback_model import Feedback
from models.turf_booking import TurfBooking
from models.turf_model import Turf
from models.user_model import User
from schemas.customer_schemas import AvailableTurf, TurfResponse


class CustomerService:
    def __init__(self, db):
        self.db = db

    def get_customer_data(self, user_id):
        """ This method get customer data."""

        return self.db.query(User).filter(User.id == user_id).first()

    async def show_available_turfs(self, game_id, booking_date, start_time, end_time,
                                   current_user, page, size):
        """ This method shows available turfs nearby the customer's location based on data and time."""
        try:
            customer_data = self.get_customer_data(current_user.user_id)
            customer_geom = customer_data.geom

            if not is_valid_game(self.db, game_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=INVALID_GAME_ID)

            if validate_reservation(booking_date, start_time, end_time):

                booked_turf_subquery = (
                    select(TurfBooking.turf_id)
                    .where(
                        TurfBooking.reservation_date == booking_date,
                        TurfBooking.start_time < end_time,
                        TurfBooking.end_time > start_time
                    )
                )

                address_alias = aliased(Address)

                query = (
                    select(
                        Turf,
                        (ST_DistanceSphere(address_alias.geom, customer_geom) / 1000).label("distance_km")
                    )
                    .join(address_alias, Turf.address_id == address_alias.id)
                    .where(
                        Turf.is_active == True,
                        Turf.is_verified == True,
                        Turf.game_id == game_id,
                        address_alias.city_id == customer_data.city_id,
                        ~exists(booked_turf_subquery.where(TurfBooking.turf_id == Turf.id))
                    )
                    .order_by("distance_km")
                    .offset((page - 1) * size)
                    .limit(size)
                )

                result = self.db.execute(query)
                total_turf = result.all()

                turfs = [
                    TurfResponse(
                        turf_name = turf.turf_name,
                        description = turf.description,
                        amenities = turf.amenities,
                        booking_price = turf.booking_price,
                        game = turf.game,
                        media = turf.media,
                        addresses = turf.addresses,
                        discounts = turf.discounts,
                        distance_turf = distance
                    )
                    for turf, distance in total_turf
                ]

                total_count_query = select(func.count()).select_from(
                    select(Turf)
                    .join(address_alias, Turf.address_id == address_alias.id)
                    .where(
                        Turf.is_active == True,
                        Turf.is_verified == True,
                        Turf.game_id == game_id,
                        address_alias.city_id == customer_data.city_id,
                        ~exists(booked_turf_subquery.where(TurfBooking.turf_id == Turf.id))
                    ).subquery()
                )
                total_count = self.db.execute(total_count_query).scalar()

                load_dotenv()
                HOST = os.environ.get("HOST")
                PORT = os.environ.get("PORT")

                next_page = (f"http://{HOST}:{PORT}/api/v1/customer/get-turf-data/{game_id}/{booking_date}/{start_time}/"
                             f"{end_time}?page={page + 1}&size={size}") if (page * size) < total_count else None

                previous_page = (f"http://{HOST}:{PORT}/api/v1/customer/get-turf-data/{game_id}/{booking_date}/"
                                 f"{start_time}/{end_time}?page={page - 1}&size={size}") if page > 1 else None

                return_data = AvailableTurf(
                    turf_data = turfs,
                    next_page = next_page,
                    previous_page = previous_page
                )

                return return_data

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    def validate_booking_data(self, turf_id, reservation_date, end_time, start_time, user_id = None):
        """ This method validates the bookings data of turf."""
        conflicting_bookings_query = select(TurfBooking).where(
            and_(
                TurfBooking.turf_id == turf_id,
                TurfBooking.reservation_date == reservation_date,
                TurfBooking.start_time < end_time,
                TurfBooking.end_time > start_time
            )
        )
        conflict_exists = self.db.execute(conflicting_bookings_query).first()

        if conflict_exists:
            if conflict_exists[0].customer_id == user_id:
                return True
            raise HTTPException(status_code = 400, detail = TURF_SLOT_ALREADY_BOOKED)


    async def book_turf(self, booking_data, current_user):
        """ This method book the turf."""
        try:
            turf_data = is_valid_turf(self.db, booking_data.turf_id)

            if validate_reservation(booking_data.reservation_date, booking_data.start_time, booking_data.end_time):

                self.validate_booking_data(
                                           booking_data.turf_id,
                                           booking_data.reservation_date,
                                           booking_data.end_time,
                                           booking_data.start_time
                                           )

                discount =  (
                              self.db.query(Discount).
                             filter(and_(Discount.turf_id == booking_data.turf_id, Discount.is_active == True)).
                             first()
                )

                discount_amount = discount.discount_amount if discount else 0
                duration = booking_data.end_time - booking_data.start_time
                duration_in_s = duration.total_seconds()
                total_hour =  divmod(duration_in_s, 3600)[0]

                total_amount = total_hour * turf_data.booking_price - discount_amount

                turf_booking_data = TurfBooking(
                    reservation_date = booking_data.reservation_date.date(),
                    start_time = booking_data.start_time,
                    end_time = booking_data.end_time,
                    total_amount = total_amount,
                    payment_status = PAYMENT_STATUS_UNPAID,
                    booking_status = STATUS_RESERVED,
                    turf_id = booking_data.turf_id,
                    customer_id = current_user.user_id
                )
                turf_booking_data.created_by = current_user.user_id
                self.db.add(turf_booking_data)
                self.db.commit()
                self.db.refresh(turf_booking_data)

                return JSONResponse({
                    ID: str(turf_booking_data.id),
                    DETAILS: TURF_BOOKED
                })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail = ERROR_MESSAGE.format(str(e)))

    async def update_turf_booking(self, update_booking_data, current_user):
        """ This method update the turf booking data."""
        try:
            if validate_reservation(update_booking_data.reservation_date,
                                    update_booking_data.start_time, update_booking_data.end_time):

                turf_booking_data = is_turf_booking(self.db, update_booking_data.booking_id, current_user)

                self.validate_booking_data(
                    turf_booking_data.turf_id,
                    update_booking_data.reservation_date,
                    update_booking_data.end_time,
                    update_booking_data.start_time,
                    current_user.user_id
                )

                if turf_booking_data.reservation_date.date() < datetime.now().date():
                    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail= BOOKING_ACTION_NOT_ALLOWED)

                if datetime.now() > (turf_booking_data.start_time - timedelta(hours=1)):
                    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = UPDATE_BEFORE_ONE_HOUR)

                discount = self.db.query(Discount).filter(
                    and_(Discount.turf_id == turf_booking_data.turf_id, Discount.is_active == True)).first()

                discount_amount = discount.discount_amount if discount else 0
                duration = update_booking_data.end_time - update_booking_data.start_time
                duration_in_s = duration.total_seconds()
                total_hour = divmod(duration_in_s, 3600)[0]

                turf_data = is_valid_turf(self.db, turf_booking_data.turf_id)
                total_amount = total_hour * turf_data.booking_price - discount_amount

                turf_booking_data.reservation_date = update_booking_data.reservation_date.date()
                turf_booking_data.start_time = update_booking_data.start_time
                turf_booking_data.end_time = update_booking_data.end_time
                turf_booking_data.updated_by = current_user.user_id
                turf_booking_data.updated_at = datetime.now()
                turf_booking_data.total_amount = total_amount

                self.db.commit()
                self.db.refresh(turf_booking_data)

                return JSONResponse({
                    DETAILS: TURF_UPDATE_SUCCESS
                })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail = ERROR_MESSAGE.format(str(e)))

    async def show_turf_booking_history(self, current_user, page, size):
        """ This method shows the turf booking history of customer."""
        try:
            turf_booking_data = (self.db.query(TurfBooking).
                                 filter(TurfBooking.customer_id == current_user.user_id)
                                 .order_by(TurfBooking.created_at.desc())
                                 .offset((page - 1) * size).limit(size)
                                 .all()
                                 )

            if not turf_booking_data:
                raise HTTPException(status_code = 404, detail = NO_BOOKING_FOUND)

            load_dotenv()
            HOST = os.environ.get("HOST")
            PORT = os.environ.get("PORT")

            total_turf_booking = (self.db.query(TurfBooking).
                                  filter(TurfBooking.customer_id == current_user.user_id).all())

            next_page = f"http://{HOST}:{PORT}/api/v1/customer/show-turf-booking?page={page + 1}&size={size}"\
                if (page * size) < len(total_turf_booking) else None

            previous_page = f"http://{HOST}:{PORT}/api/v1/customer/show-turf-booking?page={page - 1}&size={size}"\
                if page > 1 else None

            return {
                BOOKINGS : turf_booking_data,
                NEXT_PAGE : next_page,
                PREV_PAGE : previous_page
            }

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code = 500, detail = ERROR_MESSAGE.format(str(e)))

    async def extend_turf_booking(self, extend_booking_data, current_user):
        """ This method extends the turf booking."""
        try:
            turf_booking_data = is_turf_booking(self.db, extend_booking_data.booking_id, current_user)
            if validate_extend_reservation(turf_booking_data, extend_booking_data):

                if turf_booking_data.reservation_date.date() < datetime.now().date():
                    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail= BOOKING_ACTION_NOT_ALLOWED)

                conflicting_bookings_query = select(TurfBooking).where(
                    and_(
                        TurfBooking.turf_id == turf_booking_data.turf_id,
                        TurfBooking.reservation_date == extend_booking_data.reservation_date,
                        TurfBooking.start_time < extend_booking_data.end_time,
                    )
                )
                conflict_exists = self.db.execute(conflicting_bookings_query).first()

                if conflict_exists and conflict_exists[0].customer_id != current_user.user_id:
                    raise HTTPException(status_code=400, detail=TURF_SLOT_ALREADY_BOOKED)

                discount = self.db.query(Discount).filter(
                    and_(Discount.turf_id == turf_booking_data.turf_id, Discount.is_active == True)).first()

                discount_amount = discount.discount_amount if discount else 0
                duration = extend_booking_data.end_time - turf_booking_data.start_time
                duration_in_s = duration.total_seconds()
                total_hour = divmod(duration_in_s, 3600)[0]
                turf_data = is_valid_turf(self.db, turf_booking_data.turf_id)
                total_amount = total_hour * turf_data.booking_price - discount_amount

                turf_booking_data.end_time = extend_booking_data.end_time
                turf_booking_data.updated_by = current_user.user_id
                turf_booking_data.updated_at = datetime.now()
                turf_booking_data.total_amount = total_amount

                self.db.commit()
                self.db.refresh(turf_booking_data)

                return JSONResponse({
                    DETAILS: TURF_UPDATE_SUCCESS
                })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def cancel_booking(self, booking_data, current_user):
        """ This method cancel the booking of turf."""
        try:
            turf_booking_data = is_turf_booking(self.db, booking_data.id, current_user)
            if turf_booking_data.reservation_date.date() < datetime.now().date():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = BOOKING_ACTION_NOT_ALLOWED)

            if turf_booking_data.start_time < datetime.now() + timedelta(hours = 5):
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = NOT_ALLOWED_TO_CANCEL)

            turf_booking_data.booking_status = STATUS_CANCELLED
            turf_booking_data.cancelled_by = current_user.user_id
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


    async def add_feedback_turf(self, feedback_data, current_user):
        """ This method add feedback for turf bookings."""
        try:
            turf_booking_data = is_turf_booking(self.db, feedback_data.turf_booking_id, current_user)

            if turf_booking_data.booking_status != STATUS_CONFIRM:
                raise HTTPException(status_code=400, detail=FEEDBACK_NOT_ALLOWED)

            if is_valid_string(feedback_data.feedback) and feedback_data.rating > 0:
                feedback_data = Feedback(
                    turf_booking_id= turf_booking_data.id,
                    feedback = feedback_data.feedback,
                    rating =  feedback_data.rating,
                    customer_id = current_user.user_id
                )
                self.db.add(feedback_data)
                self.db.commit()
                self.db.refresh(feedback_data)

                return JSONResponse({
                    ID: str(feedback_data.id),
                    DETAILS: FEEDBACK_ADDED
                })
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=INVALID_FEEDBACK_INPUT)

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))


