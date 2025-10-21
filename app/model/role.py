import uuid
from typing import Optional
from pydantic import BaseModel, Field

class RoleModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str = Field(..., description="Role name")
    permissions: list[str] = Field([], description="List of permissions associated with the role")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "name": "admin",
                "permissions": ["read_role"]
            }
        }
        
        