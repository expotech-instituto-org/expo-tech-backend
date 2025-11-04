import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class ExhibitionUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    banners: Optional[list[str]] = None

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
                "start_date": "2025-01-01",
                "end_date": "2025-01-01",
                "banners": ["https://example.com/banner1.png", "https://example.com/banner2.png"],
                "criteria": [
                    {"name": "Ideia", "weight": 0.5 },
                    {"name": "Execução", "weight": 0.5 },
                ],
                "roles": [
                    {"_id": str(uuid.uuid4()), "name": "Guest", "weight": 0.8 },
                ]
            }
        }