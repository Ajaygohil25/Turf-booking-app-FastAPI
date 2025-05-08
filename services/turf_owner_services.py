import os
import shutil
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException
from geoalchemy2.shape import from_shape
from shapely.geometry.point import Point
from sqlalchemy import select, and_
from starlette import status
from starlette.responses import JSONResponse

from authentication.hashing import Hash
from core.constant import (NOT_ALLOWED, ERROR_MESSAGE, DETAILS, TURF_ADDRESS_ADDED, TURF_ADDED_SUCCESS,
                           NO_DATA_TO_UPDATE, TURF_DATA_UPDATED, TURF_DEACTIVATED, OWNER_ROLE,
                           TURF_DISCOUNT_ADDED, INVALID_DISCOUNT_ID, DISCOUNT_EXPIRED, INVALID_DISCOUNT_AMOUNT,
                           TURF_DISCOUNT_DEACTIVATED, TURF_MANAGER_ADDED, MANAGER_ACTIVATION_UPDATED, USER_NOT_FOUND,
                           ID, MANAGER_ROLE, INVALID_USER_ACTION, MANAGER_ACTION_NOT_ALLOWED, NO_DATA_FOUND, BOOKINGS,
                           NEXT_PAGE, PREV_PAGE, INVALID_END_TIME)
from core.validations import validate_turf_data, validate_address_data, verify_turf_name, verify_turf_description, \
    validate_turf_amenities, verify_turf_booking_price, is_valid_user, is_valid_turf, validate_input
from models.address_model import Address
from models.admin_revenue_model import AdminRevenue
from models.discount_model import Discount
from models.feedback_model import Feedback
from models.manage_turf_manager_model import ManageTurfManager
from models.media_model import Media
from models.roles_model import Roles
from models.turf_booking import TurfBooking
from models.turf_model import Turf
from models.user_model import User
from schemas.turf_owner_schema import FeedbackResponseSchema


