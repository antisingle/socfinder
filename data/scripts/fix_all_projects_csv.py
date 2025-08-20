#!/usr/bin/env python3
"""
Скрипт для исправления всех проектов в базе данных из CSV
"""
import os
import sys
import csv
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем путь к app для импорта моделей
sys.path.append('/app')
from app.models.project import Project, Base

def parse_date(date_str):
    """Парсит дату из строки"""
    if not date_str or date_str.strip() == '':
        return None
    
    try:
        # Пробуем разные форматы дат
        for fmt in ['%Y.%m.%d', '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        return None
    except:
        return None

def parse_number(num_str):
    """Парсит число из строки"""
    if not num_str or str(num_str).strip() == '':
        return None
    
    try:
        # Убираем пробелы и заменяем запятые на точки
        clean_str = str(num_str).replace(' ', '').replace(',', '.')
        if clean_str.replace('.', '').replace('-', '').isdigit():
            return float(clean_str)
        return None
    except:
        return None

def parse_boolean(bool_str):
    """Парсит булево значение"""
    if not bool_str or str(bool_str).strip() == '':
        return False
    
    bool_val = str(bool_str).lower().strip()
    return bool_val in ['true', '1', 'да', 'победитель', 'winner', '+', 'true']

def clean_text(text):
    """Очищает текст от лишних символов"""
    if not text:
        return None
    
    # Убираем лишние пробелы и переносы строк
    cleaned = str(text).strip()
    if cleaned == '':
        return None
    return cleaned

def get_coordinates(region_name):
    """Получает координаты для региона"""
    # Базовые координаты для основных регионов
    region_coords = {
        'Москва': {'lat': 55.7558, 'lng': 37.6173},
        'Санкт-Петербург': {'lat': 59.9311, 'lng': 30.3609},
        'Республика Марий Эл': {'lat': 56.4307, 'lng': 48.9964},
        'Ульяновская область': {'lat': 54.3176, 'lng': 48.3706},
        'Красноярский край': {'lat': 56.0184, 'lng': 92.8672},
        'Омская область': {'lat': 54.9914, 'lng': 73.3645},
        'Республика Татарстан': {'lat': 55.7887, 'lng': 49.1221},
        'Нижегородская область': {'lat': 56.2965, 'lng': 43.9361},
        'Свердловская область': {'lat': 56.8519, 'lng': 60.6122},
        'Челябинская область': {'lat': 55.1644, 'lng': 61.4368}
    }
    
    # Ищем точное совпадение
    for region, coords in region_coords.items():
        if region_name and region in region_name:
            return coords
    
    # Возвращаем координаты Москвы как fallback
    return {'lat': 55.7558, 'lng': 37.6173}

def main():
    """Основная функция исправления всех проектов"""
    logger.info("🚀 Начинаем исправление всех проектов из CSV...")
    
    # Подключение к базе данных
    database_url = os.getenv("DATABASE_URL", "postgresql://socfinder_user:Ant1$1ngleoe@postgres:5432/socfinder")
    logger.info(f"Подключение к базе: {database_url}")
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Путь к CSV файлу
    csv_path = '/app/data/raw/data_114_pres_grants_v20250313.csv'
    
    if not os.path.exists(csv_path):
        logger.error(f"❌ CSV файл не найден: {csv_path}")
        return
    
    session = SessionLocal()
    
    try:
        # Очищаем все существующие проекты
        logger.info("🗑️ Очищаем существующие проекты...")
        session.query(Project).delete()
        session.commit()
        logger.info("✅ Существующие проекты удалены")
        
        # Читаем CSV файл
        logger.info("📖 Читаем CSV файл...")
        projects_added = 0
        batch_size = 1000
        batch = []
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            # Используем csv.reader с правильным разделителем
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            headers = next(reader)  # Пропускаем заголовки
            logger.info(f"CSV заголовки: {headers[:5]}...")
            
            for row_num, row in enumerate(reader, 2):
                if row_num % 10000 == 0:
                    logger.info(f"Обработано строк: {row_num}")
                
                try:
                    # Проверяем что строка не пустая
                    if not row or len(row) < 15:
                        continue
                    
                    # Маппим данные по позициям
                    name = clean_text(row[0]) if len(row) > 0 else None
                    contest = clean_text(row[1]) if len(row) > 1 else None
                    year = int(row[2]) if len(row) > 2 and row[2] and str(row[2]).isdigit() else None
                    direction = clean_text(row[3]) if len(row) > 3 else None
                    date_req = parse_date(row[4]) if len(row) > 4 else None
                    region = clean_text(row[5]) if len(row) > 5 else None
                    org = clean_text(row[6]) if len(row) > 6 else None
                    inn = clean_text(row[7]) if len(row) > 7 else None
                    ogrn = clean_text(row[8]) if len(row) > 8 else None
                    implem_start = parse_date(row[9]) if len(row) > 9 else None
                    implem_end = parse_date(row[10]) if len(row) > 10 else None
                    winner = parse_boolean(row[11]) if len(row) > 11 else False
                    rate = parse_number(row[12]) if len(row) > 12 else None
                    money_req_grant = parse_number(row[13]) if len(row) > 13 else None
                    cofunding = parse_number(row[14]) if len(row) > 14 else None
                    total_money = parse_number(row[15]) if len(row) > 15 else None
                    description = clean_text(row[16]) if len(row) > 16 else None
                    goal = clean_text(row[17]) if len(row) > 17 else None
                    tasks = clean_text(row[18]) if len(row) > 18 else None
                    soc_signif = clean_text(row[19]) if len(row) > 19 else None
                    pj_geo = clean_text(row[20]) if len(row) > 20 else None
                    target_groups = clean_text(row[21]) if len(row) > 21 else None
                    address = clean_text(row[22]) if len(row) > 22 else None
                    web_site = clean_text(row[23]) if len(row) > 23 else None
                    req_num = clean_text(row[24]) if len(row) > 24 else None
                    link = clean_text(row[25]) if len(row) > 25 else None
                    okato = clean_text(row[26]) if len(row) > 26 else None
                    oktmo = clean_text(row[27]) if len(row) > 27 else None
                    level = clean_text(row[28]) if len(row) > 28 else None
                    
                    # Получаем координаты для региона
                    coordinates = get_coordinates(region)
                    
                    # Создаем проект
                    project = Project(
                        name=name,
                        contest=contest,
                        year=year,
                        direction=direction,
                        date_req=date_req,
                        region=region,
                        org=org,
                        inn=inn,
                        ogrn=ogrn,
                        implem_start=implem_start,
                        implem_end=implem_end,
                        winner=winner,
                        rate=rate,
                        money_req_grant=money_req_grant,
                        cofunding=cofunding,
                        total_money=total_money,
                        description=description,
                        goal=goal,
                        tasks=tasks,
                        soc_signif=soc_signif,
                        pj_geo=pj_geo,
                        target_groups=target_groups,
                        address=address,
                        web_site=web_site,
                        req_num=req_num,
                        link=link,
                        okato=okato,
                        oktmo=oktmo,
                        level=level,
                        coordinates=coordinates
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
        
        logger.info(f"🎉 Исправление завершено!")
        logger.info(f"✅ Добавлено проектов: {projects_added}")
        
        # Проверяем результат
        total_projects = session.query(Project).count()
        logger.info(f"📊 Всего проектов в базе: {total_projects}")
        
        # Проверяем проект 289110
        project_289110 = session.query(Project).filter(Project.id == 289110).first()
        if project_289110:
            logger.info(f"✅ Проект 289110: {project_289110.name}")
            logger.info(f"   Регион: {project_289110.region}")
            logger.info(f"   Организация: {project_289110.org}")
        else:
            logger.warning("⚠️ Проект 289110 не найден")
        
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
