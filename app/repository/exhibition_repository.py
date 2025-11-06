from http.client import HTTPException
from typing import Optional
from app.database import db
from app.dto.exhibition.exhibition_create_dto import ExhibitionCreate
from app.dto.exhibition.exhibition_update_dto import ExhibitionUpdate
from app.dto.exhibition.exhibition_resume_dto import ExhibitionResumeDTO
from app.model.exhibition import ExhibitionModel
from app.model.role import RoleModel
from app.repository import project_repository, roles_repository
import app.constants as c
import uuid
from datetime import datetime, timezone
from pymongo import ASCENDING
from app.bucket import upload_image
from fastapi import UploadFile

exhibition_collection= db["exhibitions"]


def get_all_exhibition(name: Optional[str] = None, start_date: Optional[datetime] = None) -> list[ExhibitionResumeDTO]:
    query = {"deactivation_date": None}
    
    if name is not None:
        query["name"] = {"$regex": name, "$options": "i"}
    
    if start_date is not None:
        query["start_date"] = {"$gte": start_date}
    
    exhibition_cursor = exhibition_collection.find(query)
    return [ExhibitionResumeDTO(**exhibition, id=exhibition.get("_id")) for exhibition in exhibition_cursor]

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

async def create_exhibition(exhibition: ExhibitionCreate, image: UploadFile = None):
    if exhibition.end_date < exhibition.start_date:
        raise ValueError("End date must be greater than start date")

    default_role = roles_repository.get_default_role()

    image_url = None
    if image:
        image_url = await upload_image(image, folder="exhibitions")

    exhibition_model = ExhibitionModel(
        _id = str(uuid.uuid4()),
        **exhibition.model_dump(),
        image=image_url,
        projects = [],
        roles = [
            ExhibitionModel.RoleResume(
                _id = default_role.id,
                name=default_role.name,
                weight=1.0
            )
        ],
        criteria = [
            ExhibitionModel.CriteriaResume(
                name="Nota",
                weight=1.0
            )
        ],
    )
    result = exhibition_collection.insert_one(exhibition_model.model_dump(by_alias=True))
    if result.inserted_id:
        return exhibition_model
    return None

def update_exhibion_with_role(role_id: str, updated_role: RoleModel) -> int:
    result = exhibition_collection.update_many(
        {"role.id": role_id},
        {"$set": {"role": updated_role.model_dump(by_alias=True)}}
    )
    return result.modified_count

async def update_exhibition(exhibition_id: str, update_data: ExhibitionUpdate, image: UploadFile = None) -> Optional[ExhibitionModel]:
    if update_data.roles and not any(role.id == c.DEFAULT_ROLE_ID for role in update_data.roles):
        raise ValueError("Default role must be present in roles")
    if update_data.roles and sum(role.weight for role in update_data.roles) != 1.0:
        raise ValueError("Sum of role weights must be 1.0")
    if update_data.criteria and sum(criteria.weight for criteria in update_data.criteria) != 1.0:
        raise ValueError("Sum of criteria weights must be 1.0")
    if update_data.end_date and update_data.start_date and update_data.end_date < update_data.start_date:
        raise ValueError("End date must be greater than start date")

    image_url = None
    if image:
        image_url = await upload_image(image, folder="exhibitions")

    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True, by_alias=True)
    if image_url:
        update_dict["image"] = image_url

    result = exhibition_collection.update_one(
        {"_id": exhibition_id},
        {"$set": update_dict}
    )
    if result.matched_count:
        updated = exhibition_collection.find_one({"_id": exhibition_id})
        return ExhibitionModel(**updated)
    return None

def add_project(exhibition_id: str, project: ExhibitionModel.ProjectResume):
    result = exhibition_collection.update_one(
        {"_id": exhibition_id, "deactivation_date": {"$exists": False}},
        {
            "$addToSet": {
                **({"banners": project.banners[0]} if project.banners else {}),
                "projects": project.model_dump()
            }
        }
    )
    return result.modified_count > 0

def update_project(exhibition_id: str, project_id: str, updated_project: ExhibitionModel.ProjectResume) -> bool:
    result = exhibition_collection.update_one(
        {
            "_id": exhibition_id,
            "deactivation_date": {"$exists": False},
            "projects.id": project_id
        },
        {
            "$set": {
                "projects.$": updated_project.model_dump()
            }
        }
    )
    return result.modified_count > 0

def remove_project(exhibition_id: str, project_id: str):
    result = exhibition_collection.update_one(
        {"_id": exhibition_id, "deactivation_date": {"$exists": False}},
        {"$pull": {"projects": {"id": project_id}}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Project not found in any exhibition")
    result_project = project_repository.delete_project_by_id(project_id)
    return result_project

def is_role_in_use(role_id: str) -> bool:
    exhibition = exhibition_collection.find_one(
        {
            "roles.id": role_id,
            "deactivation_date": {"$exists": False}
        }
    )
    return exhibition is not None

def get_exhibition_by_current_date() -> Optional[ExhibitionModel]:
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    query = {
        "$or": [
            {
                "start_date": {"$lte": today},
                "end_date": {"$gte": today},
                "deactivation_date": None
            },
            {
                "start_date": {"$gt": today},
                "deactivation_date": None
            }
        ]
    }
    exhibition_cursor = exhibition_collection.find(query).sort("start_date", ASCENDING).limit(1)
    exhibition_data = next(exhibition_cursor, None)
    if exhibition_data:
        return ExhibitionModel(**exhibition_data)
    return None