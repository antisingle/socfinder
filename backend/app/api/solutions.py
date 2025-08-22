from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from ..core.database import get_db

router = APIRouter()

class SolutionResponse(BaseModel):
    id: int
    grant_id: str
    solution_text: str
    project_name: Optional[str]
    created_at: Optional[str]

class GrantIdsRequest(BaseModel):
    grant_ids: List[str]

@router.post("/api/solutions/by-grants", response_model=List[SolutionResponse])
async def get_solutions_by_grants(
    request: GrantIdsRequest,
    db: Session = Depends(get_db)
):
    """
    Получить решения для списка грантов.
    
    Args:
        request: Запрос с списком ID грантов
        db: Сессия базы данных
    
    Returns:
        Список решений для указанных грантов
    """
    try:
        if not request.grant_ids:
            return []
        
        # SQL запрос для получения решений по списку grant_id
        placeholders = ','.join([':grant_id_' + str(i) for i in range(len(request.grant_ids))])
        params = {f'grant_id_{i}': grant_id for i, grant_id in enumerate(request.grant_ids)}
        
        solutions = db.execute(text(f"""
            SELECT 
                s.id,
                s.grant_id,
                s.solution_text,
                pr.name as project_name,
                s.created_at
            FROM solutions s
            LEFT JOIN projects pr ON s.grant_id = pr.req_num
            WHERE s.grant_id IN ({placeholders})
            ORDER BY s.grant_id, s.created_at DESC
        """), params)
        
        result = []
        for row in solutions:
            result.append(SolutionResponse(
                id=row.id,
                grant_id=row.grant_id,
                solution_text=row.solution_text,
                project_name=row.project_name,
                created_at=str(row.created_at) if row.created_at else None
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении решений: {str(e)}"
        )

@router.get("/api/solutions", response_model=List[SolutionResponse])
async def get_solutions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список всех решений с информацией о проектах.
    
    Args:
        skip: Количество записей для пропуска (для пагинации)
        limit: Максимальное количество записей для возврата
        db: Сессия базы данных
    
    Returns:
        Список решений с информацией о проектах
    """
    try:
        solutions = db.execute(text("""
            SELECT 
                s.id,
                s.grant_id,
                s.solution_text,
                pr.name as project_name,
                s.created_at
            FROM solutions s
            LEFT JOIN projects pr ON s.grant_id = pr.req_num
            ORDER BY s.created_at DESC
            LIMIT :limit OFFSET :skip
        """), {"limit": limit, "skip": skip})
        
        result = []
        for row in solutions:
            result.append(SolutionResponse(
                id=row.id,
                grant_id=row.grant_id,
                solution_text=row.solution_text,
                project_name=row.project_name,
                created_at=str(row.created_at) if row.created_at else None
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении решений: {str(e)}"
        )

@router.get("/api/solutions/count")
async def get_solutions_count(db: Session = Depends(get_db)):
    """
    Получить общее количество решений.
    
    Args:
        db: Сессия базы данных
    
    Returns:
        Общее количество решений
    """
    try:
        result = db.execute(text("SELECT COUNT(*) as count FROM solutions"))
        count = result.fetchone().count
        return {"count": count}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при подсчете решений: {str(e)}"
        )

@router.get("/api/solutions/by-grant/{grant_id}")
async def get_solutions_by_grant(
    grant_id: str,
    db: Session = Depends(get_db)
):
    """
    Получить решения для конкретного гранта.
    
    Args:
        grant_id: ID гранта
        db: Сессия базы данных
    
    Returns:
        Список решений для указанного гранта
    """
    try:
        solutions = db.execute(text("""
            SELECT 
                s.id,
                s.grant_id,
                s.solution_text,
                pr.name as project_name,
                s.created_at
            FROM solutions s
            LEFT JOIN projects pr ON s.grant_id = pr.req_num
            WHERE s.grant_id = :grant_id
            ORDER BY s.created_at DESC
        """), {"grant_id": grant_id})
        
        result = []
        for row in solutions:
            result.append(SolutionResponse(
                id=row.id,
                grant_id=row.grant_id,
                solution_text=row.solution_text,
                project_name=row.project_name,
                created_at=str(row.created_at) if row.created_at else None
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении решений для гранта {grant_id}: {str(e)}"
        )

@router.get("/api/solutions/search")
async def search_solutions(
    query: str,
    db: Session = Depends(get_db)
):
    """
    Поиск решений по тексту.
    
    Args:
        query: Поисковый запрос
        db: Сессия базы данных
    
    Returns:
        Список решений, соответствующих поисковому запросу
    """
    try:
        search_pattern = f"%{query}%"
        solutions = db.execute(text("""
            SELECT 
                s.id,
                s.grant_id,
                s.solution_text,
                pr.name as project_name,
                s.created_at
            FROM solutions s
            LEFT JOIN projects pr ON s.grant_id = pr.req_num
            WHERE s.solution_text ILIKE :search_pattern
            ORDER BY s.created_at DESC
            LIMIT 50
        """), {"search_pattern": search_pattern})
        
        result = []
        for row in solutions:
            result.append(SolutionResponse(
                id=row.id,
                grant_id=row.grant_id,
                solution_text=row.solution_text,
                project_name=row.project_name,
                created_at=str(row.created_at) if row.created_at else None
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при поиске решений: {str(e)}"
        )

@router.get("/api/solutions/stats")
async def get_solutions_stats(db: Session = Depends(get_db)):
    """
    Получить статистику по решениям.
    
    Args:
        db: Сессия базы данных
    
    Returns:
        Статистика по решениям
    """
    try:
        # Общее количество решений
        total_count = db.execute(text("SELECT COUNT(*) as count FROM solutions")).fetchone().count
        
        # Количество уникальных грантов с решениями
        unique_grants = db.execute(text("SELECT COUNT(DISTINCT grant_id) as count FROM solutions")).fetchone().count
        
        # Среднее количество решений на грант
        avg_solutions = db.execute(text("""
            SELECT AVG(solution_count) as avg_count 
            FROM (
                SELECT grant_id, COUNT(*) as solution_count 
                FROM solutions 
                GROUP BY grant_id
            ) as grant_solutions
        """)).fetchone().avg_count
        
        return {
            "total_solutions": total_count,
            "unique_grants": unique_grants,
            "average_solutions_per_grant": round(float(avg_solutions), 2) if avg_solutions else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении статистики: {str(e)}"
        )
