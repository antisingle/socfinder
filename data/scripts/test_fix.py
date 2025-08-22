#!/usr/bin/env python3
"""
Тест исправления ошибки сохранения
"""

import logging
from postgres_manager import PostgresManager
from ollama_analyzer import OllamaAnalyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_fix():
    """Тестируем исправление ошибки"""
    pg_manager = PostgresManager()
    ollama_analyzer = OllamaAnalyzer()
    
    # Получаем один грант для тестирования
    conn = pg_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, req_num, name, date_req, direction, description, goal, tasks, soc_signif, pj_geo, target_groups
        FROM projects 
        WHERE winner = true 
        AND date_req IS NOT NULL
        AND req_num NOT IN (
            SELECT DISTINCT grant_id FROM problems
        )
        ORDER BY date_req DESC, id DESC
        LIMIT 1
    ''')
    
    row = cursor.fetchone()
    if not row:
        print("❌ Не найдено грантов для тестирования")
        return
        
    grant_data = {
        'id': row[0],
        'req_num': row[1],
        'name': row[2],
        'date_req': row[3],
        'direction': row[4],
        'description': row[5],
        'goal': row[6],
        'tasks': row[7],
        'soc_signif': row[8],
        'pj_geo': row[9],
        'target_groups': row[10]
    }
    
    conn.close()
    
    print(f"🔍 Тестирую исправление на гранте: {grant_data['req_num']}")
    print(f"📝 Название: {grant_data['name']}")
    
    # Анализируем грант
    analysis_result = ollama_analyzer.analyze_grant({
        'name': grant_data['name'],
        'direction': grant_data['direction'],
        'description': grant_data['description'] or 'Не указано',
        'goal': grant_data['goal'] or 'Не указано',
        'tasks': grant_data['tasks'] or 'Не указано',
        'soc_signif': grant_data['soc_signif'] or 'Не указано',
        'pj_geo': grant_data['pj_geo'] or 'Не указано',
        'target_groups': grant_data['target_groups'] or 'Не указано'
    })
    
    if analysis_result and isinstance(analysis_result, dict):
        print(f"✅ LLM анализ успешен: {len(analysis_result.get('problems', []))} проблем, {len(analysis_result.get('solutions', []))} решений")
        
        # Пытаемся сохранить
        analysis_data = [{
            'grant_id': grant_data['req_num'],
            'problems': analysis_result.get('problems', []),
            'solutions': analysis_result.get('solutions', [])
        }]
        
        success = pg_manager.save_analysis_results(analysis_data)
        if success:
            print("✅ Сохранение успешно!")
        else:
            print("❌ Ошибка сохранения")
    else:
        print("❌ LLM анализ не удался")

if __name__ == "__main__":
    test_fix()

