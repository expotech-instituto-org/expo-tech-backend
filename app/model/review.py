import uuid
from typing import Optional, List
from pydantic import BaseModel, Field

class ReviewModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")

    class Grade(BaseModel):
        name: str = Field(..., description="Criteria name")
        score: float = Field(..., ge=0, le=5, description="Score between 0 and 5")
        weight: float = Field(..., ge=0, le=1, description="Criteria weight")
    
    grades: List[Grade] = Field(...)
    project_id: Optional[str] = Field(None, alias="_id")
    exhibition_id: str = Field(...)

    class UserResume(BaseModel):
        id: Optional[str] = Field(None, alias="_id")
        name: str = Field(..., description="User full name")

        class UserRole(BaseModel):
            id: Optional[str] = Field(None, alias="_id")
            name: str = Field(..., description="User full name")
            weight: float = Field(..., ge=0, le=1, description="User weight for review scoring")

        role: UserRole = Field(..., description="User role")
    
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
                    "role": {
                        "_id": str(uuid.uuid4()),
                        "name": "Jurídico",
                        "weight": 0.7,
                    },
                },
                "comment": "Ótimo projeto, bem executado!",
                "active": True,
            }
        }