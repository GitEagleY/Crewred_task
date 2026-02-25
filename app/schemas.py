from pydantic import BaseModel
from datetime import date
from typing import Optional


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    places: Optional[list["PlaceCreate"]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    completed: bool
    places: list["PlaceResponse"] = []

    class Config:
        from_attributes = True


class PlaceCreate(BaseModel):
    external_api_id: str
    notes: Optional[str] = None


class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    visited: Optional[bool] = None


class PlaceResponse(BaseModel):
    id: int
    external_api_id: str
    external_api_title: str
    external_api_url: Optional[str]
    notes: Optional[str]
    visited: bool

    class Config:
        from_attributes = True


ProjectCreate.model_rebuild()