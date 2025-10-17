from typing import List
from fastapi import APIRouter
from app.model.review import ReviewModel
from app.repository import review_repository


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

@router.get("", response_model=List[ReviewModel])
async def list_reviews():
    return review_repository.get_all_reviews()

@router.put("/{review_id}", response_model=ReviewModel)
async def update_review(review_id: str, review: ReviewModel):
    return review_repository.update_review(review_id, review)

@router.post("", response_model=ReviewModel)
async def create_review(review: ReviewModel):
    return review_repository.create_review(review)

@router.delete("/{review_id}", response_model=bool)
async def delete_review(review_id: str):
    return review_repository.delete_review(review_id)