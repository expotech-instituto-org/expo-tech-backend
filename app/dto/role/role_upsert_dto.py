from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional

class RoleUpsert(BaseModel):
    name: str = Field(..., description="Role name")
    permissions: Optional[list[str]] = Field(None, description="List of permissions associated with the role")


class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "admin",
                "permissions": ["read_role", "write_role"]
            }
        }