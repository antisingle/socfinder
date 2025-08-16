from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.project import Project
from typing import List
import json
import os

class RegionService:
    def __init__(self, db: Session):
        self.db = db
        self.coordinates = self._load_coordinates()
    
    def _load_coordinates(self) -> dict:
        """Загружает координаты регионов из JSON файла"""
        try:
            coords_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "regions_coordinates.json")
            with open(coords_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_regions_with_stats(self) -> List[dict]:
        """Возвращает список регионов с количеством проектов и координатами"""
        regions_stats = (
            self.db.query(
                Project.region,
                func.count(Project.id).label('projects_count')
            )
            .filter(Project.region.isnot(None))
            .group_by(Project.region)
            .all()
        )
        
        result = []
        for region, count in regions_stats:
            coordinates = self.coordinates.get(region, {"lat": 55.7558, "lng": 37.6173})  # Москва по умолчанию
            result.append({
                "name": region,
                "projects_count": count,
                "coordinates": coordinates
            })
        
        return result


