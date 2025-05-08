from fastapi_mail import ConnectionConfig
import os
from dotenv import load_dotenv
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME"),
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD"),
    MAIL_FROM = os.environ.get("MAIL_FROM"),
    MAIL_PORT = int(os.environ.get("MAIL_PORT")),
    MAIL_SERVER = os.environ.get("MAIL_SERVER"),
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
