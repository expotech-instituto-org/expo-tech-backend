from typing import Optional
from app.database import db
from app.dto.class_.class_create_dto import ClassCreateDTO
from app.model.class_ import ClassModel
import uuid

class_collection= db["classes"]

def get_all_class() -> list[ClassModel]:
    class_cursor = class_collection.find()
    return [ClassModel (**class_model) for class_model in class_cursor]

def get_class_by_id(class_id: str) -> Optional[ClassModel]:
    class_data = class_collection.find_one({"_id": class_id})
    if class_data:
        return ClassModel(**class_data)
    return None

def delete_class(class_id: str) -> bool:
    result = class_collection.delete_one({"_id": class_id})
    return result.deleted_count > 0

def create_class(class_name: str, class_year: str):
    class_dict = {
        "_id": str(uuid.uuid4()),
        "name": class_name,
        "year": class_year
    }
    result = class_collection.insert_one(class_dict)
    if result.inserted_id:
        return ClassModel(**class_dict)
    return None

def update_class(class_id: str, update_data: ClassCreateDTO) -> Optional[ClassModel]:
    result = class_collection.update_one(
        {"_id": class_id},
        {"$set": {"name": update_data.name, "year": update_data.year}}
    )
    if result.modified_count > 0:
        return ClassModel(_id=class_id, **update_data.model_dump())
    return None