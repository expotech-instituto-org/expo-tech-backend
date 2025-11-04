from datetime import datetime
from typing import Annotated, List, Optional
from app.routes.security import User, get_current_user
from fastapi import APIRouter, HTTPException, Query, Depends, status
from app.dto.exhibition.exhibition_resume_dto import ExhibitionResumeDTO

from app.dto.exhibition.exhibition_update_dto import ExhibitionUpdate
from app.model.exhibition import ExhibitionModel
from app.repository import exhibition_repository
from app.dto.exhibition.exhibition_create_dto import ExhibitionCreate
import app.constants as c

router = APIRouter(
    prefix="/exhibitions",
    tags=["Exhibitions"]
)

@router.get("", response_model=List[ExhibitionResumeDTO])
async def list_exhibitions(
    current_user: Annotated[User, Depends(get_current_user)],
    name: Optional[str] = Query(None, description="Name of the exhibition"),    
    start_date: Optional[datetime] = Query(None, description="Start date of the exhibition")                                                                    
):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_EXHIBITION not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return exhibition_repository.get_all_exhibition(name, start_date)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.put("/{exhibition_id}", response_model=ExhibitionModel)
async def update_exhibition(exhibition_id: str, exhibition: ExhibitionUpdate, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_UPDATE_EXHIBITION not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return exhibition_repository.update_exhibition(exhibition_id, exhibition)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.post("", response_model=ExhibitionModel)
async def create_exhibition(exhibition: ExhibitionCreate, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_CREATE_EXHIBITION not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return exhibition_repository.create_exhibition(exhibition)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.delete("/{exhibition_id}", response_model=bool)
async def delete_exhibition(exhibition_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_DELETE_EXHIBITION not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return exhibition_repository.delete_exhibition(exhibition_id)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.get("/{exhibition_id}", response_model=ExhibitionModel)
async def get_exhibition_by_id(exhibition_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_EXHIBITION not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        exhibition = exhibition_repository.get_exhibition_by_id(exhibition_id)
        if exhibition is None:
            raise HTTPException(status_code=404, detail="Exhibition not found")
        return exhibition
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.get("/current/", response_model=ExhibitionModel)
async def get_exhibition_by_current_date(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_EXHIBITION not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        exhibition = exhibition_repository.get_exhibition_by_current_date()
        if exhibition is None:
            raise HTTPException(status_code=404, detail="Exhibition not found")
        return exhibition
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
