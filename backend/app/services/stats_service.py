from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.project import Project
from typing import List

class StatsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_overview_stats(self) -> dict:
        """Общая статистика по проектам"""
        total_projects = self.db.query(func.count(Project.id)).scalar()
        total_winners = self.db.query(func.count(Project.id)).filter(Project.winner == True).scalar()
        total_money = self.db.query(func.sum(Project.money_req_grant)).filter(Project.winner == True).scalar() or 0
        regions_count = self.db.query(func.count(func.distinct(Project.region))).scalar()
        organizations_count = self.db.query(func.count(func.distinct(Project.org))).scalar()
        
        return {
            "total_projects": total_projects,
            "total_winners": total_winners,
            "total_money": float(total_money) if total_money else 0.0,
            "regions_count": regions_count,
            "organizations_count": organizations_count
        }
    
    def get_stats_by_region(self) -> List[dict]:
        """Статистика по регионам"""
        stats = (
            self.db.query(
                Project.region,
                func.count(Project.id).label('projects_count'),
                func.count(Project.id).filter(Project.winner == True).label('winners_count'),
                func.sum(Project.money_req_grant).filter(Project.winner == True).label('total_money')
            )
            .filter(Project.region.isnot(None))
            .group_by(Project.region)
            .all()
        )
        
        return [
            {
                "region": region,
                "projects_count": projects_count,
                "winners_count": winners_count or 0,
                "total_money": float(total_money) if total_money else 0.0
            }
            for region, projects_count, winners_count, total_money in stats
        ]
    
    def get_stats_by_year(self) -> List[dict]:
        """Статистика по годам"""
        stats = (
            self.db.query(
                Project.year,
                func.count(Project.id).label('projects_count'),
                func.count(Project.id).filter(Project.winner == True).label('winners_count'),
                func.sum(Project.money_req_grant).filter(Project.winner == True).label('total_money')
            )
            .group_by(Project.year)
            .order_by(Project.year)
            .all()
        )
        
        return [
            {
                "year": year,
                "projects_count": projects_count,
                "winners_count": winners_count or 0,
                "total_money": float(total_money) if total_money else 0.0
            }
            for year, projects_count, winners_count, total_money in stats
        ]


