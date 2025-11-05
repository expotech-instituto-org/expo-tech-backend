from typing import Optional, Callable, Any
import logging
from datetime import datetime

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

logger = logging.getLogger(__name__)

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
    profile_picture: Optional[UploadFile],
    post_create_callback: Optional[Callable[[UserModel], Any]] = None
) -> Optional[UserModel]:
    """
    Create a new user in the database.
    If a callback is provided and fails, the user is automatically deleted (rollback).
    """
    created_user = None
    try:
        logger.info(f"[REPO_CREATE_USER] Iniciando criação - Role ID: {user.role_id}, Tem foto: {profile_picture is not None}")
        
        role = get_role_by_id(user.role_id, requesting_role_permissions) if user.role_id else get_default_role()
        if role is None:
            raise ValueError("Invalid role ID" if user.role_id else "Default role not found")

        user_dump = user.model_dump()
        user_dump.pop("password")
        user_id = str(uuid.uuid4())
        user_model = UserModel(
            id=user_id,
            **user_dump,
            role=role,
            password=bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()),
        )
        
        if profile_picture:
            logger.info(f"[REPO_CREATE_USER] Iniciando upload de imagem - Filename: {profile_picture.filename}")
            upload_start = datetime.now()
            url = await upload_image(profile_picture)
            upload_duration = (datetime.now() - upload_start).total_seconds()
            logger.info(f"[REPO_CREATE_USER] Upload de imagem concluído em {upload_duration:.2f}s - URL: {url}")
            user_model.profile_picture = url
        
        logger.info(f"[REPO_CREATE_USER] Inserindo usuário no banco - User ID: {user_model.id}")
        db_start = datetime.now()
        result = users_collection.insert_one(user_model.model_dump(by_alias=True))
        db_duration = (datetime.now() - db_start).total_seconds()
        logger.info(f"[REPO_CREATE_USER] Usuário inserido no banco em {db_duration:.2f}s - Inserted ID: {result.inserted_id}")
        
        if not result.inserted_id:
            logger.error("[REPO_CREATE_USER] Falha ao inserir - result.inserted_id é None")
            return None
        
        created_user = user_model
        
        # Execute callback if provided (ex: send email)
        # If it fails, the exception will be captured and the user will be deleted
        if post_create_callback:
            logger.info("[REPO_CREATE_USER] Executando callback pós-criação")
            post_create_callback(created_user)
        
        logger.info(f"[REPO_CREATE_USER] Criação concluída com sucesso - User ID: {created_user.id}")
        return created_user
    except Exception as e:
        logger.error(f"[REPO_CREATE_USER] Erro durante criação: {type(e).__name__}: {str(e)}", exc_info=True)
        # Rollback: delete the user if something fails after creation
        if created_user:
            try:
                logger.info(f"[REPO_CREATE_USER] Fazendo rollback - deletando usuário {created_user.id}")
                delete_user(created_user.id)
                logger.info(f"[REPO_CREATE_USER] Rollback concluído - usuário {created_user.id} deletado")
            except Exception as rollback_error:
                logger.error(f"[REPO_CREATE_USER] Erro no rollback: {str(rollback_error)}")
        raise

async def update_user(user_id: str, update_data: UserModel, profile_picture: Optional[UploadFile]) -> Optional[UserModel]:
    user_data = users_collection.find_one({"_id": user_id})
    if user_data is None:
        raise ValueError("User not found")
    if profile_picture:
        url = await upload_image(profile_picture, user_data.get("profile_picture"))
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

    url = await upload_image(file, user.get("profile_picture") if user_id else None)
    return url