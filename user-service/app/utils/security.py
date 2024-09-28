from datetime import datetime, timedelta
from typing import Any
from passlib.context import CryptContext
from jose import jwt
from app.settings import SECRET_KEY

ALGORITHM = "HS256"



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)




def get_password_hash(password: str)->str:
    return pwd_context.hash(password)



def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt