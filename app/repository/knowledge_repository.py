from typing import Optional
from app.database import db
from app.model.knowledge import KnowledgeModel
from app.dto.user_login_dto import UserLogin
import uuid
from passlib.hash import bcrypt


knowledge_collection= db["knowledges"]

def get_all_knowledge() -> list[KnowledgeModel]:
    knowledge_cursor = knowledge_collection.find()
    return [KnowledgeModel (**knowledge) for knowledge in knowledge_cursor]

def get_knowledge_by_id(knowledge_id: str) -> Optional[KnowledgeModel]:
    knowledge_data = knowledge_collection.find_one({"_id": knowledge_id})
    if knowledge_data:
        return KnowledgeModel(**knowledge_data)
    return None

def delete_knowledge(knowledge_id: str) -> bool:
    result = knowledge_collection.delete_one({"_id": knowledge_id})
    return result.deleted_count > 0

def create_knowledge(knowledge_name: str ):
    knowledge_dict = {
        "_id": str(uuid.uuid4()),
        "name": knowledge_name
    }
    result = knowledge_collection.insert_one(knowledge_dict)
    if result.inserted_id:
        return KnowledgeModel(**knowledge_dict)
    return None

def update_knowledge(update_data: KnowledgeModel) -> Optional[KnowledgeModel]:
    result = knowledge_collection.update_one(
        {"_id": update_data.id},             
        {"$set": {"name": update_data.name}} 
    )
    if result.modified_count > 0:
        updated_knowledge = knowledge_collection.find_one({"_id": update_data.id})
        if updated_knowledge:
            return KnowledgeModel(**updated_knowledge)
    return None