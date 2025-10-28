from typing import List
from fastapi import APIRouter, HTTPException
from app.dto.exhibition.exhibition_resume_dto import ExhibitionResumeDTO

from app.dto.exhibition.exhibition_update_dto import ExhibitionUpdate
from app.model.exhibition import ExhibitionModel
from app.repository import exhibition_repository
from app.dto.exhibition.exhibition_create_dto import ExhibitionCreate

router = APIRouter(
    prefix="/exhibitions",
    tags=["Exhibitions"]
)

@router.get("", response_model=List[ExhibitionResumeDTO])
async def list_exhibitions():
    return exhibition_repository.get_all_exhibition()

@router.put("/{exhibition_id}", response_model=ExhibitionModel)
async def update_exhibition(exhibition_id: str, exhibition: ExhibitionUpdate):
    return exhibition_repository.update_exhibition(exhibition_id, exhibition)

@router.post("", response_model=ExhibitionModel)
async def create_exhibition(exhibition: ExhibitionCreate):
    return exhibition_repository.create_exhibition(exhibition)

@router.delete("/{exhibition_id}", response_model=bool)
async def delete_exhibition(exhibition_id: str):
    return exhibition_repository.delete_exhibition(exhibition_id)

@router.get("/{exhibition_id}", response_model=ExhibitionModel)
async def get_exhibition_by_id(exhibition_id: str):
    exhibition = exhibition_repository.get_exhibition_by_id(exhibition_id)
    if exhibition is None:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return exhibition

@router.get("/current/", response_model=ExhibitionModel)
async def get_exhibition_by_current_date():
    exhibition = exhibition_repository.get_exhibition_by_current_date()
    if exhibition is None:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return exhibition
