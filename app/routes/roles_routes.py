from app.routes.security import User, get_current_user
from fastapi import APIRouter, HTTPException, status, Depends
from app.dto.role.role_upsert_dto import RoleUpsert
from app.repository import roles_repository
from typing import Annotated, List
from app.model.role import RoleModel
from app import constants as c

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.get("", response_model=List[RoleModel])
async def list_roles(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_READ_ROLE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return roles_repository.list_all_roles()
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.get("/default", response_model=RoleModel)
async def get_default_role(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_READ_ROLE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        role = roles_repository.get_default_role()
        if role is None:
            raise HTTPException(status_code=404, detail="Default role not found")
        return role
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.get("/{role_id}", response_model=RoleModel)
async def get_role(role_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_READ_ROLE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        role = roles_repository.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        return role
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.post("", response_model=RoleModel, status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleUpsert, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_CREATE_ROLE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        created = roles_repository.create_role(role)
        if created is None:
            raise HTTPException(status_code=400, detail="Could not create role")
        return created
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.put("/{role_id}", response_model=RoleModel)
async def update_role(role_id: str, role: RoleModel, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_UPDATE_ROLE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        updated = roles_repository.update_role(role_id, role)
        if updated is None:
            raise HTTPException(status_code=404, detail="Role not found")
        return updated
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))