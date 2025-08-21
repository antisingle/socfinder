#!/usr/bin/env python3
"""
Тестовый скрипт для интеграции ollama и PostgreSQL
Анализирует 1 реальную заявку из базы данных
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from postgres_manager import PostgresManager
from ollama_analyzer import OllamaAnalyzer
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_single_grant_analysis():
    """Тест анализа одной заявки"""
    
    logger.info("🚀 НАЧИНАЮ ТЕСТ ИНТЕГРАЦИИ OLLAMA + POSTGRESQL")
    logger.info("=" * 60)
    
    # 1. Инициализация компонентов
    logger.info("1️⃣ Инициализация компонентов...")
    
    db_manager = PostgresManager()
    ollama_analyzer = OllamaAnalyzer()
    
    # 2. Проверка подключений
    logger.info("2️⃣ Проверка подключений...")
    
    if not db_manager.test_connection():
        logger.error("❌ Не удалось подключиться к PostgreSQL")
        return False
    
    if not ollama_analyzer.test_connection():
        logger.error("❌ Не удалось подключиться к ollama")
        return False
    
    logger.info("✅ Все подключения работают")
    
    # 3. Получение тестовой заявки
    logger.info("3️⃣ Получение тестовой заявки из БД...")
    
    # Получаем первую доступную заявку
    grants = db_manager.get_grants_batch(1, 1)
    if not grants:
        logger.error("❌ Не удалось получить заявки из БД")
        return False
    
    test_grant = grants[0]
    logger.info(f"✅ Получена заявка: {test_grant.get('name', 'N/A')}")
    logger.info(f"   ID: {test_grant.get('id')}")
    logger.info(f"   req_num: {test_grant.get('req_num')}")
    logger.info(f"   Направление: {test_grant.get('direction')}")
    
    # 4. Анализ через LLM
    logger.info("4️⃣ Анализ заявки через LLM...")
    
    start_time = time.time()
    analysis_result = ollama_analyzer.analyze_grant(test_grant)
    analysis_time = time.time() - start_time
    
    if not analysis_result:
        logger.error("❌ LLM не смог проанализировать заявку")
        return False
    
    logger.info(f"✅ Анализ завершен за {analysis_time:.2f} сек")
    
    # 5. Проверка результата
    logger.info("5️⃣ Проверка результата анализа...")
    
    logger.info(f"   Проблемы найдено: {len(analysis_result.get('problems', []))}")
    for i, problem in enumerate(analysis_result.get('problems', []), 1):
        logger.info(f"     {i}. {problem[:100]}...")
    
    logger.info(f"   Решений найдено: {len(analysis_result.get('solutions', []))}")
    for i, solution in enumerate(analysis_result.get('solutions', []), 1):
        logger.info(f"     {i}. {solution[:100]}...")
    
    logger.info(f"   Краткое описание: {analysis_result.get('summary', 'N/A')[:100]}...")
    
    # 6. Сохранение в БД
    logger.info("6️⃣ Сохранение результатов в БД...")
    
    if db_manager.save_analysis_results([analysis_result]):
        logger.info("✅ Результаты успешно сохранены в БД")
    else:
        logger.error("❌ Ошибка сохранения в БД")
        return False
    
    # 7. Проверка сохраненных данных
    logger.info("7️⃣ Проверка сохраненных данных...")
    
    summary = db_manager.get_analysis_summary()
    logger.info(f"📊 Сводка после анализа:")
    logger.info(f"   Всего грантов: {summary.get('total_grants', 0)}")
    logger.info(f"   Проанализировано: {summary.get('analyzed_grants', 0)}")
    logger.info(f"   Всего проблем: {summary.get('total_problems', 0)}")
    logger.info(f"   Всего решений: {summary.get('total_solutions', 0)}")
    
    # 8. Тест SQL запросов
    logger.info("8️⃣ Тест SQL запросов для проверки связей...")
    
    grant_id = analysis_result.get('grant_id')
    if grant_id:
        logger.info(f"   Тестирую запросы для гранта: {grant_id}")
        
        # Проверяем проблемы
        problems = db_manager.get_connection()
        if problems:
            with problems.cursor() as cursor:
                cursor.execute("SELECT problem_text FROM problems WHERE grant_id = %s", (grant_id,))
                saved_problems = cursor.fetchall()
                logger.info(f"   Сохранено проблем: {len(saved_problems)}")
            
            problems.close()
        
        # Проверяем решения
        solutions = db_manager.get_connection()
        if solutions:
            with solutions.cursor() as cursor:
                cursor.execute("SELECT solution_text FROM solutions WHERE grant_id = %s", (grant_id,))
                saved_solutions = cursor.fetchall()
                logger.info(f"   Сохранено решений: {len(saved_solutions)}")
            
            solutions.close()
    
    logger.info("=" * 60)
    logger.info("🎉 ТЕСТ ИНТЕГРАЦИИ УСПЕШНО ЗАВЕРШЕН!")
    logger.info(f"⏱️ Общее время: {analysis_time:.2f} сек")
    logger.info(f"📊 Проанализировано грантов: 1")
    
    return True

if __name__ == "__main__":
    import time
    success = test_single_grant_analysis()
    sys.exit(0 if success else 1)
