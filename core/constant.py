import os

from dotenv import load_dotenv

MESSAGE = "Message"
WELCOME_MSG = "Welcome! Turf booking mode is ON"
INCORRECT_CREDENTIALS = "Email id or password is incorrect, try again"

LOGIN_SUCCESS = "Login Successful"
LOGIN_FAILED = "Login Failed"
OTP_MESSAGE = "OTP is : {0}"
LOGIN_CONTENT = "Thank you for logging in our system !"
LOGIN_SUB = "This is a mail for Log in system"
INVALID_PASSWORD = ("Password must be at least 8 characters long, include at least one uppercase letter, "
                    "one lowercase letter, one number, and one special character.")
INVALID_EMAIL = ("An email address must contain exactly one `@` symbol, separating the local part (user name) from the domain part (email provider or organization domain). "
                 "It should not have spaces, and special characters like periods, underscores, and hyphens are allowed but with certain restrictions.")

INVALID_CONTACT = "Invalid contact number. Please enter a 10-digit Indian contact number starting with either 6, 7, 8, or 9."
INVALID_ROLE_ID = "Invalid role ID. Please enter a valid role ID."
INVALID_CITY_ID = "Invalid city ID. Please enter a valid city ID."
INVALID_TURF_ID = "Invalid Turf ID. Please enter a valid Turf ID."

INVALID_TURF_OWNER_ID = "Invalid turf owner ID. Please enter a valid turf owner ID."
INVALID_STRING_INPUT = "Invalid string input, should not contain any special character. Please enter a valid string input."
INVALID_BOOKING_PRICE = "Invalid booking price. Please enter a valid booking price."
INVALID_AMOUNT = "Invalid amount. Please enter a valid amount."
MINIMUM_MEDIA = "At least 5 images are required or At least 1 video is required."
INVALID_FILE_TYPE = "Invalid file format"
INVALID_ADDRESS_ID = "Invalid address ID. Please enter a valid address ID."
INVALID_ADDRESS_SELECTION = "Invalid address selection! you are not allowed to select this address"
INVALID_CREDENTIALS = "Could not validate credentials, Sing-in again ! "
INVALID_USER = "User is not active or not verified, please contact the administrator"
INACTIVE_TURF = "Turf is not active or not verified, please contact the administrator"
INVALID_FORMAT = "Invalid format of email or password"
DETAILS = "Details"
NO_DATA_TO_UPDATE = "There is no data to update"
INVALID_IMAGE_FORMAT = "Invalid image type, only jpg, png and jpeg are allowed!"
ERROR_MESSAGE = "Something went wrong, please try again later ! {0}"
NOT_ALLOWED = "You are not allowed to perform this action"
TURF_NAME_ALREADY_EXISTS = "Turf name on this address already exist, Try with different name."
IMAGE_DELETED = "Image deleted successfully !"
INVALID_IMAGE_ID = "Invalid image ID or no data available for image ID"
IMAGE_UPDATED = "Image updated successfully !"
USER_ALREADY_EXISTS = "User with {0} already exists"
USER_CREATED = "Account created successfully !"
USER_DELETED = "User deleted successfully !"
USER_UPDATED = "User updated successfully !"
USER_NOT_FOUND = "User not found"
USER_NOT_REGISTERED = "User with this mail id not registered"
NOT_AUTHORIZED = "Not authorized to perform this action, please Sing-in again !"
USER_ALREADY_LOGGED_IN = "User already logged in"
USER_NOT_LOGGED_IN = "User not logged in"
SING_IN = "sign-in app"

TOKEN_SUB = "sub"
TOKEN_USER_ID = "user_id"
TOKEN_TYPE = "bearer"
PASSWORD_DOES_NOT_MATCH = "New password and confirm password do not match! Try again"
PASSWORD_CHANGED = "Password changed successfully !"
PASSWORD_SHOULD_NOT_BE_SAME = "New password and old password should not be same! Try again"
EXPIRES = "exp"
IS_REFRESH = "is_refresh"

FORGOT_PASSWORD_SUB = "Reset your password"
EMAIL_SENT = "Email has been sent for password reset"
WWW_AUTHENTICATE = "WWW-Authenticate"
NEW_PASSWORD_NOT_SAME = "New password and confirm password do not match! Try again."
LOGOUT_SUCCESS = "Logout successful"
NEXT_PAGE = "next_page"
PREV_PAGE = "previous_page"
INVALID_FEEDBACK_INPUT = "Invalid feedback input data !"

INVALID_ACCESS_TOKEN = "Invalid access token !"
VALID_ACCESS_TOKEN = "Token is valid"
REFRESH_TOKEN_INVALID = "Refresh token is invalid, Please sing-in in the application."
REFRESH_TOKEN_REQUIRED = "Refresh token is required. Please provide a valid refresh token"
ACCESS_TOKEN_REQUIRED = "Access token is required. Please provide a valid access token, not refresh token"
TOKEN_EXPIRED = "This token has expired"
ID = "id"
PROMPT = "prompt"
CONSENT = "consent"
ACCESS_TYPE = "access_type"
OFFLINE = "offline"
INVALID_NAME = "Name can only contain alphabets"
INVALID_CURRENT_PASSWORD = "Current password is incorrect"

