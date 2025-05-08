import os
import uuid
from datetime import date, datetime
from unittest.mock import patch
from uuid import UUID

import jwt
import pytest
from dotenv import load_dotenv
from geoalchemy2.functions import ST_DistanceSphere
from sqlalchemy import select, exists
from sqlalchemy.orm import aliased

from core.constant import INVALID_GAME_ID, INVALID_START_TIME, INVALID_END_TIME_OVERNIGHT, \
    INVALID_DATE, MAXIMUM_ADVANCE_DAYS_ERROR, TURF_BOOKED, INVALID_TURF_ID, INVALID_SLOT_TIME, INVALID_END_TIME, \
    INVALID_BOOKING_TIME, TURF_SLOT_ALREADY_BOOKED, TURF_UPDATE_SUCCESS, NOT_ALLOWED_TO_UPDATE, BOOKING_NOT_FOUND, \
    BOOKING_ACTION_NOT_ALLOWED, UPDATE_NOT_ALLOWED, UPDATE_BEFORE_ONE_HOUR, NO_BOOKING_FOUND, \
    END_TIME_UPDATE_NOT_ALLOWED, BOOKING_CANCELLED, NOT_ALLOWED_TO_CANCEL, FEEDBACK_ADDED, INVALID_FEEDBACK_INPUT, \
    NOT_ALLOWED, FEEDBACK_NOT_ALLOWED
from core.database import TestSessionLocal
from models.address_model import Address
from models.feedback_model import Feedback
from models.turf_booking import TurfBooking
from models.turf_model import Turf
from models.user_model import User
from schemas.customer_schemas import BookingSchema
from services.customer_service import CustomerService
from test.api.conftest import header
from test.test_data.customer_json_data import valid_turf_booking_payload, turf_booking_payload_invalid_turf_id, \
    turf_booking_payload_with_past_reservation_date, turf_booking_payload_with_date_more_than_30_days, \
    turf_booking_payload_with_start_time_not_in_format, turf_booking_payload_with_past_start_time, \
    turf_booking_payload_with_next_day_start_time, \
    turf_booking_payload_with_wrong_end_time, turf_booking_payload_with_invalid_end_time_format, \
    turf_booking_payload_with_invalid_end_time, turf_booking_payload_with_less_than_hour_slot, \
    turf_booking_payload_with_already_booked_slot, update_booking_valid_payload, update_booking_within_hour, \
    extend_booking_valid_payload, extend_booking_past_booking_date_payload, extend_booking_lesser_end_time_than_actual, \
    extend_booking_invalid_end_time_date, extend_booking_with_conflict, feedback_valid_payload, \
    feedback_invalid_payload, feedback_invalid_rating


