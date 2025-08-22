#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API endpoints проблем и решений
Запуск: python test_problems_solutions_api.py
"""

import requests
import json
import time
from typing import Dict, List, Any

# Конфигурация
API_BASE_URL = "http://localhost:8001"
TEST_TIMEOUT = 10  # секунды

def test_api_endpoint(url: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Тестирует API endpoint и возвращает результат"""
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=TEST_TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TEST_TIMEOUT)
        else:
            return {"error": f"Неподдерживаемый метод: {method}"}
        
        response_time = time.time() - start_time
        
        result = {
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "response_time": round(response_time, 3),
            "success": response.status_code == 200,
            "data_size": len(response.content) if response.content else 0
        }
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                result["data_count"] = len(json_data) if isinstance(json_data, list) else 1
                result["sample_data"] = json_data[:2] if isinstance(json_data, list) and len(json_data) > 0 else json_data
            except json.JSONDecodeError:
                result["error"] = "Не удалось декодировать JSON"
        else:
            result["error"] = response.text[:200] if response.text else "Нет текста ошибки"
            
        return result
        
    except requests.exceptions.Timeout:
        return {"error": f"Таймаут запроса ({TEST_TIMEOUT}с)", "url": url}
    except requests.exceptions.ConnectionError:
        return {"error": "Ошибка подключения к серверу", "url": url}
    except Exception as e:
        return {"error": f"Неожиданная ошибка: {str(e)}", "url": url}

def test_problems_api() -> List[Dict[str, Any]]:
    """Тестирует API endpoints для проблем"""
    print("🔍 Тестирование API проблем...")
    
    tests = [
        {"url": f"{API_BASE_URL}/api/problems", "method": "GET"},
        {"url": f"{API_BASE_URL}/api/problems/count", "method": "GET"},
        {"url": f"{API_BASE_URL}/api/problems/search?query=социальная", "method": "GET"},
    ]
    
    results = []
    for test in tests:
        result = test_api_endpoint(test["url"], test["method"])
        results.append(result)
        
        if result["success"]:
            print(f"✅ {test['url']} - {result['response_time']}с")
        else:
            print(f"❌ {test['url']} - {result.get('error', 'Неизвестная ошибка')}")
    
    return results

def test_solutions_api() -> List[Dict[str, Any]]:
    """Тестирует API endpoints для решений"""
    print("\n🔍 Тестирование API решений...")
    
    tests = [
        {"url": f"{API_BASE_URL}/api/solutions", "method": "GET"},
        {"url": f"{API_BASE_URL}/api/solutions/count", "method": "GET"},
        {"url": f"{API_BASE_URL}/api/solutions/search?query=решение", "method": "GET"},
        {
            "url": f"{API_BASE_URL}/api/solutions/by-grants", 
            "method": "POST", 
            "data": {"grant_ids": ["25-1-008623", "15-2-001234"]}
        },
    ]
    
    results = []
    for test in tests:
        result = test_api_endpoint(test["url"], test["method"], test.get("data"))
        results.append(result)
        
        if result["success"]:
            print(f"✅ {test['url']} - {result['response_time']}с")
        else:
            print(f"❌ {test['url']} - {result.get('error', 'Неизвестная ошибка')}")
    
    return results

