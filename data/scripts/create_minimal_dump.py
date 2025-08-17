#!/usr/bin/env python3
"""
Скрипт для создания минимального дампа базы данных с тестовыми данными
"""
import os
import sys
import json
import subprocess
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем путь к app для импорта моделей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
from app.models.project import Project, Base

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
    if not region_name:
        return None
    
    # Ищем точное совпадение
    if region_name in coordinates_dict:
        coords = coordinates_dict[region_name]
        return {"lat": coords["lat"], "lng": coords["lng"]}
    
    # Ищем частичное совпадение
    for region, coords in coordinates_dict.items():
        if region_name.lower() in region.lower() or region.lower() in region_name.lower():
            return {"lat": coords["lat"], "lng": coords["lng"]}
    
    return None

def create_test_data(session, coordinates_dict):
    """Создаем тестовые данные для демонстрации"""
    logger.info("🧪 Создаем тестовые данные")
    
    test_projects = [
        {
            "name": "Социальный проект 'Помощь пожилым'",
            "contest": "Президентские гранты 2023",
            "year": 2023,
            "direction": "Поддержка пожилых людей",
            "region": "Москва",
            "org": "НКО 'Забота о старших'",
            "winner": True,
            "money_req_grant": 500000
        },
        {
            "name": "Детский центр творчества",
            "contest": "Президентские гранты 2023",
            "year": 2023,
            "direction": "Поддержка детей и подростков",
            "region": "Санкт-Петербург",
            "org": "Фонд 'Детское творчество'",
            "winner": True,
            "money_req_grant": 750000
        },
        {
            "name": "Экологический проект 'Чистый город'",
            "contest": "Президентские гранты 2023",
            "year": 2023,
            "direction": "Охрана окружающей среды",
            "region": "Краснодарский край",
            "org": "Экологический центр 'Зеленый мир'",
            "winner": False,
            "money_req_grant": 300000
        },
        {
            "name": "Спортивная программа для инвалидов",
            "contest": "Президентские гранты 2023",
            "year": 2023,
            "direction": "Поддержка людей с инвалидностью",
            "region": "Республика Татарстан",
            "org": "Центр адаптивного спорта",
            "winner": True,
            "money_req_grant": 1200000
        },
        {
            "name": "Культурный фестиваль народов России",
            "contest": "Президентские гранты 2023",
            "year": 2023,
            "direction": "Укрепление межнационального единства",
            "region": "Свердловская область",
            "org": "Дом дружбы народов",
            "winner": False,
            "money_req_grant": 800000
        }
    ]
    
    projects = []
    for data in test_projects:
        project = Project(
            name=data["name"],
            contest=data["contest"],
            year=data["year"],
            direction=data["direction"],
            region=data["region"],
            org=data["org"],
            winner=data["winner"],
            money_req_grant=data["money_req_grant"],
            coordinates=get_coordinates(data["region"], coordinates_dict)
        )
        projects.append(project)
    
    session.add_all(projects)
    session.commit()
    
    return len(projects)

def create_database_dump():
    """Создаем дамп базы данных"""
    logger.info("📦 Создаем дамп базы данных...")
    
    dump_dir = os.path.join(os.path.dirname(__file__), '..', 'dumps')
    os.makedirs(dump_dir, exist_ok=True)
    
    dump_path = os.path.join(dump_dir, 'socfinder_minimal_dump.sql')
    
    try:
        # Используем pg_dump для создания дампа
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
            '--format=c',
            'socfinder'
        ]
        
        with open(dump_path, 'wb') as f:
            subprocess.run(cmd, stdout=f, check=True)
        
        logger.info(f"✅ Дамп успешно создан: {dump_path}")
        
        # Проверяем размер дампа
        dump_size = os.path.getsize(dump_path) / (1024)  # в КБ
        logger.info(f"📊 Размер дампа: {dump_size:.2f} КБ")
        
        return dump_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка при создании дампа: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return None

def main():
    """Основная функция"""
    logger.info("🚀 Начинаем создание минимального дампа...")
    
    # Подключение к базе данных
    try:
        # Получаем порт PostgreSQL
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.minimal.yml", "port", "postgres", "5432"],
            capture_output=True, text=True, check=True
        )
        port = result.stdout.strip().split(":")[-1]
        database_url = f"postgresql://socfinder:test_password_123@localhost:{port}/socfinder"
        logger.info(f"URL базы данных: {database_url}")
    except Exception as e:
        logger.error(f"Не удалось определить порт PostgreSQL: {e}")
        database_url = "postgresql://socfinder:test_password_123@localhost:5432/socfinder"
    
    try:
        engine = create_engine(database_url)
        
        # Создаем таблицы
        logger.info("Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        
        # Создаем сессию
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        try:
            # Загружаем координаты
            logger.info("Загрузка координат регионов...")
            coordinates_dict = load_coordinates()
            logger.info(f"Загружено {len(coordinates_dict)} регионов с координатами")
            
            # Создаем тестовые данные
            projects_added = create_test_data(session, coordinates_dict)
            logger.info(f"✅ Добавлено тестовых проектов: {projects_added}")
            
            # Создаем дамп
            dump_path = create_database_dump()
            if dump_path:
                logger.info(f"✅ Минимальный дамп успешно создан: {dump_path}")
                
                # Создаем скрипт для восстановления из дампа
                restore_script_path = os.path.join(os.path.dirname(__file__), 'restore_from_minimal_dump.py')
                with open(restore_script_path, 'w') as f:
                    f.write('''#!/usr/bin/env python3
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
''')
                
                logger.info(f"✅ Создан скрипт для восстановления: {restore_script_path}")
                os.chmod(restore_script_path, 0o755)
                
                # Создаем новый Dockerfile
                dockerfile_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'Dockerfile.minimal')
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
CMD ["sh", "-c", "python data/scripts/restore_from_minimal_dump.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
''')
                
                logger.info(f"✅ Создан новый Dockerfile: {dockerfile_path}")
                
                logger.info('''
🚀 Для использования минимального дампа:
1. Переименуйте backend/Dockerfile.minimal в backend/Dockerfile
2. Пересоберите образ: docker-compose -f docker-compose.minimal.yml build backend
3. Запустите контейнеры: docker-compose -f docker-compose.minimal.yml up -d
''')
            
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            session.rollback()
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к базе данных: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
