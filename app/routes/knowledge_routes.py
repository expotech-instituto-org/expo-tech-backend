from typing_extensions import Annotated
from app.routes.security import User, get_current_user
from fastapi import APIRouter, HTTPException, Depends, status
from app.repository import knowledge_repository
from typing import List
from app.model.knowledge import KnowledgeModel
from app.dto.knowledge.knowledge_create_dto import KnowledgeCreateDTO
import app.constants as c

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"]
)

@router.get("", response_model=List[KnowledgeModel])
async def get_all_knowledge(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_KNOWLEDGE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return knowledge_repository.get_all_knowledge()
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.get("/{knowledge_id}", response_model=KnowledgeModel)
async def get_knowledge_by_id(knowledge_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_KNOWLEDGE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        knowledge_data = knowledge_repository.get_knowledge_by_id(knowledge_id)
        if knowledge_data is None:
            raise HTTPException(status_code=404, detail="Knowledge not found")
        return knowledge_data
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.post("", response_model=KnowledgeModel)
async def create_knowledge(knowledge_dto: KnowledgeCreateDTO, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_CREATE_KNOWLEDGE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        knowledge_created = knowledge_repository.create_knowledge(knowledge_dto.name)
        if knowledge_created is None:
            raise HTTPException(status_code=400, detail="Failed to create knowledge")
        return knowledge_created
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.put("/{knowledge_id}", response_model=KnowledgeModel)
async def update_knowledge(knowledge_id: str, knowledge_update: KnowledgeCreateDTO, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_UPDATE_KNOWLEDGE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        updated = knowledge_repository.update_knowledge(knowledge_id, knowledge_update)
        if updated is None:
            raise HTTPException(status_code=404, detail="Knowledge not found or not updated")
        return updated
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.delete("/{knowledge_id}", response_model=dict)
async def delete_knowledge(knowledge_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_DELETE_KNOWLEDGE not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        knowledge_deleted = knowledge_repository.delete_knowledge(knowledge_id)
        if not knowledge_deleted:
            raise HTTPException(status_code=404, detail="Knowledge not found")
        return {"message": "Knowledge deleted successfully"}
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))