def test_integration() -> Dict[str, Any]:
    """Тестирует интеграцию между проблемами и решениями"""
    print("\n🔍 Тестирование интеграции...")
    
    # Получаем список проблем
    problems_response = requests.get(f"{API_BASE_URL}/api/problems", timeout=TEST_TIMEOUT)
    if problems_response.status_code != 200:
        return {"error": "Не удалось получить проблемы для интеграционного теста"}
    
    problems = problems_response.json()
    if not problems:
        return {"error": "Нет проблем для интеграционного теста"}
    
    # Берем первые 3 grant_id для теста
    test_grant_ids = list(set([p["grant_id"] for p in problems[:3]]))
    
    # Получаем решения для этих грантов
    solutions_response = requests.post(
        f"{API_BASE_URL}/api/solutions/by-grants",
        json={"grant_ids": test_grant_ids},
        timeout=TEST_TIMEOUT
    )
    
    if solutions_response.status_code != 200:
        return {"error": "Не удалось получить решения для интеграционного теста"}
    
    solutions = solutions_response.json()
    
    # Анализируем связи
    problem_grant_ids = set(p["grant_id"] for p in problems)
    solution_grant_ids = set(s["grant_id"] for s in solutions)
    
    # Все grant_id из решений должны быть в проблемах
    orphaned_solutions = solution_grant_ids - problem_grant_ids
    
    result = {
        "problems_count": len(problems),
        "solutions_count": len(solutions),
        "unique_grant_ids_in_problems": len(problem_grant_ids),
        "unique_grant_ids_in_solutions": len(solution_grant_ids),
        "test_grant_ids": test_grant_ids,
        "orphaned_solutions": list(orphaned_solutions),
        "integration_success": len(orphaned_solutions) == 0
    }
    
    if result["integration_success"]:
        print(f"✅ Интеграция успешна: {len(problems)} проблем, {len(solutions)} решений")
    else:
        print(f"⚠️  Проблемы интеграции: {len(orphaned_solutions)} решений без соответствующих проблем")
    
    return result

def print_summary(problems_results: List[Dict], solutions_results: List[Dict], integration_result: Dict):
    """Выводит сводку по всем тестам"""
    print("\n" + "="*60)
    print("📊 СВОДКА ТЕСТИРОВАНИЯ")
    print("="*60)
    
    # Статистика по проблемам
    problems_success = sum(1 for r in problems_results if r["success"])
    problems_total = len(problems_results)
    print(f"🔍 API проблем: {problems_success}/{problems_total} успешно")
    
    # Статистика по решениям
    solutions_success = sum(1 for r in solutions_results if r["success"])
    solutions_total = len(solutions_results)
    print(f"🔍 API решений: {solutions_success}/{solutions_total} успешно")
    
    # Интеграция
    if "error" not in integration_result:
        print(f"🔗 Интеграция: {'✅ Успешно' if integration_result['integration_success'] else '⚠️  Есть проблемы'}")
    else:
        print(f"🔗 Интеграция: ❌ {integration_result['error']}")
    
    # Время ответа
    all_results = problems_results + solutions_results
    successful_results = [r for r in all_results if r["success"]]
    
    if successful_results:
        avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
        print(f"⏱️  Среднее время ответа: {avg_response_time:.3f}с")
        
        max_response_time = max(r["response_time"] for r in successful_results)
        print(f"⏱️  Максимальное время ответа: {max_response_time:.3f}с")
    
    # Общие рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    
    if problems_success == problems_total and solutions_success == solutions_total:
        print("✅ Все API endpoints работают корректно")
        
        if "integration_success" in integration_result and integration_result["integration_success"]:
            print("✅ Интеграция между проблемами и решениями работает корректно")
        else:
            print("⚠️  Проверьте связи между проблемами и решениями в базе данных")
    else:
        print("❌ Есть проблемы с API endpoints - проверьте логи сервера")
    
    if successful_results:
        slow_endpoints = [r for r in successful_results if r["response_time"] > 1.0]
        if slow_endpoints:
            print(f"⚠️  {len(slow_endpoints)} endpoints работают медленно (>1с)")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования API проблем и решений")
    print(f"🌐 API сервер: {API_BASE_URL}")
    print(f"⏱️  Таймаут: {TEST_TIMEOUT}с")
    print("-" * 60)
    
    try:
        # Тестируем API проблем
        problems_results = test_problems_api()
        
        # Тестируем API решений
        solutions_results = test_solutions_api()
        
        # Тестируем интеграцию
        integration_result = test_integration()
        
        # Выводим сводку
        print_summary(problems_results, solutions_results, integration_result)
        
        # Сохраняем результаты в файл
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_base_url": API_BASE_URL,
            "problems_results": problems_results,
            "solutions_results": solutions_results,
            "integration_result": integration_result
        }
        
        with open("api_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в api_test_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️  Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {str(e)}")

if __name__ == "__main__":
    main()
