import uuid
from typing import Optional, List
from app.database import db
from app.model.project import ProjectModel
from app.model.review import ReviewModel
from app.model.user import UserModel


project_collection = db["projects"]
review_collection = db["reviews"]
user_collection = db["users"]
exhibition_collection = db["exhibitions"]


# -------------------------------
# GET /projects/{id}
# -------------------------------
def get_project_by_id(project_id: str) -> Optional[ProjectModel]:
    project_data = project_collection.find_one({"_id": project_id})
    if project_data:
        return ProjectModel(**project_data)
    return None


# -------------------------------
# GET /projects/
# -------------------------------
def get_all_projects() -> List[ProjectModel]:
    projects = project_collection.find()
    return [ProjectModel(**p) for p in projects]


# -------------------------------
# POST /projects/
# -------------------------------
def add_project(project: ProjectModel) -> Optional[ProjectModel]:
    project_dict = project.model_dump(by_alias=True)
    project_dict["_id"] = str(uuid.uuid4())

    # Insert the new project into the projects collection
    result = project_collection.insert_one(project_dict)

    if result.inserted_id:
        # Update users to link them to the new project
        expositor_ids = [e["_id"] for e in project_dict["expositors"]]
        user_collection.update_many(
            {"_id": {"$in": expositor_ids}},
            {"$set": {"project_id": project_dict["_id"]}}
        )

        # Add the new project to the corresponding exhibition
        exhibition_collection.update_one(
            {"_id": project_dict["exhibition_id"]},
            {"$push": {"projects": project_dict}}
        )

        return ProjectModel(**project_dict)

    return None


# -------------------------------
# PUT /projects/{id}
# Update project and related users and exhibition
# -------------------------------
def update_project_by_id(project_id: str, update_data: ProjectModel) -> Optional[ProjectModel]:
    update_dict = update_data.model_dump(by_alias=True)

    result = project_collection.update_one(
        {"_id": project_id},
        {"$set": update_dict}
    )

    if result.modified_count > 0:
        # Update users linked to the project
        project_resume = {
            "_id": project_id,
            "name": update_dict.get("name"),
            "logo": update_dict.get("logo"),
            "company_name": update_dict.get("company_name")
        }

        user_collection.update_many(
            {"project._id": project_id},
            {"$set": {"project": project_resume}}
        )

        # Update users if expositors changed
        if "expositors" in update_dict:
            expositor_ids = [e["_id"] for e in update_dict["expositors"]]
            user_collection.update_many(
                {"_id": {"$in": expositor_ids}},
                {"$set": {"project": project_resume}}
            )

        # Update the project in the exhibition's projects array
        exhibition_collection.update_one(
            {"projects._id": project_id},
            {"$set": {"projects.$": update_dict}}
        )

        updated_project = project_collection.find_one({"_id": project_id})
        if updated_project:
            return ProjectModel(**updated_project)

    return None


# -------------------------------
# DELETE /projects/{id}
# Delete project and clean up related data
# -------------------------------
def delete_project_by_id(project_id: str) -> bool:
    # Deactivate related reviews
    review_collection.update_many(
        {"project_id": project_id},
        {"$set": {"active": False}}
    )

    # Detach project from users
    user_collection.update_many(
        {"project._id": project_id},
        {"$unset": {"project": ""}}
    )

    # Remove the project from exhibitions
    exhibition_collection.update_many(
        {"projects._id": project_id},
        {"$pull": {"projects": {"_id": project_id}}}
    )

    # Remove the project itself
    result = project_collection.delete_one({"_id": project_id})
    return result.deleted_count > 0