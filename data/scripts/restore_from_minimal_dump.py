#!/usr/bin/env python3
"""
Скрипт для восстановления базы данных из минимального дампа
"""
import os
import sys
import subprocess
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def restore_from_dump():
    """Восстанавливаем базу данных из дампа"""
    logger.info("🔄 Восстанавливаем базу данных из минимального дампа...")
    
    # Путь к дампу
    dump_path = '/app/data/dumps/socfinder_minimal_dump.sql'
    
    if not os.path.exists(dump_path):
        logger.error(f"❌ Дамп не найден: {dump_path}")
        return False
    
    try:
        # Проверяем размер дампа
        dump_size = os.path.getsize(dump_path) / (1024)  # в КБ
        logger.info(f"📊 Размер дампа: {dump_size:.2f} КБ")
        
        # Восстанавливаем из дампа
        cmd = [
            'pg_restore',
            '--host=postgres',
            '--port=5432',
            '--username=socfinder',
            '--dbname=socfinder',
            '--clean',
            '--if-exists',
            '--no-owner',
            '--no-privileges',
            '--verbose',
            dump_path
        ]
        
        # Запускаем восстановление
        env = os.environ.copy()
        env['PGPASSWORD'] = os.getenv('POSTGRES_PASSWORD', 'test_password_123')
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Ошибка при восстановлении: {result.stderr}")
            return False
        
        logger.info(f"✅ База данных успешно восстановлена из минимального дампа")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция"""
    start_time = time.time()
    
    # Восстанавливаем из дампа
    success = restore_from_dump()
    
    end_time = time.time()
    logger.info(f"⏱️ Общее время выполнения: {end_time - start_time:.2f} секунд")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