ROLE_ADDED = "Role added successfully !"
ROLE_TYPE = "Role"
GAME_ADDED_SUCCESS = "Game added successfully !"
INVALID_GAME_ID = "Invalid game ID or no data available for game ID"
GAME_NAME_UPDATED = "Game name updated successfully !"
GAME_ACTIVATE_MESSAGE = "Game activation data updated successfully !"
GAME_ALREADY_EXISTS = "Game already exists"
TURF_OWNER_ACTIVATION_UPDATED = "Turf owner activation and verification data updated successfully !"
TURF_ACTIVATION_UPDATED =  "Turf activation and verification data updated successfully !"
TURF_DEACTIVATED = "Turf deactivate successfully !"
TURF_DISCOUNT_ADDED = "Turf discount added successfully !"
TURF_DISCOUNT_DEACTIVATED = "Turf discount deactivated successfully !"
TURF_OWNER_ALREADY_VERIFIED = "Turf owner already verified !"
TURF_ADDRESS_ADDED = "Turf address address added successfully !"
TURF_ADDED_SUCCESS = "Turf added successfully !"
TURF_DATA_UPDATED = "Turf data updated successfully !"
USER_DATA_UPDATED = "User data updated successfully !"
TURF_ALREADY_BOOKED = "Turf is already booked !"

INVALID_DISCOUNT_ID = "Invalid discount id !"
DISCOUNT_EXPIRED = "Discount has been expired!"
INVALID_DISCOUNT_AMOUNT = "Invalid discount amount must be greater than zero and minimum discount amount is 100 Rs."
INVALID_DATE_TIME_FORMAT = "Invalid date time format !"
INVALID_DATE = "Error: Reservation date cannot be in the past."
INVALID_END_TIME = "Error: End time must be on the same day as reservation date or the very next day (for overnight bookings)."
INVALID_START_TIME = "Error: Invalid start time ! must be a future date and time and must be same date as reservation date."
INVALID_SLOT_TIME = "Error: Slot time must be in 30-minute intervals (e.g., 10:00, 10:30, 11:00)."
PAST_TIME_ERROR = "Error: slot time cannot be in the past."
INVALID_END_TIME_OVERNIGHT = "Error: End time must be after start time or select valid date and time for booking !"
INVALID_BOOKING_TIME = "Error: Booking must be at least 1 hour long."
MAXIMUM_ADVANCE_DAYS_ERROR = "Error: You can only book up to 30 days in advance."
CUSTOMER_ROLE = "Customer"
OWNER_ROLE = "Owner"
MANAGER_ROLE = "Manager"
ADMIN_ROLE = "Admin"
TURF_DATA = "Available turf data"
TURF_BOOKED = "Turf booked successfully !"
TURF_SLOT_ALREADY_BOOKED = "Turf is already booked for the selected time slot."
BOOKING_NOT_FOUND = "Booking not found !"
UPDATE_NOT_ALLOWED = "Update not allowed"
NOT_ALLOWED_TO_UPDATE = "You are not authorize to update this booking !"
UPDATE_BEFORE_ONE_HOUR = "You are only not allowed to update booking within one hour of the time-span of actual booking"
TURF_UPDATE_SUCCESS = "Turf booking update successful"
NO_BOOKING_FOUND = "No booking found !"
STATUS_CONFIRM = "confirm"
STATUS_CANCELLED = "cancelled"
STATUS_RESERVED = "reserved"
PAYMENT_STATUS_UNPAID = "unpaid"
PAYMENT_STATUS_PAID = "paid"
END_TIME_UPDATE_NOT_ALLOWED = "End time update not allowed, new end time must be greater than previous time"
NOT_ALLOWED_TO_CANCEL = "You can only cancel booking before 5 hours of booking slot."
BOOKING_ACTION_NOT_ALLOWED = "You are not allowed to perform action on this booking as it is past booking !"
BOOKING_CANCELLED = "Turf booking cancelled successfully !"
BOOKINGS = "bookings"
TURF_MANAGER_ADDED = "Turf manager added successfully"
MANAGER_ACTIVATION_UPDATED = "Turf manager activation-deactivation updated successfully"
MANAGER_ACTION_NOT_ALLOWED = "Turf manager action not allowed ! You are not valid user to perform this action"
INVALID_DATES = "Start date cannot be after the end date"
NO_DATA_FOUND = "No data found !"
FIXED_REVENUE = "fixed"
PERCENTAGE_REVENUE = "percentage"
PAYMENT_SUCCESSFUL = "Payment successful !"
BOOKING_ALREADY_CANCELLED = "Booking already cancelled"
FEEDBACK_ADDED = "Feedback added successfully"
NO_TURF_FOUND = "No turfs found for this owner"
FEEDBACK_NOT_ALLOWED = "Feedback not allowed, you can only give the feedback on confirm booking."
INVALID_USER_ACTION = "Invalid user action ! This user has not a role of manager"
load_dotenv()
HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")

#URL
SOCIAL_AUTH_REDIRECT_URL= f"http://{HOST}:{PORT}/api/v1/user/callback"
FORGOT_PASSWORD_URL= "http://localhost:8000/api/v1/user/reset-forgot-password/?token={0}"
SING_IN_URL= f"http://{HOST}:{PORT}/api/v1/user/sign-in"
