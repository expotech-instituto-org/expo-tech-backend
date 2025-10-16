from typing import List
from fastapi import APIRouter
from app.model.exhibition import ExhibitionModel
from app.repository import exhibition_repository

router = APIRouter(
    prefix="/exhibitions",
    tags=["Exhibitions"]
)

@router.get("", response_model=List[ExhibitionModel])
async def list_exhibitions():
    return exhibition_repository.get_all_exhibition()

@router.put("/{exhibition_id}", response_model=ExhibitionModel)
async def update_exhibition(exhibition_id: str, exhibition: ExhibitionModel):
    return exhibition_repository.update_exhibition(exhibition_id, exhibition)

@router.post("", response_model=ExhibitionModel)
async def create_exhibition(exhibition: ExhibitionModel):
    return exhibition_repository.create_exhibition(exhibition)

@router.delete("/{exhibition_id}", response_model=bool)
async def delete_exhibition(exhibition_id: str):
    return exhibition_repository.delete_exhibition(exhibition_id)