from app.routes.security import User, get_current_user
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated, List
from app.repository import class_repository
from app.model.class_ import ClassModel
from app.dto.class_.class_create_dto import ClassCreateDTO
import app.constants as c

router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)

@router.get("", response_model=List[ClassModel])
async def list_classes():
    try:
        return class_repository.get_all_class()
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.get("/{class_id}", response_model=ClassModel)
async def get_class(class_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_CLASS not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        class_data = class_repository.get_class_by_id(class_id)
        if not class_data:
            raise HTTPException(status_code=404, detail="Class not found")
        return class_data
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.post("", response_model=ClassModel)
async def create_class(class_dto: ClassCreateDTO, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_CREATE_CLASS not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        created = class_repository.create_class(class_dto.name, class_dto.year)
        if not created:
            raise HTTPException(status_code=400, detail="Failed to create class")
        return created
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.put("/{class_id}", response_model=ClassModel)
async def update_class(class_id: str, class_update: ClassCreateDTO, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_UPDATE_CLASS not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        updated = class_repository.update_class(class_id, class_update)
        if not updated:
            raise HTTPException(status_code=404, detail="Class not found or not updated")
        return updated
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.delete("/{class_id}", response_model=dict)
async def delete_class(class_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_DELETE_CLASS not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        deleted = class_repository.delete_class(class_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Class not found")
        return {"message": "Class deleted successfully"}
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
