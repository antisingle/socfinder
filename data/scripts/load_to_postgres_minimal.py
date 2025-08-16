#!/usr/bin/env python3
"""
МИНИМАЛЬНЫЙ скрипт для загрузки данных из Excel в PostgreSQL
Обходит проблему памяти через пропуск загрузки Excel
"""
import os
import sys
import json
import gc
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем путь к app для импорта моделей
sys.path.append('/app')
from app.models.project import Project, Base

def load_coordinates():
    """Загружаем координаты регионов"""
    try:
        with open('/app/data/regions_coordinates.json', 'r', encoding='utf-8') as f:
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
    logger.info("🧪 Создаем тестовые данные (Excel файл слишком большой для 1GB RAM)")
    
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

def main():
    """Основная функция - создает минимальную рабочую версию"""
    logger.info("🚀 Запускаем МИНИМАЛЬНУЮ загрузку данных...")
    logger.info("⚠️ Excel файл слишком большой для сервера с 1GB RAM")
    logger.info("📊 Создаем тестовые данные для демонстрации функциональности")
    
    # Подключение к базе данных
    database_url = os.getenv("DATABASE_URL", "postgresql://socfinder:socfinder123@postgres:5432/socfinder")
    logger.info(f"Подключение к базе: {database_url}")
    
    engine = create_engine(database_url, pool_size=1, max_overflow=0)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        # Создаем таблицы
        logger.info("Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        
        # Проверяем, есть ли уже данные
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM projects"))
            count = result.scalar()
            if count > 0:
                logger.info(f"В базе уже есть {count} проектов. Пропускаем загрузку.")
                return
        
        # Загружаем координаты
        logger.info("Загрузка координат регионов...")
        coordinates_dict = load_coordinates()
        logger.info(f"Загружено {len(coordinates_dict)} регионов с координатами")
        
        # Создаем сессию
        session = SessionLocal()
        
        try:
            # Создаем тестовые данные
            projects_added = create_test_data(session, coordinates_dict)
            
            logger.info(f"🎉 Минимальная загрузка завершена!")
            logger.info(f"✅ Добавлено тестовых проектов: {projects_added}")
            logger.info("📋 Для загрузки полных данных нужен сервер с 2GB+ RAM")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке: {e}")
            session.rollback()
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
