from fastapi import APIRouter
from app.service import user as user_service
from typing import List
from app.model.user import UserModel, User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("", response_model=List[UserModel])
async def list_users():
    return user_service.list_all_users()

@router.get("/{user_id}", response_model=UserModel)
async def get_user(user_id: int):
    return user_service.get_user_by_id(user_id)

@router.post("", response_model=UserModel)
async def create_user(user: User):
    return user_service.create_user(user)

@router.put("/{user_id}", response_model=UserModel)
async def update_user(user_id: int, user: User):
    return user_service.update_user(user_id, user)

@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    return user_service.delete_user(user_id)