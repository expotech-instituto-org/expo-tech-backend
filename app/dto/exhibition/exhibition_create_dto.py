from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class ExhibitionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Exhibition name",
                "description": "Exhibition description",
                "start_date": "2025-01-01",
                "end_date": "2025-01-01"
            }
        }