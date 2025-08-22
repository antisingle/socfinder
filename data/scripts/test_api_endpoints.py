#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API endpoints проблем и решений
"""

import requests
import json
from typing import Dict, Any

class APIEndpointTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_endpoint(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Тестирует API endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                return {"error": f"Неподдерживаемый метод: {method}"}
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json(),
                    "count": len(response.json()) if isinstance(response.json(), list) else None
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except requests.exceptions.ConnectionError:
            return {"error": "Не удается подключиться к серверу. Убедитесь что backend запущен."}
        except Exception as e:
            return {"error": f"Ошибка: {str(e)}"}
    
    def run_all_tests(self):
        """Запускает все тесты API"""
        print("🧪 Тестирование API endpoints для проблем и решений")
        print("=" * 60)
        
        # Тест 1: Получение списка проблем
        print("\n📋 Тест 1: GET /api/problems")
        result = self.test_endpoint("GET", "/api/problems")
        self.print_result(result)
        
        # Тест 2: Подсчет проблем
        print("\n📊 Тест 2: GET /api/problems/count")
        result = self.test_endpoint("GET", "/api/problems/count")
        self.print_result(result)
        
        # Тест 3: Получение списка решений
        print("\n🔧 Тест 3: GET /api/solutions")
        result = self.test_endpoint("GET", "/api/solutions")
        self.print_result(result)
        
        # Тест 4: Подсчет решений
        print("\n📊 Тест 4: GET /api/solutions/count")
        result = self.test_endpoint("GET", "/api/solutions/count")
        self.print_result(result)
        
        # Тест 5: Получение решений по grant_id
        print("\n🔗 Тест 5: POST /api/solutions/by-grants")
        test_data = {"grant_ids": ["25-2-002591", "25-1-008623"]}
        result = self.test_endpoint("POST", "/api/solutions/by-grants", test_data)
        self.print_result(result)
        
        # Тест 6: Статистика решений
        print("\n📈 Тест 6: GET /api/solutions/stats")
        result = self.test_endpoint("GET", "/api/solutions/stats")
        self.print_result(result)
        
        # Тест 7: Поиск проблем
        print("\n🔍 Тест 7: GET /api/problems/search?query=пенсионеры")
        result = self.test_endpoint("GET", "/api/problems/search?query=пенсионеры")
        self.print_result(result)
        
        print("\n" + "=" * 60)
        print("✅ Тестирование завершено!")
    
    def print_result(self, result: Dict[str, Any]):
        """Выводит результат теста"""
        if "error" in result:
            print(f"❌ Ошибка: {result['error']}")
        elif result.get("success"):
            print(f"✅ Успешно (код: {result['status_code']})")
            if result.get("count") is not None:
                print(f"   📊 Получено записей: {result['count']}")
            if result.get("data") and isinstance(result["data"], list) and len(result["data"]) > 0:
                print(f"   📝 Первая запись: {result['data'][0].get('id', 'N/A')}")
        else:
            print(f"❌ Неуспешно (код: {result['status_code']})")
            if "error" in result:
                print(f"   Ошибка: {result['error']}")

def main():
    """Основная функция"""
    print("🚀 Запуск тестирования API endpoints")
    print("Убедитесь что backend запущен: uvicorn app.main:app --reload")
    
    tester = APIEndpointTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
