from typing import Optional
from app.database import db
from app.model.review import ReviewModel
from app.model.user import UserModel
from app.dto.review.review_create_dto import ReviewCreate
from app.dto.review.review_update_dto import ReviewUpdate
from app.dto.review.review_resume_dto import ReviewResume
from app.repository import exhibition_repository, project_repository
import uuid
from app.model.role import RoleModel


from app.routes.security import User
from app.constants import DEFAULT_ROLE_ID

reviews_collection = db["reviews"]    

def get_all_reviews() -> list[ReviewModel]:
    reviews_cursor = reviews_collection.find()
    return [ReviewModel(**review) for review in reviews_cursor]

def create_review(dto: ReviewCreate, current_user: User) -> Optional[ReviewModel]:
    exhibition = exhibition_repository.get_exhibition_by_id(dto.exhibition_id)
    if exhibition is None:
        raise ValueError("Exhibition not found")
    project = next((p for p in exhibition.projects if p.id == dto.project_id), None)
    if project is None:
        raise ValueError("Project not found")

    criteria_weight_map = {c.name: c.weight for c in exhibition.criteria}
    exhibition_criteria_names = set(criteria_weight_map.keys())
    review_grade_names = set([g.name for g in dto.grades])
    if exhibition_criteria_names != review_grade_names:
        raise ValueError("Grades do not match exhibition criteria")


    exhibition_role = next((r for r in exhibition.roles if r.id == current_user.role.id), None)
    if exhibition_role is None:
        exhibition_role = next(r for r in exhibition.roles if r.id == DEFAULT_ROLE_ID)

    review_model = ReviewModel(
        _id=str(uuid.uuid4()),
        grades=[
            ReviewModel.Grade(
                name=grade.name,
                score=grade.score,
                weight=criteria_weight_map[grade.name]
            ) for grade in dto.grades
        ],
        project=ReviewModel.ProjectResume(
            _id=project.id,
            name=project.name
        ),
        exhibition=ReviewModel.ExhibitionResume(
            _id=exhibition.id,
            name=exhibition.name
        ),
        user=ReviewModel.UserResume(
            _id=current_user.id,
            name=current_user.email,
            role=ReviewModel.UserResume.UserRole(
                _id=exhibition_role.id,
                name=exhibition_role.name,
                weight=exhibition_role.weight
            )
        ),
        comment=dto.comment
    )

    result = reviews_collection.insert_one(review_model.model_dump(by_alias=True))
    if result.inserted_id:
        user_repository.add_review_to_user(
            review_model.user._id,
            review_model.project._id,
            review_model.exhibition._id,
            review_model.comment
        )
        return review_model
    return None

def update_review(review_id: str, update_data: ReviewUpdate) -> Optional[ReviewModel]:
    update_fields = {}

    if update_data.grades is not None:
        update_fields["grades"] = [grade.model_dump() for grade in update_data.grades]
    if update_data.comment is not None:
        update_fields["comment"] = update_data.comment
    if not update_fields:
        return None 
    
    result = reviews_collection.update_one(
        {"_id": review_id},
        {"$set": update_fields}
    )

    if result.modified_count > 0:
        updated_review = reviews_collection.find_one({"_id": update_data.id})
        if updated_review:
            return ReviewModel(**updated_review)
    return None

def get_review_by_id(review_id: str) -> Optional[ReviewModel]:
    review_data = reviews_collection.find_one({"_id": review_id})
    if review_data:
        return ReviewModel(**review_data)
    return None

def delete_review(review_id: str) -> Optional[ReviewModel]:
    review = reviews_collection.find_one({"_id": review_id})
    if not review:
        raise ValueError("Review not found")
    result = reviews_collection.delete_one({"_id": review_id})
    if result.deleted_count == 0:
        raise Exception("Error deleting review")
    return ReviewModel(**review)

def is_role_in_use(role_id: str) -> bool:
    review = reviews_collection.find_one(
        {"user.role.id": role_id}
    )
    return review is not None

def get_reviews_by_exhibition(
    exhibition_id: str,
    entire_project: bool = False,
    entire_user: bool = False
) -> list[ReviewModel]:
    pipeline = [
        {
            "$match": {
                "exhibition._id": exhibition_id
            }
        }
    ]
    if entire_project:
        pipeline.extend([
            {
                "$lookup": {
                    "from": "projects",
                    "localField": "project._id",
                    "foreignField": "_id",
                    "as": "project"
                }
            },
            {
                "$unwind": "$project"
            }
        ])
    if entire_user:
        pipeline.extend([
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user._id",
                    "foreignField": "_id",
                    "as": "user"
                }
            },
            {
                "$unwind": "$user"
            }
        ])

    reviews_cursor = reviews_collection.aggregate(pipeline)
    return [ReviewModel(**review) for review in reviews_cursor]

def get_reviews_by_project(project_id: str) -> list[ReviewModel]:
    reviews_cursor = reviews_collection.find({"project._id": project_id})

    return [ReviewModel(**review) for review in reviews_cursor]

def update_reviews_with_role(role_id: str, updated_role: RoleModel) -> int:
    result = reviews_collection.update_many(
        {"role.id": role_id},
        {"$set": {"role": updated_role.model_dump(by_alias=True)}}
    )
    return result.modified_count

def update_reviews_with_user(user_id: str, update_user: UserModel) -> int:
    result = reviews_collection.update_many(
        {"user._id": user_id},
        {"$set": {"user": update_user.model_dump(by_alias=True)}}
    )
    return result.modified_count