#!/usr/bin/env python3
"""
Скрипт для загрузки данных из Excel порциями с минимальным использованием памяти
"""
import os
import sys
import json
import gc
import time
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем путь к app для импорта моделей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

def load_coordinates():
    """Загружаем координаты регионов"""
    try:
        coords_path = os.path.join(os.path.dirname(__file__), '..', 'regions_coordinates.json')
        with open(coords_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки координат: {e}")
        return {}

def get_coordinates(region_name, coordinates_dict):
    """Получаем координаты для региона"""
    if not region_name or pd.isna(region_name):
        return None
    
    region_name = str(region_name)
    
    # Ищем точное совпадение
    if region_name in coordinates_dict:
        coords = coordinates_dict[region_name]
        return {"lat": coords["lat"], "lng": coords["lng"]}
    
    # Ищем частичное совпадение
    for region, coords in coordinates_dict.items():
        if region_name.lower() in region.lower() or region.lower() in region_name.lower():
            return {"lat": coords["lat"], "lng": coords["lng"]}
    
    return None

def clean_value(value):
    """Очищаем значение от NaN и т.п."""
    if pd.isna(value):
        return None
    return value

def parse_money(value):
    """Парсим денежное значение"""
    if pd.isna(value):
        return 0
    
    try:
        if isinstance(value, (int, float)):
            return int(value)
        else:
            money_str = str(value).replace(' ', '').replace(',', '')
            if money_str.replace('.', '').isdigit():
                return int(float(money_str))
    except:
        pass
    
    return 0

def parse_boolean(value):
    """Парсим булево значение"""
    if pd.isna(value):
        return False
    
    if isinstance(value, bool):
        return value
    
    value_str = str(value).lower().strip()
    return value_str in ['true', '1', 'да', 'победитель', 'winner', '+']

def main():
    """Основная функция"""
    start_time = time.time()
    
    logger.info("🚀 Начинаем загрузку данных из Excel порциями...")
    
    # Путь к Excel файлу
    excel_path = os.path.join(os.path.dirname(__file__), '..', 'raw', 'data_114_pres_grants_v20250313.xlsx')
    logger.info(f"Excel файл: {excel_path}")
    
    if not os.path.exists(excel_path):
        logger.error(f"❌ Файл не найден: {excel_path}")
        return 1
    
    # Подключение к базе данных
    database_url = "postgresql://socfinder:test_password_123@localhost:5432/socfinder"
    logger.info(f"Подключение к базе: {database_url}")
    
    # Создаем таблицу если не существует
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Проверяем, существует ли таблица
        result = conn.execute(text("SELECT to_regclass('public.projects')"))
        table_exists = result.scalar() is not None
        
        if not table_exists:
            logger.info("Создаем таблицу projects...")
            conn.execute(text("""
            CREATE TABLE projects (
                id SERIAL PRIMARY KEY,
                name TEXT,
                contest TEXT,
                year INTEGER,
                direction TEXT,
                region TEXT,
                org TEXT,
                winner BOOLEAN DEFAULT FALSE,
                money_req_grant BIGINT DEFAULT 0,
                cofunding BIGINT DEFAULT 0,
                total_money BIGINT DEFAULT 0,
                coordinates JSONB
            )
            """))
            conn.execute(text("CREATE INDEX idx_projects_region ON projects (region)"))
            conn.execute(text("CREATE INDEX idx_projects_winner ON projects (winner)"))
            conn.commit()
        else:
            # Проверяем, есть ли уже данные
            result = conn.execute(text("SELECT COUNT(*) FROM projects"))
            count = result.scalar()
            if count > 0:
                logger.info(f"В базе уже есть {count} проектов. Пропускаем загрузку.")
                return 0
    
    # Загружаем координаты
    logger.info("Загрузка координат регионов...")
    coordinates_dict = load_coordinates()
    logger.info(f"Загружено {len(coordinates_dict)} регионов с координатами")
    
    # Определяем количество строк в Excel
    logger.info("Определяем количество строк в Excel...")
    
    # Используем openpyxl для подсчета строк
    import openpyxl
    wb = openpyxl.load_workbook(excel_path, read_only=True)
    sheet = wb.active
    
    # Подсчитываем строки (за вычетом заголовка)
    nrows = sheet.max_row - 1
    logger.info(f"Всего строк в Excel: {nrows}")
    wb.close()
    
    # Загружаем данные порциями
    chunk_size = 1000
    total_chunks = (nrows // chunk_size) + 1
    total_rows_processed = 0
    
    for chunk_idx in range(total_chunks):
        skip_rows = 1 + chunk_idx * chunk_size  # Пропускаем заголовок и предыдущие чанки
        
        logger.info(f"Загрузка чанка {chunk_idx+1}/{total_chunks} (строки {skip_rows}-{skip_rows+chunk_size-1})...")
        
        try:
            # Загружаем чанк данных
            df_chunk = pd.read_excel(
                excel_path, 
                skiprows=skip_rows,
                nrows=chunk_size,
                dtype=str  # Загружаем все как строки для экономии памяти
            )
            
            if df_chunk.empty:
                logger.info("Достигнут конец файла.")
                break
            
            # Подготавливаем данные для вставки
            rows = []
            for _, row in df_chunk.iterrows():
                try:
                    # Извлекаем данные из строки
                    name = clean_value(row.get(0))
                    contest = clean_value(row.get(1))
                    year = int(row.get(2)) if row.get(2) and str(row.get(2)).isdigit() else None
                    direction = clean_value(row.get(3))
                    region = clean_value(row.get(5))  # Колонка 5
                    org = clean_value(row.get(6))     # Колонка 6
                    
                    # Обрабатываем winner (колонка 11)
                    winner = parse_boolean(row.get(11) if len(row) > 11 else None)
                    
                    # Обрабатываем money_req_grant (колонка 13)
                    money_req_grant = parse_money(row.get(13) if len(row) > 13 else None)
                    
                    # Получаем координаты
                    coords = get_coordinates(region, coordinates_dict)
                    
                    # Добавляем строку
                    rows.append({
                        'name': name,
                        'contest': contest,
                        'year': year,
                        'direction': direction,
                        'region': region,
                        'org': org,
                        'winner': winner,
                        'money_req_grant': money_req_grant,
                        'coordinates': json.dumps(coords) if coords else None
                    })
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки строки: {e}")
                    continue
            
            # Вставляем данные в базу
            if rows:
                with engine.begin() as conn:
                    # Вставляем данные по одной строке
                    for row in rows:
                        insert_query = text("""
                        INSERT INTO projects (name, contest, year, direction, region, org, winner, money_req_grant, coordinates)
                        VALUES (:name, :contest, :year, :direction, :region, :org, :winner, :money_req_grant, :coordinates)
                        """)
                        
                        conn.execute(insert_query, row)
                
                total_rows_processed += len(rows)
                logger.info(f"Вставлено {len(rows)} строк. Всего обработано: {total_rows_processed}")
            
            # Очищаем память
            del df_chunk
            del rows
            gc.collect()
            
        except Exception as e:
            logger.error(f"Ошибка при обработке чанка {chunk_idx+1}: {e}")
            continue
    
    # Создаем индексы для оптимизации запросов
    logger.info("Создаем индексы...")
    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_name ON projects (name)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_org ON projects (org)"))
        conn.execute(text("ANALYZE projects"))
    
    # Проверяем количество загруженных строк
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM projects"))
        count = result.scalar()
        logger.info(f"Всего в базе {count} проектов")
    
    end_time = time.time()
    logger.info(f"✅ Загрузка завершена за {end_time - start_time:.2f} секунд")
    
    # Создаем дамп базы данных
    logger.info("📦 Создаем дамп базы данных...")
    
    dump_dir = os.path.join(os.path.dirname(__file__), '..', 'dumps')
    os.makedirs(dump_dir, exist_ok=True)
    
    dump_path = os.path.join(dump_dir, 'socfinder_full_dump.sql')
    
    try:
        import subprocess
        
        # Используем docker-compose exec для запуска pg_dump внутри контейнера
        cmd = [
            'docker-compose',
            '-f', 'docker-compose.minimal.yml',
            'exec',
            '-T',
            'postgres',
            'pg_dump',
            '-U', 'socfinder',
            '--clean',
            '--if-exists',
            '--no-comments',
            '--no-security-labels',
            '--no-tablespaces',
            '--no-unlogged-table-data',
            '-Fc',  # Custom format
            'socfinder'
        ]
        
        with open(dump_path, 'wb') as f:
            subprocess.run(cmd, stdout=f, check=True)
        
        # Проверяем размер дампа
        dump_size = os.path.getsize(dump_path) / (1024 * 1024)  # в МБ
        logger.info(f"✅ Дамп успешно создан: {dump_path}")
        logger.info(f"📊 Размер дампа: {dump_size:.2f} МБ")
        
        # Создаем скрипт для восстановления из дампа
        restore_script_path = os.path.join(os.path.dirname(__file__), 'restore_from_full_dump.py')
        with open(restore_script_path, 'w') as f:
            f.write('''#!/usr/bin/env python3
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
    dump_path = '/app/data/dumps/socfinder_full_dump.sql'
    
    if not os.path.exists(dump_path):
        logger.error(f"❌ Дамп не найден: {dump_path}")
        return False
    
    try:
        # Проверяем размер дампа
        dump_size = os.path.getsize(dump_path) / (1024 * 1024)  # в МБ
        logger.info(f"📊 Размер дампа: {dump_size:.2f} МБ")
        
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
''')
        
        # Делаем скрипт исполняемым
        os.chmod(restore_script_path, 0o755)
        logger.info(f"✅ Создан скрипт для восстановления: {restore_script_path}")
        
        # Создаем новый Dockerfile
        dockerfile_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'Dockerfile.full')
        with open(dockerfile_path, 'w') as f:
            f.write('''FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Запускаем восстановление из дампа и FastAPI
CMD ["sh", "-c", "python data/scripts/restore_from_full_dump.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
''')
        
        logger.info(f"✅ Создан новый Dockerfile: {dockerfile_path}")
        
        logger.info('''
🚀 Для использования полного дампа:
1. Переименуйте backend/Dockerfile.full в backend/Dockerfile
2. Пересоберите образ: docker-compose -f docker-compose.minimal.yml build backend
3. Запустите контейнеры: docker-compose -f docker-compose.minimal.yml up -d
''')
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка при создании дампа: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
