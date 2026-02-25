from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .database import engine, Base, get_db
from .models import TravelProject, ProjectPlace
from .schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from .places import router as places_router

app = FastAPI(title="Travel Planner System")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(places_router)


@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    places = data.places or []
    
    project = TravelProject(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )
    db.add(project)
    await db.flush()
    
    if places:
        from .art_institute import validate_artwork
        
        for place_data in places:
            artwork = await validate_artwork(place_data.external_api_id)
            if artwork:
                place = ProjectPlace(
                    project_id=project.id,
                    external_api_id=artwork["id"],
                    external_api_title=artwork["title"],
                    external_api_url=artwork["url"],
                    notes=place_data.notes,
                )
                db.add(place)
    
    await db.commit()
    await db.refresh(project)
    return project


@app.get("/projects", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TravelProject))
    return result.scalars().all()


@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@app.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.start_date is not None:
        project.start_date = data.start_date
    
    await db.commit()
    await db.refresh(project)
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    if any(p.visited for p in project.places):
        raise HTTPException(status_code=400, detail="Cannot delete - has visited places")
    
    await db.delete(project)
    await db.commit()