from typing import Optional
from app.database import db
from app.model.user import UserModel
from app.dto.user.user_create_dto import UserCreate
from app.model.role import RoleModel
import uuid
import bcrypt
from app.repository.roles_repository import get_role_by_id, get_default_role

users_collection = db["users"]
users_collection.create_index("email", unique=True) # TODO Fazer isso direto no mongo

def get_user_by_id(user_id: str) -> Optional[UserModel]:
    user_data = users_collection.find_one({"_id": user_id})
    if user_data:
        return UserModel(**user_data)
    return None

def list_all_users() -> list[UserModel]:
    users_cursor = users_collection.find()
    return [UserModel(**user) for user in users_cursor]

def create_user(user: UserCreate, requesting_role_permissions: list[str]) -> Optional[UserModel]:
    role = get_role_by_id(user.role_id, requesting_role_permissions) if user.role_id else get_default_role()
    if role is None:
        raise ValueError("Invalid role ID" if user.role_id else "Default role not found")

    user_dump = user.model_dump()
    user_dump.pop("password")
    user_model = UserModel(
        _id=str(uuid.uuid4()),
        **user_dump,
        role=role,
        password=bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()),
    )
    result = users_collection.insert_one(user_model.model_dump(by_alias=True))
    if result.inserted_id:
        return user_model
    return None

def update_user(user_id: str, update_data: UserModel) -> Optional[UserModel]:
    user_dict = update_data.model_dump(exclude_unset=True)
    result = users_collection.update_one({"id": user_id}, {"$set": user_dict})
    if result.modified_count == 0:
        return None
    updated_user = users_collection.find_one({"id": user_id})
    if updated_user:
        return UserModel(**updated_user)
    return None


def update_users_with_role(role_id: str, updated_role: RoleModel) -> int:
    result = users_collection.update_many(
        {"role.id": role_id},
        {"$set": {"role": updated_role.dict()}}
    )
    return result.modified_count

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
    if user and bcrypt.checkpw(password.encode("utf-8"), user.password):
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

def get_users_by_role(role_id: str) -> list[UserModel]:
    users_data = users_collection.find({"role.id": role_id})
    return [UserModel(**user) for user in users_data]

def add_review_to_user(user_id: str, project_id: str, exhibition_id: str, comment: str):
    users_collection = db["users"]
    users_collection.update_one(
        {"_id": user_id},
        {"$push": {
            "reviews": {
                "project_id": project_id,
                "exhibition_id": exhibition_id,
                "comment": comment
            }
        }}
    )


def remove_review_from_user(user_id: str, project_id: str):
    users_collection = db["users"]
    users_collection.update_one(
        {"_id": user_id},
        {"$pull": {"reviews": {"project_id": project_id}}}
    )