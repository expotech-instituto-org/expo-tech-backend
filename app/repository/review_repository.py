from typing import Optional
from app.database import db
from app.model.review import ReviewModel
from app.dto.review import ReviewCreate, ReviewUpdate
import uuid

reviews_collection = db["reviews"]    

def get_all_reviews() -> list[ReviewModel]:
    reviews_cursor = reviews_collection.find()
    return [ReviewModel(**review) for review in reviews_cursor]

def create_review(dto: ReviewCreate) -> ReviewModel:
    review_model = ReviewModel(
        id=str(uuid.uuid4()),
        grades=[ReviewModel.Grade(**grade.model_dump()) for grade in dto.grades],
        project_id=dto.project_id,
        exhibition_id=dto.exhibition_id,
        user=ReviewModel.UserResume(
            id=dto.user.id,
            name="(nome do usuário)",
            role=ReviewModel.UserResume.UserRole(
                id=dto.user.role_id,
                name="(nome do papel)",
                weight=1.0
            )
        ),
        comment=dto.comment    
    )
    return review_model

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