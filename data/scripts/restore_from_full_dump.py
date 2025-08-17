#!/usr/bin/env python3
"""
Скрипт для восстановления базы данных из полного дампа
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
    logger.info("🔄 Восстанавливаем базу данных из полного дампа...")
    
    # Путь к дампу
    dump_path = '/app/data/dumps/socfinder_full_dump_29_fields.sql'
    
    if not os.path.exists(dump_path):
        logger.error(f"❌ Дамп не найден: {dump_path}")
        return False
    
    try:
        # Проверяем размер дампа
        dump_size = os.path.getsize(dump_path) / (1024 * 1024)  # в МБ
        logger.info(f"📊 Размер дампа: {dump_size:.2f} МБ")
        
        # Восстанавливаем из дампа (текстовый формат)
        cmd = [
            'psql',
            '--host=postgres',
            '--port=5432',
            '--username=socfinder',
            '--dbname=socfinder',
            '--file=' + dump_path
        ]
        
        # Запускаем восстановление
        env = os.environ.copy()
        env['PGPASSWORD'] = os.getenv('POSTGRES_PASSWORD', 'test_password_123')
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Проверяем, есть ли данные в базе, несмотря на ошибку
            logger.warning(f"⚠️ pg_restore завершился с кодом {result.returncode}")
            logger.warning(f"⚠️ stderr: {result.stderr}")
            
            # Проверяем, что таблица projects существует и содержит данные
            try:
                check_cmd = [
                    'psql',
                    '--host=postgres',
                    '--port=5432',
                    '--username=socfinder',
                    '--dbname=socfinder',
                    '--command=SELECT COUNT(*) FROM projects;'
                ]
                
                check_result = subprocess.run(check_cmd, env=env, capture_output=True, text=True)
                if check_result.returncode == 0 and '166848' in check_result.stdout:
                    logger.info("✅ Данные в базе есть, несмотря на ошибку pg_restore")
                    return True
                else:
                    logger.error("❌ Данные в базе отсутствуют")
                    return False
            except Exception as e:
                logger.error(f"❌ Не удалось проверить данные: {e}")
                return False
        
        logger.info(f"✅ База данных успешно восстановлена из полного дампа")
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
