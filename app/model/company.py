import uuid
from typing import Optional
from pydantic import BaseModel, Field

class CompanyModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str = Field(...)
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "name": "Tech Corp"
            }
        }