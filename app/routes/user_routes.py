from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError

from app.repository import user_repository
from typing import List, Annotated, Optional
from app.model.user import UserModel
from app.routes.security import get_current_user, create_access_token, User, Token
from app.dto.user.user_create_dto import UserCreate

import app.constants as c

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("", response_model=List[UserModel])
async def list_users(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_USER not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return user_repository.list_all_users()
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.get("/{user_id}", response_model=UserModel)
async def get_user(user_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_USER not in current_user.permissions and user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        user = user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return user
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.post("", response_model=UserModel)
async def create_user(
    user: UserCreate,
    current_user: Annotated[User | None, Depends(get_current_user)] = None
):# <--- Carinha triste ou brava?
    try:
        permissions = current_user.permissions if current_user else None
        return user_repository.create_user(user, permissions)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    except DuplicateKeyError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, "Duplicate email")
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.put("/{user_id}", response_model=UserModel)
async def update_user(user_id: str, user: UserModel, current_user: Annotated[User, Depends(get_current_user)]):
    if c.PERMISSION_UPDATE_USER not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return user_repository.update_user(user_id, user)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.patch("/{user_id}/{project_id}")
async def favorite_project(project_id: str, user_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_USER not in current_user.permissions and user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return user_repository.favorite_project(user_id, project_id)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))




@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if c.PERMISSION_DELETE_USER not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return user_repository.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.get("/me/", response_model=Optional[User])
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    #TODO: Remover depois
    return current_user

@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = user_repository.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        token = create_access_token(data={
            "sub": user.email,
            "user_id": user.id,
            "project_id": user.project.id if user.project else None,
            "scope": " ".join(form_data.scopes),
            "permissions": user.role.permissions,
            "role": {"id": user.role.id, "name": user.role.name}
        })
        return token
