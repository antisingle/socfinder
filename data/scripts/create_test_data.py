#!/usr/bin/env python3
"""
Создание тестовых данных для быстрой проверки API
"""
import sqlite3
import json
import os
from datetime import datetime

def create_test_database():
    """Создает базу с тестовыми данными"""
    
    # Путь к базе данных
    db_path = '/app/socfinder.db'
    
    # Подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу
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
    
    # Индексы
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
    
    # Тестовые данные
    test_projects = [
        {
            'name': 'Развитие волонтерства в Москве',
            'contest': 'Первый конкурс 2023',
            'year': 2023,
            'direction': 'Социальное обслуживание',
            'date_req': '2023-03-15',
            'region': 'Москва',
            'org': 'Фонд "Добрые дела"',
            'inn': '7701234567',
            'ogrn': '1027700123456',
            'winner': True,
            'money_req_grant': 500000,
            'cofunding': 100000,
            'total_money': 600000,
            'description': 'Проект направлен на развитие волонтерского движения в Москве',
            'goal': 'Увеличить количество волонтеров на 30%',
            'coordinates': '{"lat": 55.7558, "lng": 37.6173}'
        },
        {
            'name': 'Помощь пожилым людям',
            'contest': 'Первый конкурс 2023',
            'year': 2023,
            'direction': 'Социальное обслуживание',
            'date_req': '2023-03-20',
            'region': 'Санкт-Петербург',
            'org': 'НКО "Забота"',
            'inn': '7801234567',
            'ogrn': '1027800123456',
            'winner': True,
            'money_req_grant': 300000,
            'cofunding': 50000,
            'total_money': 350000,
            'description': 'Социальная поддержка пожилых людей',
            'goal': 'Помочь 200 пожилым людям',
            'coordinates': '{"lat": 59.9311, "lng": 30.3609}'
        },
        {
            'name': 'Экологический проект',
            'contest': 'Второй конкурс 2023',
            'year': 2023,
            'direction': 'Охрана окружающей среды',
            'date_req': '2023-09-10',
            'region': 'Московская область',
            'org': 'Экофонд "Зеленая планета"',
            'inn': '5001234567',
            'ogrn': '1025000123456',
            'winner': False,
            'money_req_grant': 800000,
            'cofunding': 200000,
            'total_money': 1000000,
            'description': 'Очистка водоемов и лесов',
            'goal': 'Очистить 10 водоемов',
            'coordinates': '{"lat": 55.5815, "lng": 36.9741}'
        },
        {
            'name': 'Спорт для детей',
            'contest': 'Первый конкурс 2024',
            'year': 2024,
            'direction': 'Физическая культура и спорт',
            'date_req': '2024-02-01',
            'region': 'Краснодарский край',
            'org': 'Спортивный клуб "Чемпион"',
            'inn': '2301234567',
            'ogrn': '1022300123456',
            'winner': True,
            'money_req_grant': 400000,
            'cofunding': 80000,
            'total_money': 480000,
            'description': 'Развитие детского спорта в крае',
            'goal': 'Привлечь 500 детей к спорту',
            'coordinates': '{"lat": 45.0355, "lng": 38.9753}'
        }
    ]
    
    # Вставляем тестовые данные
    for project in test_projects:
        cursor.execute('''
        INSERT INTO projects (
            name, contest, year, direction, date_req, region, org, inn, ogrn,
            winner, money_req_grant, cofunding, total_money, description, goal, coordinates
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project['name'], project['contest'], project['year'], project['direction'],
            project['date_req'], project['region'], project['org'], project['inn'], project['ogrn'],
            project['winner'], project['money_req_grant'], project['cofunding'], 
            project['total_money'], project['description'], project['goal'], project['coordinates']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Тестовые данные созданы! Добавлено {len(test_projects)} проектов")
    return True

if __name__ == "__main__":
    create_test_database()


