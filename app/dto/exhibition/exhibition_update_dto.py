import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class ExhibitionUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    start_date: datetime
    end_date: datetime

    class Criteria(BaseModel):
        name: str
        weight: float

    criteria: list[Criteria]

    class Role(BaseModel):
        id: str
        name: str
        weight: float

    roles: list[Role]

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Exhibition name",
                "description": "Exhibition description",
                "image": "https://br.pinterest.com/pin/345088390217105894/",
                "start_date": "2025-01-01",
                "end_date": "2025-01-01",
                "criteria": [
                    {"name": "Ideia", "weight": 0.5 },
                    {"name": "Execução", "weight": 0.5 },
                ],
                "roles": [
                    {"_id": str(uuid.uuid4()), "name": "Guest", "weight": 0.8 },
                    {"_id": str(uuid.uuid4()), "name": "Professor Tech", "weight": 0.2 },
                ]
            }
        }