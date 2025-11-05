from pydantic import BaseModel, Field

class KnowledgeCreateDTO(BaseModel):
    name: str = Field(..., description="Knowledge name")
    
    class config:
        validate_by_name = True
        schema_extra = {
            "example": {
                "name": "Mathematics"
            }
        }