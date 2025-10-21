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
    id: str
    project_id: str
    email: str
    class Role(BaseModel):
        id: str
        name: str
    role: Role
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
        email = payload.get("sub")
        if email is None:
            return None
        user = User(
            id=payload.get("user_id"),
            project_id=payload.get("project_id"),
            email=email,
            role=payload.get("role"),
            permissions=payload.get("permissions", [])
        )
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return user
