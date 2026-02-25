from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .models import TravelProject, ProjectPlace
from .schemas import PlaceCreate, PlaceUpdate, PlaceResponse
from .art_institute import validate_artwork

router = APIRouter(prefix="/projects/{project_id}/places", tags=["places"])


@router.post("", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
async def add_place(
    project_id: int,
    place_data: PlaceCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if len(project.places) >= 10:
        raise HTTPException(status_code=422, detail="Max 10 places per project")
    
    if any(p.external_api_id == place_data.external_api_id for p in project.places):
        raise HTTPException(status_code=409, detail="Place already in project")
    
    artwork = await validate_artwork(place_data.external_api_id)
    if not artwork:
        raise HTTPException(status_code=422, detail="Artwork not found in API")
    
    place = ProjectPlace(
        project_id=project_id,
        external_api_id=artwork["id"],
        external_api_title=artwork["title"],
        external_api_url=artwork["url"],
        notes=place_data.notes,
    )
    db.add(place)
    await db.commit()
    await db.refresh(place)
    return place


@router.get("", response_model=list[PlaceResponse])
async def list_places(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectPlace).where(ProjectPlace.project_id == project_id)
    )
    return result.scalars().all()


@router.get("/{place_id}", response_model=PlaceResponse)
async def get_place(project_id: int, place_id: int, db: AsyncSession = Depends(get_db)):
    place = await db.get(ProjectPlace, place_id)
    if not place or place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.patch("/{place_id}", response_model=PlaceResponse)
async def update_place(
    project_id: int,
    place_id: int,
    data: PlaceUpdate,
    db: AsyncSession = Depends(get_db),
):
    place = await db.get(ProjectPlace, place_id)
    if not place or place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found")
    
    if data.notes is not None:
        place.notes = data.notes
    if data.visited is not None:
        place.visited = data.visited
        
        project = await db.get(TravelProject, project_id)
        if place.visited and all(p.visited for p in project.places):
            project.completed = True
    
    await db.commit()
    await db.refresh(place)
    return place


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_place(
    project_id: int,
    place_id: int,
    db: AsyncSession = Depends(get_db),
):
    place = await db.get(ProjectPlace, place_id)
    if not place or place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found")
    
    await db.delete(place)
    
    project = await db.get(TravelProject, project_id)
    if project:
        project.completed = False
    
    await db.commit()