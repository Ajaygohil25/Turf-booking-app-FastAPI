from passlib.context import CryptContext

class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def encrypt(password: str):
        return Hash.pwd_context.hash(password)
    @staticmethod
    def verify_password(input_password: str, hashed_password: str):
        return Hash.pwd_context.verify(input_password, hashed_password)