from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.region_service import RegionService
from pydantic import BaseModel

router = APIRouter()

class RegionResponse(BaseModel):
    name: str
    projects_count: int
    coordinates: dict

@router.get("/regions", response_model=List[RegionResponse])
def get_regions(db: Session = Depends(get_db)):
    service = RegionService(db)
    return service.get_regions_with_stats()


