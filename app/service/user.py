from typing import Optional
from app.database import mongo_db
from app.model.user import User

users_collection = mongo_db["users"]

def get_user_by_id(user_id: int) -> Optional[User]:
    user_data = users_collection.find_one({"id": user_id})
    if user_data:
        return User(**user_data)
    return None

def list_all_users() -> list[User]:
    users_cursor = users_collection.find()
    return [User(**user) for user in users_cursor]
