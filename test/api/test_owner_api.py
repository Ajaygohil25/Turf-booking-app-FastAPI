import os
import uuid
from datetime import date
from io import BytesIO
from unittest.mock import patch
import jwt
import pytest
from dotenv import load_dotenv
from sqlalchemy import select, and_
from models.feedback_model import Feedback
from models.turf_booking import TurfBooking
from schemas.turf_owner_schema import AddressSchema, TurfResponseSchema, ShowTurfBooking, Booking, \
    FeedbackResponseSchema
from services.turf_owner_services import TurfOwnerService
from core.constant import INVALID_AMOUNT, INVALID_STRING_INPUT, TURF_NAME_ALREADY_EXISTS, TURF_ADDED_SUCCESS, \
    INVALID_GAME_ID, TURF_ADDRESS_ADDED, INVALID_CITY_ID, TURF_DATA_UPDATED, INVALID_TURF_ID, NOT_ALLOWED, \
    TURF_DISCOUNT_DEACTIVATED, TURF_DISCOUNT_ADDED, INVALID_DISCOUNT_ID, TURF_DEACTIVATED, DETAILS, \
    MANAGER_ACTIVATION_UPDATED, INVALID_USER_ACTION, MANAGER_ACTION_NOT_ALLOWED, USER_NOT_FOUND, \
    INVALID_ADDRESS_SELECTION, INVALID_ADDRESS_ID, INVALID_DISCOUNT_AMOUNT, DISCOUNT_EXPIRED
from core.database import TestSessionLocal
from models.address_model import Address
from models.manage_turf_manager_model import ManageTurfManager
from models.turf_model import Turf
from models.user_model import User
from test.test_data.owner_json_data import address_valid_payload, turf_form_data, \
    update_turf_payload, invalid_turf_payload, street_address_invalid_payload, area_invalid_payload, \
    city_invalid_payload, invalid_turf_name, invalid_description, invalid_amenities, invalid_booking_price, \
    invalid_game_id, turf_already_exist, turf_manager_payload
from test.test_data.user_json_data import owner_credentials


def test_owner_sing_in(test_db, client, create_turf_owner):
    response = client.post(
        "/api/v1/user/sign-in",
        json=owner_credentials,
    )
    assert response.status_code == 200
    assert response.json().get("access_token") is not None


@pytest.mark.parametrize(
    "address_payload, expected_status, expected_details",
    [
        (address_valid_payload, 200, TURF_ADDRESS_ADDED),
        (street_address_invalid_payload, 400, INVALID_STRING_INPUT),
        (area_invalid_payload, 400, INVALID_STRING_INPUT),
        (city_invalid_payload, 404, INVALID_CITY_ID)
    ]
)
def test_add_address(test_db, client, owner_1_token, header, address_payload, expected_status, expected_details):
    header["Authorization"] = f"Bearer {owner_1_token}"
    response = client.post(
        "/api/v1/turf-owner/add-turf-address",
        json=address_payload,
        headers=header,
    )
    assert response.status_code == expected_status

    if response.status_code == 200:
        address_id = response.json()["id"]
        load_dotenv()
        SECRET_KEY = os.environ.get("HASH_KEY")
        ALGORITHM = os.environ.get("HASH_ALGO")

        token_payload = jwt.decode(owner_1_token, SECRET_KEY, algorithms=[ALGORITHM])
        with TestSessionLocal() as db_session:
            address_data = db_session.query(Address).filter(Address.id == address_id).first()

            assert address_data.street_address == address_valid_payload["street_address"]
            assert address_data.area == address_valid_payload["area"]
            assert address_data.city_id == address_valid_payload["city_id"]
            assert address_data.is_active == address_valid_payload["is_active"]
            assert address_data.lat == address_valid_payload["lat"]
            assert address_data.long == address_valid_payload["long"]
            assert str(address_data.turf_owner_id) == token_payload.get("user_id")
    else:
        assert response.json()["detail"] == expected_details


