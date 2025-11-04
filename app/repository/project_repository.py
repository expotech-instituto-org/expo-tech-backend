import uuid
from typing import Optional, List
from app.database import db
from app.model.project import ProjectModel
from app.model.review import ReviewModel
from app.model.user import UserModel
from app.model.exhibition import ExhibitionModel
from app.repository import user_repository
from app.repository import exhibition_repository

project_collection = db["projects"]
review_collection = db["reviews"]

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

def add_project(project: ProjectModel) -> Optional[ProjectModel]:
    project_dict = project.model_dump(by_alias=True)
    project_dict["_id"] = str(uuid.uuid4())

    result = project_collection.insert_one(project_dict)

    if result.inserted_id:
        expositor_ids = []
        for expositor in project_dict.get("expositors", []):
            if isinstance(expositor, dict):
                if "_id" in expositor and expositor["_id"]:
                    expositor_ids.append(expositor["_id"])
                elif "id" in expositor and expositor["id"]:
                    expositor_ids.append(expositor["id"])
            elif hasattr(expositor, 'id') and expositor.id:
                expositor_ids.append(expositor.id)
            elif hasattr(expositor, '_id') and expositor._id:
                expositor_ids.append(expositor._id)
        
        if expositor_ids:
            user_repository.set_project_id_on_users(expositor_ids, project_dict["_id"])

        exhibition_repository.add_project(
            project_dict["exhibition_id"],
            ExhibitionModel.ProjectResume(
                _id= project_dict["_id"],
                name= project_dict.get("name"),
                logo= project_dict.get("logo"),
                company_name= project_dict.get("company_name"),
                banners= project_dict.get("images") if project_dict.get("images") else None,
                coordinates= project_dict.get("coordinates")
            )
        )

        return ProjectModel(**project_dict)

    return None

def update_project_by_id(project_id: str, update_data: dict) -> Optional[ProjectModel]:
    update_dict = update_data.copy() 
    
    if "_id" in update_dict:
        update_dict.pop("_id")

    current_project = project_collection.find_one({"_id": project_id})
    old_exhibition_id = None
    if current_project:
        old_exhibition_id = current_project.get("exhibition_id")

    result = project_collection.update_one(
        {"_id": project_id},
        {"$set": update_dict}
    )

    if result.modified_count > 0:
        project_resume_dict = {
            "_id": project_id,
            "name": update_dict.get("name"),
            "logo": update_dict.get("logo"),
            "company_name": update_dict.get("company_name"),
            "banners": update_dict.get("images") if update_dict.get("images") else None,
            "coordinates": update_dict.get("coordinates")
        }

        user_repository.set_project(project_id, project_resume_dict)

        if "expositors" in update_dict and update_dict["expositors"]:
            expositor_ids = []
            for e in update_dict.get("expositors", []):
                if isinstance(e, dict):
                    if "_id" in e and e["_id"]:
                        expositor_ids.append(e["_id"])
                    elif "id" in e and e["id"]:
                        expositor_ids.append(e["id"])
                elif hasattr(e, 'id') and e.id:
                    expositor_ids.append(e.id)
                elif hasattr(e, '_id') and e._id:
                    expositor_ids.append(e._id)
            if expositor_ids:
                user_repository.set_project_resume_on_users_by_ids(expositor_ids, project_resume_dict)

        new_exhibition_id = update_dict.get("exhibition_id") or (current_project.get("exhibition_id") if current_project else None)
        
        try:
            if old_exhibition_id and old_exhibition_id != new_exhibition_id:
                exhibition_repository.remove_project(old_exhibition_id, project_id)

            if new_exhibition_id:
                exhibition_repository.add_project(
                    new_exhibition_id,
                    ExhibitionModel.ProjectResume(
                        _id=project_id,
                        name=project_resume_dict.get("name"),
                        logo=project_resume_dict.get("logo"),
                        company_name=project_resume_dict.get("company_name"),
                        banners= project_resume_dict.get("images") if project_resume_dict.get("images") else None,
                        coordinates= project_resume_dict.get("coordinates")
                    )
                )
        except Exception:
            pass

        updated_project = project_collection.find_one({"_id": project_id})
        
        if updated_project:
            try:
                if updated_project.get("_id"):
                    updated_project["_id"] = str(updated_project["_id"])
                return ProjectModel(**updated_project)
            except Exception as e:
                return None

    return None

def update_project_with_user(user_id: str, update_user: UserModel) -> int:
    result = project_collection.update_many(
        {"user_id": user_id},
        {"$set": {"user": update_user.model_dump(by_alias=True)}}
    )
    return result.modified_count

def delete_project_by_id(project_id: str) -> bool:
    try:
        review_collection.update_many(
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