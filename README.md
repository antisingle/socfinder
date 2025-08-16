# 🗺️ SocFinder - Карта грантовых проектов

Интерактивная карта для отображения и анализа грантовых проектов президентских грантов.

## 🚀 Быстрый старт

### Локальная разработка
```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f backend
```

### Доступные сервисы
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Test Page**: http://localhost:8080/test.html

## 📊 Данные

- **Всего проектов**: 166,849
- **Победителей**: 32,107
- **Общая сумма**: 71,151,289,518 ₽
- **Регионов**: 90
- **Организаций**: 47,583

## 🔧 API Endpoints

### Статистика
```
GET /api/v1/stats/overview
```

### Проекты
```
GET /api/v1/projects?limit=5000&region=Москва&year=2023
```

### Регионы
```
GET /api/v1/regions
```

## 🛠️ Технологии

- **Backend**: FastAPI + SQLite + SQLAlchemy
- **Frontend**: React + TypeScript + Leaflet
- **Карты**: React-Leaflet
- **Деплой**: Docker + Docker Compose

## 📁 Структура проекта

```
socfinder/
├── backend/          # FastAPI приложение
├── frontend/         # React приложение
├── data/            # Данные и скрипты
├── docker-compose.yml
└── README.md
```

## 🚀 Деплой на сервер

1. Скопировать проект на VPS
2. Установить Docker и Docker Compose
3. Запустить: `docker-compose up -d`
4. Настроить домен и SSL (опционально)

## 🎯 Возможности

- ✅ Интерактивная карта с 166K проектов
- ✅ Фильтрация по региону, году, направлению
- ✅ Статистика по проектам и регионам
- ✅ Адаптивный дизайн
- ✅ Быстрая загрузка данных

## 📝 Лицензия

MIT License


