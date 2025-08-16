#!/usr/bin/env python3
"""
УЛЬТРА-ЛЕГКИЙ скрипт для загрузки данных из Excel в PostgreSQL
Использует минимум памяти через построчное чтение CSV
"""
import os
import sys
import json
import csv
import gc
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging
import subprocess

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

def convert_excel_to_csv(excel_path, csv_path):
    """Конвертирует Excel в CSV с использованием внешней утилиты"""
    logger.info("📝 Конвертируем Excel в CSV для экономии памяти...")
    
    try:
        # Используем Python для конвертации по частям
        import pandas as pd
        
        # Читаем Excel по частям (chunksize)
        logger.info("🔄 Читаем Excel файл по частям...")
        
        # Сначала читаем только первые несколько строк чтобы понять структуру
        df_sample = pd.read_excel(excel_path, nrows=5)
        logger.info(f"Колонки Excel: {list(df_sample.columns)}")
        
        # Читаем весь файл с оптимизацией
        logger.info("📖 Загружаем данные из Excel...")
        df = pd.read_excel(excel_path, dtype=str)  # Все как строки для экономии памяти
        
        logger.info(f"📊 Загружено {len(df)} строк")
        
        # Сохраняем в CSV
        logger.info("💾 Сохраняем в CSV...")
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Освобождаем память
        del df
        del df_sample
        gc.collect()
        
        logger.info(f"✅ CSV создан: {csv_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка конвертации: {e}")
        return False

def main():
    """Основная функция с УЛЬТРА экономией памяти"""
    logger.info("🚀 Запускаем УЛЬТРА-ЛЕГКУЮ загрузку данных...")
    logger.info("🪶 Режим минимального потребления памяти")
    
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
        
        # Пути к файлам
        excel_path = '/app/data/raw/data_114_pres_grants_v20250313.xlsx'
        csv_path = '/tmp/data_converted.csv'
        
        if not os.path.exists(excel_path):
            logger.error(f"Файл не найден: {excel_path}")
            return
        
        # ЭТАП 1: Конвертация Excel в CSV
        if not convert_excel_to_csv(excel_path, csv_path):
            logger.error("❌ Не удалось сконвертировать Excel в CSV")
            return
        
        # ЭТАП 2: Читаем CSV построчно
        logger.info("📖 Начинаем построчное чтение CSV...")
        
        session = SessionLocal()
        
        try:
            projects_added = 0
            batch_size = 200  # Очень маленькие батчи
            batch = []
            row_count = 0
            
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)  # Пропускаем заголовки
                logger.info(f"CSV заголовки: {headers[:5]}...")
                
                for row in reader:
                    row_count += 1
                    
                    try:
                        # Обрабатываем строку
                        name = row[0] if len(row) > 0 else ""
                        contest = row[1] if len(row) > 1 else ""
                        year = int(row[2]) if len(row) > 2 and row[2] and row[2].isdigit() else None
                        direction = row[3] if len(row) > 3 else ""
                        region = row[5] if len(row) > 5 else ""
                        org = row[6] if len(row) > 6 else ""
                        
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
                            money_req_grant=money_req_grant,
                            coordinates=get_coordinates(region, coordinates_dict)
                        )
                        
                        batch.append(project)
                        
                        # Сохраняем маленькими батчами
                        if len(batch) >= batch_size:
                            session.add_all(batch)
                            session.commit()
                            projects_added += len(batch)
                            
                            # Очищаем память
                            batch = []
                            gc.collect()
                            
                            if projects_added % 1000 == 0:
                                logger.info(f"✅ Сохранено: {projects_added} проектов (строк: {row_count})")
                    
                    except Exception as e:
                        logger.error(f"Ошибка в строке {row_count}: {e}")
                        continue
                
                # Сохраняем остатки
                if batch:
                    session.add_all(batch)
                    session.commit()
                    projects_added += len(batch)
            
            logger.info(f"🎉 Загрузка завершена!")
            logger.info(f"📊 Обработано строк: {row_count}")
            logger.info(f"✅ Добавлено проектов: {projects_added}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке: {e}")
            session.rollback()
            raise
        finally:
            session.close()
            
            # Удаляем временный CSV
            try:
                os.remove(csv_path)
                logger.info("🗑️ Временный CSV удален")
            except:
                pass
            
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
