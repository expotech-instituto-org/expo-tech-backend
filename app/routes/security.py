from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

class User(BaseModel):
    username: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict) -> Token:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = User(username=username, role="none")
    except InvalidTokenError:
        raise credentials_exception
    return user
