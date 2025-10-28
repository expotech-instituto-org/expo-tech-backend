from fastapi import APIRouter, HTTPException
from app.repository import knowledge_repository
from typing import List
from app.model.knowledge import KnowledgeModel
from app.dto.knowledge.knowledge_create_dto import KnowledgeCreateDTO

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"]
)

@router.get("", response_model=List[KnowledgeModel])
async def get_all_knowledge():
    return knowledge_repository.get_all_knowledge()

@router.get("/{knowledge_id}", response_model=KnowledgeModel)
async def get_knowledge_by_id(knowledge_id: str):
    knowledge_data = knowledge_repository.get_knowledge_by_id(knowledge_id)
    if knowledge_data is None:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return knowledge_data

@router.post("", response_model=KnowledgeModel)
async def create_knowledge(knowledge_dto: KnowledgeCreateDTO):
    knowledge_created = knowledge_repository.create_knowledge(knowledge_dto.name)
    if knowledge_created is None:
        raise HTTPException(status_code=400, detail="Failed to create knowledge")
    return knowledge_created

@router.put("/{knowledge_id}", response_model=KnowledgeModel)
async def update_knowledge(knowledge_id: str, knowledge_update: KnowledgeCreateDTO):
    updated = knowledge_repository.update_knowledge(knowledge_id, knowledge_update)
    if updated is None:
        raise HTTPException(status_code=404, detail="Knowledge not found or not updated")
    return updated

@router.delete("/{knowledge_id}", response_model=dict)
async def delete_knowledge(knowledge_id: str):
    knowledge_deleted = knowledge_repository.delete_knowledge(knowledge_id)
    if not knowledge_deleted:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return {"message": "Knowledge deleted successfully"}