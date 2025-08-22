from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from ..core.database import get_db
from ..models.project import Project
from pydantic import BaseModel

router = APIRouter()

class ProblemResponse(BaseModel):
    id: int
    grant_id: str
    problem_text: str
    project_name: Optional[str]
    created_at: Optional[str]

@router.get("/api/problems", response_model=List[ProblemResponse])
async def get_problems(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех проблем с информацией о проектах.
    
    Args:
        skip: Количество записей для пропуска (для пагинации)
        limit: Максимальное количество записей для возврата
        db: Сессия базы данных
    
    Returns:
        Список проблем с информацией о проектах
    """
    try:
        # SQL запрос для получения проблем с названиями проектов
        problems = db.execute(text("""
            SELECT 
                p.id,
                p.grant_id,
                p.problem_text,
                pr.name as project_name,
                p.created_at
            FROM problems p
            LEFT JOIN projects pr ON p.grant_id = pr.req_num
            ORDER BY p.created_at DESC
            LIMIT :limit OFFSET :skip
        """), {"limit": limit, "skip": skip})
        
        result = []
        for row in problems:
            result.append(ProblemResponse(
                id=row.id,
                grant_id=row.grant_id,
                problem_text=row.problem_text,
                project_name=row.project_name,
                created_at=str(row.created_at) if row.created_at else None
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении проблем: {str(e)}"
        )

@router.get("/api/problems/count")
async def get_problems_count(db: Session = Depends(get_db)):
    """
    Получить общее количество проблем.
    
    Args:
        db: Сессия базы данных
    
    Returns:
        Общее количество проблем
    """
    try:
        result = db.execute(text("SELECT COUNT(*) as count FROM problems"))
        count = result.fetchone().count
        return {"count": count}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при подсчете проблем: {str(e)}"
        )

@router.get("/api/problems/by-grant/{grant_id}")
async def get_problems_by_grant(
    grant_id: str,
    db: Session = Depends(get_db)
):
    """
    Получить проблемы для конкретного гранта.
    
    Args:
        grant_id: ID гранта
        db: Сессия базы данных
    
    Returns:
        Список проблем для указанного гранта
    """
    try:
        problems = db.execute(text("""
            SELECT 
                p.id,
                p.grant_id,
                p.problem_text,
                pr.name as project_name,
                p.created_at
            FROM problems p
            LEFT JOIN projects pr ON p.grant_id = pr.req_num
            WHERE p.grant_id = :grant_id
            ORDER BY p.created_at DESC
        """), {"grant_id": grant_id})
        
        result = []
        for row in problems:
            result.append(ProblemResponse(
                id=row.id,
                grant_id=row.grant_id,
                problem_text=row.problem_text,
                project_name=row.project_name,
                created_at=str(row.created_at) if row.created_at else None
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении проблем для гранта {grant_id}: {str(e)}"
        )

@router.get("/api/problems/search")
async def search_problems(
    query: str,
    db: Session = Depends(get_db)
):
    """
    Поиск проблем по тексту.
    
    Args:
        query: Поисковый запрос
        db: Сессия базы данных
    
    Returns:
        Список проблем, соответствующих поисковому запросу
    """
    try:
        search_pattern = f"%{query}%"
        problems = db.execute(text("""
            SELECT 
                p.id,
                p.grant_id,
                p.problem_text,
                pr.name as project_name,
            FROM problems p
            LEFT JOIN projects pr ON p.grant_id = pr.req_num
            WHERE p.problem_text ILIKE :search_pattern
            ORDER BY p.created_at DESC
            LIMIT 50
        """), {"search_pattern": search_pattern})
        
        result = []
        for row in problems:
            result.append(ProblemResponse(
                id=row.id,
                grant_id=row.grant_id,
                problem_text=row.problem_text,
                project_name=row.project_name,
                created_at=str(row.created_at) if row.created_at else None
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при поиске проблем: {str(e)}"
        )
