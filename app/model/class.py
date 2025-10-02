import uuid
from typing import Optional
from pydantic import BaseModel, Field

class ClassModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str = Field(..., description="Company name")
    year: str = Field(..., description="Company name")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "name": "3ºF Dev",
                "ano": "2025"
            }
        }