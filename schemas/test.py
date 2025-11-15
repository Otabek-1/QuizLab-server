from pydantic import BaseModel
from typing import Optional

class TestCreate(BaseModel):
    title:str
    description: Optional[str] = None
    duration_minutes: int
    max_attempts: int