class TurfOwnerService:
    def __init__(self, db):
        self.db = db
        self.upload_dir = Path("media")

    def upload_images(self, media, turf_id, user_id):
        """ This method upload images to the database."""
        media_url = self.upload_dir / media
        media_url_str = "/" + str(media_url).replace("\\", "/")
        print("media_url", media_url)
        media_data = Media(
            turf_id=turf_id,
            media_url=media_url_str
        )
        media_data.created_by = user_id
        media_data.created_at = datetime.now()
        self.db.add(media_data)
        self.db.commit()
        self.db.refresh(media_data)

    async def add_turf_address(self, request_data, current_user):
        """ This method adds a turf address to the database."""
        try:
            is_valid_user(self.db, current_user.user_id)

            if validate_address_data(self.db, request_data):
                turf_address = Address(
                    street_address=request_data.street_address,
                    area=request_data.area,
                    city_id=request_data.city_id,
                    is_active=True,
                    turf_owner_id=current_user.user_id,
                    lat=request_data.lat,
                    long=request_data.long,
                    geom=from_shape(Point(request_data.long, request_data.lat), srid=4326)
                )
                turf_address.created_by = current_user.user_id
                turf_address.created_at = datetime.now()
                self.db.add(turf_address)
                self.db.commit()
                self.db.refresh(turf_address)

                return JSONResponse({
                    ID: str(turf_address.id),
                    DETAILS: TURF_ADDRESS_ADDED
                })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def add_turfs(self, request_data, login_user):
        """ This method adds a turf to the database."""
        try:
            is_valid_user(self.db, login_user.user_id)

            if validate_turf_data(self.db, request_data, login_user.user_id):

                turf_data = Turf(
                    turf_name=request_data.turf_name,
                    description=request_data.description,
                    amenities=request_data.amenities,
                    booking_price=request_data.booking_price,
                    is_active=False,
                    is_verified=False,
                    turf_owner_id=login_user.user_id,
                    game_id=request_data.game_id,
                    address_id=request_data.address_id
                )
                turf_data.created_by = login_user.user_id
                turf_data.created_at = datetime.now()

                self.db.add(turf_data)
                self.db.flush()

                turf_id = turf_data.id

                # saving the file in folder
                media_paths = []
                for media in request_data.media:
                    filepath = self.upload_dir / media.filename
                    with open(filepath, "wb") as image_file:
                        shutil.copyfileobj(media.file, image_file)
                    media_paths.append(media.filename)

                # Adding the Admin revenue in database.
                admin_revenue_data = AdminRevenue(
                    turf_id=turf_id,
                    revenue_mode=request_data.revenue_mode,
                    amount=request_data.amount
                )

                self.db.add(admin_revenue_data)
                self.db.commit()

                # Adding media into database.
                for filename in media_paths:
                    self.upload_images(filename, turf_id, login_user.user_id)

                return JSONResponse({
                    ID: str(turf_id),
                    DETAILS: TURF_ADDED_SUCCESS
                })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    def valid_owner_request(self, turf_data, current_user):
        """ This method validates the ownership of turf owner."""
        if turf_data.turf_owner_id != current_user.user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_ALLOWED)

    async def update_turf_details(self, turf_id, update_turf_data, current_user):
        """ This method update turf details based on turf_id."""
        try:
            turf_data = is_valid_turf(self.db, turf_id)
            is_valid_user(self.db, current_user.user_id)
            self.valid_owner_request(turf_data, current_user)

            if update_turf_data:

                if update_turf_data.turf_name:
                    if verify_turf_name(self.db, turf_data.address_id, update_turf_data.turf_name):
                        turf_data.turf_name = update_turf_data.turf_name

                if update_turf_data.description:
                    if verify_turf_description(update_turf_data.description):
                        turf_data.description = update_turf_data.description

                if update_turf_data.amenities:
                    if validate_turf_amenities(update_turf_data.amenities):
                        turf_data.amenities.append(update_turf_data.amenities)

                if update_turf_data.booking_price:
                    if verify_turf_booking_price(update_turf_data.booking_price):
                        turf_data.booking_price = update_turf_data.booking_price

                turf_data.updated_by = current_user.user_id
                turf_data.updated_at = datetime.now()

                self.db.commit()
                self.db.refresh(turf_data)

                return JSONResponse({
                    DETAILS: TURF_DATA_UPDATED
                })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def show_turf_details(self, turf_id, current_user):
        """ This method show turf details based on turf_id."""
        try:
            turf_data = is_valid_turf(self.db, turf_id)
            is_valid_user(self.db, current_user.user_id)
            self.valid_owner_request(turf_data, current_user)

            return turf_data

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def deactivate_turf(self, data, current_user):
        """ This method deactivates the turf if valid turf owner."""
        try:
            turf_data = is_valid_turf(self.db, data.id)
            is_valid_user(self.db, current_user.user_id)
            self.valid_owner_request(turf_data, current_user)

            turf_data.is_active = False
            turf_data.updated_by = current_user.user_id
            turf_data.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(turf_data)

            return JSONResponse({
                DETAILS: TURF_DEACTIVATED
            })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def add_turf_discount(self, request_data, current_user):
        """ This method adds a turf discount."""
        try:
            turf_data = is_valid_turf(self.db, request_data.turf_id)
            is_valid_user(self.db, current_user.user_id)
            self.valid_owner_request(turf_data, current_user)

            if request_data.discount_amount < 0 or request_data.discount_amount < 100:
                raise HTTPException(status_code=400, detail=INVALID_DISCOUNT_AMOUNT)

            discount_data = Discount(
                turf_id=request_data.turf_id,
                discount_amount=request_data.discount_amount,
                is_active=True
            )

            self.db.add(discount_data)
            self.db.commit()
            self.db.refresh(discount_data)

            return JSONResponse({
                ID: str(discount_data.id),
                DETAILS: TURF_DISCOUNT_ADDED
            })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def deactivate_turf_discount(self, request_data, current_user):
        """ This method deactivates the turf discount."""
        try:
            discount_data = self.db.query(Discount).filter(Discount.id == request_data.id).first()
            is_valid_user(self.db, current_user.user_id)
            if not discount_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=INVALID_DISCOUNT_ID)
            else:
                if not discount_data.is_active:
                    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                        detail=DISCOUNT_EXPIRED)

            turf_data = is_valid_turf(self.db, discount_data.turf_id)
            self.valid_owner_request(turf_data, current_user)
            discount_data.is_active = False
            discount_data.updated_by = current_user.user_id
            discount_data.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(discount_data)

            return JSONResponse({
                DETAILS: TURF_DISCOUNT_DEACTIVATED
            })

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def add_turf_manager(self, request_data, current_user):
        """ This method register turf manager for the specified turf."""
        try:
            turf_data = is_valid_turf(self.db, request_data.turf_id)
            self.valid_owner_request(turf_data, current_user)

            if validate_input(request_data, self.db):
                encrypted_password = Hash.encrypt(request_data.password)
                user_data = User(
                    name=request_data.name,
                    contact_no=request_data.contact_no,
                    email=request_data.email,
                    password=encrypted_password,
                    role_id=request_data.role_id,
                    city_id=request_data.city_id,
                    is_active=request_data.is_active,
                    is_verified=request_data.is_verified,
                    lat=request_data.lat,
                    long=request_data.long,
                    geom=from_shape(Point(request_data.long, request_data.lat), srid=4326)
                )
                self.db.add(user_data)
                self.db.commit()
                self.db.refresh(user_data)

                turf_manager_data = ManageTurfManager(
                    turf_id=request_data.turf_id,
                    turf_manager_id=user_data.id,
                    is_active=True
                )

                turf_manager_data.created_by = current_user.user_id
                self.db.add(turf_manager_data)
                self.db.commit()
                self.db.refresh(turf_manager_data)

                return JSONResponse(
                    {
                        DETAILS: TURF_MANAGER_ADDED,
                    })
        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def activate_deactivate_manager(self, request_data, current_user, is_active=False):
        """ This method deactivates the turf manager."""
        try:
            turf_manager_data = is_valid_user(self.db, request_data.id, is_exception=False)

            user_role = self.db.query(Roles).filter(Roles.id == turf_manager_data.role_id).first()
            if user_role.role_name != MANAGER_ROLE:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_USER_ACTION)

            valid_turf_details = self.db.query(Turf).join(ManageTurfManager,
                                                          ManageTurfManager.turf_id == Turf.id).first()

            if valid_turf_details.turf_owner_id != current_user.user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MANAGER_ACTION_NOT_ALLOWED)

            # If is_active is true then activate turf manager otherwise deactivate it.
            if is_active:
                turf_manager_data.is_active = True
            else:
                turf_manager_data.is_active = False

            turf_manager_data.updated_by = current_user.user_id
            turf_manager_data.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(turf_manager_data)

            return JSONResponse(
                {
                    DETAILS: MANAGER_ACTIVATION_UPDATED,
                }
            )

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def get_turf_feedbacks(self, turf_id, current_user):
        """ This method get all the feedback of turf"""
        try:
            turf_data = is_valid_turf(self.db, turf_id)
            self.valid_owner_request(turf_data, current_user)

            feedbacks = (
                self.db.query(Feedback)
                .join(TurfBooking)
                .filter(TurfBooking.turf_id == turf_id)
                .order_by(Feedback.created_at)
                .all()
            )

            return feedbacks

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def get_addresses(self, current_user):
        """ This method get all the addresses added by the turf owner."""
        try:
            addresses = self.db.query(Address).filter(Address.turf_owner_id == current_user.user_id).all()

            return addresses

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def get_turfs(self, current_user):
        try:
            turfs = self.db.query(Turf).filter(Turf.turf_owner_id == current_user.user_id).all()
            return turfs

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))

    async def get_bookings(self,turf_id, current_user, start_date, end_date, page, size):
        try:
            turf_data = is_valid_turf(self.db, turf_id)
            is_valid_user(self.db, current_user.user_id)
            self.valid_owner_request(turf_data, current_user)

            if start_date > end_date:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_END_TIME)

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
                f"http://{HOST}:{PORT}/api/v1/turf-owner/get-bookings/"
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

        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=ERROR_MESSAGE.format(str(e)))