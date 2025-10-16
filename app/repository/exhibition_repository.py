from typing import Optional
from app.database import db
from app.dto.exhibition.exhibition_create_dto import ExhibitionCreate
from app.dto.exhibition.exhibition_update_dto import ExhibitionUpdate
from app.model.exhibition import ExhibitionModel
from app.model.role import RoleModel
from app.repository import project_repository
import uuid

exhibition_collection= db["exhibions"]

def get_all_exhibition() -> list[ExhibitionModel]:
    exhibition_cursor = exhibition_collection.find()
    return [ExhibitionModel (**exhibition) for exhibition in exhibition_cursor]

def get_exhibition_by_id(exhibition_id: str) -> Optional[ExhibitionModel]:
    exhibition_data = exhibition_collection.find_one({"_id": exhibition_id})
    if exhibition_data:
        return ExhibitionModel(**exhibition_data)
    return None

def delete_exhibition(exhibition_id: str) -> bool:
    result = exhibition_collection.update_one(
        {"_id": exhibition_id},
        {"$set": {"deactivation_date": db.client.server_info()['localTime']}}
    )
    return result.deleted_count > 0

def create_exhibition(exhibition: ExhibitionCreate):
    if exhibition.end_date < exhibition.start_date:
        raise ValueError("End date must be greater than start date")
    exhibition_model = ExhibitionModel(
        _id = str(uuid.uuid4()),
        **exhibition.model_dump(),
        projects = [],
        roles = [
            ExhibitionModel.RoleModel(
                id = str(uuid.uuid4()),
                name="Guest",
                weight=1.0
            )
            # role_repository.get_default_role()
        ],
        criteria = [
            ExhibitionModel.CriteriaModel(
                name="Nota",
                weight=1.0
            )
        ],
    )
    result = exhibition_collection.insert_one(exhibition_model)
    if result.inserted_id:
        return exhibition_model
    return None

# def update_exhibion_with_role(role_id: str, updated_role: RoleModel) -> int:
#     result = exhibition_collection.update_many(
#         {"role.id": role_id},
#         {"$set": {"role": updated_role.dict()}}
#     )
#     return result.modified_count

def update_exhibition(update_data: ExhibitionUpdate) -> Optional[ExhibitionModel]:
    if update_data.roles and sum(role.weight for role in update_data.roles) != 1.0:
        raise ValueError("Sum of role weights must be 1.0")
    if update_data.criteria and sum(criteria.weight for criteria in update_data.criteria) != 1.0:
        raise ValueError("Sum of criteria weights must be 1.0")
    if update_data.end_date < update_data.start_date:
        raise ValueError("End date must be greater than start date")
    result = exhibition_collection.update_one(
        {"_id": update_data.id, "deactivation_date": {"$exists": False}},
        {"$set": {
            "name": update_data.name,
            "description": update_data.description,
            "image": update_data.image,
            "start_date": update_data.start_date,
            "end_date": update_data.end_date,
            "criteria": update_data.criteria,
            "roles": update_data.roles,
            }
        }
    )
    if result.modified_count > 0:
        updated_exhibition = exhibition_collection.find_one({"_id": update_data.id})
        if updated_exhibition:
            return ExhibitionModel(**updated_exhibition)
    return None

def add_project(exhibition_id: str, project: ExhibitionModel.ProjectResume):
    result = exhibition_collection.update_one(
        {"_id": exhibition_id, "deactivation_date": {"$exists": False}},
        {"$addToSet": {"projects": project.model_dump()}}
    )
    return result.modified_count > 0

def remove_project(exhibition_id: str, project_id: str):
    result = exhibition_collection.update_one(
        {"_id": exhibition_id, "deactivation_date": {"$exists": False}},
        {"$pull": {"projects": {"id": project_id}}}
    )
    
    project_repository.delete_project_by_id(project_id)

    return result.modified_count > 0