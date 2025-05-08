import re
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, and_
from starlette import status

from core.constant import INVALID_EMAIL, INVALID_PASSWORD, INVALID_NAME, USER_ALREADY_EXISTS, INVALID_CONTACT, \
    INVALID_ROLE_ID, INVALID_CITY_ID, INVALID_GAME_ID, INVALID_TURF_OWNER_ID, INVALID_STRING_INPUT, INVALID_AMOUNT, \
    INVALID_FILE_TYPE, MINIMUM_MEDIA, INVALID_ADDRESS_ID, TURF_NAME_ALREADY_EXISTS, INVALID_USER, USER_NOT_FOUND, \
    INVALID_TURF_ID, INACTIVE_TURF, INVALID_DATE_TIME_FORMAT, INVALID_DATE, PAST_TIME_ERROR, \
    INVALID_END_TIME, INVALID_BOOKING_TIME, MAXIMUM_ADVANCE_DAYS_ERROR, INVALID_END_TIME_OVERNIGHT, INVALID_SLOT_TIME, \
    END_TIME_UPDATE_NOT_ALLOWED, BOOKING_NOT_FOUND, STATUS_CANCELLED, UPDATE_NOT_ALLOWED, NOT_ALLOWED_TO_UPDATE, \
    INVALID_ADDRESS_SELECTION, INVALID_START_TIME
from models.address_model import Address
from models.city_model import City
from models.game_model import Game
from models.roles_model import Roles
from models.turf_booking import TurfBooking
from models.turf_model import Turf
from models.user_model import User
from datetime import datetime, timedelta


def is_valid_string(string, min_length=1, max_length=255
):
    """ This function validate Name."""
    pattern = r'^[a-zA-Z\s]+$'
    if not re.match(pattern, string):
        return False
    elif not isinstance(string, str) or not (min_length <= len(string) <= max_length):
        return False
    return True

def validate_email(email: str, db=None, is_exception = False):
    """ This function validate email input"""
    if not re.fullmatch(r'^[\w.-]+@[\w.-]+\.\w{2,4}$', email):
        return False
    else:
        if is_exception:
            user_data = db.query(User).filter(User.email == email).first()
            if user_data:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=USER_ALREADY_EXISTS.format(email))
    return True

def validate_password(password: str):
    """ This function validate password."""
    if not re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        return False
    return True

def validate_contact_no(contact_no: int):
    """ This function validate contact number."""
    pattern = r'^[6-9]\d{9}$'
    if not re.fullmatch(pattern, str(contact_no)):
        return False
    return True

def validate_role_id(role_id: UUID, db):
    """ This function validate role id."""
    is_role =  db.query(Roles).filter(Roles.id == role_id).first()
    if not is_role:
        return False
    return True

def validate_city_id(city_id: int, db):
    """ This function validate city id."""
    is_city = db.query(City).filter(City.id == city_id).first()
    if not is_city:
        return False
    return True

def validate_input(values, db):
    """ This function validate input data."""
    print("Sign Up Payload", values)
    if not is_valid_string(values.name):
        raise HTTPException(status_code=400, detail = INVALID_NAME)

    if not validate_email(values.email, db, is_exception=True):
        raise HTTPException(status_code=400, detail = INVALID_EMAIL)

    if not validate_contact_no(values.contact_no):
        raise HTTPException(status_code=400, detail=INVALID_CONTACT)

    if not validate_password(values.password):
        raise HTTPException(status_code=400, detail = INVALID_PASSWORD)

    if not validate_role_id(values.role_id, db):
        raise HTTPException(status_code=404, detail = INVALID_ROLE_ID)

    if not validate_city_id(values.city_id, db):
        raise HTTPException(status_code=404, detail = INVALID_CITY_ID)

    return True

def validate_login_input(email: str, password: str):
    """ This function validate login input data."""
    if not validate_email(email):
        raise HTTPException(status_code=400, detail=INVALID_EMAIL)
    if not validate_password(password):
        raise HTTPException(status_code=400, detail=INVALID_PASSWORD)
    return True

def is_valid_game(db,game_id):
    """ This method check if game_id is valid."""
    game_data = db.query(Game).filter(Game.id == game_id).first()

    if not game_data:
        return False
    return game_data

