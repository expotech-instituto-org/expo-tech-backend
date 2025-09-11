from typing import Optional
from app.database import db
from app.model.user import UserModel, User
import uuid

users_collection = db["users"]

def get_user_by_id(user_id: int) -> Optional[UserModel]:
    user_data = users_collection.find_one({"id": user_id})
    if user_data:
        return UserModel(**user_data)
    return None

def list_all_users() -> list[UserModel]:
    users_cursor = users_collection.find()
    return [UserModel(**user) for user in users_cursor]

def create_user(user: User) -> Optional[UserModel]:
    user_dict = user.model_dump()
    user_dict["_id"] = str(uuid.uuid4())
    result = users_collection.insert_one(user_dict)
    if result.inserted_id:
        return UserModel(_id = result.inserted_id, email=user.email)
    return None

def update_user(user_id: int, update_data: UserModel) -> Optional[UserModel]:
    user_dict = update_data.model_dump(exclude_unset=True)
    result = users_collection.update_one({"id": user_id}, {"$set": user_dict})
    if result.modified_count > 0:
        updated_user = users_collection.find_one({"id": user_id})
        if updated_user:
            return UserModel(**updated_user)
    return None

def delete_user(user_id: int) -> bool:
    result = users_collection.delete_one({"id": user_id})
    return result.deleted_count > 0
