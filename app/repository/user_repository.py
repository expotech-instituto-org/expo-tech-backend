from typing import Optional
from app.database import db
from app.model.user import UserModel
from app.dto.user.user_login_dto import UserLogin
import uuid
from passlib.hash import bcrypt

users_collection = db["users"]

def get_user_by_id(user_id: str) -> Optional[UserModel]:
    user_data = users_collection.find_one({"id": user_id})
    if user_data:
        return UserModel(**user_data)
    return None

def list_all_users() -> list[UserModel]:
    users_cursor = users_collection.find()
    return [UserModel(**user) for user in users_cursor]

def create_user(user: UserLogin) -> Optional[UserModel]:
    user_dict = user.model_dump()
    user_dict['password'] = bcrypt.hash(user_dict['password'])
    user_dict["_id"] = str(uuid.uuid4())
    result = users_collection.insert_one(user_dict)
    if result.inserted_id:
        return UserModel(**user_dict)
    return None

def update_user(user_id: str, update_data: UserModel) -> Optional[UserModel]:
    user_dict = update_data.model_dump(exclude_unset=True)
    result = users_collection.update_one({"id": user_id}, {"$set": user_dict})
    if result.modified_count > 0:
        updated_user = users_collection.find_one({"id": user_id})
        if updated_user:
            return UserModel(**updated_user)
    return None

def delete_user(user_id: str) -> bool:
    result = users_collection.delete_one({"id": user_id})
    return result.deleted_count > 0

def get_user_by_email(email: str):
    user_data = users_collection.find_one({"email": email})
    if user_data:
        return UserModel(**user_data)
    return None

def authenticate_user(email: str, password: str) -> UserModel | None:
    user = get_user_by_email(email)
    if user and bcrypt.verify(password, user.password):
        return user
    return None


def set_project_id_on_users(user_ids: list[str], project_id: str) -> None:
    if not user_ids:
        return
    users_collection.update_many(
        {"_id": {"$in": user_ids}},
        {"$set": {"project_id": project_id}}
    )


def set_project(project_id: str, project_resume: dict) -> None:
    users_collection.update_many(
        {"project._id": project_id},
        {"$set": {"project": project_resume}}
    )


def set_project_resume_on_users_by_ids(user_ids: list[str], project_resume: dict) -> None:
    if not user_ids:
        return
    users_collection.update_many(
        {"_id": {"$in": user_ids}},
        {"$set": {"project": project_resume}}
    )


def unset_project_by_project_id(project_id: str) -> None:
    users_collection.update_many(
        {"project._id": project_id},
        {"$unset": {"project": ""}}
    )