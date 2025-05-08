import copy
import uuid

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry.point import Point
from starlette.testclient import TestClient

from authentication.hashing import Hash
from core.database import TestSessionLocal, test_engine, Base, get_db
from core.seed_data import admin_data_payload
from main import app
from models.game_model import Game
from models.roles_model import Roles
from models.user_model import User
from test.test_data.user_json_data import user_data_payload


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=test_engine)

    with TestSessionLocal() as db_session:
        # If there is no roles then add it
        if not db_session.query(Roles).first():
            admin_role = Roles(id=uuid.uuid4(), role_name="Admin")
            customer_role = Roles(id=uuid.uuid4(), role_name="Customer")
            owner_role = Roles(id=uuid.uuid4(), role_name="Owner")
            manager_role = Roles(id=uuid.uuid4(), role_name="Manager")
            db_session.add_all([admin_role, customer_role, owner_role, manager_role])
            db_session.commit()

    with TestSessionLocal() as db_session:
        if not db_session.query(Game).first():
            cricket = Game(game_name="cricket", is_active=True)
            pickle = Game(game_name="pickle ball", is_active=True)
            db_session.add_all([cricket, pickle])
            db_session.commit()
    try:
        yield
    finally:
        tables_to_keep = {"state", "city", "roles", "game"}

        tables_to_drop = [
            table for table in Base.metadata.sorted_tables
            if table.name not in tables_to_keep
        ]

        # Drop all except state, city, and roles
        if tables_to_drop:
            Base.metadata.drop_all(bind=test_engine, tables=tables_to_drop)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def create_admin(test_db):
    """ This fixture create admin"""
    with TestSessionLocal() as db_session:
        role = db_session.query(Roles).filter_by(role_name="Admin").first()
        if not db_session.query(User).filter_by(email="admin@test.com").first():
            admin_data = copy.deepcopy(user_data_payload)
            admin_data["name"] = "ajay"
            admin_data["email"] = "admin@test.com"
            admin_data["password"] = Hash.encrypt("Admin@test123")
            admin_data["role_id"] = str(role.id)
            user_data = User(**admin_data)
            user_data.geom = from_shape(Point(admin_data["long"], admin_data["lat"]), srid=4326)
            db_session.add(user_data)
            db_session.commit()
            db_session.refresh(user_data)
            return user_data

@pytest.fixture(scope="module")
def create_turf_owner(test_db):
    """ This fixture create the turf owner in the database"""
    users = []

    with TestSessionLocal() as db_session:
        role = db_session.query(Roles).filter_by(role_name="Owner").first()
        if not db_session.query(User).filter_by(email="vishal@gmail.com").first():
            owner_data = copy.deepcopy(user_data_payload)
            owner_data["name"] = "vishal shah"
            owner_data["email"] = "vishal@gmail.com"
            owner_data["password"] = Hash.encrypt("Vishal@1234")
            owner_data["role_id"] = str(role.id)
            owner_data["is_active"] = True
            owner_data["is_verified"] = True
            user_data = User(**owner_data)
            user_data.geom = from_shape(Point(owner_data["long"], owner_data["lat"]), srid=4326)
            db_session.add(user_data)
            db_session.commit()
            db_session.refresh(user_data)
            users.append(user_data)

    with TestSessionLocal() as db_session:
        role = db_session.query(Roles).filter_by(role_name="Owner").first()
        if not db_session.query(User).filter_by(email="abhi@gmail.com").first():
            owner_data = copy.deepcopy(user_data_payload)
            owner_data["name"] = "abhi shah"
            owner_data["email"] = "abhi@gmail.com"
            owner_data["password"] = Hash.encrypt("abhi@1234")
            owner_data["role_id"] = str(role.id)
            owner_data["is_active"] = True
            owner_data["is_verified"] = True
            user_data = User(**owner_data)
            user_data.geom = from_shape(Point(owner_data["long"], owner_data["lat"]), srid=4326)
            db_session.add(user_data)
            db_session.commit()
            db_session.refresh(user_data)
            users.append(user_data)

    with TestSessionLocal() as db_session:
        role = db_session.query(Roles).filter_by(role_name="Owner").first()
        if not db_session.query(User).filter_by(email="darshanP@gmail.com").first():
            owner_data = copy.deepcopy(user_data_payload)
            owner_data["name"] = "darshan patel"
            owner_data["email"] = "darshanP@gmail.com"
            owner_data["password"] = Hash.encrypt("darshanP@1234")
            owner_data["role_id"] = str(role.id)
            owner_data["is_active"] = True
            owner_data["is_verified"] = True
            user_data = User(**owner_data)
            user_data.geom = from_shape(Point(owner_data["long"], owner_data["lat"]), srid=4326)
            db_session.add(user_data)
            db_session.commit()
            db_session.refresh(user_data)
            users.append(user_data)

    return users

@pytest.fixture(scope="module")
def create_customer(test_db):
    customers = []
    with TestSessionLocal() as db_session:
        role = db_session.query(Roles).filter_by(role_name="Customer").first()

        if not db_session.query(User).filter_by(email="dishaa@gmail.com").first():
            user_payload = copy.deepcopy(user_data_payload)
            user_payload["role_id"] = str(role.id)
            user_payload["password"] = Hash.encrypt(user_payload["password"])
            user_data = User(**user_payload)
            user_data.geom = from_shape(Point(user_data_payload["long"],
                                              user_data_payload["lat"]), srid=4326)
            db_session.add(user_data)
            db_session.commit()
            db_session.refresh(user_data)
            customers.append(user_data)

    with TestSessionLocal() as db_session:
        role = db_session.query(Roles).filter_by(role_name="Customer").first()

        if not db_session.query(User).filter_by(email="kamleshh@gmail.com").first():
            user_payload = copy.deepcopy(user_data_payload)
            user_payload["email"] = "kamleshh@gmail.com"
            user_payload["role_id"] = str(role.id)
            user_payload["password"] = Hash.encrypt("Kamlesh@1234")
            user_data = User(**user_payload)
            user_data.geom = from_shape(Point(user_data_payload["long"],
                                              user_data_payload["lat"]), srid=4326)
            db_session.add(user_data)
            db_session.commit()
            db_session.refresh(user_data)
            customers.append(user_data)

        with TestSessionLocal() as db_session:
            role = db_session.query(Roles).filter_by(role_name="Customer").first()

            if not db_session.query(User).filter_by(email="customer@gmail.com").first():
                user_payload = copy.deepcopy(user_data_payload)
                user_payload["email"] = "customer@gmail.com"
                user_payload["role_id"] = str(role.id)
                user_payload["password"] = Hash.encrypt("Customer@1234")
                user_data = User(**user_payload)
                user_data.geom = from_shape(Point(user_data_payload["long"],
                                                  user_data_payload["lat"]), srid=4326)
                db_session.add(user_data)
                db_session.commit()
                db_session.refresh(user_data)
                customers.append(user_data)

        return customers
