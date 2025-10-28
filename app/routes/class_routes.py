from fastapi import APIRouter, HTTPException
from typing import List
from app.repository import class_repository
from app.model.class_ import ClassModel
from app.dto.class_.class_create_dto import ClassCreateDTO

router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)

@router.get("", response_model=List[ClassModel])
async def list_classes():
    return class_repository.get_all_class()

@router.get("/{class_id}", response_model=ClassModel)
async def get_class(class_id: str):
    class_data = class_repository.get_class_by_id(class_id)
    if not class_data:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_data

@router.post("", response_model=ClassModel)
async def create_class(class_dto: ClassCreateDTO):
    created = class_repository.create_class(class_dto.name, class_dto.year)
    if not created:
        raise HTTPException(status_code=400, detail="Failed to create class")
    return created

@router.put("/{class_id}", response_model=ClassModel)
async def update_class(class_id: str, class_update: ClassCreateDTO):
    updated = class_repository.update_class(class_id, class_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Class not found or not updated")
    return updated

@router.delete("/{class_id}", response_model=dict)
async def delete_class(class_id: str):
    deleted = class_repository.delete_class(class_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted successfully"}
