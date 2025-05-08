from unittest.mock import patch
import jwt
import pytest
import os
from dotenv import load_dotenv
from core.database import TestSessionLocal
from models.roles_model import Roles
from models.user_model import User
from test.conftest import test_db
from test.test_data.user_json_data import (user_data_payload, user_login_payload, update_user_payload,
                                           forget_password_payload, invalid_password_payload,
                                           invalid_email_payload, invalid_update_user_payload,
                                           invalid_reset_password_payload, invalid_confirm_password,
                                           reset_password_payload, invalid_password_user_payload,
                                           invalid_contact_no_payload, invalid_mail_user_payload, invalid_role_id,
                                           invalid_city_id, user_data_api_payload)
from authentication.hashing import Hash


@pytest.mark.parametrize(
    "data_payload, expected_status",
    [
        (user_data_api_payload, 200),
        (invalid_mail_user_payload, 400),
        (invalid_password_user_payload, 400),
        (invalid_contact_no_payload, 400),
        (invalid_role_id, 404),
        (invalid_city_id, 404)
    ]
)
def test_create_user(test_db, client, data_payload, expected_status):
    response = client.post(
        "/api/v1/user/sign-up",
        json=data_payload,
    )
    assert response.status_code == expected_status
    if response.status_code == 200:
        assert response.json() == {
            "Details": "Account created successfully !",
            "sign-in app": "http://localhost:8000/api/v1/user/sign-in"
        }
        with TestSessionLocal() as db_session:
            user_data = db_session.query(User).filter(User.email == user_data_api_payload.get("email")).first()
            assert user_data.name == user_data_api_payload.get("name")
            assert user_data.contact_no == user_data_api_payload.get("contact_no")
            assert user_data.email ==user_data_api_payload.get("email")
            assert user_data.is_active == user_data_api_payload.get("is_active")
            assert user_data.is_verified == user_data_api_payload.get("is_verified")
            assert str(user_data.role_id) == user_data_api_payload.get("role_id")
            assert user_data.city_id == user_data_api_payload.get("city_id")


@pytest.mark.parametrize(
    "login_payload, expected_status",
    [
        (user_login_payload, 200),
        (invalid_password_payload, 401),
        (invalid_email_payload, 404)
    ]
)
def test_login_user(test_db, login_payload, create_customer, expected_status, client):
    with ((patch("services.user_service.send_mail"))):
        response = client.post(
            "/api/v1/user/sign-in",
            json=login_payload,
        )
        assert response.status_code == expected_status, response.text

        if response.status_code == 200:
            access_token = response.json()["access_token"]
            refresh_token = response.json()["refresh_token"]

            load_dotenv()
            SECRET_KEY = os.environ.get("HASH_KEY")
            ALGORITHM = os.environ.get("HASH_ALGO")

            access_token_payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            refresh_token_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

            # Checking for the valid metadata in the access token

            assert login_payload.get("username") == access_token_payload.get("sub")
            assert access_token_payload.get("is_refresh") == False

            # Checking for the valid metadata in the refresh token
            assert login_payload.get("username") == refresh_token_payload.get("sub")
            assert refresh_token_payload.get("is_refresh") == True

            # Checking roles in both token
            with TestSessionLocal() as db_session:
                role_name = (
                    db_session.query(Roles.role_name)
                    .select_from(User)
                    .join(Roles, User.role_id == Roles.id)
                    .filter(User.email == login_payload.get("username"))
                    .first()
                )

                assert role_name[0] == access_token_payload.get("Role")
                assert role_name[0] == refresh_token_payload.get("Role")


def test_get_user_data(test_db, client, customer_token, header):
    header["Authorization"] = f"Bearer {customer_token}"
    response = client.get(
        "/api/v1/user/profile",
        headers=header,
    )

    if response.status_code == 200:
        load_dotenv()
        SECRET_KEY = os.environ.get("HASH_KEY")
        ALGORITHM = os.environ.get("HASH_ALGO")

        token_payload = jwt.decode(customer_token, SECRET_KEY, algorithms=[ALGORITHM])
        print("token payload", token_payload)

        with TestSessionLocal() as db_session:
            user_data = db_session.query(User).filter(User.email == token_payload.get("sub")).first()
            assert user_data.name == user_data_payload["name"]
            assert user_data.contact_no == user_data_payload["contact_no"]
            assert user_data.email == user_data_payload["email"]

@pytest.mark.parametrize(
    "payload, expected_status",
    [
        (update_user_payload, 200),
        (invalid_update_user_payload, 400)
    ]
)
def test_update_profile(test_db, client, payload, expected_status, customer_token, header):
    header["Authorization"] = f"Bearer {customer_token}"
    response = client.patch(
        "/api/v1/user/update-profile",
        json=payload,
        headers=header,
    )
    assert response.status_code == expected_status, response.text

    if response.status_code == 200:
        load_dotenv()
        SECRET_KEY = os.environ.get("HASH_KEY")
        ALGORITHM = os.environ.get("HASH_ALGO")

        token_payload = jwt.decode(customer_token, SECRET_KEY, algorithms=[ALGORITHM])

        with TestSessionLocal() as db_session:
            user_data = db_session.query(User).filter(User.email == token_payload.get("sub")).first()

            user_data.contact_no = update_user_payload.get("contact_no")
            user_data.name = user_data_payload.get("name")


def test_update_profile_invalid_token(test_db, client, header):
    """ This function  test update profile with invalid token."""
    header["Authorization"] = "Bearer eyJhbKciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhamF5QGdtYWlsLmNvbS"

    response = client.patch(
        "/api/v1/user/update-profile",
        json=update_user_payload,
        headers=header,
    )
    assert response.status_code == 401, response.text
    assert response.json() == {
        "detail": "Not authorized to perform this action, please Sing-in again !"
    }


def test_forgot_password(test_db, client):
    with patch("services.user_service.send_mail"):
        response = client.post(
            "/api/v1/user/forgot-password",
            json=forget_password_payload,
        )
        assert response.status_code == 200, response.text
        assert response.json() == {
            "Message": "Email has been sent for password reset"
        }


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        (invalid_reset_password_payload, 401),
        (invalid_confirm_password, 400),
        (reset_password_payload, 200)
        # keep the above test cases at last only otherwise other test cases will be failed due to password change.
    ]
)
def test_reset_password(test_db, client, payload, expected_status, customer_token, header):
    header["Authorization"] = f"Bearer {customer_token}"
    response = client.patch(
        "/api/v1/user/reset-password",
        json=payload,
        headers=header
    )
    assert response.status_code == expected_status, response.text
    if response.status_code == 200:
        assert response.json() == {
            "Details": "Password changed successfully !",
            "sign-in app": "http://localhost:8000/api/v1/user/sign-in"
        }
