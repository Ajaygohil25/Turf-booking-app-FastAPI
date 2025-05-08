from functools import wraps
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from core.constant import NOT_ALLOWED

load_dotenv()
SECRET_KEY = os.environ.get("HASH_KEY")
ALGORITHM = os.environ.get("HASH_ALGO")

def pre_authorize(authorized_roles: list = []):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")

            if current_user.role not in authorized_roles:
                raise HTTPException(status_code=401, detail=NOT_ALLOWED)

            return await func(*args, **kwargs)
        return wrapper
    return decorator