def is_valid_user(db, user_id, is_exception = True):
    """ This function check for turf owner id is valid or not. """
    user_data = db.query(User).filter(User.id == user_id).first()

    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)

    if is_exception and  not user_data.is_active or not user_data.is_verified:
            raise  HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = INVALID_USER)

    return user_data


def is_valid_string_input(string):
    """ This function validate string input for not having any special characters."""
    regex = re.compile(r'[^a-zA-Z0-9\s\/\-,\.]')

    if regex.search(string):
        return False

    return True

def is_valid_amount(amount):
    """ This function validate amount."""
    if amount <= 0:
        return False
    return True

def is_valid_media(medias):
    """ This function validate media type and count of media. """
    valid_image_types = {"image/jpeg", "image/png", "image/jpg"}
    valid_video_types = {"video/mp4", "video/mkv"}

    image_count = 0
    video_count = 0

    for media in medias:
        if media.content_type in valid_image_types:
            image_count += 1
        elif media.content_type in valid_video_types:
            video_count += 1
        else:
            raise HTTPException(status_code=400, detail = INVALID_FILE_TYPE)

    if image_count < 5 and video_count < 1:
            raise HTTPException(status_code=400, detail = MINIMUM_MEDIA)

    return True

def is_valid_address_id(db, address_id, turf_owner_id):
    """ This function check if address_id is valid."""
    address_data = db.query(Address).filter(Address.id == address_id).first()

    if not address_data:
        return False

    if address_data.turf_owner_id != turf_owner_id:
        raise HTTPException(status_code=401, detail = INVALID_ADDRESS_SELECTION)

    return True

def is_turf_name_exist(db, address_id, turf_name):
    """ This function check if turf name exist on same address. """
    is_exist = db.query(Turf).filter(
        and_(
            func.lower(Turf.turf_name) == func.lower(turf_name),
            Turf.address_id == address_id
        )
    ).first()

    if is_exist:
        return True

    return False

def validate_turf_data(db, request_data, turf_owner_id):
    """ This function validate turf data."""

    if not is_valid_game(db, request_data.game_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=INVALID_GAME_ID)

    if not is_valid_string_input(request_data.turf_name):
        raise HTTPException(status_code=400, detail=INVALID_STRING_INPUT)
    else:
        if is_turf_name_exist(db, request_data.address_id, request_data.turf_name):
            raise HTTPException(status_code=400, detail = TURF_NAME_ALREADY_EXISTS)

    if not is_valid_string_input(request_data.description):
        raise HTTPException(status_code=400, detail=INVALID_STRING_INPUT)

    if not [is_valid_string_input(i) for i in request_data.amenities]:
        raise HTTPException(status_code=400, detail=INVALID_STRING_INPUT)

    if not is_valid_amount(request_data.booking_price):
        raise HTTPException(status_code=400, detail=INVALID_AMOUNT)

    if not is_valid_media(request_data.media):
        return False

    if not is_valid_amount(request_data.amount):
        raise HTTPException(status_code=400, detail=INVALID_AMOUNT)

    if not is_valid_address_id(db,request_data.address_id, turf_owner_id):
        raise HTTPException(status_code=404, detail=INVALID_ADDRESS_ID)

    return True


def validate_address_data(db, request_data):
    """ This function validate address data."""

    if not is_valid_string_input(request_data.street_address):
        raise HTTPException(status_code=400, detail=INVALID_STRING_INPUT)

    if not is_valid_string_input(request_data.area):
        raise HTTPException(status_code=400, detail=INVALID_STRING_INPUT)

    if not validate_city_id(request_data.city_id, db):
        raise HTTPException(status_code=404, detail=INVALID_CITY_ID)

    return True

def verify_turf_name(db, address_id, turf_name):
    """ This function verify the turf name."""

    if not is_valid_string_input(turf_name):
        raise HTTPException(status_code=400, detail=INVALID_STRING_INPUT)
    else:
        if is_turf_name_exist(db, address_id, turf_name):
            raise HTTPException(status_code=400, detail=TURF_NAME_ALREADY_EXISTS)

    return True

def verify_turf_description(description):
    """ This function verify the turf description."""

    if not is_valid_string_input(description):
        raise HTTPException(status_code=400, detail=INVALID_STRING_INPUT)
    return True

