import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.project import Project
from app.models.problem import Problem
from app.models.solution import Solution

# Тестовая база данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем тестовые таблицы
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Настройка тестовой базы данных перед каждым тестом"""
    # Очищаем таблицы
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Создаем тестовые данные
    db = TestingSessionLocal()
    
    # Тестовый проект
    test_project = Project(
        req_num="TEST-001",
        name="Тестовый проект",
        region="Тестовый регион",
        org="Тестовая организация",
        winner=True,
        money_req_grant=1000000
    )
    db.add(test_project)
    db.commit()
    
    # Тестовая проблема
    test_problem = Problem(
        grant_id="TEST-001",
        problem_text="Тестовая социальная проблема",
        created_at="2025-01-01T00:00:00"
    )
    db.add(test_problem)
    db.commit()
    
    # Тестовое решение
    test_solution = Solution(
        grant_id="TEST-001",
        solution_text="Тестовое решение проблемы",
        created_at="2025-01-01T00:00:00"
    )
    db.add(test_solution)
    db.commit()
    
    db.close()
    yield
    db.close()

class TestProblemsAPI:
    """Тесты для API проблем"""
    
    def test_get_problems(self):
        """Тест получения списка проблем"""
        response = client.get("/api/problems")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        problem = data[0]
        assert "id" in problem
        assert "grant_id" in problem
        assert "problem_text" in problem
        assert "project_name" in problem
    
    def test_get_problems_count(self):
        """Тест получения количества проблем"""
        response = client.get("/api/problems/count")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert data["count"] > 0
    
    def test_get_problems_by_grant(self):
        """Тест получения проблем по grant_id"""
        response = client.get("/api/problems/by-grant/TEST-001")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        problem = data[0]
        assert problem["grant_id"] == "TEST-001"
    
    def test_search_problems(self):
        """Тест поиска проблем"""
        response = client.get("/api/problems/search?query=социальная")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        problem = data[0]
        assert "социальная" in problem["problem_text"].lower()

class TestSolutionsAPI:
    """Тесты для API решений"""
    
    def test_get_solutions(self):
        """Тест получения списка решений"""
        response = client.get("/api/solutions")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        solution = data[0]
        assert "id" in solution
        assert "grant_id" in solution
        assert "solution_text" in solution
        assert "project_name" in solution
    
    def test_get_solutions_by_grants(self):
        """Тест получения решений по списку grant_ids"""
        response = client.post(
            "/api/solutions/by-grants",
            json={"grant_ids": ["TEST-001"]}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        solution = data[0]
        assert solution["grant_id"] == "TEST-001"
    
    def test_get_solutions_by_grant(self):
        """Тест получения решений по grant_id"""
        response = client.get("/api/solutions/by-grant/TEST-001")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        solution = data[0]
        assert solution["grant_id"] == "TEST-001"
    
    def test_search_solutions(self):
        """Тест поиска решений"""
        response = client.get("/api/solutions/search?query=решение")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        solution = data[0]
        assert "решение" in solution["solution_text"].lower()

class TestIntegration:
    """Интеграционные тесты"""
    
    def test_problem_solution_relationship(self):
        """Тест связи проблемы и решения через grant_id"""
        # Получаем проблемы
        problems_response = client.get("/api/problems")
        assert problems_response.status_code == 200
        problems = problems_response.json()
        
        # Получаем решения для проблем
        if problems:
            grant_ids = [p["grant_id"] for p in problems]
            solutions_response = client.post(
                "/api/solutions/by-grants",
                json={"grant_ids": grant_ids}
            )
            assert solutions_response.status_code == 200
            solutions = solutions_response.json()
            
            # Проверяем, что все решения имеют соответствующие grant_id
            solution_grant_ids = set(s["grant_id"] for s in solutions)
            problem_grant_ids = set(grant_ids)
            
            # Все grant_id из решений должны быть в проблемах
            assert solution_grant_ids.issubset(problem_grant_ids)
    
    def test_empty_grant_ids_request(self):
        """Тест запроса с пустым списком grant_ids"""
        response = client.post(
            "/api/solutions/by-grants",
            json={"grant_ids": []}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
