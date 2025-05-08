from datetime import datetime, timedelta

valid_turf_booking_payload = {
  "turf_id": "",
  "reservation_date": "2025-04-25",
  "start_time": "2025-04-25 13:00:00",
  "end_time": "2025-04-25 18:00:00"
}

turf_booking_payload_invalid_turf_id = {
  "turf_id": "bda7dc28-0fa9-45b7-9e1c-be0dd3e454b5",
  "reservation_date": "2025-04-25",
  "start_time": "2025-04-25 13:00:00",
  "end_time": "2025-04-25 18:00:00"
}

turf_booking_payload_with_past_reservation_date = {
  "turf_id": "",
  "reservation_date": "2024-04-10",
  "start_time": "2025-04-10 13:00:00",
  "end_time": "2025-04-10 18:00:00"
}

turf_booking_payload_with_date_more_than_30_days = {
  "turf_id": "",
  "reservation_date": "2025-07-10",
  "start_time": "2025-07-10 13:00:00",
  "end_time": "2025-07-10 18:00:00"
}

turf_booking_payload_with_start_time_not_in_format = {
  "turf_id": "",
  "reservation_date": "2025-04-25",
  "start_time": "2025-04-25 13:10:00",
  "end_time": "2025-04-25 18:00:00"
}

turf_booking_payload_with_past_start_time = {
  "turf_id": "",
  "reservation_date": "2025-04-25",
  "start_time": "2024-04-10 13:10:00",
  "end_time": "2025-04-25 18:00:00"
}

turf_booking_payload_with_next_day_start_time = {
  "turf_id": "",
  "reservation_date": "2025-04-25",
  "start_time": "2025-04-26 13:00:00",
  "end_time": "2025-04-2518:00:00"
}

turf_booking_payload_with_wrong_end_time = {
  "turf_id": "",
  "reservation_date": "2025-04-25",
  "start_time": "2025-04-25 16:00:00",
  "end_time": "2025-04-10 14:00:00"
}

turf_booking_payload_with_invalid_end_time_format = {
  "turf_id": "",
  "reservation_date": "2025-04-25",
  "start_time": "2025-04-25 12:00:00",
  "end_time": "2025-04-25 14:20:00"
}


turf_booking_payload_with_invalid_end_time = {
  "turf_id": "",
  "reservation_date": "2025-04-25",
  "start_time": "2025-04-25 12:00:00",
  "end_time": "2025-04-27 14:00:00"
}

turf_booking_payload_with_less_than_hour_slot = {
  "turf_id": "",
  "reservation_date": "2025-04-25",
  "start_time": "2025-04-25 13:00:00",
  "end_time": "2025-04-25 13:30:00"
}

turf_booking_payload_with_already_booked_slot = {
    "turf_id": "",
    "reservation_date": "2025-04-25",
    "start_time": "2025-04-25 13:00:00",
    "end_time": "2025-04-25 18:00:00"
}

update_booking_valid_payload = {
  "booking_id": "",
  "reservation_date": "2025-04-20",
  "start_time": "2025-04-20 15:30",
  "end_time": "2025-04-20 18:30"
}

update_booking_within_hour = {
  "booking_id": "",
  "reservation_date": "2025-04-27",
  "start_time": "2025-04-27 14:30",
  "end_time": "2025-04-27 18:30"
}

extend_booking_valid_payload = {
  "booking_id": "",
  "reservation_date": "2025-04-25",
  "end_time": "2025-04-25 18:30:00"
}

extend_booking_past_booking_date_payload = {
  "booking_id": "",
  "reservation_date": "2024-04-14",
  "end_time": "2025-04-25 19:30:00"
}


extend_booking_lesser_end_time_than_actual = {
  "booking_id": "",
  "reservation_date": "2025-04-25",
  "end_time": "2025-04-25 17:00:00"
}

extend_booking_invalid_end_time_date = {
  "booking_id": "",
  "reservation_date": "2025-04-25",
  "end_time": "2025-04-24 17:00:00"
}

extend_booking_with_conflict = {
  "booking_id": "",
  "reservation_date": "2025-04-25",
  "end_time": "2025-04-25 19:30:00"
}

feedback_valid_payload = {
  "turf_booking_id": "",
  "feedback": "Good turf and excellent staff",
  "rating": 4
}


feedback_invalid_payload = {
  "turf_booking_id": "",
  "feedback": "Good @#@D crfr312sxturf and excellent staff",
  "rating": 4
}

feedback_invalid_rating = {
  "turf_booking_id": "",
  "feedback": "Good staff",
  "rating": -1
}