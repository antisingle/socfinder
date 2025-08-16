from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.project import Project
from typing import Optional, List
from fastapi import HTTPException

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_projects(
        self,
        region: Optional[str] = None,
        year: Optional[int] = None,
        direction: Optional[str] = None,
        winner: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Project]:
        query = self.db.query(Project)
        
        filters = []
        if region:
            filters.append(Project.region == region)
        if year:
            filters.append(Project.year == year)
        if direction:
            filters.append(Project.direction == direction)
        if winner is not None:
            filters.append(Project.winner == winner)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Получаем результаты и обрабатываем None значения
        results = query.offset(offset).limit(limit).all()
        
        # Исправляем None значения в winner поле для каждого проекта
        for project in results:
            if project.winner is None:
                project.winner = False
            # Исправляем другие None значения
            if project.name is None:
                project.name = ""
            if project.region is None:
                project.region = ""
            if project.org is None:
                project.org = ""
        
        return results
    
    def get_project_by_id(self, project_id: int) -> Project:
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    
    def get_projects_table(
        self,
        region: Optional[str] = None,
        year: Optional[int] = None,
        direction: Optional[str] = None,
        winner: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: str = "asc"
    ) -> List[Project]:
        query = self.db.query(Project)
        
        filters = []
        if region:
            filters.append(Project.region == region)
        if year:
            filters.append(Project.year == year)
        if direction:
            filters.append(Project.direction == direction)
        if winner is not None:
            filters.append(Project.winner == winner)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Сортировка
        if hasattr(Project, sort_by):
            sort_column = getattr(Project, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        # Получаем результаты и обрабатываем None значения
        results = query.offset(offset).limit(limit).all()
        
        # Исправляем None значения
        for project in results:
            if project.winner is None:
                project.winner = False
            if project.name is None:
                project.name = ""
            if project.region is None:
                project.region = ""
            if project.org is None:
                project.org = ""
        
        return results
    
    def export_projects(
        self,
        region: Optional[str] = None,
        year: Optional[int] = None,
        direction: Optional[str] = None,
        winner: Optional[bool] = None,
        format: str = "csv"
    ) -> dict:
        query = self.db.query(Project)
        
        filters = []
        if region:
            filters.append(Project.region == region)
        if year:
            filters.append(Project.year == year)
        if direction:
            filters.append(Project.direction == direction)
        if winner is not None:
            filters.append(Project.winner == winner)
        
        if filters:
            query = query.filter(and_(*filters))
        
        projects = query.all()
        
        # Формируем CSV данные
        csv_data = []
        headers = ["ID", "Название", "Организация", "Регион", "Год", "Направление", "Сумма", "Статус", "Конкурс"]
        
        for project in projects:
            row = [
                project.id,
                project.name or "",
                project.org or "",
                project.region or "",
                project.year or "",
                project.direction or "",
                project.money_req_grant or 0,
                "Победитель" if project.winner else "Не прошел",
                project.contest or ""
            ]
            csv_data.append(row)
        
        return {
            "format": format,
            "count": len(projects),
            "headers": headers,
            "data": csv_data
        }
