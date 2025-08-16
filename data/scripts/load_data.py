#!/usr/bin/env python3
"""
Скрипт для загрузки данных из Excel в SQLite базу данных (упрощенная версия без pandas)
"""
import sqlite3
import json
import os
import sys
from openpyxl import load_workbook
from datetime import datetime

# Добавляем путь к модулям приложения
sys.path.append('/app')

def load_regions_coordinates():
    """Загружает координаты регионов"""
    with open('/app/data/regions_coordinates.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_data(df):
    """Очищает и подготавливает данные"""
    print("Очистка данных...")
    
    # Заменяем пустые строки на None
    df = df.replace('', None)
    
    # Конвертируем даты
    date_columns = ['date_req', 'implem_start', 'implem_end']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Конвертируем числовые поля
    numeric_columns = ['money_req_grant', 'cofunding', 'total_money', 'rate']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Конвертируем boolean поля
    if 'winner' in df.columns:
        df['winner'] = df['winner'].map({'Да': True, 'Нет': False, True: True, False: False})
    
    print(f"Данные очищены. Строк: {len(df)}")
    return df

def add_coordinates(df, coordinates_map):
    """Добавляет координаты к проектам на основе региона"""
    print("Добавление координат...")
    
    def get_coordinates(region):
        if pd.isna(region) or region is None:
            return None
        return coordinates_map.get(region, {"lat": 55.7558, "lng": 37.6173})  # Москва по умолчанию
    
    df['coordinates'] = df['region'].apply(get_coordinates)
    df['coordinates'] = df['coordinates'].apply(lambda x: json.dumps(x) if x else None)
    
    print("Координаты добавлены")
    return df

def create_database():
    """Создает базу данных и таблицы"""
    print("Создание базы данных...")
    
    conn = sqlite3.connect('/app/socfinder.db')
    cursor = conn.cursor()
    
    # Создаем таблицу projects
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contest TEXT,
        year INTEGER,
        direction TEXT,
        date_req DATETIME,
        region TEXT,
        org TEXT,
        inn TEXT,
        ogrn TEXT,
        implem_start DATETIME,
        implem_end DATETIME,
        winner BOOLEAN,
        rate REAL,
        money_req_grant INTEGER,
        cofunding INTEGER,
        total_money INTEGER,
        description TEXT,
        goal TEXT,
        tasks TEXT,
        soc_signif TEXT,
        pj_geo TEXT,
        target_groups TEXT,
        address TEXT,
        web_site TEXT,
        req_num TEXT,
        link TEXT,
        okato TEXT,
        oktmo TEXT,
        level TEXT,
        coordinates TEXT
    )
    ''')
    
    # Создаем индексы для быстрого поиска
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_region ON projects(region)',
        'CREATE INDEX IF NOT EXISTS idx_year ON projects(year)',
        'CREATE INDEX IF NOT EXISTS idx_direction ON projects(direction)',
        'CREATE INDEX IF NOT EXISTS idx_winner ON projects(winner)',
        'CREATE INDEX IF NOT EXISTS idx_org ON projects(org)',
        'CREATE INDEX IF NOT EXISTS idx_name ON projects(name)'
    ]
    
    for index in indexes:
        cursor.execute(index)
    
    conn.commit()
    conn.close()
    print("База данных создана")

def load_excel_to_db():
    """Основная функция загрузки данных"""
    print("Начинаем загрузку данных...")
    
    # Проверяем наличие файла
    excel_file = '/app/data/raw/data_114_pres_grants_v20250313.xlsx'
    if not os.path.exists(excel_file):
        print(f"ОШИБКА: Файл {excel_file} не найден!")
        return False
    
    try:
        # Загружаем координаты регионов
        coordinates_map = load_regions_coordinates()
        
        # Создаем базу данных
        create_database()
        
        # Читаем Excel файл
        print("Загрузка Excel файла...")
        df = pd.read_excel(excel_file)
        print(f"Загружено строк из Excel: {len(df)}")
        
        # Очищаем данные
        df = clean_data(df)
        
        # Добавляем координаты
        df = add_coordinates(df, coordinates_map)
        
        # Загружаем в базу данных
        print("Загрузка в базу данных...")
        conn = sqlite3.connect('/app/socfinder.db')
        
        # Загружаем данные порциями для больших файлов
        chunk_size = 1000
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            chunk.to_sql('projects', conn, if_exists='append', index=False)
            print(f"Загружено {min(i+chunk_size, len(df))}/{len(df)} записей")
        
        conn.close()
        
        print("✅ Данные успешно загружены!")
        print(f"Всего проектов в базе: {len(df)}")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА при загрузке данных: {e}")
        return False

if __name__ == "__main__":
    success = load_excel_to_db()
    sys.exit(0 if success else 1)
