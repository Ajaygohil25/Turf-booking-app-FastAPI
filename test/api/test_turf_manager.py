import uuid
from datetime import date

from sqlalchemy import select, and_

from core.constant import NOT_ALLOWED, NO_DATA_FOUND, DETAILS, PAYMENT_SUCCESSFUL, NO_BOOKING_FOUND, \
    BOOKING_ALREADY_CANCELLED, BOOKING_CANCELLED
from core.database import TestSessionLocal
from models.turf_booking import TurfBooking
from schemas.turf_owner_schema import Booking


def test_get_bookings(turf_manager_token, header, client, turf_booking, turf):
    """ This function test get turf bookings API of the turf manager"""
    header["Authorization"] = f"Bearer {turf_manager_token}"

    response = client.get(
            "/api/v1/manager/get-turf-bookings/"
            "?start_date=2025-01-01&end_date=2025-12-31&page=1&size=5",
        headers=header
    )

    assert response.status_code == 200, response.text

    if response.status_code == 200:
        start_date = date(2025, 1, 1)
        end_date = date(2025, 12, 31)

        with TestSessionLocal() as db_session:
            query = (
                select(
                    TurfBooking
                )
                .where(
                    and_(
                        TurfBooking.turf_id == turf.id,
                        TurfBooking.reservation_date >= start_date,
                        TurfBooking.reservation_date <= end_date
                    )
                )
                .order_by(TurfBooking.created_at.desc())
                .offset((1 - 1) * 5)
                .limit(5)
            )
            result = db_session.execute(query)
            turf_bookings = result.scalars().all()

            expected_turf_booking = [
                Booking.model_validate({
                    "reservation_date": booking_obj.reservation_date,
                    "start_time": booking_obj.start_time,
                    "end_time": booking_obj.end_time,
                    "total_amount": booking_obj.total_amount,
                    "payment_status": booking_obj.payment_status,
                    "booking_status": booking_obj.booking_status,
                    "customer": {
                        "name": booking_obj.customer.name,
                        "contact_no": booking_obj.customer.contact_no
                    } if booking_obj.customer else None,
                }).model_dump(mode="json")
                for booking_obj in turf_bookings
            ]
            response_data = response.json()["bookings"]

        for response_obj, expected_res in zip(response_data, expected_turf_booking):
            assert response_obj == expected_res


def test_get_booking_with_customer_token(customer_token, header, client, turf_booking, turf):
    """ This function test get turf bookings API with customer token"""

    header["Authorization"] = f"Bearer {customer_token}"

    response = client.get(
            "/api/v1/manager/get-turf-bookings/"
            "?start_date=2025-01-01&end_date=2025-12-31&page=1&size=5",
        headers=header
    )

    assert response.status_code == 401, response.text
    assert response.json()["detail"] == NOT_ALLOWED

def test_get_booking_with_no_booking_on_date(turf_manager_token, header, client, turf_booking, turf):
    """ This function test get turf bookings API with no booking on date"""

    header["Authorization"] = f"Bearer {turf_manager_token}"

    response = client.get(
        "/api/v1/manager/get-turf-bookings/"
        "?start_date=2025-01-01&end_date=2025-01-01&page=1&size=5",
        headers=header
    )

    assert response.status_code == 400, response.text
    assert response.json()["detail"] == NO_DATA_FOUND


def test_take_booking_payment(turf_manager_token, header, client, turf_booking, turf, admin_revenue):
    """ This function test take booking payment API"""
    header["Authorization"] = f"Bearer {turf_manager_token}"

    payload = {"id" : f"{turf_booking[0].id}"}
    response = client.post(
        "/api/v1/manager/take-booking-payment",
        headers=header,
        json=payload
    )
    assert response.status_code == 200, response.text
    assert response.json()[DETAILS] == PAYMENT_SUCCESSFUL


def test_take_booking_payment_with_invalid_id(turf_manager_token, header, client, turf_booking, turf):
    """ This function test take booking payment API with invalid id"""
    header["Authorization"] = f"Bearer {turf_manager_token}"
    payload = {"id": f"{uuid.uuid4()}"}
    response = client.post(
        "/api/v1/manager/take-booking-payment",
        headers=header,
        json=payload
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == NO_BOOKING_FOUND


def test_take_booking_payment_with_cancelled_booking(turf_manager_token, header, client, turf_booking, turf):
    """ This function test take booking payment API with invalid id"""
    header["Authorization"] = f"Bearer {turf_manager_token}"
    payload = {"id": f"{turf_booking[2].id}"}
    response = client.post(
        "/api/v1/manager/take-booking-payment",
        headers=header,
        json=payload
    )
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == BOOKING_ALREADY_CANCELLED

def test_take_booking_payment_with_customer_token(customer_token, header, client, turf_booking, turf):
    """ This function test take booking payment API with invalid id"""

    header["Authorization"] = f"Bearer {customer_token}"
    payload = {"id": f"{turf_booking[2].id}"}
    response = client.post(
        "/api/v1/manager/take-booking-payment",
        headers=header,
        json=payload
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == NOT_ALLOWED


def test_cancel_booking(turf_manager_token, client, turf_booking, header):
    """ This function test cancel booking API."""
    header["Authorization"] = f"Bearer {turf_manager_token}"
    payload = {
        "booking_id": f"{turf_booking[5].id}",
        "cancel_reason": "user not available on place."
    }
    response = client.post(
        "/api/v1/manager/cancel-booking",
        json=payload,
        headers=header
    )

    assert response.status_code == 200, response.text
    assert response.json()[DETAILS] == BOOKING_CANCELLED


def test_cancel_booking_with_invalid_booking_id(turf_manager_token, client, turf_booking, header):
    """ This function test cancel booking API."""

    header["Authorization"] = f"Bearer {turf_manager_token}"
    payload = {
        "booking_id": f"{uuid.uuid4()}",
        "cancel_reason": "user not available on place."
    }
    response = client.post(
        "/api/v1/manager/cancel-booking",
        json=payload,
        headers=header
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == NO_BOOKING_FOUND


def test_cancel_booking_with_customer_token(customer_token, client, turf_booking, header):
    """ This function test cancel booking API."""
    header["Authorization"] = f"Bearer {customer_token}"
    payload = {
        "booking_id": f"{turf_booking[5].id}",
        "cancel_reason": "user not available on place."
    }
    response = client.post(
        "/api/v1/manager/cancel-booking",
        json=payload,
        headers=header
    )

    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED