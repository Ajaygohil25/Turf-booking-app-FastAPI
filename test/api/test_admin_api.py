import uuid
from datetime import date, datetime
from unittest.mock import patch

import pytest
from sqlalchemy import select, and_

from core.constant import GAME_ADDED_SUCCESS, GAME_ALREADY_EXISTS, NOT_ALLOWED, GAME_NAME_UPDATED, INVALID_GAME_ID, \
    TURF_OWNER_ACTIVATION_UPDATED, USER_NOT_FOUND, TURF_ACTIVATION_UPDATED, INVALID_TURF_ID, \
    NO_TURF_FOUND, NO_DATA_FOUND
from core.database import TestSessionLocal
from models.game_model import Game
from models.revenue_model import Revenue
from models.turf_booking import TurfBooking
from models.turf_model import Turf
from schemas.admin_schemas import GameSchema, RevenueDetails, RevenueResponse, Booking
from services.admin_service import AdminService
from test.test_data.admin_json_data import valid_game_payload, game_already_exist_payload, update_game_payload


@pytest.mark.parametrize(
    "add_game_payload, expected_status_code, expected_message",
    [
        (valid_game_payload, 200, GAME_ADDED_SUCCESS),
        (game_already_exist_payload, 400, GAME_ALREADY_EXISTS)
    ]
)
def test_add_game(client, test_db, add_game_payload, expected_status_code, expected_message, header, admin_token):
    """ This function test add game API """
    header["Authorization"] = f"Bearer {admin_token}"

    response = client.post(
            "/api/v1/admin/add-game",
            json=add_game_payload,
            headers=header
    )

    assert response.status_code == expected_status_code, response.text

    if response.status_code == 200:
        game_id = response.json()["id"]

        with TestSessionLocal() as db_session:
            game_data = db_session.query(Game).filter(Game.id == game_id).one()

            assert game_data.game_name == valid_game_payload["game_name"]
            assert game_data.is_active == valid_game_payload["is_active"]
            db_session.delete(game_data)
            db_session.commit()
    else:
        assert response.json()["detail"] == expected_message


def test_add_game_with_customer_token(client, header, customer_token):
    """ This function  test add game API with customer's token. """
    header["Authorization"] = f"Bearer {customer_token}"

    response = client.post(
        "/api/v1/admin/add-game",
        json=valid_game_payload,
        headers=header
    )

    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_update_game_data(client, admin_token, header, game):
    """ This function test update game data."""
    header["Authorization"] = f"Bearer {admin_token}"

    response = client.patch(
        f"/api/v1/admin/game/{game.id}",
        headers=header,
        json=update_game_payload
    )
    assert response.status_code == 200, response.text
    assert response.json()["Details"] == GAME_NAME_UPDATED

    if response.status_code == 200:
        with TestSessionLocal() as db_session:
            game_data = db_session.query(Game).filter(Game.id == game.id).one()
            game_data.game_name = "table tennis"
            db_session.commit()
            db_session.refresh(game_data)



def test_update_game_data_with_wrong_game_id(client, admin_token, header, game):
    """ This function test update game data with wrong game id. """
    header["Authorization"] = f"Bearer {admin_token}"

    response = client.patch(
        f"/api/v1/admin/game/{uuid.uuid4()}",
        headers=header,
        json=update_game_payload
    )
    assert response.status_code == 404
    assert response.json()["detail"] == INVALID_GAME_ID


