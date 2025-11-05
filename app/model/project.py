import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ProjectModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(..., description="Project name")
    company_name: str = Field(..., description="Company Name")
    description: str = Field(..., description="Description")
    coordinates: Optional[int] = Field(None, description="Coordinates")
    exhibition_id: str = Field(..., description="Exhibition id")

    class UserResume(BaseModel):
        id: Optional[str] = Field(None, alias="_id")
        name: Optional[str] = Field(None, description="User full name")
        profile_picture: Optional[str] = Field(None, description="User profile picture")
        class_field: Optional[str] = Field(None, description="User class")
    
    expositors: list[UserResume] = Field(..., description="List users")
    images: Optional[list[str]] = Field(default_factory=list, description="List images")
    logo: Optional[str] = Field(None, description="Logo")
    deactivation_date: Optional[datetime] = Field(None, description="Exhibition deactivation date")

    class CriteriaResume(BaseModel):
        name: str = Field(..., description="Criteria name")
        score: float = Field(..., description="Criteria score")

    criterias: Optional[List[CriteriaResume]] = Field(None, description="List of criterias")
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
                        "name": "John Doe",
                        "profile_picture": "profile1.png"
                    }
                ],
                "images": ["img1.png", "img2.png"],
                "logo": "logo.png",
            }
        }