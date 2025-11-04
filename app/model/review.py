import uuid
from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field

from app.model.project import ProjectModel
from app.model.user import UserModel


class ReviewModel(BaseModel):
    id: Optional[str] = Field(alias="_id")

    class Grade(BaseModel):
        name: str = Field(..., description="Criteria name")
        score: float = Field(..., ge=0, le=5, description="Score between 0 and 5")
        weight: float = Field(..., ge=0, le=1, description="Criteria weight")
    
    grades: List[Grade] = Field(...)

    class ProjectResume(BaseModel):
        id: str = Field(..., alias="_id")
        name: str = Field(..., description="Project name")

    project: Union[ProjectResume, ProjectModel] = Field(...)

    class ExhibitionResume(BaseModel):
        id: str = Field(..., alias="_id")
        name: str = Field(..., description="Exhibition name")

    exhibition: ExhibitionResume = Field(...)

    class UserResume(BaseModel):
        id: str = Field(None, alias="_id")
        name: str = Field(..., description="User full name")

        class UserRole(BaseModel):
            id: Optional[str] = Field(None, alias="_id")
            name: str = Field(..., description="User full name")
            weight: float = Field(..., ge=0, le=1, description="User weight for review scoring")

        role: UserRole = Field(..., description="User role")
    
    user: Union[UserResume, UserModel] = Field(...)
    comment: Optional[str] = Field(None, max_length=300)

    class Config:
        validate_by_name = True
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
                    "role": {
                        "_id": str(uuid.uuid4()),
                        "name": "Jurídico",
                        "weight": 0.7,
                    },
                },
                "comment": "Ótimo projeto, bem executado!",
            }
        }