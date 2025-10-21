from typing import Optional

from pydantic import BaseModel, Field
import uuid

class UserCreate(BaseModel):
    email: str
    phone: Optional[str] = None
    password: str
    name: str
    role_id: Optional[str] = None
    profile_picture: Optional[str] = None
    knowledge: Optional[str] = None
    age: Optional[int] = None
    company: Optional[str] = None
    class_field: Optional[str] = Field(None, alias="class")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "email": "email@email.com",
                "phone": "(11) 99999-9999",
                "password": "xxxxxxx",
                "name": "John Doe",
                "role_id": str(uuid.uuid4()),
                "profile_picture": "url",
                "knowledge": "Python",
                "age": 30,
                "company": "PicPay",
                "class": "A",
            }
        }