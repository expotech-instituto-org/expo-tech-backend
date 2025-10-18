from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.repository import knowledge_repository
from typing import List, Annotated
from app.model.knowledge import KnowledgeModel
from app.dto.user.user_login_dto import UserLogin
from app.routes.security import get_current_user, create_access_token, User, Token

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"]
)

@router.get("", response_model=List[KnowledgeModel])
async def get_all_knowledge():
    return knowledge_repository.get_all_knowledge()

@router.get("/{knowledge_id}", response_model=KnowledgeModel)
async def get_knowledge_by_id(knowledge_id: str):
    knowledge = knowledge_repository.get_knowledge_by_id(knowledge_id)
    if knowledge is None:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return knowledge