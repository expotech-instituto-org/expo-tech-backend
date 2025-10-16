from typing import Optional
from app.database import db
from app.model.role import RoleModel
import uuid
from passlib.hash import bcrypt
from pymongo.collection import Collection
from app.repository import user_repository, exhibition_repository, review_repository

roles_collection = db["roles"]

def get_role_by_id(role_id: str) -> Optional[RoleModel]:
    role_data = roles_collection.find_one({"id": role_id})
    if role_data:
        return RoleModel(**role_data)
    return None

def get_default_role() -> Optional[RoleModel]:
    role_data = roles_collection.find_one({"default": "True"})
    if role_data:
        return RoleModel(**role_data)
    return None

def list_all_roles() -> list[RoleModel]:
    roles_cursor = roles_collection.find()
    return [RoleModel(**role) for role in roles_cursor]

def create_role(roles_collection: Collection, role: RoleModel) -> Optional[RoleModel]:
    role_dict = role.model_dump(by_alias=True)

    if not role_dict.get("_id"):
        role_dict["_id"] = str(uuid.uuid4())

    result = roles_collection.insert_one(role_dict)

    if result.inserted_id:
        return RoleModel(**role_dict)
    return None


def update_role(role_id: str, update_data: RoleModel) -> Optional[RoleModel]:
    role_data = roles_collection.find_one({"id": role_id})
    if role_data:
        updated_role = {**role_data, **update_data.model_dump(exclude_unset=True)}
        
        roles_collection.replace_one({"id": role_id}, updated_role)

        return RoleModel(**updated_role)
    return None

def delete_role(role_id: str) -> bool:
    
    if user_repository.is_role_in_use(role_id):
        return False
    if exhibition_repository.is_role_in_use(role_id):
        return False
    if review_repository.is_role_in_use(role_id):
        return False

    result = roles_collection.delete_one({"id": role_id})
    return result.deleted_count > 0