def test_address_with_customer_token(test_db, client, create_turf_owner, customer_token, header):
    """ This function test add address with customer access token. """

    header["Authorization"] = f"Bearer {customer_token}"
    response = client.post(
        "/api/v1/turf-owner/add-turf-address",
        json=address_valid_payload,
        headers=header,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_add_turf_with_other_owner_address(client, address, owner_2_token, header):
    """ This function add turf with invalid token. """
    header["Authorization"] = f"Bearer {owner_2_token}"
    files = []
    for i in range(5):
        mock_file = BytesIO(b"fake_image_data")
        mock_file.name = f"image{i}.jpg"
        files.append(("media", (mock_file.name, mock_file, "image/jpeg")))

    turf_form_data["address_id"] = str(address.id)

    response = client.post(
        "/api/v1/turf-owner/add-turf",
        data=turf_form_data,
        files=files,
        headers=header,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == INVALID_ADDRESS_SELECTION


def test_add_turf_with_invalid_address_id(client, owner_1_token, address, header):
    """ This function add turf with invalid address. """
    header["Authorization"] = f"Bearer {owner_1_token}"
    files = []
    for i in range(5):
        mock_file = BytesIO(b"fake_image_data")
        mock_file.name = f"image{i}.jpg"
        files.append(("media", (mock_file.name, mock_file, "image/jpeg")))

    turf_form_data["address_id"] = str(uuid.uuid4())

    response = client.post(
        "/api/v1/turf-owner/add-turf",
        data=turf_form_data,
        files=files,
        headers=header,
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == INVALID_ADDRESS_ID


def test_add_turf_with_customer_token(client, customer_token, address, header):
    """ This function add turf with invalid address. """
    header["Authorization"] = f"Bearer {customer_token}"
    files = []
    for i in range(5):
        mock_file = BytesIO(b"fake_image_data")
        mock_file.name = f"image{i}.jpg"
        files.append(("media", (mock_file.name, mock_file, "image/jpeg")))

    turf_form_data["address_id"] = str(uuid.uuid4())

    response = client.post(
        "/api/v1/turf-owner/add-turf",
        data=turf_form_data,
        files=files,
        headers=header,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


@pytest.mark.parametrize(
    "turf_data, expected_status, expected_details",
    [
        (turf_form_data, 200, TURF_ADDED_SUCCESS),
        (invalid_turf_name, 400, INVALID_STRING_INPUT),
        (turf_already_exist, 400, TURF_NAME_ALREADY_EXISTS),
        (invalid_description, 400, INVALID_STRING_INPUT),
        (invalid_amenities, 400, INVALID_STRING_INPUT),
        (invalid_booking_price, 400, INVALID_AMOUNT),
        (invalid_game_id, 404, INVALID_GAME_ID)
    ]
)
def test_add_turf(client, address, owner_1_token, turf_data, expected_status, header, expected_details):
    """ This function add turf."""

    header["Authorization"] = f"Bearer {owner_1_token}"
    files = []
    for i in range(5):
        mock_file = BytesIO(b"fake_image_data")
        mock_file.name = f"image{i}.jpg"
        files.append(("media", (mock_file.name, mock_file, "image/jpeg")))

    turf_data["address_id"] = str(address.id)

    response = client.post(
        "/api/v1/turf-owner/add-turf",
        data=turf_data,
        files=files,
        headers=header,
    )
    assert response.status_code == expected_status

    if response.status_code == 200:
        turf_id = response.json()["id"]
        load_dotenv()
        SECRET_KEY = os.environ.get("HASH_KEY")
        ALGORITHM = os.environ.get("HASH_ALGO")

        token_payload = jwt.decode(owner_1_token, SECRET_KEY, algorithms=[ALGORITHM])
        with TestSessionLocal() as db_session:
            turf_data = db_session.query(Turf).filter(Turf.id == turf_id).first()

            assert turf_data.turf_name == turf_form_data["turf_name"]
            assert turf_data.description == turf_form_data["description"]
            assert turf_data.booking_price == int(turf_form_data["booking_price"])
            assert turf_data.is_active == turf_form_data["is_active"]
            assert turf_data.is_verified == turf_form_data["is_verified"]
            assert str(turf_data.turf_owner_id) == token_payload.get("user_id")
            assert turf_data.address_id == address.id
    else:
        assert response.json()["detail"] == expected_details

def test_get_turf(client, owner_1_token, turf, header):
    """ This function get turf details."""
    header["Authorization"] = f"Bearer {owner_1_token}"
    response = client.get(
        f"/api/v1/turf-owner/get-turf-details/{turf.id}",
        headers=header,
    )
    assert response.status_code == 200, response.text

    if response.status_code == 200:
        with TestSessionLocal() as db_session:
            turf_data = db_session.query(Turf).filter(Turf.id == turf.id).first()
            assert turf_data.turf_name == turf.turf_name
            assert turf_data.description == turf.description
            assert turf_data.amenities == turf.amenities
            assert turf_data.booking_price == turf.booking_price
            assert turf_data.is_active == turf.is_active
            assert turf_data.is_verified == turf.is_verified
            assert turf_data.turf_owner_id == turf.turf_owner_id
            assert turf_data.address_id == turf.address_id


def test_get_turf_with_other_owner_token(client, owner_2_token, turf, header):
    """ This function get turf details with invalid token. """
    header["Authorization"] = f"Bearer {owner_2_token}"
    response = client.get(
        f"/api/v1/turf-owner/get-turf-details/{turf.id}",
        headers=header,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_get_turf_with_invalid_turf_id(client, owner_1_token, turf, header):
    """ This function get turf details with invalid token. """

    header["Authorization"] = f"Bearer {owner_1_token}"
    response = client.get(
        f"/api/v1/turf-owner/get-turf-details/{uuid.uuid4()}",
        headers=header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == INVALID_TURF_ID


@pytest.mark.parametrize(
    "payload, expected_status, expected_details",
    [
        (update_turf_payload, 200, TURF_DATA_UPDATED),
        (invalid_turf_payload, 400, INVALID_STRING_INPUT)
    ]
)
def test_update_turf(client, payload, expected_status, expected_details, turf, owner_1_token, header):
    """ This function test the update turf."""

    header["Authorization"] = f"Bearer {owner_1_token}"
    response = client.patch(
        f"/api/v1/turf-owner/update-turf-details/{turf.id}",
        json=payload,
        headers=header,
    )
    assert response.status_code == expected_status, response.text

    if response.status_code == 200:
        with TestSessionLocal() as db_session:
            turf_data = db_session.query(Turf).filter(Turf.id == turf.id).first()
            assert turf_data.turf_name == update_turf_payload["turf_name"]
            assert turf_data.description == update_turf_payload["description"]
            assert turf_data.booking_price == update_turf_payload["booking_price"]
    else:
        assert response.json()["detail"] == expected_details


def test_update_turf_with_invalid_id(client, owner_1_token, turf, header):
    """ This function test the update turf with invalid token. """

    header["Authorization"] = f"Bearer {owner_1_token}"
    response = client.patch(
        f"/api/v1/turf-owner/update-turf-details/{uuid.uuid4()}",
        json=update_turf_payload,
        headers=header,
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == INVALID_TURF_ID


def test_update_turf_with_other_token(client, owner_2_token, turf, header):
    """ This function test the update turf with invalid token. """

    header["Authorization"] = f"Bearer {owner_2_token}"
    response = client.patch(
        f"/api/v1/turf-owner/update-turf-details/{turf.id}",
        json=update_turf_payload,
        headers=header,
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == NOT_ALLOWED


def test_add_turf_discount(client, turf, owner_1_token, header):
    """ This function tests the add turf discount."""
    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"turf_id": str(turf.id), "discount_amount": 100}

    response = client.post(
        "/api/v1/turf-owner/add-turf-discount",
        json=payload,
        headers=header,
    )
    assert response.status_code == 200, response.text
    assert response.json()["Details"] == TURF_DISCOUNT_ADDED

def test_add_turf_discount_with_invalid_amount(client, turf, owner_1_token, header):
    """ This function tests the add turf discount."""
    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"turf_id": str(turf.id), "discount_amount": -100}

    response = client.post(
        "/api/v1/turf-owner/add-turf-discount",
        json=payload,
        headers=header,
    )
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == INVALID_DISCOUNT_AMOUNT

def test_add_discount_with_invalid_turf_id(client, owner_1_token, turf, header):
    """ This function tests the add turf discount with invalid turf id. """

    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"turf_id": str(uuid.uuid4()), "discount_amount": 100}

    response = client.post(
        "/api/v1/turf-owner/add-turf-discount",
        json=payload,
        headers=header,
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == INVALID_TURF_ID

def test_deactivate_discount_with_other_user_token(client, owner_2_token, discount, header):
    """ This function tests the deactivate turf discount with invalid token. """
    header["Authorization"] = f"Bearer {owner_2_token}"
    payload = {"id": str(discount[0].id)}

    response = client.post(
        "/api/v1/turf-owner/deactivate-turf-discount",
        json=payload,
        headers=header,
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == NOT_ALLOWED


def test_deactivate_discount_with_invalid_turf_id(client, owner_1_token, header):
    """ This function tests the deactivate turf discount with invalid id. """
    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"id": str(uuid.uuid4())}
    response = client.post(
        "/api/v1/turf-owner/deactivate-turf-discount",
        json=payload,
        headers=header,
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == INVALID_DISCOUNT_ID


def test_deactivate_discount(client, owner_1_token, discount, header):
    """ This function deactivate turf discount. """
    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"id": str(discount[0].id)}

    response = client.post(
        "/api/v1/turf-owner/deactivate-turf-discount",
        json=payload,
        headers=header,
    )
    assert response.status_code == 200, response.text
    assert response.json()["Details"] == TURF_DISCOUNT_DEACTIVATED

def test_deactivate_expired_discount(client, owner_1_token, discount, header):
    """ This function deactivate turf discount. """
    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"id": str(discount[0].id)}

    response = client.post(
        "/api/v1/turf-owner/deactivate-turf-discount",
        json=payload,
        headers=header,
    )
    assert response.status_code == 406, response.text
    assert response.json()["detail"] == DISCOUNT_EXPIRED

def test_deactivate_turf_with_other_user_token(client, owner_2_token, turf, header):
    """ This function tests the deactivate turf with invalid token. """
    header["Authorization"] = f"Bearer {owner_2_token}"
    payload = {"id": str(turf.id)}
    response = client.post(
        "/api/v1/turf-owner/deactivate-turf",
        json=payload,
        headers=header,
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == NOT_ALLOWED


def test_deactivate_turf_with_invalid_id(client, owner_1_token, header):
    """ This function tests the deactivate turf with invalid id. """
    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"id": str(uuid.uuid4())}
    response = client.post(
        "/api/v1/turf-owner/deactivate-turf",
        json=payload,
        headers=header,
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == INVALID_TURF_ID


def test_add_turf_manager(client, owner_1_token, turf, header):
    """ Test adding a turf manager. """
    header["Authorization"] = f"Bearer {owner_1_token}"
    turf_manager_payload["turf_id"] = str(turf.id)
    response = client.post(
        "/api/v1/turf-owner/add-turf-manager",
        json=turf_manager_payload,
        headers=header,
    )
    assert response.status_code == 200, response.text
    if response.status_code == 200:
        assert response.json() == {
            "Details": "Turf manager added successfully"
        }
        with TestSessionLocal() as db_session:
            user_data = db_session.query(User).filter(User.email == turf_manager_payload.get("email")).first()
            manager_turf_owner = db_session.query(ManageTurfManager
                                                  ).filter(ManageTurfManager.turf_id == turf.id).first()

            # Check mapping of turf manager with turf
            assert user_data.id == manager_turf_owner.turf_manager_id
            assert user_data.name == turf_manager_payload.get("name")
            assert user_data.contact_no == turf_manager_payload.get("contact_no")
            assert user_data.email == turf_manager_payload.get("email")
            assert user_data.is_active == turf_manager_payload.get("is_active")
            assert user_data.is_verified == turf_manager_payload.get("is_verified")
            assert str(user_data.role_id) == turf_manager_payload.get("role_id")
            assert user_data.city_id == turf_manager_payload.get("city_id")


def test_add_turf_manager_with_other_owner_token(client, owner_2_token, turf, header):
    """ This function tests the adding a turf manager with invalid token. """

    header["Authorization"] = f"Bearer {owner_2_token}"
    turf_manager_payload["turf_id"] = str(turf.id)
    response = client.post(
        "/api/v1/turf-owner/add-turf-manager",
        json=turf_manager_payload,
        headers=header,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_add_turf_manager_with_invalid_turf_id(client, owner_1_token, header):
    """ This function tests the adding a turf manager with invalid id. """

    header["Authorization"] = f"Bearer {owner_1_token}"
    turf_manager_payload["turf_id"] = str(uuid.uuid4())
    response = client.post(
        "/api/v1/turf-owner/add-turf-manager",
        json=turf_manager_payload,
        headers=header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == INVALID_TURF_ID


def test_deactivate_turf_manager(client, owner_1_token, turf_manager, header):
    """ This function test deactivating a turf manager. """
    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"id": str(turf_manager.id)}

    response = client.post(
        "/api/v1/turf-owner/deactivate-turf-manager",
        json=payload,
        headers=header,
    )
    assert response.status_code == 200
    assert response.json()[DETAILS] == MANAGER_ACTIVATION_UPDATED


def test_deactivate_manager_with_other_owner_token(client, owner_2_token, turf_manager, header):
    """ This function test the deactivate turf manager by invalid token. """

    header["Authorization"] = f"Bearer {owner_2_token}"
    payload = {"id": str(turf_manager.id)}

    response = client.post(
        "/api/v1/turf-owner/deactivate-turf-manager",
        json=payload,
        headers=header,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == MANAGER_ACTION_NOT_ALLOWED


def test_deactivate_manager_with_invalid_id(client, owner_1_token, turf_manager, header):
    """ This function test the deactivate turf manager by the invalid turf id. """

    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"id": str(uuid.uuid4())}

    response = client.post(
        "/api/v1/turf-owner/deactivate-turf-manager",
        json=payload,
        headers=header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == USER_NOT_FOUND


def test_deactivate_manager_with_customer_id(client, owner_1_token, create_customer, header):
    """ This function test the deactivation of turf manager by customer id"""

    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"id": str(create_customer[0].id)}

    response = client.post(
        "/api/v1/turf-owner/deactivate-turf-manager",
        json=payload,
        headers=header,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == INVALID_USER_ACTION


def test_get_all_address(client, address, owner_1_token, header):
    """ This function test get all address API. """

    header["Authorization"] = f"Bearer {owner_1_token}"

    response = client.get(
        "/api/v1/turf-owner/get-all-address",
        headers=header,
    )
    assert response.status_code == 200

    if response.status_code == 200:
        load_dotenv()
        SECRET_KEY = os.environ.get("HASH_KEY")
        ALGORITHM = os.environ.get("HASH_ALGO")

        token_payload = jwt.decode(owner_1_token, SECRET_KEY, algorithms=[ALGORITHM])
        with TestSessionLocal() as db_session:
            addresses = db_session.query(Address).filter(Address.turf_owner_id == token_payload.get("user_id")).all()

            # dump the sqlalchemy model into pydantic
            expected_addresses = [AddressSchema.model_validate(addr).model_dump() for addr in addresses]
            response_addresses = response.json()

            assert len(expected_addresses) == len(response_addresses)

            for resp_item, expected_item in zip(response_addresses, expected_addresses):
                assert resp_item == expected_item

def test_get_all_address_with_customer_token(client, customer_token, header):
    """ This function test get all address API. """

    header["Authorization"] = f"Bearer {customer_token}"

    response = client.get(
        "/api/v1/turf-owner/get-all-address",
        headers=header,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED



def test_get_all_turfs(client, owner_1_token, header):
    """ This function test get all turfs API."""
    header["Authorization"] = f"Bearer {owner_1_token}"

    response = client.get(
        "/api/v1/turf-owner/get-all-turfs",
        headers=header,
    )
    assert response.status_code == 200

    if response.status_code == 200:
        load_dotenv()
        SECRET_KEY = os.environ.get("HASH_KEY")
        ALGORITHM = os.environ.get("HASH_ALGO")

        token_payload = jwt.decode(owner_1_token, SECRET_KEY, algorithms=[ALGORITHM])

        with TestSessionLocal() as db_session:
            turfs = db_session.query(Turf).filter(Turf.turf_owner_id == token_payload.get("user_id")).all()

            # dump the sqlalchemy model into pydantic
            expected_turfs = [TurfResponseSchema.model_validate(turf_obj).model_dump() for turf_obj in turfs]

            for expected_turf in expected_turfs:
                for discount_obj in expected_turf.get("discounts", []):
                    discount_obj["turf_id"] = str(discount_obj["turf_id"])

            response_turfs = response.json()

            assert len(expected_turfs) == len(response_turfs)

            for resp_item, expected_item in zip(response_turfs, expected_turfs):
                assert resp_item == expected_item


def test_get_turfs_with_customer_token(client, customer_token, header):
    """ This function test get all turfs API with invalid owner token."""
    header["Authorization"] = f"Bearer {customer_token}"

    response = client.get(
        "/api/v1/turf-owner/get-all-turfs",
        headers=header,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_get_bookings(client, turf, owner_1_token, header, turf_booking):
    """ This function test get turf bookings API."""
    header["Authorization"] = f"Bearer {owner_1_token}"

    response = client.get(
        f"/api/v1/turf-owner/get-turf-bookings/{turf.id}"
        f"?start_date=2025-01-01&end_date=2025-12-31&page=1&size=3",
        headers=header,
    )

    assert response.status_code == 200, response.text

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
                        TurfBooking.turf_id == str(turf.id) ,
                        TurfBooking.reservation_date >= start_date,
                        TurfBooking.reservation_date <= end_date,
                    )
                )
                .order_by(TurfBooking.created_at.desc())
                .offset((1 - 1) * 3)
                .limit(3)
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
                }).model_dump(mode="json")
                for booking_obj in turf_bookings
            ]

            response_turf_booking = response.json()["bookings"]

            assert len(expected_turf_booking) == len(response_turf_booking)

            for resp_item, expected_item in zip(response_turf_booking, expected_turf_booking):
                assert resp_item == expected_item


def test_get_bookings_with_other_owner_token(client, turf, owner_2_token, header, turf_booking):
    """ This function test get turf bookings API with invalid owner token."""

    header["Authorization"] = f"Bearer {owner_2_token}"
    response = client.get(
        f"/api/v1/turf-owner/get-turf-bookings/{turf.id}"
        f"?{2025 - 1 - 1}&{2025 - 12 - 31}&{1}&{3}",
        headers=header,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_get_bookings_with_invalid_turf_id(client, owner_1_token, header, turf_booking):
    """ This function test get turf bookings API with invalid turf id."""

    header["Authorization"] = f"Bearer {owner_1_token}"
    response = client.get(
        f"/api/v1/turf-owner/get-turf-bookings/{uuid.uuid4()}"
        f"?{2025 - 1 - 1}&{2025 - 12 - 31}&{1}&{3}",
        headers=header,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == INVALID_TURF_ID


def test_get_feedbacks(client, turf, owner_1_token, header):
    """ This function test get feedbacks API."""
    header["Authorization"] = f"Bearer {owner_1_token}"

    response = client.get(
        f"/api/v1/turf-owner/get-feedback/{turf.id}",
        headers=header,
    )
    assert response.status_code == 200

    with TestSessionLocal() as db_session:
        feedbacks = (
            db_session.query(Feedback)
            .join(TurfBooking)
            .filter(TurfBooking.turf_id == turf.id)
            .order_by(Feedback.created_at)
            .all()
        )

        expected_feedback = [FeedbackResponseSchema.model_validate(feedback_obj).model_dump() for feedback_obj in feedbacks]

        response_feedback = response.json()

        assert len(expected_feedback) == len(response_feedback)

        for resp_item, expected_item in zip(response_feedback, expected_feedback):
            assert resp_item == expected_item


def test_get_feedback_with_other_owner_token(client, owner_2_token, turf, header):
    """ This function test get feedback API with invalid owner token."""
    header["Authorization"] = f"Bearer {owner_2_token}"

    response = client.get(
        f"/api/v1/turf-owner/get-feedback/{turf.id}",
        headers=header,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_ALLOWED


def test_get_feedback_with_invalid_turf_id(client, owner_1_token, header):
    """ This function test get feedback API with invalid turf id."""
    header["Authorization"] = f"Bearer {owner_1_token}"

    response = client.get(
        f"/api/v1/turf-owner/get-feedback/{uuid.uuid4()}",
        headers=header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == INVALID_TURF_ID

def test_deactivate_turf(client, turf, owner_1_token, header):
    """ Test the deactivation of turf."""
    header["Authorization"] = f"Bearer {owner_1_token}"
    payload = {"id": str(turf.id)}

    response = client.post(
        "/api/v1/turf-owner/deactivate-turf",
        json=payload,
        headers=header,
    )
    assert response.status_code == 200, response.text
    assert response.json()["Details"] == TURF_DEACTIVATED


def test_add_turf_with_video_file(client, address, owner_1_token, header):
    """ This function add turf with video file. """

    header["Authorization"] = f"Bearer {owner_1_token}"
    files = []
    for i in range(5):
        mock_file = BytesIO(b"fake_image_data")
        mock_file.name = f"image{i}.jpg"
        files.append(("media", (mock_file.name, mock_file, "image/jpeg")))

    with open("media/test_video.mp4", "w") as file:
        file.write("This is a test video.")

    with open("media/test_video.mp4", "rb") as video:
        turf_form_data["turf_name"] = "test turf"
        turf_form_data["address_id"] = str(address.id)
        response = client.post(
            "/api/v1/turf-owner/add-turf",
            data=turf_form_data,
            files={"media": video},
            headers=header,
        )

    assert response.status_code == 200, response.text