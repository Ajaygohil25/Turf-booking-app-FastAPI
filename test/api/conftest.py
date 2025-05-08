import copy
from datetime import datetime, timedelta

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry.point import Point

from authentication.token_management import create_access_token
from core.constant import TOKEN_SUB, TOKEN_USER_ID, ROLE_TYPE
from core.database import TestSessionLocal
from models.address_model import Address
from models.admin_revenue_model import AdminRevenue
from models.discount_model import Discount
from models.game_model import Game
from models.manage_turf_manager_model import ManageTurfManager
from models.turf_booking import TurfBooking
from models.turf_model import Turf
from models.user_model import User
from test.test_data.owner_json_data import address_valid_payload, turf_api_data, discount_payload, turf_manager_payload
from authentication.hashing import Hash

def token(user, role):
    access_token = create_access_token(
        data={
            TOKEN_SUB: user.email,
            TOKEN_USER_ID: str(user.id),
            ROLE_TYPE: role
        }
    )
    return access_token


@pytest.fixture(scope="module")
def admin_token(create_admin):
    """ This fixture login admin and generate access token. """
    return token(create_admin, "Admin")


@pytest.fixture(scope="module")
def customer_token(create_customer):
    """ This fixture login customer and generate access token. """
    return token(create_customer[0], "Customer")

@pytest.fixture(scope="module")
def customer_2_token(create_customer):
    """ This fixture login customer and generate access token. """
    return token(create_customer[1], "Customer")

@pytest.fixture(scope="module")
def owner_1_token(create_turf_owner):
    """ This fixture login customer and generate access token. """
    return token(create_turf_owner[0], "Owner")


@pytest.fixture(scope="module")
def owner_2_token(create_turf_owner):
    """ This fixture login customer and generate access token. """
    return token(create_turf_owner[1], "Owner")


@pytest.fixture(scope="module")
def address(create_turf_owner):
    """ this function add address"""
    with TestSessionLocal() as db_session:
        address_data = db_session.query(Address).first()
        if not address_data:
            address_valid_payload["turf_owner_id"] = str(create_turf_owner[0].id)
            address_data = Address(**address_valid_payload)
            address_data.geom = from_shape(Point(address_valid_payload["long"],
                                                 address_valid_payload["lat"]), srid=4326)
            db_session.add(address_data)
            db_session.commit()
            db_session.refresh(address_data)
            return address_data

        return address_data


@pytest.fixture(scope="module")
def turf(create_turf_owner, address):
    with TestSessionLocal() as db_session:
        game_data = db_session.query(Game).filter(Game.game_name == "cricket").first()
        turf_api_data["game_id"] = str(game_data.id)
        turf_api_data["address_id"] = str(address.id)
        turf_api_data["turf_owner_id"] = str(create_turf_owner[0].id)
        turf_data = Turf(**turf_api_data)
        db_session.add(turf_data)
        db_session.commit()
        db_session.refresh(turf_data)
        return turf_data


@pytest.fixture(scope="module")
def admin_revenue(turf):
    with TestSessionLocal() as db_session:
        revenue_data = AdminRevenue(
            turf_id=turf.id,
            revenue_mode="fixed",
            amount=100
        )
        db_session.add(revenue_data)
        db_session.commit()
        db_session.refresh(revenue_data)
        return revenue_data


@pytest.fixture(scope="module")
def second_turf(create_turf_owner, address):
    with TestSessionLocal() as db_session:
        game_data = db_session.query(Game).filter(Game.game_name == "cricket").first()
        turf_data = copy.deepcopy(turf_api_data)
        turf_data["game_id"] = str(game_data.id)
        turf_data["is_active"] = False
        turf_data["is_verified"] = False
        turf_data["address_id"] = str(address.id)
        turf_data["turf_owner_id"] = str(create_turf_owner[2].id)
        second_turf_data = Turf(**turf_data)
        db_session.add(second_turf_data)
        db_session.commit()
        db_session.refresh(second_turf_data)
        return second_turf_data

@pytest.fixture(scope="module")
def discount(turf):
    """ this function add discount to turf. """
    discounts = []
    with TestSessionLocal() as db_session:
        discount_payload["turf_id"] = str(turf.id)
        discount_data = Discount(**discount_payload)
        db_session.add(discount_data)
        db_session.commit()
        db_session.refresh(discount_data)
        discounts.append(discount_data)

    with TestSessionLocal() as db_session:
        discount_payload["turf_id"] = str(turf.id)
        discount_payload["is_active"] = False
        discount_data = Discount(**discount_payload)
        db_session.add(discount_data)
        db_session.commit()
        db_session.refresh(discount_data)
        discounts.append(discount_data)

    return discounts

@pytest.fixture(scope="module")
def header():
    return {"Authorization": ""}


@pytest.fixture(scope="module")
def turf_manager(turf):
    """ This function add turf manager into database. """
    with TestSessionLocal() as db_session:
        turf_manager = User(
            name=turf_manager_payload.get("name"),
            contact_no=turf_manager_payload.get("contact_no"),
            email=turf_manager_payload.get("email"),
            password=Hash.encrypt(turf_manager_payload.get("password")),
            is_active=turf_manager_payload.get("is_active"),
            is_verified=turf_manager_payload.get("is_verified"),
            lat=turf_manager_payload.get("lat"),
            long=turf_manager_payload.get("long"),
            geom=from_shape(Point(turf_manager_payload["long"], turf_manager_payload["lat"]), srid=4326),
            role_id=turf_manager_payload.get("role_id"),
            city_id=turf_manager_payload.get("city_id"),
        )

        db_session.add(turf_manager)
        db_session.flush()

        turf_manager_id = str(turf_manager.id)
        manage_turf_manager = ManageTurfManager(
            turf_id=turf.id,
            turf_manager_id=turf_manager_id,
            is_active=True
        )

        db_session.add(manage_turf_manager)
        db_session.commit()
        db_session.refresh(turf_manager)
        db_session.refresh(manage_turf_manager)

        return turf_manager

