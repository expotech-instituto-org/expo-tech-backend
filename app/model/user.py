import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.model.role import RoleModel


class UserModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    email: str = Field(...)
    phone: Optional[str] = Field(None)
    password: bytes = Field(...)
    name: Optional[str] = Field(None)
    role: RoleModel = Field(...)
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    knowledge: Optional[str] = Field(None, description="How the user got to know about the event")
    age: Optional[int] = Field(None, description="User age")
    company: Optional[str] = Field(None, description="Company name associated with the user")
    class_field: Optional[str] = Field(None, alias="class")

    class ProjectResume(BaseModel):
        id: str = Field(..., alias="_id", description="Project ID")
        name: str = Field(..., description="Project name")
        logo: str = Field(..., description="Project logo URL")
        company_name: str = Field(..., description="Company name associated with the project")

    project: Optional[ProjectResume] = Field(None, description="User's project summary")

    class ReviewResume(BaseModel):
        id: str = Field(..., alias="_id", description="Review ID")
        project_id: str = Field(..., description="Project ID")
        exhibition_id: str = Field(..., description="Exhibition ID")
        comment: Optional[str] = Field(None, max_length=300, description="Review comment")

    reviews: list[ReviewResume] = Field([], description="List of user reviews")
    deactivation_date: Optional[datetime] = Field(None, description="Exhibition deactivation date")
    favorited_projects: list[str] = Field([], description="List of favorited projects")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "email": "email@email.com",
                "password": "xxxxxxx",
                "phone": "(11) 99999-9999",
                "role": {
                    "_id": str(uuid.uuid4()),
                    "name": "admin"
                },
                "company": "PicPay",
                "knowledge": "Amigos",
                "age": 30,
                "class": "A",
                "profile_picture": "https://link-to-image.com/image.png",
                "project": {
                    "_id": str(uuid.uuid4()),
                    "name": "Projeto Exemplo",
                    "logo": "https://link-to-image.com/image.png",
                    "company_name": "Tech Corporation"
                },
                "reviews": [
                    {
                        "_id": str(uuid.uuid4()),
                        "project_id": str(uuid.uuid4()),
                        "exhibition_id": str(uuid.uuid4()),
                        "comment": "Great project!"
                    }
                ],
                "favorited_projects": [str(uuid.uuid4())],
            }
        }
