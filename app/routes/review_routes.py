from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.model.review import ReviewModel
from app.repository import review_repository
from app.dto.review.review_resume_dto import ReviewResume
from app.dto.review.review_create_dto import ReviewCreate
from app.routes.security import User, get_current_user
from app import constants as c
router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

@router.get("", response_model=List[ReviewModel])
async def list_reviews():
    return review_repository.get_all_reviews()

@router.post("", response_model=ReviewModel)
async def create_review(review: ReviewCreate, current_user: Annotated[User, Depends(get_current_user)] = None):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        created = review_repository.create_review(review, current_user)
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{review_id}", response_model=ReviewModel)
async def delete_review(review_id: str):
    try:
        review = review_repository.delete_review(review_id)
        return review
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/exhibition/{exhibition_id}", response_model=List[ReviewModel])
async def get_reviews_by_exhibition(exhibition_id: str):
    return review_repository.get_reviews_by_exhibition(exhibition_id)

@router.get("/project/", response_model=List[ReviewResume|ReviewModel])
async def get_reviews_by_user(project_id: Optional[str] = None, current_user: Annotated[User, Depends(get_current_user)] = None):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not project_id:
        project_id = current_user.project_id
    if not project_id:
        raise HTTPException(status_code=400, detail="Project ID is required")
    if c.PERMISSION_READ_REVIEW not in current_user.permissions and current_user.project_id != project_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    reviews = review_repository.get_reviews_by_project(project_id)
    if c.PERMISSION_READ_REVIEW in current_user.permissions:
        return reviews
    return [ReviewResume(
        id=review.id,
        grades=[ReviewResume.Grade(**grade.model_dump()) for grade in review.grades],
        project_id=project_id
    ) for review in reviews]