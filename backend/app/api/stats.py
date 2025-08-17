from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.stats_service import StatsService
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

class OverviewStats(BaseModel):
    total_projects: int
    total_winners: int
    total_money: float
    regions_count: int
    organizations_count: int

class RegionStats(BaseModel):
    region: str
    projects_count: int
    winners_count: int
    total_money: float

class YearStats(BaseModel):
    year: int
    projects_count: int
    winners_count: int
    total_money: float

@router.get("/stats/overview", response_model=OverviewStats)
def get_overview_stats(db: Session = Depends(get_db)):
    service = StatsService(db)
    return service.get_overview_stats()

@router.get("/stats/by-region", response_model=List[RegionStats])
def get_stats_by_region(db: Session = Depends(get_db)):
    service = StatsService(db)
    return service.get_stats_by_region()

@router.get("/stats/by-year", response_model=List[YearStats])
def get_stats_by_year(db: Session = Depends(get_db)):
    service = StatsService(db)
    return service.get_stats_by_year()


