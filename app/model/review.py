import uuid
from typing import Optional, List
from pydantic import BaseModel, Field

from app.model.user import UserModel
from app.model.project import ProjectModel
from app.model.exhibition import CriteriaModel

class Grade(CriteriaModel):
    score: float = Field(..., ge=0, le=5, description="Score between 0 and 5")

    class Config:
        fields = {
            "name": {"alias": "criteria", "description": "Criteria name"},
            "weight": {"description": "Criteria weight"},
        }
        extra = "ignore"
        allow_population_by_field_name = True


class ProjectResume(ProjectModel):
    class Config:
        fields = {
            "id": {"alias": "_id", "description": "Project ID"}
        }
        allow_population_by_field_name = True
        extra = "ignore"


class UserResume(UserModel):
    class Config:
        fields = {
            "id": {"alias": "_id", "description": "User ID"},
            "name": {"description": "User full name"},
            "role": {"description": "User role"},
            "weight": {"description": "User weight for review scoring"},
        }
        allow_population_by_field_name = True
        extra = "ignore"


class ReviewModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    grades: List[Grade] = Field(...)
    project: ProjectResume = Field(...)
    exhibition_id: str = Field(...)
    user: UserResume = Field(...)
    comment: Optional[str] = Field(None, max_length=300)
    active: bool = Field(default=True)

    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "grades": [
                    {"criteria": "Ideia", "weight": 0.5, "score": 4.5},
                    {"criteria": "Execução", "weight": 0.3, "score": 4.0},
                    {"criteria": "Apresentação", "weight": 0.2, "score": 3.5},
                ],
                "project": {
                    "_id": str(uuid.uuid4()),
                    "name": "Projeto Exemplo",
                },
                "exhibition_id": str(uuid.uuid4()),
                "user": {
                    "_id": str(uuid.uuid4()),
                    "name": "Avaliador Exemplo",
                    "role": "jurado",
                    "weight": 1.0,
                },
                "comment": "Ótimo projeto, bem executado!",
                "active": True,
            }
        }