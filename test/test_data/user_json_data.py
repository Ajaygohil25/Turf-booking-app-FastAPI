import uuid
from copy import deepcopy

user_data_payload = {
          "name": "disha patel",
          "contact_no": 9066121299,
          "email": "dishaa@gmail.com",
          "password": "Disha@123456",
          "role_id": "2869f01f-6b13-474f-ae2b-c4925d627f50",
          "city_id": 262,
          "is_active": True,
          "is_verified": True,
          "lat": 23.063745,
          "long": 72.560005
        }

invalid_mail_user_payload = deepcopy(user_data_payload)
invalid_mail_user_payload["email"] = "asdaasd.cac"

invalid_password_user_payload = deepcopy(user_data_payload)
invalid_password_user_payload["email"] = "isha@gmail.com"
invalid_password_user_payload["password"] = "hyeyyyee"

invalid_contact_no_payload = deepcopy(user_data_payload)
invalid_contact_no_payload["email"] = "isha@gmail.com"
invalid_contact_no_payload["contact_no"] = -66121299

invalid_role_id = deepcopy(user_data_payload)
invalid_role_id["email"] = "isha@gmail.com"
invalid_role_id["role_id"] = str(uuid.uuid4())

invalid_city_id = deepcopy(user_data_payload)
invalid_city_id["email"] = "isha@gmail.com"
invalid_city_id["city_id"] = 999




user_login_payload = {
    "username": "dishaa@gmail.com",
    "password": "Disha@123456"
}
invalid_password_payload = {
    "username": "dishaa@gmail.com",
    "password": "Disha@45678"
}

invalid_email_payload = {
    "username": "disha@gmail.com",
    "password": "Disha@123456"
}


update_user_payload = {
    "name" : "patel disha",
    "contact_no": 9898980000
}
invalid_update_user_payload = {
    "name" : "dish",
    "contact_no": -1231
}
patch_update_user_payload = {
    "name" : "dish"
}

forget_password_payload = {
  "email": "dishaa@gmail.com"
}

reset_password_payload = {
  "current_password": "Disha@123456",
  "new_password": "Disha@12345",
  "confirm_password": "Disha@12345"
}

invalid_reset_password_payload = {
  "current_password": "Disha@9909",
  "new_password": "Disha@12345",
  "confirm_password": "Disha@12345"
}
invalid_confirm_password = {
    "current_password": "Disha@123456",
    "new_password": "Disha@12345",
    "confirm_password": "Disha@12346"
}

admin_credentials = {
    "username" : "admin@test.com",
    "password" : "Admin@test123"
}

owner_credentials = {
    "username" : "vishal@gmail.com",
    "password" : "Vishal@1234"
}

admin_token = {
    "email" : "admin@test.com",
    "role_id" : "86156e77-0bf2-4e7b-a8bf-b93b60245f12"
}

user_data_api_payload = {
          "name": "manav patel",
          "contact_no": 8866121299,
          "email": "manav@gmail.com",
          "password": "Manav@123456",
          "role_id": "2869f01f-6b13-474f-ae2b-c4925d627f50",
          "city_id": 262,
          "is_active": True,
          "is_verified": True,
          "lat": 23.063745,
          "long": 72.560005
}