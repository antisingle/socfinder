from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import field_validator
from datetime import date
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
    money_req_grant: Optional[float] = None
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
    date_req: Optional[date] = None
    inn: Optional[str] = None
    ogrn: Optional[str] = None
    implem_start: Optional[date] = None
    implem_end: Optional[date] = None
    rate: Optional[float] = None
    cofunding: Optional[float] = None
    total_money: Optional[float] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    tasks: Optional[str] = None
    soc_signif: Optional[str] = None
    pj_geo: Optional[str] = None
    target_groups: Optional[str] = None
    address: Optional[str] = None
    web_site: Optional[str] = None
    req_num: Optional[str] = None
    link: Optional[str] = None
    okato: Optional[str] = None
    oktmo: Optional[str] = None
    level: Optional[str] = None

class ProjectTableResponse(BaseModel):
    id: int
    name: Optional[str] = None
    org: Optional[str] = None
    region: Optional[str] = None
    year: Optional[int] = None
    direction: Optional[str] = None
    money_req_grant: Optional[float] = None
    winner: Optional[bool] = None
    contest: Optional[str] = None
    
    @field_validator('winner', mode='before')
    @classmethod
    def validate_winner(cls, v):
        if v is None:
            return False
        return v
    
    class Config:
        from_attributes = True

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

@router.get("/projects/table", response_model=List[ProjectTableResponse])
def get_projects_table(
    region: Optional[str] = None,
    year: Optional[int] = None,
    direction: Optional[str] = None,
    winner: Optional[bool] = None,
    limit: int = Query(default=100, le=10000),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="id", description="Поле для сортировки"),
    sort_order: str = Query(default="asc", description="Порядок сортировки: asc/desc"),
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    return service.get_projects_table(
        region=region,
        year=year,
        direction=direction,
        winner=winner,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get("/projects/export")
def export_projects(
    region: Optional[str] = None,
    year: Optional[int] = None,
    direction: Optional[str] = None,
    winner: Optional[bool] = None,
    format: str = Query(default="csv", description="Формат экспорта: csv/excel"),
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    return service.export_projects(
        region=region,
        year=year,
        direction=direction,
        winner=winner,
        format=format
    )

@router.get("/projects/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    service = ProjectService(db)
    return service.get_project_by_id(project_id)