def validate_turf_amenities(amenities):
    """ This function validate turf amenities."""

    if not [is_valid_string_input(i) for i in amenities]:
        raise HTTPException(status_code=400, detail=INVALID_STRING_INPUT)
    return True

def verify_turf_booking_price(booking_price):
    """ This function verify the turf booking price."""

    if not is_valid_amount(booking_price):
        raise HTTPException(status_code=400, detail=INVALID_AMOUNT)
    return True

def is_turf(db, turf_id):
    """ This function check whether the turf exist or not. if exist then return turf data."""
    turf_data = db.query(Turf).filter(Turf.id ==  turf_id).first()

    if not turf_data:
        return False
    return turf_data

def is_valid_turf(db, turf_id):
    """ This function check for the turf id is valid or not. """
    turf_data = db.query(Turf).filter(Turf.id == turf_id).first()

    if not turf_data:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = INVALID_TURF_ID)
    else:
        if not turf_data.is_active or not turf_data.is_verified:
            raise HTTPException(status_code = status.HTTP_405_METHOD_NOT_ALLOWED,
                                detail = INACTIVE_TURF)
    return turf_data


def validate_reservation(reservation_date, start_time, end_time):
    """
    Validates the reservation data for a turf booking.
    """

    current_datetime = datetime.now()
    current_date = current_datetime.date()

    # Convert reservation_date to a date if it's a datetime
    if isinstance(reservation_date, datetime):
        reservation_date = reservation_date.date()

    # Convert end_time to a date for overnight booking check
    if isinstance(end_time, datetime):
        end_date = end_time.date()
    else:
        end_date = end_time

    # Check if reservation date is in the past
    if reservation_date < current_date:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = INVALID_DATE
        )

    # Check maximum advance booking days (30 days)
    if (reservation_date - current_date).days > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=MAXIMUM_ADVANCE_DAYS_ERROR
        )

    # If booking is for today, ensure the start time is not in the past
    if reservation_date == current_date and start_time < current_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PAST_TIME_ERROR
        )
    else:
        if start_time < current_datetime or start_time.date() != reservation_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID_START_TIME
            )


    # Validate that both start_time and end_time fall on valid slots (full hour or half-hour)
    if start_time.minute not in [0, 30] or end_time.minute not in [0, 30]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_SLOT_TIME
        )

    # If the end time is on a different date than the reservation date,
    # it must be exactly the next day (overnight booking rule).
    if end_date != reservation_date and end_date != (reservation_date + timedelta(days=1)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID_END_TIME_OVERNIGHT
            )

    # Check if the entire booking (end_time) is not in the past
    if end_time < current_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PAST_TIME_ERROR
        )

    # Ensure that the end time is after the start time
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_END_TIME
        )

    # Enforce a minimum booking duration of 1 hour
    if end_time < start_time + timedelta(hours=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_BOOKING_TIME
        )

    return True

def validate_extend_reservation(turf_booking_data, extend_booking_data):
    """ This function validates the update booking data. """
    current_datetime = datetime.now()

    if extend_booking_data.reservation_date < current_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_DATE
        )

    if extend_booking_data.end_time < turf_booking_data.end_time:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = END_TIME_UPDATE_NOT_ALLOWED
        )

    if extend_booking_data.end_time.date() != turf_booking_data.reservation_date.date():
        if extend_booking_data.end_time.date() != (turf_booking_data.reservation_date.date() + timedelta(days=1)):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = INVALID_END_TIME_OVERNIGHT
            )

    if extend_booking_data.end_time < current_datetime:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = PAST_TIME_ERROR
        )

    return True

def is_turf_booking(db,booking_id, current_user):
    """ This function validates the turf booking by turf booking id."""
    turf_booking_data = (
        db.query(TurfBooking)
        .filter(TurfBooking.id == booking_id).
        first())

    if not turf_booking_data:
        raise HTTPException(status_code = 404, detail = BOOKING_NOT_FOUND)

    if current_user.user_id != turf_booking_data.customer_id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = NOT_ALLOWED_TO_UPDATE)

    if turf_booking_data.booking_status == STATUS_CANCELLED:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = UPDATE_NOT_ALLOWED)

    return turf_booking_data