@pytest.fixture(scope="module")
def turf_manager_token(turf_manager):
    """ This fixture create turf manager token. """
    return token(turf_manager, "Manager")


@pytest.fixture(scope="module")
def turf_booking(create_customer, turf):
    """ This function add turf bookings into database. """
    bookings = []
    # index 0 : valid booking
    with TestSessionLocal() as db_session:
        turf_booking = TurfBooking(
            customer_id=str(create_customer[0].id),
            turf_id=str(turf.id),
            reservation_date=datetime.strptime("2025-04-10", "%Y-%m-%d"),
            start_time=datetime.strptime("2025-04-10 13:00:00", "%Y-%m-%d %H:%M:%S"),
            end_time=datetime.strptime("2025-04-10 18:00:00", "%Y-%m-%d %H:%M:%S"),
            booking_status="confirm",
            payment_status="unpaid",
            total_amount= 1200,
        )

        db_session.add(turf_booking)
        db_session.commit()
        db_session.refresh(turf_booking)
        bookings.append(turf_booking)

    # index 1 :past booking of turf
    with TestSessionLocal() as db_session:
        turf_booking = TurfBooking(
            customer_id=str(create_customer[0].id),
            turf_id=str(turf.id),
            reservation_date=datetime.strptime( "2025-03-01", "%Y-%m-%d"),
            start_time=datetime.strptime( "2025-03-01 13:00:00", "%Y-%m-%d %H:%M:%S"),
            end_time=datetime.strptime( "2025-03-01 18:00:00", "%Y-%m-%d %H:%M:%S"),
            booking_status="booked",
            payment_status="unpaid",
            total_amount= 1000,
        )

        db_session.add(turf_booking)
        db_session.commit()
        db_session.refresh(turf_booking)
        bookings.append(turf_booking)

    # index 2 : cancelled booking data
    with TestSessionLocal() as db_session:
        turf_booking = TurfBooking(
            customer_id=str(create_customer[0].id),
            turf_id=str(turf.id),
            reservation_date=datetime.strptime( "2025-04-10", "%Y-%m-%d"),
            start_time=datetime.strptime( "2025-04-10 13:00:00", "%Y-%m-%d %H:%M:%S"),
            end_time=datetime.strptime( "2025-04-10 18:00:00", "%Y-%m-%d %H:%M:%S"),
            booking_status="cancelled",
            payment_status="unpaid",
            total_amount= 1000,
        )

        db_session.add(turf_booking)
        db_session.commit()
        db_session.refresh(turf_booking)
        bookings.append(turf_booking)

    # index 3 : turf booking data with current date and time
    with TestSessionLocal() as db_session:
        now = datetime.now()
        reservation_date = datetime.strptime(now.strftime("%Y-%m-%d"), "%Y-%m-%d")
        start_time = now + timedelta(minutes=30)
        end_time = start_time + timedelta(hours=2)

        turf_booking = TurfBooking(
            customer_id=str(create_customer[0].id),
            turf_id=str(turf.id),
            reservation_date=reservation_date,
            start_time=datetime.strptime(start_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"),
            end_time=datetime.strptime(end_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"),
            booking_status="confirm",
            payment_status="unpaid",
            total_amount=1000,
        )

        db_session.add(turf_booking)
        db_session.commit()
        db_session.refresh(turf_booking)
        bookings.append(turf_booking)

    # index 4: data for test extend booking
    with TestSessionLocal() as db_session:
        turf_booking = TurfBooking(
            customer_id=str(create_customer[0].id),
            turf_id=str(turf.id),
            reservation_date=datetime.strptime("2025-04-11", "%Y-%m-%d"),
            start_time=datetime.strptime("2025-04-11 13:00:00", "%Y-%m-%d %H:%M:%S"),
            end_time=datetime.strptime("2025-04-11 18:00:00", "%Y-%m-%d %H:%M:%S"),
            booking_status="confirm",
            payment_status="unpaid",
            total_amount=1200,
        )

        db_session.add(turf_booking)
        db_session.commit()
        db_session.refresh(turf_booking)
        bookings.append(turf_booking)

    # index 5: another customer's booking to check conflict booking
    with TestSessionLocal() as db_session:
        turf_booking = TurfBooking(
            customer_id=str(create_customer[2].id),
            turf_id=str(turf.id),
            reservation_date=datetime.strptime("2025-04-11", "%Y-%m-%d"),
            start_time=datetime.strptime("2025-04-11 19:00:00", "%Y-%m-%d %H:%M:%S"),
            end_time=datetime.strptime("2025-04-11 20:00:00", "%Y-%m-%d %H:%M:%S"),
            booking_status="confirm",
            payment_status="unpaid",
            total_amount=1200,
        )

        db_session.add(turf_booking)
        db_session.commit()
        db_session.refresh(turf_booking)
        bookings.append(turf_booking)

    return bookings

@pytest.fixture(scope="module")
def game():
    """ This fixture add game into database."""

    with TestSessionLocal() as db_session:
        game_exist = db_session.query(Game).filter(Game.game_name=="table tennis").first()

        if not game_exist:
            game_data = Game(
                game_name = "table tennis",
                is_active = True
            )

            db_session.add(game_data)
            db_session.commit()
            db_session.refresh(game_data)
            return game_data

        return game_exist
