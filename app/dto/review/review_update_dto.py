from pydantic import BaseModel
from typing import List, Optional

class ReviewUpdate(BaseModel):
    class GradeUpdate(BaseModel):
        name: str
        score: float
        weight: float

    grades: Optional[List[GradeUpdate]] = None
    comment: Optional[str] = None

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "grades": [
                    {"name": "Ideia", "score": 4.5, "weight": 0.5},
                    {"name": "Execução", "score": 4.0, "weight": 0.3},
                    {"name": "Apresentação", "score": 3.5, "weight": 0.2}
                ],
                "comment": "Ótima execução do projeto!"
            }
        }