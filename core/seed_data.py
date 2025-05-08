from sqlalchemy.orm import Session
from core.database import engine
from models.roles_model import Roles

admin_data_payload = {
          "name": "Ajay Gohil",
          "contact_no": 9066121299,
          "email": "ajay@gmail.com",
          "password": "Ajay@2525",
          "role_id": "3cd84328-4c6f-4b58-88a3-f45549b97f48",
          "city_id": 262,
          "is_active": True,
          "is_verified": True,
          "lat": 23.063745,
          "long": 72.560005
        }

def seed_data():
    with Session(engine) as session:
        existing_roles = session.query(Roles).all()
        if not existing_roles:
            roles_data = [
                Roles(role_name="Admin"),
                Roles(role_name="User"),
                Roles(role_name="Manager"),
                Roles(role_name="Owner"),
            ]
            session.add_all(roles_data)
            session.commit()
            print("Data inserted successfully.")
        else:
            print("Roles already exist in the database.")

