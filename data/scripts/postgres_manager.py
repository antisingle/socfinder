#!/usr/bin/env python3
"""
Скрипт для работы с PostgreSQL: чтение грантов и сохранение результатов анализа
"""

try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️ psycopg2 не установлен. Используйте: pip install psycopg2-binary")
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('postgres_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PostgresManager:
    def __init__(self, host: str = "localhost", port: int = 5432, 
                 database: str = "socfinder", user: str = "socfinder_user", 
                 password: str = None):
        """
        Инициализация менеджера PostgreSQL
        
        Args:
            host: хост базы данных
            port: порт базы данных
            database: название базы данных
            user: имя пользователя
            password: пароль (если None, берется из переменной окружения)
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password or "Ant1$1ngleoe"  # дефолтный пароль из проекта
        
        # Поля для чтения из таблицы projects
        self.project_fields = [
            'id', 'req_num', 'name', 'direction', 'description', 
            'goal', 'tasks', 'soc_signif', 'pj_geo', 'target_groups'
        ]
    
    def get_connection(self):
        """Получение соединения с базой данных"""
        try:
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Тест подключения к базе данных"""
        try:
            conn = self.get_connection()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()
                    logger.info(f"✅ Подключение к PostgreSQL успешно: {version[0]}")
                    conn.close()
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка теста подключения: {e}")
            return False
    
    def get_grant_by_id(self, grant_id: int) -> Optional[Dict]:
        """
        Получение гранта по ID
        
        Args:
            grant_id: ID гранта в таблице projects
            
        Returns:
            Словарь с данными гранта или None
        """
        try:
            conn = self.get_connection()
            if not conn:
                return None
            
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                fields_str = ', '.join(self.project_fields)
                query = f"SELECT {fields_str} FROM projects WHERE id = %s"
                cursor.execute(query, (grant_id,))
                
                result = cursor.fetchone()
                if result:
                    logger.info(f"✅ Грант {grant_id} получен: {result.get('name', 'N/A')[:50]}...")
                    return dict(result)
                else:
                    logger.warning(f"⚠️ Грант с ID {grant_id} не найден")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения гранта {grant_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_grants_batch(self, start_id: int, batch_size: int) -> List[Dict]:
        """
        Получение пакета грантов
        
        Args:
            start_id: начальный ID
            batch_size: размер пакета
            
        Returns:
            Список словарей с данными грантов
        """
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                fields_str = ', '.join(self.project_fields)
                query = f"""
                    SELECT {fields_str} 
                    FROM projects 
                    WHERE id >= %s 
                    ORDER BY id 
                    LIMIT %s
                """
                cursor.execute(query, (start_id, batch_size))
                
                results = cursor.fetchall()
                grants = [dict(row) for row in results]
                
                logger.info(f"✅ Получен пакет грантов: {len(grants)} записей (ID {start_id}-{start_id + len(grants) - 1})")
                return grants
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения пакета грантов: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def save_analysis_results(self, analysis_results: List[Dict]) -> bool:
        """
        Сохранение результатов анализа в базу данных
        
        Args:
            analysis_results: список результатов анализа от LLM
            
        Returns:
            True если сохранение успешно, False иначе
        """
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                saved_count = 0
                
                for analysis in analysis_results:
                    grant_id = analysis.get('grant_id')
                    problems = analysis.get('problems', [])
                    solutions = analysis.get('solutions', [])
                    
                    if not grant_id:
                        logger.warning("⚠️ Пропускаю запись без grant_id")
                        continue
                    
                    # Сохраняем проблемы
                    for problem_text in problems:
                        # Проверяем тип и преобразуем в строку
                        if problem_text:
                            if isinstance(problem_text, dict):
                                # Если это словарь, берем первый ключ или значение
                                problem_str = str(list(problem_text.values())[0]) if problem_text.values() else str(problem_text)
                            else:
                                problem_str = str(problem_text)
                            
                            if problem_str.strip():
                                cursor.execute(
                                    "INSERT INTO problems (grant_id, problem_text) VALUES (%s, %s)",
                                    (grant_id, problem_str.strip())
                                )
                    
                    # Сохраняем решения
                    for solution_text in solutions:
                        # Проверяем тип и преобразуем в строку
                        if solution_text:
                            if isinstance(solution_text, dict):
                                # Если это словарь, берем первый ключ или значение
                                solution_str = str(list(solution_text.values())[0]) if solution_text.values() else str(solution_text)
                            else:
                                solution_str = str(solution_text)
                            
                            if solution_str.strip():
                                cursor.execute(
                                    "INSERT INTO solutions (grant_id, solution_text) VALUES (%s, %s)",
                                    (grant_id, solution_str.strip())
                                )
                    
                    saved_count += 1
                
                conn.commit()
                logger.info(f"✅ Результаты анализа сохранены: {saved_count} грантов")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результатов: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def get_analysis_summary(self) -> Dict:
        """
        Получение сводки по анализу
        
        Returns:
            Словарь со статистикой
        """
        try:
            conn = self.get_connection()
            if not conn:
                return {}
            
            with conn.cursor() as cursor:
                # Общее количество грантов
                cursor.execute("SELECT COUNT(*) FROM projects")
                total_grants = cursor.fetchone()[0]
                
                # Количество проанализированных грантов
                cursor.execute("SELECT COUNT(DISTINCT grant_id) FROM problems")
                analyzed_grants = cursor.fetchone()[0]
                
                # Общее количество проблем
                cursor.execute("SELECT COUNT(*) FROM problems")
                total_problems = cursor.fetchone()[0]
                
                # Общее количество решений
                cursor.execute("SELECT COUNT(*) FROM solutions")
                total_solutions = cursor.fetchone()[0]
                
                summary = {
                    'total_grants': total_grants,
                    'analyzed_grants': analyzed_grants,
                    'total_problems': total_problems,
                    'total_solutions': total_solutions,
                    'analysis_progress': f"{(analyzed_grants/total_grants*100):.1f}%" if total_grants > 0 else "0%"
                }
                
                logger.info(f"📊 Сводка анализа: {summary}")
                return summary
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения сводки: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def check_existing_analysis(self, grant_id: str) -> bool:
        """
        Проверка, анализировался ли уже грант
        
        Args:
            grant_id: ID гранта
            
        Returns:
            True если анализ уже есть, False иначе
        """
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM problems WHERE grant_id = %s",
                    (grant_id,)
                )
                count = cursor.fetchone()[0]
                
                return count > 0
                
        except Exception as e:
            logger.error(f"❌ Ошибка проверки существующего анализа: {e}")
            return False
        finally:
            if conn:
                conn.close()

def main():
    """Тестовая функция"""
    if not POSTGRES_AVAILABLE:
        logger.error("❌ psycopg2 не доступен. Установите: pip install psycopg2-binary")
        return
    
    manager = PostgresManager()
    
    # Проверяем подключение
    if not manager.test_connection():
        logger.error("Не удалось подключиться к PostgreSQL")
        return
    
    # Получаем первый грант для теста
    logger.info("🧪 Тестирую получение первого гранта...")
    first_grant = manager.get_grant_by_id(1)
    
    if first_grant:
        logger.info("✅ Первый грант получен успешно!")
        logger.info(f"Название: {first_grant.get('name', 'N/A')}")
        logger.info(f"Направление: {first_grant.get('direction', 'N/A')}")
        logger.info(f"Описание: {first_grant.get('description', 'N/A')[:100]}...")
    else:
        logger.error("❌ Не удалось получить первый грант")
    
    # Получаем сводку
    logger.info("📊 Получаю сводку по базе...")
    summary = manager.get_analysis_summary()
    if summary:
        logger.info(f"Всего грантов: {summary.get('total_grants', 0)}")
        logger.info(f"Проанализировано: {summary.get('analyzed_grants', 0)}")

if __name__ == "__main__":
    main()
