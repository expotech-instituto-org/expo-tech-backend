from pydantic import BaseModel
from typing import List, Optional

class ReviewCreate(BaseModel):
    exhibition_id: str
    project_id: str

    class GradeCreate(BaseModel):
        name: str
        score: float
        weight: float

    grades: List[GradeCreate]

    class UserCreate(BaseModel):
        id: str
        role_id: str

    user: UserCreate

    comment: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "8f6e5c3e-5a1b-4c3a-8d3a-7c9e0f4c3b2d",
                "grades": [
                    {"name": "Ideia", "score": 4.5, "weight": 0.5},
                    {"name": "Apresentação", "score": 4.0, "weight": 0.3}
                ],
                "project_id": "c2a1b1c2-3e3d-4a2a-9f1a-8b9c0f4a5d6e",
                "exhibition_id": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
                "user": {
                    "_id": "b1c2d3e4-f5a6-b7c8-d9e0-f1a2b3c4d5e6",
                    "name": "Professor",
                    "role": {
                        "_id": "d2e3f4a5-b6c7-d8e9-f0a1-b2c3d4e5f6a7",
                        "name": "Professor",
                        "weight": 0.7
                    }
                },
                "comment": "Excelente projeto!"
            }
        }