def test_show_turf_data(test_db, client, customer_token, header):
    """Test show turf data API by validating each turf with actual database data."""

    header["Authorization"] = f"Bearer {customer_token}"

    # Define test parameters
    game_id = "83bfc6b8-d100-4885-b13e-d619f76d18a9"
    booking_date = "2025-04-25"
    start_time = "2025-04-25 16:00:00"
    end_time = "2025-04-25 20:00:00"
    page = 1
    size = 3

    response = client.get(
        f"/api/v1/customer/get-turf-data/{game_id}"
        f"/{booking_date}/{start_time}/{end_time}"
        f"?page={page}&size={size}",
        headers=header,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    load_dotenv()
    SECRET_KEY = os.getenv("HASH_KEY")
    ALGORITHM = os.getenv("HASH_ALGO")

    token_payload = jwt.decode(customer_token, SECRET_KEY, algorithms=[ALGORITHM])

    with TestSessionLocal() as db_session:
        customer_data = db_session.query(User).filter(User.id == token_payload.get("user_id")).first()
        assert customer_data is not None, "Customer should exist in the database"

        customer_geom = customer_data.geom

        # Fetch expected turf data from the database
        booked_turf_subquery = (
            select(TurfBooking.turf_id)
            .where(
                TurfBooking.reservation_date == date.fromisoformat(booking_date),
                TurfBooking.start_time < datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'),
                TurfBooking.end_time > datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'),
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
                Turf.game_id == UUID(game_id),
                address_alias.city_id == customer_data.city_id,
                ~exists(booked_turf_subquery.where(TurfBooking.turf_id == Turf.id)),
            )
            .order_by("distance_km")
            .offset((page - 1) * size)
            .limit(size)
        )

        result = db_session.execute(query)
        expected_turfs = result.all()

        assert len(data["turf_data"]) == len(expected_turfs)

        # Validate each turf with actual data from the database
        for returned_turf, (expected_turf, expected_distance) in zip(data["turf_data"], expected_turfs):
            assert returned_turf["turf_name"] == expected_turf.turf_name
            assert returned_turf["description"] == expected_turf.description
            assert returned_turf["amenities"] == expected_turf.amenities
            assert returned_turf["booking_price"] == expected_turf.booking_price
            assert returned_turf["game"] == expected_turf.game
            assert returned_turf["media"] == expected_turf.media
            assert returned_turf["addresses"] == expected_turf.addresses
            assert returned_turf["discounts"] == expected_turf.discounts
            assert round(returned_turf["distance_turf"], 2) == round(expected_distance, 2)


def test_show_turf_with_invalid_game_id(client, customer_token, header):
    """ Test the show turf API with invalid game id."""

    header["Authorization"] = f"Bearer {customer_token}"

    booking_date = "2025-04-25"
    start_time = "2025-04-10 16:00:00"
    end_time = "2025-04-10 20:00:00"
    page = 1
    size = 3

    response = client.get(
        f"/api/v1/customer/get-turf-data/{uuid.uuid4()}"
        f"/{booking_date}/{start_time}/{end_time}"
        f"?page={page}&size={size}",
        headers=header,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == INVALID_GAME_ID


def test_show_turf_with_past_start_time(client, customer_token, header):
    """ This function test the show turf API with past start time."""
    header["Authorization"] = f"Bearer {customer_token}"

    game_id = "83bfc6b8-d100-4885-b13e-d619f76d18a9"
    booking_date = "2025-04-25"
    start_time = "2024-04-10 16:00:00"
    end_time = "2025-04-25 20:00:00"
    page = 1
    size = 3

    response = client.get(
        f"/api/v1/customer/get-turf-data/{game_id}"
        f"/{booking_date}/{start_time}/{end_time}"
        f"?page={page}&size={size}",
        headers=header,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == INVALID_START_TIME


def test_show_turf_with_past_end_time(client, customer_token, header):
    """ This function test the show turf API with past end time."""
    header["Authorization"] = f"Bearer {customer_token}"

    game_id = "83bfc6b8-d100-4885-b13e-d619f76d18a9"
    booking_date = "2025-04-25"
    start_time = "2025-04-25 16:00:00"
    end_time = "2024-04-10 20:00:00"
    page = 1
    size = 3

    response = client.get(
        f"/api/v1/customer/get-turf-data/{game_id}"
        f"/{booking_date}/{start_time}/{end_time}"
        f"?page={page}&size={size}",
        headers=header,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == INVALID_END_TIME_OVERNIGHT


def test_show_turf_with_past_booking_date(client, customer_token, header):
    """ This function test the show turf API with past booking date."""

    header["Authorization"] = f"Bearer {customer_token}"

    game_id = "83bfc6b8-d100-4885-b13e-d619f76d18a9"
    booking_date = "2024-04-10"
    start_time = "2025-04-10 16:00:00"
    end_time = "2025-04-10 20:00:00"
    page = 1
    size = 3

    response = client.get(
        f"/api/v1/customer/get-turf-data/{game_id}"
        f"/{booking_date}/{start_time}/{end_time}"
        f"?page={page}&size={size}",
        headers=header,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == INVALID_DATE


def test_show_turf_with_booking_data_more_than_30_days(client, customer_token, header):
    """ This function test the show turf API with booking data more than 30 days."""

    header["Authorization"] = f"Bearer {customer_token}"

    game_id = "83bfc6b8-d100-4885-b13e-d619f76d18a9"
    booking_date = "2025-06-10"
    start_time = "2025-06-10 16:00:00"
    end_time = "2025-06-10 20:00:00"
    page = 1
    size = 3

    response = client.get(
        f"/api/v1/customer/get-turf-data/{game_id}"
        f"/{booking_date}/{start_time}/{end_time}"
        f"?page={page}&size={size}",
        headers=header,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == MAXIMUM_ADVANCE_DAYS_ERROR


@pytest.mark.parametrize(
    "booking_payload, expected_status, expected_details",
    [
        (valid_turf_booking_payload, 200, TURF_BOOKED),
        (turf_booking_payload_with_past_reservation_date, 400, INVALID_DATE),
        (turf_booking_payload_with_date_more_than_30_days, 400, MAXIMUM_ADVANCE_DAYS_ERROR),
        (turf_booking_payload_with_start_time_not_in_format, 400, INVALID_SLOT_TIME),
        (turf_booking_payload_with_past_start_time, 400, INVALID_START_TIME),
        (turf_booking_payload_with_next_day_start_time, 400, INVALID_START_TIME),
        (turf_booking_payload_with_wrong_end_time, 400, INVALID_END_TIME),
        (turf_booking_payload_with_invalid_end_time_format, 400, INVALID_SLOT_TIME),
        (turf_booking_payload_with_invalid_end_time, 400, INVALID_END_TIME_OVERNIGHT),
        (turf_booking_payload_with_less_than_hour_slot, 400, INVALID_BOOKING_TIME),
        (turf_booking_payload_with_already_booked_slot, 400, TURF_SLOT_ALREADY_BOOKED)
    ]
)
def test_book_turf(client, turf, booking_payload, expected_status, expected_details, header, customer_token):
    """ test the turf booking API """
    header["Authorization"] = f"Bearer {customer_token}"
    booking_payload["turf_id"] = str(turf.id)

    response = client.post(
        "/api/v1/customer/book-turf",
        headers=header,
        json=booking_payload,
    )

    assert response.status_code == expected_status
    if response.status_code == 200:
        assert response.json()["Details"] == expected_details
        booking_id = response.json()["id"]
        with TestSessionLocal() as session:
            booking = session.query(TurfBooking).filter(TurfBooking.id == booking_id).first()
            assert booking is not None
            assert booking.start_time == datetime.strptime( valid_turf_booking_payload["start_time"], '%Y-%m-%d %H:%M:%S')
            assert booking.end_time == datetime.strptime(valid_turf_booking_payload["end_time"], '%Y-%m-%d %H:%M:%S')
            assert booking.payment_status == "unpaid"
    else:
        assert response.json()["detail"] == expected_details


def test_turf_booking_with_invalid_turf_id(client, customer_token, header):
    """ This function test the turf booking API with invalid turf id """

    header["Authorization"] = f"Bearer {customer_token}"

    response = client.post(
        "/api/v1/customer/book-turf",
        headers=header,
        json=turf_booking_payload_invalid_turf_id,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == INVALID_TURF_ID


@pytest.mark.parametrize(
    "update_booking_payload, expected_status, expected_details",
    [
        (update_booking_valid_payload, 200, TURF_BOOKED),
        (update_booking_within_hour, 400, UPDATE_BEFORE_ONE_HOUR)
    ]
)
def test_update_turf_booking(client, customer_token, header, turf_booking, update_booking_payload, expected_status,
                             expected_details ):
    """ test the update turf booking API """
    header["Authorization"] = f"Bearer {customer_token}"
    update_booking_payload["booking_id"] = str(turf_booking[0].id)
    response = client.put(
        "/api/v1/customer/update-turf-booking",
        headers=header,
        json=update_booking_payload,
    )

    assert response.status_code == expected_status

    if response.status_code == 200:
        assert response.json()["Details"] == TURF_UPDATE_SUCCESS
    else:
        assert response.json()["detail"] == expected_details


def test_update_turf_booking_with_other_customer_token(client, customer_2_token, header, turf_booking):
    """ test the update turf booking API with other customer token. """
    header["Authorization"] = f"Bearer {customer_2_token}"
    update_booking_valid_payload["booking_id"] = str(turf_booking[0].id)
    response = client.put(
        "/api/v1/customer/update-turf-booking",
        headers=header,
        json=update_booking_valid_payload,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == NOT_ALLOWED_TO_UPDATE


def test_update_turf_booking_with_invalid_booking_id(client, customer_token, header, turf_booking):
    """ test the update turf API with invalid turf_id"""
    header["Authorization"] = f"Bearer {customer_token}"
    update_booking_valid_payload["booking_id"] = str(uuid.uuid4())
    response = client.put(
        "/api/v1/customer/update-turf-booking",
        headers=header,
        json=update_booking_valid_payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == BOOKING_NOT_FOUND


def test_update_turf_booking_with_past_booking_id(client, customer_token, header, turf_booking):
    """ test the update turf API with past booking id"""

    header["Authorization"] = f"Bearer {customer_token}"
    update_booking_valid_payload["booking_id"] = str(turf_booking[1].id)
    response = client.put(
        "/api/v1/customer/update-turf-booking",
        headers=header,
        json=update_booking_valid_payload,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == BOOKING_ACTION_NOT_ALLOWED


def test_update_turf_booking_with_cancelled_booking_id(client, customer_token, header, turf_booking):
    """ test the update turf API with past booking id"""

    header["Authorization"] = f"Bearer {customer_token}"
    update_booking_valid_payload["booking_id"] = str(turf_booking[2].id)
    response = client.put(
        "/api/v1/customer/update-turf-booking",
        headers=header,
        json=update_booking_valid_payload,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == UPDATE_NOT_ALLOWED


def test_show_turf_booking_history(client, customer_token, header, turf_booking):
    """ test the show turf booking history API """
    header["Authorization"] = f"Bearer {customer_token}"
    response = client.get(
        "/api/v1/customer/show-turf-booking",
        headers=header
    )
    assert response.status_code == 200

    if response.status_code == 200:
        load_dotenv()
        SECRET_KEY = os.environ.get("HASH_KEY")
        ALGORITHM = os.environ.get("HASH_ALGO")

        token_payload = jwt.decode(customer_token, SECRET_KEY, algorithms=[ALGORITHM])

        with TestSessionLocal() as db_session:
            turf_booking_data = (db_session.query(TurfBooking).
                                 filter(TurfBooking.customer_id == token_payload.get("user_id"))
                                 .order_by(TurfBooking.created_at.desc())
                                 .offset((1 - 1) * 5).limit(5)
                                 .all()
                                 )

            response_data = [
                BookingSchema.model_validate(
                    {
                        "reservation_date" : booking_obj.reservation_date,
                        "start_time": booking_obj.start_time,
                        "end_time": booking_obj.end_time,
                        "total_amount": booking_obj.total_amount,
                        "payment_status": booking_obj.payment_status,
                        "booking_status": booking_obj.booking_status,
                        "turf" : {
                            "turf_name" : booking_obj.turf.turf_name
                        } if booking_obj.turf else None,
                    }).model_dump(mode="json")
                for booking_obj in turf_booking_data
            ]

            response_turf_booking = response.json()["bookings"]

            assert len(response_data) == len(response_turf_booking)

            for resp_item, expected_item in zip(response_turf_booking, response_data):
                assert resp_item == expected_item


def test_show_turf_with_customer_not_having_booking(client, customer_2_token, header, turf_booking):
    """ test the show turf booking history API of customer not having any booking."""
    header["Authorization"] = f"Bearer {customer_2_token}"
    response = client.get(
        "/api/v1/customer/show-turf-booking",
        headers=header
    )
    assert response.status_code == 404
    assert response.json()["detail"] == NO_BOOKING_FOUND


@pytest.mark.parametrize(
    "extend_booking_payload, expected_status, expected_message",
    [
        (extend_booking_valid_payload, 200, TURF_UPDATE_SUCCESS),
        (extend_booking_past_booking_date_payload, 400, INVALID_DATE),
        (extend_booking_lesser_end_time_than_actual, 400, END_TIME_UPDATE_NOT_ALLOWED),
        (extend_booking_invalid_end_time_date, 400, END_TIME_UPDATE_NOT_ALLOWED),
        (extend_booking_with_conflict, 400, TURF_SLOT_ALREADY_BOOKED)
    ]
)
def test_extend_turf_booking(client, customer_token, header, extend_booking_payload, expected_status, expected_message,
                             turf_booking):
    """ test the extent turf booking API."""
    header["Authorization"] = f"Bearer {customer_token}"
    extend_booking_payload["booking_id"] = str(turf_booking[4].id)

    response = client.post(
        "/api/v1/customer/extend-bookings",
        headers=header,
        json=extend_booking_payload
    )
    assert response.status_code == expected_status, response.text

    if response.status_code == 200:
        assert response.json()["Details"] == TURF_UPDATE_SUCCESS
    else:
        assert response.json()["detail"] == expected_message


def test_extend_turf_booking_with_invalid_booking_id(client, customer_token, turf_booking, header):
    """ test the extend turf API with invalid booking_id"""

    header["Authorization"] = f"Bearer {customer_token}"
    extend_booking_valid_payload["booking_id"] = str(uuid.uuid4())

    response = client.post(
        "/api/v1/customer/extend-bookings",
        headers=header,
        json=extend_booking_valid_payload
    )
    assert response.status_code == 404
    assert response.json()["detail"] == BOOKING_NOT_FOUND


def test_extend_turf_booking_with_other_customer_token(client, customer_2_token, turf_booking, header ):
    """ test the extend turf booking with other customer's token."""
    header["Authorization"] = f"Bearer {customer_2_token}"
    extend_booking_valid_payload["booking_id"] = str(turf_booking[4].id)

    response = client.post(
        "/api/v1/customer/extend-bookings",
        headers=header,
        json=extend_booking_valid_payload
    )
    assert response.status_code == 403
    assert response.json()["detail"] == NOT_ALLOWED_TO_UPDATE


def test_cancel_booking(client, customer_token, header, turf_booking):
    """ This function test the cancel booking with valid booking id. """
    header["Authorization"] = f"Bearer {customer_token}"
    payload = {"id" : f"{turf_booking[4].id}"}

    response = client.post(
        "/api/v1/customer/cancel-bookings",
        headers=header,
        json=payload
    )
    assert response.status_code == 200
    assert response.json()["Details"] == BOOKING_CANCELLED

    with TestSessionLocal() as db_session:
        booking_data = db_session.query(TurfBooking).filter(TurfBooking.id == turf_booking[4].id).first()
        assert booking_data.booking_status == "cancelled"



def test_cancel_past_booking(client, customer_token, header, turf_booking):
    """ This function test the cancel booking with past booking id. """
    header["Authorization"] = f"Bearer {customer_token}"
    payload = {"id": f"{turf_booking[1].id}"}

    response = client.post(
        "/api/v1/customer/cancel-bookings",
        headers=header,
        json=payload
    )
    assert response.status_code == 400
    assert response.json()["detail"] == BOOKING_ACTION_NOT_ALLOWED



def test_cancel_within_5_hour_span(client, customer_token, header, turf_booking):
    """ This function test the cancel booking with past booking id. """
    header["Authorization"] = f"Bearer {customer_token}"
    payload = {"id": f"{turf_booking[3].id}"}

    response = client.post(
        "/api/v1/customer/cancel-bookings",
        headers=header,
        json=payload
    )
    assert response.status_code == 400
    assert response.json()["detail"] == NOT_ALLOWED_TO_CANCEL


def test_cancel_booking_with_already_cancelled_booking(client, customer_token, turf_booking, header):
    """ This function test the cancel booking with already cancelled booking id. '"""
    header["Authorization"] = f"Bearer {customer_token}"
    payload = {"id": f"{turf_booking[2].id}"}

    response = client.post(
        "/api/v1/customer/cancel-bookings",
        headers=header,
        json=payload
    )
    assert response.status_code == 400
    assert response.json()["detail"] == UPDATE_NOT_ALLOWED


def test_cancel_booking_with_invalid_turf_id(client, customer_token, turf_booking, header):
    """ This function test the cancel booking with invalid turf id. """
    header["Authorization"] = f"Bearer {customer_token}"
    payload = {"id": f"{uuid.uuid4()}"}

    response = client.post(
        "/api/v1/customer/cancel-bookings",
        headers=header,
        json=payload
    )
    assert response.status_code == 404
    assert response.json()["detail"] == BOOKING_NOT_FOUND

def test_cancel_booking_with_other_customer_token(client, customer_2_token, turf_booking, header):
    """ This function test the cancel booking with other customer's token. '"""
    header["Authorization"] = f"Bearer {customer_2_token}"

    payload = {"id": f"{turf_booking[0].id}"}

    response = client.post(
        "/api/v1/customer/cancel-bookings",
        headers=header,
        json=payload
    )
    assert response.status_code == 403
    assert response.json()["detail"] == NOT_ALLOWED_TO_UPDATE

@pytest.mark.parametrize(
    "feedback_payload, expected_status, expected_message",
    [
        (feedback_valid_payload, 200, FEEDBACK_ADDED),
        (feedback_invalid_payload, 400, INVALID_FEEDBACK_INPUT),
        (feedback_invalid_rating, 400, INVALID_FEEDBACK_INPUT)
    ]
)
def test_add_feedback(client, customer_token, turf_booking, header, feedback_payload, expected_status,
                      expected_message):
    """ This function test the add feedback endpoint. """

    header["Authorization"] = f"Bearer {customer_token}"

    feedback_payload["turf_booking_id"] = str(turf_booking[3].id)
    response = client.post(
        "/api/v1/customer/add-feedback",
        headers=header,
        json=feedback_payload
    )

    assert response.status_code == expected_status

    if expected_status == 200:
        assert response.json()["Details"] == FEEDBACK_ADDED
        feedback_id = response.json()["id"]

        with TestSessionLocal() as db_session:
            feedback_data = db_session.query(Feedback).filter(Feedback.id == feedback_id).first()
            assert str(feedback_data.turf_booking_id) == feedback_valid_payload["turf_booking_id"]
            assert feedback_data.feedback == feedback_valid_payload["feedback"]
            assert feedback_data.rating == feedback_valid_payload["rating"]

    else:
        assert response.json()["detail"] == expected_message


def test_add_feedback_with_invalid_booking_id(client, customer_token, turf_booking, header):
    """ This function test the add feedback with invalid booking id. """
    header["Authorization"] = f"Bearer {customer_token}"

    feedback_valid_payload["turf_booking_id"] = str(uuid.uuid4())
    response = client.post(
        "/api/v1/customer/add-feedback",
        headers=header,
        json=feedback_valid_payload
    )
    assert response.status_code == 404, response.text

    assert response.json()["detail"] == BOOKING_NOT_FOUND

def test_add_feedback_with_turf_owner_token(client, owner_1_token, turf_booking, header):
    """ This function test the add feedback with turf owner token. """

    header["Authorization"] = f"Bearer {owner_1_token}"

    feedback_valid_payload["turf_booking_id"] = str(turf_booking[3].id)
    response = client.post(
        "/api/v1/customer/add-feedback",
        headers=header,
        json=feedback_valid_payload
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_add_feedback_with_cancelled_booking_id(client, customer_token, turf_booking, header):
    """ This function test the add feedback with cancelled booking id. """
    header["Authorization"] = f"Bearer {customer_token}"
    feedback_valid_payload["turf_booking_id"] = str(turf_booking[1].id)

    response = client.post(
        "/api/v1/customer/add-feedback",
        headers=header,
        json=feedback_valid_payload
    )
    assert response.status_code == 400
    assert response.json()["detail"] == FEEDBACK_NOT_ALLOWED


@pytest.mark.parametrize(
    "endpoint, method, payload",
    [
        ("/api/v1/customer/update-turf-booking", "put", update_booking_valid_payload),
        ("/api/v1/customer/extend-bookings","post",extend_booking_valid_payload),
        ("/api/v1/customer/cancel-bookings","post", {"id" : "fe7c6874-1368-4a57-9094-f2c5e39435a7"}),
        ("/api/v1/customer/add-feedback","post", feedback_valid_payload),
    ]
)
def test_unexpected_exception_handling(client, customer_token, endpoint, method, payload, header):
    """ This function test the exception handling for APIs"""
    header["Authorization"] = f"Bearer {customer_token}"

    with patch("services.customer_service.is_turf_booking", side_effect=Exception("Unexpected Error")):

        if method == "put":
            response = client.put(
                endpoint,
                headers=header,
                json=payload
            )

        else:
            response = client.post(
                endpoint,
                headers=header,
                json=payload
            )

    assert response.status_code == 500
    assert "Unexpected Error" in response.text


def test_unexpected_exception_handling_show_turf(client, customer_token, header):
    header["Authorization"] = f"Bearer {customer_token}"

    with patch.object(CustomerService, "get_customer_data", side_effect=Exception("Unexpected Error")):
        # Define test parameters
        game_id = "ec5ebaf1-a96a-4961-a42b-9d51b7370c5a"
        booking_date = "2025-04-10"
        start_time = "2025-04-10 16:00:00"
        end_time = "2025-04-10 20:00:00"
        page = 1
        size = 3

        response = client.get(
            f"/api/v1/customer/get-turf-data/{game_id}"
            f"/{booking_date}/{start_time}/{end_time}"
            f"?page={page}&size={size}",
            headers=header,
        )

    assert response.status_code == 500
    assert "Unexpected Error" in response.text


def test_unexpected_exception_book_turf(client, turf, customer_token, header):

    with patch("services.customer_service.is_valid_turf", side_effect=Exception("Unexpected Error")):
        header["Authorization"] = f"Bearer {customer_token}"
        valid_turf_booking_payload["turf_id"] = str(turf.id)

        response = client.post(
            "/api/v1/customer/book-turf",
            headers=header,
            json=valid_turf_booking_payload,
        )
    assert response.status_code == 500
    assert "Unexpected Error" in response.text
