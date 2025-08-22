#!/usr/bin/env python3
"""
Скрипт для выгрузки таблиц с социальными проблемами и решениями в Excel
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('export_to_excel.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ExcelExporter:
    def __init__(self, host: str = None, port: int = 5432, 
                 database: str = "socfinder", user: str = "socfinder_user", 
                 password: str = None):
        """
        Инициализация экспортера
        
        Args:
            host: хост базы данных (если None, определяется автоматически)
            port: порт базы данных
            database: название базы данных
            user: имя пользователя
            password: пароль (если None, берется из переменной окружения)
        """
        # Автоматически определяем хост: если запущено в Docker - используем имя сервиса
        if host is None:
            import os
            if os.path.exists('/.dockerenv'):
                self.host = "postgres"  # Имя сервиса в docker-compose
            else:
                self.host = "localhost"
        else:
            self.host = host
            
        self.port = port
        self.database = database
        self.user = user
        self.password = password or "Ant1$1ngleoe"  # дефолтный пароль из проекта
        
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
    
    def get_projects_data(self) -> pd.DataFrame:
        """Получение данных проектов"""
        try:
            conn = self.get_connection()
            if not conn:
                return pd.DataFrame()
            
            query = """
                SELECT 
                    id, req_num, name, contest, year, direction, 
                    date_req, region, org, inn, ogrn,
                    implem_start, implem_end, winner, rate,
                    money_req_grant, cofunding, total_money,
                    description, goal, tasks, soc_signif, pj_geo, target_groups,
                    address, web_site, link, okato, oktmo, level
                FROM projects 
                ORDER BY id
            """
            
            df = pd.read_sql_query(query, conn)
            logger.info(f"✅ Получено {len(df)} проектов")
            conn.close()
            return df
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных проектов: {e}")
            return pd.DataFrame()
    
    def get_problems_data(self) -> pd.DataFrame:
        """Получение данных социальных проблем"""
        try:
            conn = self.get_connection()
            if not conn:
                return pd.DataFrame()
            
            query = """
                SELECT 
                    p.id,
                    p.grant_id,
                    p.problem_text,
                    pr.name as project_name,
                    pr.region,
                    pr.year,
                    pr.direction
                FROM problems p
                JOIN projects pr ON p.grant_id = pr.req_num
                ORDER BY p.grant_id, p.id
            """
            
            df = pd.read_sql_query(query, conn)
            logger.info(f"✅ Получено {len(df)} социальных проблем")
            conn.close()
            return df
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных проблем: {e}")
            return pd.DataFrame()
    
    def get_solutions_data(self) -> pd.DataFrame:
        """Получение данных решений"""
        try:
            conn = self.get_connection()
            if not conn:
                return pd.DataFrame()
            
            query = """
                SELECT 
                    s.id,
                    s.grant_id,
                    s.solution_text,
                    pr.name as project_name,
                    pr.region,
                    pr.year,
                    pr.direction
                FROM solutions s
                JOIN projects pr ON s.grant_id = pr.req_num
                ORDER BY s.grant_id, s.id
            """
            
            df = pd.read_sql_query(query, conn)
            logger.info(f"✅ Получено {len(df)} решений")
            conn.close()
            return df
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных решений: {e}")
            return pd.DataFrame()
    
    def get_problems_solutions_summary(self) -> pd.DataFrame:
        """Получение сводной таблицы проблем и решений по проектам"""
        try:
            conn = self.get_connection()
            if not conn:
                return pd.DataFrame()
            
            query = """
                SELECT 
                    pr.id as project_id,
                    pr.req_num,
                    pr.name as project_name,
                    pr.region,
                    pr.year,
                    pr.direction,
                    pr.winner,
                    pr.total_money,
                    COUNT(DISTINCT p.id) as problems_count,
                    COUNT(DISTINCT s.id) as solutions_count,
                    STRING_AGG(DISTINCT p.problem_text, ' | ' ORDER BY p.problem_text) as problems_text,
                    STRING_AGG(DISTINCT s.solution_text, ' | ' ORDER BY s.solution_text) as solutions_text
                FROM projects pr
                LEFT JOIN problems p ON pr.id = p.grant_id
                LEFT JOIN solutions s ON pr.id = s.grant_id
                GROUP BY pr.id, pr.req_num, pr.name, pr.region, pr.year, pr.direction, pr.winner, pr.total_money
                HAVING COUNT(DISTINCT p.id) > 0 OR COUNT(DISTINCT s.id) > 0
                ORDER BY pr.id
            """
            
            df = pd.read_sql_query(query, conn)
            logger.info(f"✅ Получена сводная таблица для {len(df)} проектов")
            conn.close()
            return df
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения сводной таблицы: {e}")
            return pd.DataFrame()
    
    def export_to_excel(self, output_dir: str = "exports") -> str:
        """
        Экспорт только проблем и решений в Excel файл
        
        Args:
            output_dir: директория для сохранения файла
            
        Returns:
            Путь к созданному файлу
        """
        try:
            # Создаем директорию если не существует
            os.makedirs(output_dir, exist_ok=True)
            
            # Генерируем имя файла с timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"socfinder_problems_solutions_{timestamp}.xlsx"
            filepath = os.path.join(output_dir, filename)
            
            # Получаем только проблемы и решения
            logger.info("📊 Получаю данные проблем и решений...")
            
            problems_df = self.get_problems_data()
            solutions_df = self.get_solutions_data()
            
            # Создаем Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Записываем только листы с проблемами и решениями
                if not problems_df.empty:
                    problems_df.to_excel(writer, sheet_name='Социальные_проблемы', index=False)
                    logger.info("✅ Лист 'Социальные_проблемы' записан")
                
                if not solutions_df.empty:
                    solutions_df.to_excel(writer, sheet_name='Решения', index=False)
                    logger.info("✅ Лист 'Решения' записан")
                
                # Добавляем простую статистику
                stats_data = {
                    'Метрика': [
                        'Всего проблем',
                        'Всего решений',
                        'Дата экспорта'
                    ],
                    'Значение': [
                        len(problems_df),
                        len(solutions_df),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                }
                
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='Статистика', index=False)
                logger.info("✅ Лист 'Статистика' записан")
            
            logger.info(f"✅ Экспорт завершен: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Ошибка экспорта в Excel: {e}")
            return ""
    
    def get_database_stats(self) -> Dict:
        """Получение статистики базы данных"""
        try:
            conn = self.get_connection()
            if not conn:
                return {}
            
            with conn.cursor() as cursor:
                # Общее количество проектов
                cursor.execute("SELECT COUNT(*) FROM projects")
                total_projects = cursor.fetchone()[0]
                
                # Количество проектов с проблемами
                cursor.execute("SELECT COUNT(DISTINCT grant_id) FROM problems")
                projects_with_problems = cursor.fetchone()[0]
                
                # Количество проектов с решениями
                cursor.execute("SELECT COUNT(DISTINCT grant_id) FROM solutions")
                projects_with_solutions = cursor.fetchone()[0]
                
                # Общее количество проблем
                cursor.execute("SELECT COUNT(*) FROM problems")
                total_problems = cursor.fetchone()[0]
                
                # Общее количество решений
                cursor.execute("SELECT COUNT(*) FROM solutions")
                total_solutions = cursor.fetchone()[0]
                
                # Статистика по регионам
                cursor.execute("SELECT region, COUNT(*) FROM projects GROUP BY region ORDER BY COUNT(*) DESC LIMIT 10")
                top_regions = cursor.fetchall()
                
                # Статистика по годам
                cursor.execute("SELECT year, COUNT(*) FROM projects GROUP BY year ORDER BY year")
                years_stats = cursor.fetchall()
                
                stats = {
                    'total_projects': total_projects,
                    'projects_with_problems': projects_with_problems,
                    'projects_with_solutions': projects_with_solutions,
                    'total_problems': total_problems,
                    'total_solutions': total_solutions,
                    'top_regions': top_regions,
                    'years_stats': years_stats
                }
                
                conn.close()
                return stats
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {}

def main():
    """Основная функция"""
    exporter = ExcelExporter()
    
    # Проверяем подключение
    if not exporter.test_connection():
        logger.error("❌ Не удалось подключиться к базе данных")
        return
    
    # Получаем простую статистику
    logger.info("📊 Получаю статистику проблем и решений...")
    stats = exporter.get_database_stats()
    
    if stats:
        logger.info(f"📈 Статистика:")
        logger.info(f"   Всего проблем: {stats.get('total_problems', 0)}")
        logger.info(f"   Всего решений: {stats.get('total_solutions', 0)}")
    
    # Экспортируем в Excel
    logger.info("📤 Начинаю экспорт проблем и решений в Excel...")
    output_file = exporter.export_to_excel()
    
    if output_file:
        logger.info(f"🎉 Экспорт успешно завершен!")
        logger.info(f"📁 Файл сохранен: {output_file}")
        
        # Показываем размер файла
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # в МБ
        logger.info(f"📏 Размер файла: {file_size:.2f} МБ")
    else:
        logger.error("❌ Экспорт не удался")

if __name__ == "__main__":
    main()
