import os
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "swiftgov-secure-dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "120"))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def is_hashed(password: str) -> bool:
    return isinstance(password, str) and password.startswith("$2")


def verify_password(plain_password: str, stored_password: str) -> bool:
    if not stored_password:
        return False
    if is_hashed(stored_password):
        return pwd_context.verify(plain_password, stored_password)
    return plain_password == stored_password


def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return {}
