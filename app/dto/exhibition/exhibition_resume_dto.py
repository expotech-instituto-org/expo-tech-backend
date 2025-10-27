from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ExhibitionResumeDTO(BaseModel):
    id: str = None
    name: str
    image: Optional[str] = None
    start_date: datetime
    end_date: datetime

