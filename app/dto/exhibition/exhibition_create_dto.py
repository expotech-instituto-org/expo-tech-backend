from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class ExhibitionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    start_date: datetime
    end_date: datetime

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Exhibition name",
                "description": "Exhibition description",
                "image": "https://br.pinterest.com/pin/345088390217105894/",
                "start_date": "2025-01-01",
                "end_date": "2025-01-01"
            }
        }