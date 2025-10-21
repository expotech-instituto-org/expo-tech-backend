from pydantic import BaseModel
import uuid

class ReviewResume(BaseModel):
    id: str

    class Grade(BaseModel):
        name: str
        score: float
        weight: float

    grades: list[Grade]
    project_id: str

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
                "project_id": str(uuid.uuid4()),
            }
        }