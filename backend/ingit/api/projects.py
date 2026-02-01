"""
Projects API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Pydantic schemas
class ProjectBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    status: str = "active"
    visibility: str = "private"
    budget: float | None = None
    currency: str = "USD"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    budget: float | None = None


class Project(ProjectBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Endpoints
@router.get("/", response_model=List[Project])
async def list_projects():
    """List all projects"""
    # TODO: Implement with database
    return []


@router.post("/", response_model=Project, status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new project"""
    # TODO: Implement with database
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get project by ID"""
    # TODO: Implement with database
    raise HTTPException(status_code=404, detail="Project not found")


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project: ProjectUpdate):
    """Update project"""
    # TODO: Implement with database
    raise HTTPException(status_code=404, detail="Project not found")


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str):
    """Delete project (soft delete)"""
    # TODO: Implement with database
    raise HTTPException(status_code=404, detail="Project not found")
