from typing import Optional
from app.database import db
from app.model.review import ReviewModel
from app.dto.review.review_create_dto import ReviewCreate
from app.dto.review.review_update_dto import ReviewUpdate
from app.dto.review.review_resume_dto import ReviewResume
import uuid

reviews_collection = db["reviews"]    

def get_all_reviews() -> list[ReviewModel]:
    reviews_cursor = reviews_collection.find()
    return [ReviewModel(**review) for review in reviews_cursor]

def create_review(dto: ReviewCreate, ) -> Optional[ReviewModel]:
    review_model = ReviewModel(
        _id=str(uuid.uuid4()),
        grades=[ReviewModel.Grade(**grade.model_dump()) for grade in dto.grades],
        project=ReviewModel.ProjectResume(
            _id=dto.project.id,
            name=dto.project.name
        ),
        exhibition=ReviewModel.ExhibitionResume(
            _id=dto.exhibition.id,
            name=dto.exhibition.name
        ),
        user=ReviewModel.UserResume(
            _id="",
            name="(nome do usuário)",
            role=ReviewModel.UserResume.UserRole(
                _id="",
                name="(nome do papel)",
                weight=1.0
            )
        ),
        comment=dto.comment    
    )
    result = reviews_collection.insert_one(review_model.model_dump())
    if result.inserted_id:
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

def delete_review(review_id: str) -> bool:
    result = reviews_collection.delete_one({"id": review_id})
    return result.deleted_count > 0

def get_reviews_by_exhibition(exhibition_id: str):
    reviews_cursor = reviews_collection.find({"exhibition._id": exhibition_id})
    return [ReviewModel(**review) for review in reviews_cursor]

def get_reviews_by_project(project_id: str):
    reviews_cursor = reviews_collection.find({"project._id": project_id})
    print(reviews_cursor)
    return [print(review) for review in reviews_cursor]