def test_update_game_data_with_customer_token(client, header, customer_token, game):
    """ This function test update game data with customer token."""
    header["Authorization"] = f"Bearer {customer_token}"

    response = client.patch(
        f"/api/v1/admin/game/{game.id}",
        headers=header,
        json= update_game_payload,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_update_game_data_with_already_exist_game(client, header, game, admin_token):
    """ This function update game data with game already exist in db."""

    header["Authorization"] = f"Bearer {admin_token}"
    update_game_payload["game_name"] = "cricket"
    response = client.patch(
        f"/api/v1/admin/game/{game.id}",
        headers=header,
        json=update_game_payload
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GAME_ALREADY_EXISTS


def test_get_all_games(client, header, admin_token):
    """ This function test get all games API. """
    header["Authorization"] = f"Bearer {admin_token}"
    response = client.get(
        "/api/v1/admin/get-games",
        headers=header
    )
    assert response.status_code == 200

    if response.status_code == 200:
        with TestSessionLocal() as db_session:
            games = db_session.query(Game).all()

            expected_games = [GameSchema.model_validate(game_obj).model_dump() for game_obj in games]
            response_games = response.json()

            assert len(expected_games) == len(response_games)

            for resp_item, expected_item in zip(response_games, expected_games):
                assert resp_item == expected_item


def test_get_all_games_with_customer_token(client, header, customer_token):
    """ This function test get all games API with customer token. """
    header["Authorization"] = f"Bearer {customer_token}"

    response = client.get(
        "/api/v1/admin/get-games",
        headers=header
    )
    assert response.status_code == 401 , response.text
    assert response.json()["detail"] == NOT_ALLOWED


def test_approve_turf_owner(client, header, admin_token, create_turf_owner):
    """ This function approve turf owner. """
    header["Authorization"] = f"Bearer {admin_token}"
    payload = {"id" : f"{create_turf_owner[2].id}"}

    response = client.post(
        "/api/v1/admin/approve-turf-owner",
        headers=header,
        json=payload
    )

    assert response.status_code == 200

    if response.status_code == 200:
        assert response.json()["Details"] == TURF_OWNER_ACTIVATION_UPDATED


def test_approve_turf_owner_with_invalid_owner_id(client, header, admin_token, create_turf_owner):
    """ This function approve turf owner API with invalid owner id. """
    header["Authorization"] = f"Bearer {admin_token}"
    payload = {"id" : f"{uuid.uuid4()}"}

    response = client.post(
        "/api/v1/admin/approve-turf-owner",
        headers=header,
        json=payload
    )

    assert response.status_code == 404
    assert response.json()["detail"] == USER_NOT_FOUND


def test_approve_turf_owner_with_customer_token(client, header, customer_token, create_turf_owner):
    """ This function test approve turf owner API with customer token. """
    header["Authorization"] = f"Bearer {customer_token}"
    payload = {"id" : f"{create_turf_owner[2].id}"}

    response = client.post(
        "/api/v1/admin/approve-turf-owner",
        headers=header,
        json=payload
    )

    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_deactivate_turf_owner(client, header, admin_token, create_turf_owner):
    """ This function test deactivate turf owner API."""

    header["Authorization"] = f"Bearer {admin_token}"
    payload = {"id" : f"{create_turf_owner[2].id}"}

    response = client.post(
        "/api/v1/admin/deactivate-turf-owner",
        headers=header,
        json=payload
    )

    assert response.status_code == 200

    if response.status_code == 200:
        assert response.json()["Details"] == TURF_OWNER_ACTIVATION_UPDATED


def test_approve_turf(client, header, admin_token, second_turf):
    """ This function test approve turf API. """

    header["Authorization"] = f"Bearer {admin_token}"
    payload = { "id" : f"{second_turf.id}"}
    response = client.post(
        "/api/v1/admin/approve-turf",
        headers=header,
        json=payload
    )

    assert response.status_code == 200
    assert response.json()["Details"] == TURF_ACTIVATION_UPDATED


def test_approve_turf_with_customer_token(client, header, customer_token, second_turf):
    """ This function test approve turf API with customer token. """

    header["Authorization"] = f"Bearer {customer_token}"
    payload = {"id" : f"{second_turf.id}"}
    response = client.post(
        "/api/v1/admin/approve-turf",
        headers=header,
        json=payload
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_approve_turf_with_invalid_turf_id(client, header, admin_token):
    """ This function test approve turf API with invalid turf id. """
    header["Authorization"] = f"Bearer {admin_token}"
    payload = {"id" : f"{uuid.uuid4()}"}
    response = client.post(
        "/api/v1/admin/approve-turf",
        headers=header,
        json=payload
    )
    assert response.status_code == 404
    assert response.json()["detail"] == INVALID_TURF_ID


def test_deactivate_turf(client, header, admin_token, second_turf):
    """ This function test deactivate turf API. """
    header["Authorization"] = f"Bearer {admin_token}"
    payload = {"id" : f"{second_turf.id}"}
    response = client.post(
        "/api/v1/admin/deactivate-turf",
        headers=header,
        json=payload
    )

    assert response.status_code == 200
    assert response.json()["Details"] == TURF_ACTIVATION_UPDATED


def test_get_revenue_data(client, header, admin_token, create_turf_owner, turf_booking):
    """ This function test get revenue data API. """
    header["Authorization"] = f"Bearer {admin_token}"

    response = client.get(
        f"/api/v1/admin/get-revenue-data/{create_turf_owner[0].id}"
        f"?start_date=2025-01-01&end_date=2025-12-01",
        headers=header,
    )

    assert response.status_code == 200, response.text

    if response.status_code == 200:
        with TestSessionLocal() as db_session:

            start_date = date(2025, 1, 1)
            end_date = date(2025, 12, 31)

            total_revenue = 0
            revenue_details = []

            turfs_with_revenue = (
                db_session.query(Turf)
                .join(TurfBooking)
                .join(Revenue)
                .filter(
                    Revenue.turf_booking_id == TurfBooking.id,
                    TurfBooking.turf_id == Turf.id,
                    Turf.turf_owner_id == create_turf_owner[0].id
                )
                .distinct()
                .all()
            )

            # get revenue of each turf of turf owner
            for turf_obj in turfs_with_revenue:
                bookings = (
                    db_session.query(TurfBooking)
                    .join(Revenue)
                    .filter(
                        Revenue.turf_booking_id == TurfBooking.id,
                        TurfBooking.turf_id == turf_obj.id,
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
                        turf_id=turf_obj.id,
                        turf_name=turf_obj.turf_name,
                        revenue_amount=turf_revenue
                    )
                )

            expected_response = RevenueResponse(
                total_revenue=total_revenue,
                revenues=revenue_details
            )

        assert response.json()["total_revenue"] == total_revenue

        for expected_res, api_res in zip(expected_response,response.json()["revenues"]):
            assert api_res == expected_res


def test_get_revenue_data_with_owner_having_no_turf(client, header, admin_token, create_turf_owner, turf_booking):
    """ This function test get revenue data API with owner having no turf. """

    header["Authorization"] = f"Bearer {admin_token}"

    response = client.get(
        f"/api/v1/admin/get-revenue-data/{create_turf_owner[1].id}"
        f"?start_date=2025-01-01&end_date=2025-12-01",
        headers=header,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == NO_TURF_FOUND


def test_get_revenue_data_with_customer_token(client, header, create_turf_owner, customer_token):
    """ This function test get revenue data API with customer token."""

    header["Authorization"] = f"Bearer {customer_token}"

    response = client.get(
        f"/api/v1/admin/get-revenue-data/{create_turf_owner[1].id}"
        f"?start_date=2025-01-01&end_date=2025-12-01",
        headers=header,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_get_revenue_data_with_invalid_owner_id(client, header, admin_token):
    """ This function test get revenue data API with invalid owner id."""

    header["Authorization"] = f"Bearer {admin_token}"

    response = client.get(
        f"/api/v1/admin/get-revenue-data/{uuid.uuid4()}"
        f"?start_date=2025-01-01&end_date=2025-12-01",
        headers=header,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == USER_NOT_FOUND


def test_get_booking_data(client, header, turf, admin_token):
    """ This function test get booking data of particular turf ."""

    header["Authorization"] = f"Bearer {admin_token}"
    response = client.get(
        f"/api/v1/admin/get-booking-data?turf_id={turf.id}"
        "&start_date=2025-01-01&end_date=2025-12-01&page=1&size=8",
        headers= header
    )

    assert response.status_code == 200

    if response.status_code == 200:
        with TestSessionLocal() as db_session:
            start_date = date(2025, 1, 1)
            end_date = date(2025, 12, 31)

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
                .offset((1 - 1) * 8)
                .limit(8)
            )
            result = db_session.execute(query)
            turf_bookings = result.scalars().all()

            # dump the sqlalchemy model into pydantic
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
                    "turf": {
                        "turf_name" : booking_obj.turf.turf_name
                    } if booking_obj.turf else None,
                }).model_dump(mode="json")
                for booking_obj in turf_bookings
            ]
            response_data = response.json()["bookings"]

    for response_obj, expected_res in zip(response_data, expected_turf_booking):
            assert response_obj == expected_res



def test_get_booking_data_with_turf_having_no_booking(client, header, second_turf, admin_token):
    """ This function test get booking data of particular turf ."""

    header["Authorization"] = f"Bearer {admin_token}"
    response = client.get(
        f"/api/v1/admin/get-booking-data?turf_id={second_turf.id}"
        "&start_date=2025-01-01&end_date=2025-12-01&page=1&size=8",
        headers= header
    )

    assert response.status_code == 400
    assert response.json()["detail"] == NO_DATA_FOUND


def test_get_booking_data_with_invalid_turf_id(client, header, admin_token):
    """ This function test get booking data of particular turf ."""

    header["Authorization"] = f"Bearer {admin_token}"
    response = client.get(
        f"/api/v1/admin/get-booking-data?turf_id={uuid.uuid4()}"
        "&start_date=2025-01-01&end_date=2025-12-01&page=1&size=8",
        headers= header
    )

    assert response.status_code == 404
    assert response.json()["detail"] == INVALID_TURF_ID


def test_get_booking_data_with_customer_token(client, header, turf, customer_token):
    """ This function test get booking data of particular turf ."""

    header["Authorization"] = f"Bearer {customer_token}"
    response = client.get(
        f"/api/v1/admin/get-booking-data?turf_id={turf.id}"
        "&start_date=2025-01-01&end_date=2025-12-01&page=1&size=8",
        headers= header
    )

    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


class MockDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        raise Exception("Simulated datetime.now() failure")


def test_update_game_data_with_exception_to_check_db_rollback(client, admin_token, header, game, monkeypatch):
    """ This function test update game data to raise an exception."""

    header["Authorization"] = f"Bearer {admin_token}"

    monkeypatch.setattr("services.admin_service.datetime", MockDateTime)
    update_game_payload["game_name"] = "testing"
    response = client.patch(
        f"/api/v1/admin/game/{game.id}",
        headers=header,
        json=update_game_payload
    )

    assert response.status_code == 500, response.text

    if response.status_code == 500:
        with TestSessionLocal() as db_session:
            game_data = db_session.query(Game).filter(Game.id == game.id).one()
            assert game_data.game_name != update_game_payload["game_name"]
