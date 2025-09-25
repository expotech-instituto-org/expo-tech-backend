import uuid
from typing import Optional
from pydantic import BaseModel, Field

class KnowledgeModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str = Field(..., description="Knowledge name")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "name": "Knowledge name"
            }
        }
