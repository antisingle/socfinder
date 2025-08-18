#!/usr/bin/env python3
"""
Простой скрипт для загрузки данных из CSV в PostgreSQL
"""
import os
import sys
import csv
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем путь к app для импорта моделей
sys.path.append('/app')
from app.models.project import Project, Base

def main():
    """Основная функция загрузки данных из CSV"""
    logger.info("🚀 Запускаем загрузку данных из CSV...")
    
    # Подключение к базе данных
    database_url = os.getenv("DATABASE_URL", "postgresql://socfinder_user:Ant1$1ngleoe@postgres:5432/socfinder")
    logger.info(f"Подключение к базе: {database_url}")
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        # Создаем таблицы если их нет
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы созданы/проверены")
        
        session = SessionLocal()
        
        # Путь к CSV файлу
        csv_path = '/app/data/raw/data_114_pres_grants_v20250313.csv'
        
        if not os.path.exists(csv_path):
            logger.error(f"❌ CSV файл не найден: {csv_path}")
            return
        
        logger.info(f"📖 Загружаем данные из: {csv_path}")
        
        projects_added = 0
        batch_size = 100  # Размер батча
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            headers = next(reader)  # Пропускаем заголовки
            logger.info(f"CSV заголовки: {headers}")
            
            batch = []
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Проверяем что строка не пустая
                    if not row or len(row) < 15:
                        continue
                    
                    # Извлекаем данные из строки
                    name = row[0].strip() if len(row) > 0 and row[0] else ""
                    contest = row[1].strip() if len(row) > 1 and row[1] else ""
                    year = int(row[2]) if len(row) > 2 and row[2] and row[2].isdigit() else None
                    direction = row[3].strip() if len(row) > 3 and row[3] else ""
                    region = row[5].strip() if len(row) > 5 and row[5] else ""
                    org = row[6].strip() if len(row) > 6 and row[6] else ""
                    
                    # Winner (колонка 11)
                    winner = False
                    if len(row) > 11 and row[11]:
                        winner_val = str(row[11]).lower().strip()
                        winner = winner_val in ['true', '1', 'да', 'победитель', 'winner', '+']
                    
                    # Money (колонка 13)
                    money_req_grant = 0
                    if len(row) > 13 and row[13]:
                        try:
                            money_str = str(row[13]).replace(' ', '').replace(',', '')
                            if money_str.replace('.', '').isdigit():
                                money_req_grant = int(float(money_str))
                        except:
                            money_req_grant = 0
                    
                    # Создаем проект
                    project = Project(
                        name=name,
                        contest=contest,
                        year=year,
                        direction=direction,
                        region=region,
                        org=org,
                        winner=winner,
                        money_req_grant=money_req_grant
                    )
                    
                    batch.append(project)
                    
                    # Сохраняем батчами
                    if len(batch) >= batch_size:
                        session.add_all(batch)
                        session.commit()
                        projects_added += len(batch)
                        
                        # Очищаем батч
                        batch = []
                        
                        if projects_added % 1000 == 0:
                            logger.info(f"✅ Сохранено: {projects_added} проектов")
                
                except Exception as e:
                    logger.error(f"Ошибка в строке {row_num}: {e}")
                    continue
            
            # Сохраняем остатки
            if batch:
                session.add_all(batch)
                session.commit()
                projects_added += len(batch)
        
        logger.info(f"🎉 Загрузка завершена!")
        logger.info(f"✅ Добавлено проектов: {projects_added}")
        
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        if 'session' in locals():
            session.rollback()
        raise
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main()
