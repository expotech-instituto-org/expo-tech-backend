from typing import Optional
from app.database import db
from app.dto.role.role_upsert_dto import RoleUpsert
from app.model.role import RoleModel
import uuid
import app.constants as c

roles_collection = db["roles"]

def get_role_by_id(role_id: str, requesting_role_permissions: Optional[list[str]] = None) -> Optional[RoleModel]:
    role_data = roles_collection.find_one({"id": role_id})
    if not role_data:
        return None

    if requesting_role_permissions is not None:
        role_permissions = role_data.get("permissions", [])
        for perm in role_permissions:
            if perm not in requesting_role_permissions:
                raise PermissionError(f"Insufficient permissions to access role {role_id}")
    return RoleModel(**role_data)

def get_default_role() -> Optional[RoleModel]:
    role_data = roles_collection.find_one({"_id": "default"})
    if role_data:
        return RoleModel(**role_data)
    return None

def list_all_roles() -> list[RoleModel]:
    roles_cursor = roles_collection.find()
    return [RoleModel(**role) for role in roles_cursor]

def create_role (role: RoleUpsert) -> Optional[RoleModel]:
    if role.permissions is not None and len(role.permissions) > 0 and not c.is_valid_permission(role.permissions):
        raise ValueError("One or more permissions are invalid")

    role_model = RoleModel(
        _id=str(uuid.uuid4()),
        name=role.name,
        permissions=role.permissions or default_permissions(),
    )

    result = roles_collection.insert_one(role_model)

    if result.inserted_id:
        return role_model
    return None


def update_role(role_id: str, update_data: RoleModel) -> Optional[RoleModel]:
    role_data = roles_collection.find_one({"id": role_id})
    if role_data:
        updated_role = {**role_data, **update_data.model_dump(exclude_unset=True)}
        
        roles_collection.replace_one({"id": role_id}, updated_role)

        return RoleModel(**updated_role)
    return None


def default_permissions() -> list[str]:
    return [
        c.PERMISSION_READ_EXHIBITION,
        c.PERMISSION_READ_PROJECT,
        c.PERMISSION_CREATE_REVIEW,
    ]

roles_collection.update_one(
    {"_id": "default"},
    {
        "$setOnInsert": {
            "name": "guest",
            "permissions": default_permissions(),
        }
    },
    upsert=True
)