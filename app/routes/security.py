from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Optional
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

class User(BaseModel):
    username: str
    permissions: list[str]

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict) -> Token:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")

async def get_current_user(token: Annotated[Optional[str], Depends(oauth2_scheme)] = None) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        permissions = payload.get("permissions", [])
        if username is None:
            return None
        user = User(username=username, permissions=permissions)
    except InvalidTokenError:
        return None
    return user
