from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str]
    start_date: Optional[date]


class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    start_date: Optional[date]


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    completed: bool
    
    class Config:
        from_attributes = True