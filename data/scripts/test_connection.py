#!/usr/bin/env python3
"""
Простой скрипт для тестирования подключения к базе данных
"""
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Тестирует подключение к базе данных"""
    try:
        # Подключаемся к базе
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="socfinder",
            user="socfinder",
            password="test_password_123"
        )
        
        logger.info("✅ Подключение к базе успешно")
        
        # Проверяем таблицу
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM projects")
            count = cur.fetchone()[0]
            logger.info(f"📊 Количество проектов: {count}")
            
            # Проверяем структуру
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'projects'
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            logger.info(f"📋 Структура таблицы:")
            for col_name, col_type in columns:
                logger.info(f"   - {col_name}: {col_type}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    test_connection()
