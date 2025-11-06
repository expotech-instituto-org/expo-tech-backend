import uuid
from typing import Optional, List
from app.database import db
from app.dto.project.project_create_dto import ProjectCreateDto
from app.dto.project.project_update_dto import ProjectUpdateDto
from app.model.exhibition import ExhibitionModel
from app.model.project import ProjectModel
from app.model.user import UserModel
from app.repository import user_repository
from app.repository import exhibition_repository
from app.bucket import upload_image, delete_image
from fastapi import UploadFile

from app.repository.review_repository import reviews_collection

project_collection = db["projects"]

def get_project_by_id(project_id: str) -> Optional[ProjectModel]:
    project_data = project_collection.find_one({"_id": project_id})
    if project_data:
        if project_data.get("_id"):
            project_data["_id"] = str(project_data["_id"])
        return ProjectModel(**project_data)
    return None

def get_projects_with_filters(
    exhibition_id: Optional[str] = None,
    project_name: Optional[str] = None,
    company_name: Optional[str] = None
) -> List[ProjectModel]:
    query = {}
    
    if exhibition_id:
        query["exhibition_id"] = exhibition_id
    
    if project_name:
        query["name"] = {"$regex": project_name, "$options": "i"}
    
    if company_name:
        query["company_name"] = {"$regex": company_name, "$options": "i"}
    
    projects = project_collection.find(query)
    result = []
    for p in projects:
        if p.get("_id"):
            p["_id"] = str(p["_id"])
        result.append(ProjectModel(**p))
    return result

async def create_project(project_create_dto: ProjectCreateDto, logo: UploadFile = None, images: List[UploadFile] = None) -> Optional[ProjectModel]:
    exhibition = exhibition_repository.get_exhibition_by_id(project_create_dto.exhibition_id)
    if not exhibition:
        ValueError("Exhibition not found")
        return None

    expositors: List[ProjectModel.UserResume] = []
    for expositor_id in project_create_dto.expositors:
        expositor = user_repository.get_user_by_id(expositor_id)
        if not expositor:
            ValueError(f"Expositor {expositor_id} not found")
            return None
        expositors.append(expositor.model_dump(by_alias=True))

    logo_url: Optional[str] = None
    if logo:
        url = await upload_image(logo, folder="projects/logo")
        logo_url = url

    image_urls: List[str] = []
    if images:
        for image in images:
            url = await upload_image(image, folder="projects/images")
            image_urls.append(url)

    project = ProjectModel(
        _id=project_create_dto.id or str(uuid.uuid4()),
        expositors=expositors,
        logo=logo_url,
        images=image_urls,
        **project_create_dto.model_dump()
    )

    result = project_collection.insert_one(project.model_dump(by_alias=True))
    if result.inserted_id:
        exhibition_repository.add_project(exhibition.id, ExhibitionModel.ProjectResume(
            _id=project.id,
            name=project.name,
            logo=logo_url,
            company_name=project.company_name,
            description=project.description,
            banners=image_urls,
            coordinates=project.coordinates
        ))

        for expositor in expositors:
            user_repository.add_project_to_user(expositor.id, UserModel.ProjectResume(
                _id=project.id,
                name=project.name,
                logo=logo_url,
                company_name=project.company_name,
            ))

        return project
    return None

async def update_project(project_id: str, project_update_dto: ProjectUpdateDto, logo: UploadFile = None, images: List[UploadFile] = None) -> Optional[ProjectModel]:
    project = get_project_by_id(project_id)
    if not project:
        ValueError("Project not found")
        return None

    expositors: List[ProjectModel.UserResume] = []
    for expositor_id in project_update_dto.expositor_ids:
        expositor = user_repository.get_user_by_id(expositor_id)
        if not expositor:
            ValueError(f"Expositor {expositor_id} not found")
            return None
        expositors.append(expositor.model_dump(by_alias=True))

    logo_url: Optional[str] = None
    if logo:
        url = await upload_image(logo, project.logo, folder="projects/logo")
        logo_url = url


    for image_url in project.images:
        delete_image(image_url)

    image_urls: List[str] = []
    if images:
        for image in images:
            url = await upload_image(image, folder="projects/images")
            image_urls.append(url)

    project = ProjectModel(
        exhibition_id=project.exhibition_id,
        expositors=expositors,
        logo=logo_url,
        images=image_urls,
        **project_update_dto.model_dump()
    )

    project_dict = project.model_dump(by_alias=True)
    project_dict.pop("_id")
    result = project_collection.update_one({"_id": project_id}, {"$set": project_dict})
    if result.modified_count:
        exhibition_repository.update_project(project.exhibition_id, project_id, ExhibitionModel.ProjectResume(
            _id=project.id,
            name=project.name,
            logo=logo_url,
            company_name=project.company_name,
            description=project.description,
            banners=image_urls,
            coordinates=project.coordinates
        ))

        for expositor in expositors:
            user_repository.add_project_to_user(expositor["_id"], UserModel.ProjectResume(
                _id=project_id,
                name=project.name,
                logo=logo_url,
                company_name=project.company_name,
            ))
        return project

    return None

def update_project_with_user(user_id: str, update_user: UserModel) -> int:
    result = project_collection.update_many(
        {"user_id": user_id},
        {"$set": {"user": update_user.model_dump(by_alias=True)}}
    )
    return result.modified_count

def delete_project_by_id(project_id: str) -> bool:
    try:
        reviews_collection.update_many(
            {"project_id": project_id},
            {"$set": {"active": False}}
        )
        
        user_repository.unset_project_by_project_id(project_id)

        project = project_collection.find_one({"_id": project_id})
        if project and project.get("exhibition_id"):
            try:
                exhibition_repository.remove_project(project.get("exhibition_id"), project_id)
            except Exception:
                pass

        result = project_collection.delete_one({"_id": project_id})
        return result.deleted_count > 0
    except Exception as e:
        return False