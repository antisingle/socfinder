from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import field_validator
from app.core.database import get_db
from app.models.project import Project
from app.services.project_service import ProjectService
from pydantic import BaseModel

router = APIRouter()

class ProjectResponse(BaseModel):
    id: int
    name: Optional[str] = None
    contest: Optional[str] = None
    year: Optional[int] = None
    direction: Optional[str] = None
    region: Optional[str] = None
    org: Optional[str] = None
    winner: Optional[bool] = None
    money_req_grant: Optional[int] = None
    coordinates: Optional[dict] = None
    
    @field_validator('winner', mode='before')
    @classmethod
    def validate_winner(cls, v):
        if v is None:
            return False
        return v
    
    class Config:
        from_attributes = True

class ProjectDetail(ProjectResponse):
    description: Optional[str]
    goal: Optional[str]
    tasks: Optional[str]
    address: Optional[str]
    web_site: Optional[str]
    link: Optional[str]

@router.get("/projects", response_model=List[ProjectResponse])
def get_projects(
    region: Optional[str] = None,
    year: Optional[int] = None,
    direction: Optional[str] = None,
    winner: Optional[bool] = None,
    limit: int = Query(default=100, le=10000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    return service.get_projects(
        region=region,
        year=year, 
        direction=direction,
        winner=winner,
        limit=limit,
        offset=offset
    )

@router.get("/projects/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    service = ProjectService(db)
    return service.get_project_by_id(project_id)
