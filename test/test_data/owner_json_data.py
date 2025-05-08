import uuid
from copy import deepcopy

from test.test_data.user_json_data import invalid_role_id

address_valid_payload = {
  "street_address": "Power Play Cricket Turf",
  "area": "Near Ambapur Petrol Pump, Koba-Adalaj Highway To Ambapur",
  "city_id": 262,
  "is_active" : True,
  "lat": 23.167000,
  "long": 72.586998,
  "turf_owner_id": ""
}

street_address_invalid_payload = deepcopy(address_valid_payload)
street_address_invalid_payload["street_address"] = "12###D#d Play Cricket Turf"

area_invalid_payload = deepcopy(address_valid_payload)
area_invalid_payload["area"] = "#area!"

city_invalid_payload = deepcopy(address_valid_payload)
city_invalid_payload["city_id"] = 1000

turf_form_data = {
        "turf_name": "power play",
        "description": "Experience the best turf cricket in Ahmedabad",
        "amenities": "cafe,wifi",
        "booking_price": "1400",
        "is_active" : False,
        "is_verified": False,
        "revenue_mode": "percentage",
        "amount": "15",
        "address_id": "",
        "game_id": "83bfc6b8-d100-4885-b13e-d619f76d18a9",
        "turf_owner_id": ""
    }

invalid_turf_name = deepcopy(turf_form_data)
invalid_turf_name["turf_name"] = "Sky ## Rocket"

turf_already_exist = deepcopy(turf_form_data)
turf_already_exist["turf_name"] = "power play"

invalid_description = deepcopy(turf_form_data)
invalid_description["turf_name"] = "xyz"
invalid_description["description"] = "#####DEDCECC>>>Dcs....csd"

invalid_amenities = deepcopy(turf_form_data)
invalid_amenities["turf_name"] = "asdad"
invalid_amenities["amenities"] =  ['[washroom , c##fe]']

invalid_booking_price = deepcopy(turf_form_data)
invalid_booking_price["turf_name"] = "avcsd"
invalid_booking_price["booking_price"] = 0000

invalid_game_id = deepcopy(turf_form_data)
invalid_game_id["turf_name"] = "acv"
invalid_game_id["game_id"]= str(uuid.uuid4())

turf_api_data = {
        "turf_name": "Sky Rocket",
        "description": "Experience the best turf cricket in Ahmedabad",
        "amenities": "cafe,wifi",
        "booking_price": "1400",
        "is_active" : True,
        "is_verified": True,
        "address_id": "",
        "game_id": "",
        "turf_owner_id": ""
    }


update_turf_payload = {
    "turf_name" : "Sky turf booking",
    "description": "No description just come and play rest is feedback",
    "amenities": ["cafe and chill, rest area"],
    "booking_price": 1999
}

invalid_turf_payload = {
    "turf_name" : "Sky ##@E@ turffiy",
    "description": "No description just come and play rest is feedback",
    "amenities": ["cafe and chill, rest area"],
    "booking_price": -1232
}

discount_payload = {
    "turf_id" : "",
    "discount_amount" : 200,
    "is_active" : True
}


turf_manager_payload = {
          "name": "vikas patel",
          "contact_no": 8066121299,
          "email": "vikas@gmail.com",
          "password": "Vikas@123456",
          "role_id": "0b1a5212-bf3f-49fb-8e5e-57c6908dbbc4",
          "city_id": 262,
          "is_active": True,
          "is_verified": True,
          "lat": 0,
          "long": 0,
          "turf_id" : ""
        }
