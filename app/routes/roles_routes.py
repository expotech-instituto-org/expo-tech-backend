from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.repository import roles_repository
from typing import List, Annotated
from app.model.role import RoleModel
from app.routes.security import get_current_user, create_access_token, Token

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.get("", response_model=List[RoleModel])
async def list_users():
    return roles_repository.list_all_roles()


@router.get("/default", response_model=RoleModel)
async def get_default_role():
    role = roles_repository.get_default_role()
    if role is None:
        raise HTTPException(status_code=404, detail="Default role not found")
    return role

@router.get("/{role_id}", response_model=RoleModel)
async def get_role(role_id: str):
    role = roles_repository.get_role_by_id(role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.post("", response_model=RoleModel, status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleModel):
    created = roles_repository.create_(roles_repository.roles_collection, role)
    if created is None:
        raise HTTPException(status_code=400, detail="Could not create role")
    return created

@router.put("/{role_id}", response_model=RoleModel)
async def update_role(role_id: str, role: RoleModel):
    updated = roles_repository.update_role(role_id, role)
    if updated is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return updated