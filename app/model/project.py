import uuid
from typing import Optional
from pydantic import BaseModel, Field, create_model
from user import UserModel

UserExpositor = create_model(
    "UserExpositor",
    id=(UserModel.model_fields["id"].annotation, ...),
    name=(UserModel.model_fields["name"].annotation, ...),
    _class=(UserModel.model_fields["class"].annotation, Field(..., alias="class")),
)
class ProjectModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str = Field(..., description="Project name")
    company_name: str = Field(..., description="Company Name")
    description: str = Field(..., description="Description")
    coordinates: int = Field(..., description="Coordinates")
    exhibition_id: str = Field(..., description="Exhibition id")
    expositors: list[UserExpositor] = Field(..., description="List users")
    images: list[str] = Field(..., description="List images")
    logo: str = Field(..., description="Logo")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "name": "Tech Corp",
                "company_name": "Tech Corporation",
                "description": "A tech company specializing in AI",
                "coordinates": 123,
                "exhibition_id": "exh_456",
                "expositors": [],
                "images": ["img1.png", "img2.png"],
                "logo": "logo.png"
            }
        }