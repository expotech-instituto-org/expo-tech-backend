from pydantic import BaseModel
from typing import List, Optional

class ReviewCreate(BaseModel):

    class GradeResume(BaseModel):
        name: str
        score: float

    grades: List[GradeResume]

    project_id: str
    exhibition_id: str

    comment: Optional[str] = None

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "grades": [
                    {"name": "Ideia", "score": 4.5},
                    {"name": "Apresentação", "score": 4.0}
                ],
                "project_id": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
                "exhibition_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
                "comment": "Excelente projeto!"
            }
        }