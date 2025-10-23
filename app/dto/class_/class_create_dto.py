from pydantic import BaseModel, Field

class ClassCreateDTO(BaseModel):
    name: str = Field(..., description="Class name")
    year: str = Field(..., description="School year")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "3ºF Dev",
                "year": "2025"
            }
        }
