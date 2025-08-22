#!/usr/bin/env python3
"""
Скрипт для пакетной обработки президентских грантов через LLM
Принимает время работы в минутах как аргумент командной строки

Использование:
    python time_batch_processing.py <minutes>
    
Примеры:
    python time_batch_processing.py 60      # 1 час
    python time_batch_processing.py 360     # 6 часов
    python time_batch_processing.py 1440    # 24 часа
"""

import time
import logging
import sys
from datetime import datetime, timedelta
from postgres_manager import PostgresManager
from ollama_analyzer import OllamaAnalyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('time_batch_processing.log'),
        logging.StreamHandler()
    ]
)

class TimeBatchProcessor:
    def __init__(self, minutes: int):
        self.pg_manager = PostgresManager()
        self.ollama_analyzer = OllamaAnalyzer()
        self.start_time = None
        self.max_duration = timedelta(minutes=minutes)
        
    def run_processing(self):
        """Запуск обработки на заданное время"""
        self.start_time = datetime.now()
        end_time = self.start_time + self.max_duration
        
        logging.info(f"🚀 Начинаю обработку на {self.max_duration.total_seconds()/60:.0f} минут")
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
                logging.info(f"⏰ Время вышло! Обработано {processed_count} грантов за {self.max_duration.total_seconds()/60:.0f} минут")
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
        logging.info(f"\n🎯 ОБРАБОТКА ЗАВЕРШЕНА!")
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
                ORDER BY date_req DESC, id DESC
            ''')
            
            winners = []
            for row in cursor.fetchall():
                winner = {
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
                winners.append(winner)
            
            cursor.close()
            conn.close()
            return winners
            
        except Exception as e:
            logging.error(f"❌ Ошибка при получении списка победителей: {e}")
            return None
    
    def is_already_analyzed(self, grant_id: str) -> bool:
        """Проверяет, был ли грант уже проанализирован"""
        try:
            conn = self.pg_manager.get_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM problems WHERE grant_id = %s
            ''', (grant_id,))
            
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logging.error(f"❌ Ошибка при проверке существующего анализа: {e}")
            return False
    
    def analyze_grant(self, grant_data: dict) -> dict:
        """Анализирует грант через LLM"""
        try:
            # Формируем текст для анализа
            analysis_text = f"""
Название проекта: {grant_data.get('name', 'Не указано')}
Направление: {grant_data.get('direction', 'Не указано')}
Описание: {grant_data.get('description', 'Не указано')}
Цель: {grant_data.get('goal', 'Не указано')}
Задачи: {grant_data.get('tasks', 'Не указано')}
Социальная значимость: {grant_data.get('soc_signif', 'Не указано')}
География: {grant_data.get('pj_geo', 'Не указано')}
Целевые группы: {grant_data.get('target_groups', 'Не указано')}
"""
            

            result = self.ollama_analyzer.analyze_grant({
                'req_num': grant_data['req_num'],
                'name': grant_data['name'],
                'description': analysis_text
            })
            
            if result:
                logging.info(f"✅ JSON успешно распарсен: {len(result.get('problems', []))} проблем, {len(result.get('solutions', []))} решений")
                return result
            else:
                logging.warning("⚠️ LLM вернул пустой результат")
                return None
                
        except Exception as e:
            logging.error(f"❌ Ошибка при анализе гранта: {e}")
            return None

def main():
    if len(sys.argv) != 2:
        print("Использование: python time_batch_processing.py <minutes>")
        print("Примеры:")
        print("  python time_batch_processing.py 60      # 1 час")
        print("  python time_batch_processing.py 360     # 6 часов")
        print("  python time_batch_processing.py 1440    # 24 часа")
        return
    
    try:
        minutes = int(sys.argv[1])
        if minutes <= 0:
            print("❌ Время должно быть положительным числом")
            return
    except ValueError:
        print("❌ Время должно быть числом")
        return
    
    # Проверяем подключение к Ollama
    analyzer = OllamaAnalyzer()
    if not analyzer.test_connection():
        logging.error("❌ Не удалось подключиться к ollama")
        return
    
    # Запускаем обработку
    processor = TimeBatchProcessor(minutes)
    processor.run_processing()

if __name__ == "__main__":
    main()
