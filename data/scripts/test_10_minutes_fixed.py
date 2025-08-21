#!/usr/bin/env python3
"""
Тест на 10 минут с исправленной логикой
"""

import time
import logging
from datetime import datetime, timedelta
from postgres_manager import PostgresManager
from ollama_analyzer import OllamaAnalyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_10_minutes_fixed.log'),
        logging.StreamHandler()
    ]
)

class Test10MinutesFixedAnalyzer:
    def __init__(self):
        self.pg_manager = PostgresManager()
        self.ollama_analyzer = OllamaAnalyzer()
        self.start_time = None
        self.max_duration = timedelta(minutes=10)
        
    def run_test(self):
        """Запуск теста на 10 минут"""
        self.start_time = datetime.now()
        end_time = self.start_time + self.max_duration
        
        logging.info(f"🚀 Начинаю тест на 10 минут")
        logging.info(f"⏰ Время начала: {self.start_time.strftime('%H:%M:%S')}")
        logging.info(f"⏰ Время окончания: {end_time.strftime('%H:%M:%S')}")
        
        # Получаем список победителей, отсортированных по дате (от новых к старым)
        winners = self.get_winners_priority_list()
        
        if not winners:
            logging.error("❌ Не удалось получить список победителей")
            return
            
        logging.info(f"📊 Найдено {len(winners)} победителей для обработки")
        
        processed_count = 0
        total_problems = 0
        total_solutions = 0
        
        for i, winner in enumerate(winners):
            # Проверяем время
            if datetime.now() >= end_time:
                logging.info(f"⏰ Время вышло! Обработано {processed_count} грантов за 10 минут")
                break
                
            # Проверяем, не анализировали ли уже этот грант
            if self.is_already_analyzed(winner['req_num']):
                logging.info(f"⏭️ Грант {winner['req_num']} уже проанализирован, пропускаю")
                continue
                
            try:
                logging.info(f"🔍 Обрабатываю грант {i+1}/{len(winners)}: {winner['req_num']}")
                logging.info(f"📝 Название: {winner['name']}")
                logging.info(f"📅 Дата заявки: {winner['date_req']}")
                
                # Анализируем грант
                start_analysis = time.time()
                analysis_result = self.analyze_grant(winner)
                analysis_time = time.time() - start_analysis
                
                if analysis_result and isinstance(analysis_result, dict):
                    # Сохраняем результаты
                    analysis_data = [{
                        'grant_id': winner['req_num'],
                        'problems': analysis_result.get('problems', []),
                        'solutions': analysis_result.get('solutions', [])
                    }]
                    
                    success = self.pg_manager.save_analysis_results(analysis_data)
                    if success:
                        logging.info(f"✅ Результаты сохранены в БД")
                        
                        problems_count = len(analysis_result.get('problems', []))
                        solutions_count = len(analysis_result.get('solutions', []))
                        
                        total_problems += problems_count
                        total_solutions += solutions_count
                        processed_count += 1
                        
                        logging.info(f"✅ Грант {winner['req_num']} обработан за {analysis_time:.1f}с")
                        logging.info(f"📊 Найдено проблем: {problems_count}, решений: {solutions_count}")
                        
                        # Показываем прогресс
                        elapsed = datetime.now() - self.start_time
                        remaining = self.max_duration - elapsed
                        logging.info(f"⏱️ Прошло: {elapsed.total_seconds()/60:.1f} мин, осталось: {remaining.total_seconds()/60:.1f} мин")
                        
                    else:
                        logging.error(f"❌ Ошибка сохранения в БД")
                        
                else:
                    logging.warning(f"⚠️ Не удалось проанализировать грант {winner['req_num']}")
                    
            except Exception as e:
                logging.error(f"❌ Ошибка при обработке гранта {winner['req_num']}: {e}")
                continue
                
        # Итоговая статистика
        elapsed_total = datetime.now() - self.start_time
        logging.info(f"\n🎯 ТЕСТ ЗАВЕРШЕН!")
        logging.info(f"⏱️ Общее время: {elapsed_total.total_seconds()/60:.1f} минут")
        logging.info(f"📊 Обработано грантов: {processed_count}")
        logging.info(f"📝 Всего проблем: {total_problems}")
        logging.info(f"💡 Всего решений: {total_solutions}")
        if processed_count > 0:
            logging.info(f"🚀 Средняя скорость: {processed_count/(elapsed_total.total_seconds()/60):.1f} грантов/мин")
        
    def get_winners_priority_list(self):
        """Получает список победителей, отсортированных по приоритету"""
        try:
            conn = self.pg_manager.get_connection()
            cursor = conn.cursor()
            
            # Получаем победителей, отсортированных по дате (от новых к старым)
            cursor.execute('''
                SELECT id, req_num, name, date_req, direction, description, goal, tasks, soc_signif, pj_geo, target_groups
                FROM projects 
                WHERE winner = true 
                AND date_req IS NOT NULL
                ORDER BY date_req DESC, id DESC
                LIMIT 1000
            ''')
            
            winners = []
            for row in cursor.fetchall():
                winners.append({
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
                })
            
            conn.close()
            return winners
            
        except Exception as e:
            logging.error(f"❌ Ошибка при получении списка победителей: {e}")
            return []
            
    def is_already_analyzed(self, req_num):
        """Проверяет, проанализирован ли уже грант"""
        try:
            conn = self.pg_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM problems WHERE grant_id = %s
            ''', (req_num,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logging.error(f"❌ Ошибка при проверке существующего анализа: {e}")
            return False
            
    def analyze_grant(self, grant_data):
        """Анализирует один грант через LLM"""
        try:
            # Анализируем через LLM - передаем как словарь
            result = self.ollama_analyzer.analyze_grant({
                'name': grant_data['name'],
                'direction': grant_data['direction'],
                'description': grant_data['description'] or 'Не указано',
                'goal': grant_data['goal'] or 'Не указано',
                'tasks': grant_data['tasks'] or 'Не указано',
                'soc_signif': grant_data['soc_signif'] or 'Не указано',
                'pj_geo': grant_data['pj_geo'] or 'Не указано',
                'target_groups': grant_data['target_groups'] or 'Не указано'
            })
            
            # Проверяем, что результат - это словарь
            if result and isinstance(result, dict):
                return result
            else:
                logging.warning(f"⚠️ LLM вернул неверный формат: {type(result)}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Ошибка при анализе гранта: {e}")
            return None

def main():
    analyzer = Test10MinutesFixedAnalyzer()
    analyzer.run_test()

if __name__ == "__main__":
    main()
