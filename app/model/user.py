import uuid
from typing import Optional
from pydantic import BaseModel, Field
from app.model.role import RoleModel

class UserModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    email: str = Field(...)
    phone: str = Field(...)
    password: str = Field(...)
    role: RoleModel = Field(...)
    profile_picture: Optional[str] = Field(...)
    knowledge: Optional[str] = Field(...)
    age: Optional[int] = Field(...)
    company: Optional[str] = Field(...)
    class_field: Optional[str] = Field(alias="class", default=None)
    # project: ProjectModel = Field(...)
    # reviews: ReviewModel = Field(...)
    active: bool = Field(default=True)
    

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
                "active": True,
            }
        }