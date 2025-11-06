from typing import Optional, List
import os

from fastapi import UploadFile

from app.bucket import upload_image
from app.database import db
from app.model.user import UserModel
from app.dto.user.user_create_dto import UserCreate
from app.model.role import RoleModel
import uuid
import bcrypt
from app.repository.roles_repository import get_role_by_id, get_default_role
from app.repository import project_repository, review_repository
from app.service.sendEmail import send_login_token_email
from app.routes.security import create_access_token

users_collection = db["users"]
users_collection.create_index("email", unique=True) # TODO Fazer isso direto no mongo

def get_user_by_id(user_id: str) -> Optional[UserModel]:
    user_data = users_collection.find_one({"_id": user_id})
    if user_data:
        return UserModel(**user_data)
    return None

def list_all_users(name: Optional[str] = None, role_id: Optional[str] = None) -> list[UserModel]:
    query = {"deactivation_date": None}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if role_id:
        query["role._id"] = role_id
    users_cursor = users_collection.find(query)
    return [UserModel(**user) for user in users_cursor]

async def create_user(
    user: UserCreate, 
    requesting_role_permissions: list[str], 
    profile_picture: Optional[UploadFile]
) -> Optional[UserModel]:
    """
    Create a new user in the database and send welcome email.
    If email sending fails, the user is automatically deleted (rollback).
    """

    role = get_role_by_id(user.role_id, requesting_role_permissions) if user.role_id else get_default_role()
    if role is None:
        raise ValueError("Invalid role ID" if user.role_id else "Default role not found")

    user_dump = user.model_dump()
    user_dump.pop("password")
    user_id = str(uuid.uuid4())
    user_model = UserModel(
        _id=user_id,
        **user_dump,
        role=role,
        password=bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()),
        verified=False
    )

    if profile_picture:
        url = await upload_image(profile_picture, folder="/users")
        user_model.profile_picture = url

    result = users_collection.insert_one(user_model.model_dump(by_alias=True))
    print("insert")
    if not result.inserted_id:
        print("not insert")
        return None

    created_user = user_model

    # # Send welcome email
    # try:
    #     print("try")
    #     # Verify frontend URL is configured
    #     frontend_url = os.getenv("EXPO_FRONT_URL", "")
    #     if not frontend_url:
    #         print("no frontend url")
    #         raise RuntimeError("EXPO_FRONT_URL not configured")
    #
    #     # Generate the token
    #     token_data = create_access_token(data={
    #         "sub": created_user.email,
    #         "user_id": created_user.id,
    #         "project_id": created_user.project.id if created_user.project else None,
    #         "scope": "",
    #         "permissions": created_user.role.permissions,
    #         "role": {"id": created_user.role.id, "name": created_user.role.name},
    #         "verified": False
    #     })
    #
    #     # Prepare the token URL
    #     frontend_url = frontend_url.rstrip('/')
    #     token_url = f"{frontend_url}?token={token_data.access_token}"
    #     user_name = created_user.name if created_user.name else "Olá, visitante!"
    #
    #     # Send email
    #     print("send")
    #     send_login_token_email(created_user.email, user_name, token_url)
    #     print("sent")
    # except Exception as email_error:
    #     # Rollback: delete the user if email fails
    #     try:
    #         print("rollback email")
    #         delete_user(created_user.id)
    #         raise RuntimeError(f"Error sending email user: {str(email_error)}")
    #     except Exception:
    #         pass
    #     raise RuntimeError(f"Erro ao enviar email: {str(email_error)}")
    # print("return")
    return created_user


async def update_user(user_id: str, update_data: UserModel, profile_picture: Optional[UploadFile]) -> Optional[UserModel]:
    user_data = users_collection.find_one({"_id": user_id})
    if user_data is None:
        raise ValueError("User not found")
    if profile_picture:
        url = await upload_image(profile_picture, user_data.get("profile_picture"), folder="/users")
        update_data.profile_picture = url

    user_dict = update_data.model_dump(exclude_unset=True)
    users_collection.update_one({"_id": user_id}, {"$set": user_dict})
    project_update = project_repository.update_project_with_user(user_id, update_data)
    review_update = review_repository.update_reviews_with_user(user_id, update_data)
    return UserModel(**update_data.model_dump(by_alias=True))


def update_users_with_role(role_id: str, updated_role: RoleModel) -> int:
    result = users_collection.update_many(
        {"role.id": role_id},
        {"$set": {"role": updated_role.model_dump(by_alias=True)}}
    )
    return result.modified_count

def delete_user(user_id: str) -> bool:
    result = users_collection.delete_one({"_id": user_id})
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

def is_role_in_use(role_id: str) -> bool:
    user = users_collection.find_one({"role.id": role_id, "deactivation_date": {"$exists": False}})
    return user is not None
  
def get_users_by_role(role_id: str) -> list[UserModel]:
    users_data = users_collection.find({"role.id": role_id})
    return [UserModel(**user) for user in users_data]


def favorite_project(user_id: str, project_id: str):
    user = users_collection.find_one({"_id": user_id})
    if not user or "favorited_projects" not in user:
        raise Exception("User not updated")

    favorited_projects = user.get("favorited_projects", [])
    if project_id in favorited_projects:
        # Remove project_id
        new_projects = favorited_projects.copy()
        new_projects.remove(project_id)
        action_result = False
    else:
        # Add project_id
        new_projects = favorited_projects + [project_id]
        action_result = True

    result = users_collection.update_one(
        {"_id": user_id},
        {"$set": {"favorited_projects": new_projects}}
    )
    if result.modified_count == 0:
        raise Exception("User not updated")
    return action_result

async def upload_profile_picture(user_id: Optional[str], file: UploadFile) -> str:
    if user_id:
        user = users_collection.find_one({"_id": user_id})
        if not user:
            raise ValueError("User not found")

    url = await upload_image(file, user.get("profile_picture") if user_id else None, folder="/users")
    return url

def add_review_to_user(user_id: str, review_id: str, project_id: str, exhibition_id: str, comment: Optional[str], criteria: Optional[List[dict]] = None) -> None:
    review_resume = {
        "_id": review_id,
        "project_id": project_id,
        "exhibition_id": exhibition_id,
        "comment": comment
    }
    if criteria:
        review_resume["criteria"] = criteria

    # Upsert logic: update if exists, else push
    result = users_collection.update_one(
        {
            "_id": user_id,
            "reviews": {
                "$elemMatch": {
                    "_id": review_id,
                    "project_id": project_id,
                    "exhibition_id": exhibition_id
                }
            }
        },
        {
            "$set": {
                "reviews.$.comment": comment,
                "reviews.$.criteria": criteria if criteria else []
            }
        }
    )
    if result.modified_count == 0:
        # If not found, push new review
        result = users_collection.update_one(
            {"_id": user_id},
            {"$push": {"reviews": review_resume}}
        )
        if result.modified_count == 0:
            raise ValueError("User not found or not updated")


def add_project_to_user(user_id: str, project_resume: UserModel.ProjectResume) -> Optional[UserModel]:
    result = users_collection.update_one({"_id": user_id},{"$set": {"project": project_resume.model_dump(by_alias=True)}})
    if result.matched_count == 0:
        raise ValueError("User not found")
