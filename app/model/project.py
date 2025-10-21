import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ProjectModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(..., description="Project name")
    company_name: str = Field(..., description="Company Name")
    description: str = Field(..., description="Description")
    coordinates: int = Field(..., description="Coordinates")
    exhibition_id: str = Field(..., description="Exhibition id")

    class UserResume(BaseModel):
        id: Optional[str] = Field(None, alias="_id")
        name: str = Field(..., description="User full name")
    
    expositors: list[UserResume] = Field(..., description="List users")
    images: list[str] = Field(..., description="List images")
    logo: str = Field(..., description="Logo")
    deactivation_date: Optional[datetime] = Field(..., description="Exhibition deactivation date")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "name": "Tech Corp",
                "company_name": "Tech Corporation",
                "description": "A tech company specializing in AI",
                "coordinates": 1,
                "exhibition_id": str(uuid.uuid4()),
                "expositors": [
                    {
                        "_id": str(uuid.uuid4()),
                        "name": "John Doe"
                    }
                ],
                "images": ["img1.png", "img2.png"],
                "logo": "logo.png",
            }
        }