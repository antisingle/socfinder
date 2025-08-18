# PRD: SocFinder - Техническая реализация

## 1. Реализованная архитектура ✅

### Backend ✅ ГОТОВ
- **Framework**: FastAPI (Python 3.11+)
- **База данных**: PostgreSQL 15 (постоянное хранение)
- **ORM**: SQLAlchemy с BigInteger для больших сумм
- **Обработка данных**: openpyxl (замена pandas для стабильности)
- **Валидация**: Pydantic
- **Данные**: 166,849 проектов загружены в PostgreSQL

### Frontend ✅ ГОТОВ
- **Framework**: React 18 + TypeScript
- **Карты**: Leaflet + React-Leaflet
- **Таблица**: Встроенная HTML таблица с поиском и сортировкой
- **Сборка**: Create React App
- **Стили**: CSS с адаптивным дизайном
- **Переключение режимов**: Карта/Таблица одним кликом

### DevOps ✅ ГОТОВ
- **Контейнеризация**: Docker + Docker Compose
- **Постоянные данные**: PostgreSQL volumes
- **Одноразовая загрузка**: Автоматическая загрузка Excel при старте

## 2. Структура проекта

```
socfinder/                    ✅ РЕАЛИЗОВАНО
├── backend/                  ✅ Готов
│   ├── app/
│   │   ├── api/             ✅ projects.py, regions.py, stats.py
│   │   ├── core/            ✅ database.py с PostgreSQL
│   │   ├── models/          ✅ project.py с BigInteger
│   │   ├── services/        ✅ project_service.py
│   │   └── main.py          ✅ FastAPI приложение
│   ├── Dockerfile           ✅ с автозагрузкой данных
│   └── requirements.txt     ✅ с psycopg2-binary
├── frontend/                ✅ Готов
│   ├── src/
│   │   ├── components/      ✅ ProjectMap, встроенная таблица
│   │   ├── services/        ✅ api.ts для вызовов backend
│   │   ├── types/           ✅ Project interface
│   │   ├── App.tsx          ✅ с переключением режимов
│   │   └── App.css          ✅ стили для карты и таблицы
│   ├── public/              ✅ статические файлы
│   ├── Dockerfile           ✅ production build
│   └── package.json         ✅ React dependencies
├── data/                    ✅ Готов
│   ├── raw/                 ✅ data_114_pres_grants_v20250313.xlsx
│   ├── scripts/             ✅ load_to_postgres.py
│   └── regions_coordinates.json  ✅ координаты 90 регионов
├── docker-compose.yml       ✅ PostgreSQL + backend + frontend
└── README.md                ✅ инструкции по запуску
```

## 3. API Endpoints

### Основные эндпоинты
```
GET /api/v1/projects
- Параметры: region, year, direction, winner, limit, offset
- Возвращает: список проектов с пагинацией

GET /api/v1/projects/{id}
- Возвращает: детальную информацию о проекте

GET /api/v1/regions
- Возвращает: список регионов с координатами

GET /api/v1/stats/overview
- Возвращает: общую статистику по проектам

GET /api/v1/stats/by-region
- Возвращает: статистику по регионам

GET /api/v1/stats/by-year
- Возвращает: статистику по годам

GET /api/v1/search
- Параметры: query, filters
- Возвращает: результаты поиска по проектам

GET /api/v1/organizations
- Возвращает: список организаций с количеством проектов

GET /api/v1/projects/table
- Параметры: region, year, direction, winner, limit, offset, sort_by, sort_order
- Возвращает: проекты в формате для таблицы с сортировкой

GET /api/v1/projects/export
- Параметры: region, year, direction, winner, format (csv/excel)
- Возвращает: файл для скачивания с отфильтрованными данными
```

### Модель данных
```python
class Project(Base):
    id: int
    name: str
    contest: str
    year: int
    direction: str
    date_req: datetime
    region: str
    org: str
    inn: str
    ogrn: str
    winner: bool
    money_req_grant: int
    coordinates: dict  # {lat, lng} - координаты города
    description: str
    goal: str
    tasks: str
    address: str
    web_site: str
    link: str

class ProjectTableResponse(BaseModel):
    id: int
    name: str
    org: str
    region: str
    year: int
    direction: str
    money_req_grant: int
    winner: bool
    contest: str
```

## 4. Фактическая реализация ✅ ЗАВЕРШЕНО

### Этап 1: Backend с PostgreSQL ✅
**Реализовано**:
1. ✅ PostgreSQL вместо SQLite для производительности
2. ✅ Скрипт `load_to_postgres.py` с правильным парсингом Excel
3. ✅ 166,849 проектов загружены с корректными winner и money_req_grant
4. ✅ FastAPI с эндпоинтами: `/projects`, `/stats/overview`, `/regions`
5. ✅ SQLAlchemy с BigInteger для больших сумм грантов
6. ✅ Координаты 90 регионов для картографии

**Результат**: ✅ Стабильный API с полной базой данных PostgreSQL

### Этап 2: Frontend с таблицей ✅
**Реализовано**:
1. ✅ React + TypeScript с Create React App
2. ✅ Leaflet карта с маркерами проектов
3. ✅ Полнофункциональная таблица с поиском и сортировкой
4. ✅ Переключение режимов карта/таблица одним кликом
5. ✅ Экспорт данных в CSV
6. ✅ Адаптивный дизайн

**Результат**: ✅ Современный интерфейс с мощной таблицей

### Этап 3: Production готовность ✅
**Реализовано**:
1. ✅ Docker Compose с PostgreSQL, backend, frontend
2. ✅ Постоянные volumes для сохранения данных
3. ✅ Автоматическая загрузка данных при первом запуске
4. ✅ CORS настроен для production

**Результат**: ✅ Production-ready система с Docker

## 4.1. Технические решения
✅ **PostgreSQL** - выбран для производительности и надежности
✅ **Статичные координаты** - 90 регионов с готовыми координатами
✅ **Встроенная таблица** - вместо Ant Design для упрощения
✅ **Одноразовая загрузка** - данные загружаются автоматически при старте

## 5. Компоненты интерфейса

### Карта проектов
- **Технология**: Leaflet + React-Leaflet
- **Функции**: отображение точек, кластеризация, зум
- **Интеграция**: синхронизация с таблицей

### Таблица проектов
- **Технология**: React Table / Ant Design Table
- **Столбцы**: название, организация, регион, год, направление, сумма, статус
- **Функции**: сортировка, пагинация, фильтрация
- **Интеграция**: синхронизация с картой

### Фильтры
- **Регион**: выбор одного или нескольких регионов
- **Год**: диапазон лет (2017-2024)
- **Направление**: тематика проектов
- **Статус**: победители/все проекты
- **Сумма**: диапазон грантов

### Статистика
- **Общая сводка**: количество проектов, победителей, общая сумма
- **По регионам**: активность и успешность
- **По годам**: динамика развития

## 6. Варианты деплоя

### Вариант 1: Docker на VPS (Рекомендуемый)
**Преимущества**:
- Полный контроль над инфраструктурой
- Простота развертывания через docker-compose
- Возможность горизонтального масштабирования
- Низкая стоимость

**Конфигурация**:
```yaml
# docker-compose.prod.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: socfinder
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/socfinder
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    environment:
      VITE_API_URL: https://api.yourdomain.com

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
```

**Команды деплоя**:
```bash
# На сервере
git clone <repo>
cd socfinder
cp .env.example .env  # настроить переменные
docker-compose -f docker-compose.prod.yml up -d
```

**Используется при**: >10k пользователей в день

## 6. Локальная разработка

### Быстрый старт MVP (1 день)
```bash
# Клонирование и настройка
git clone <repo>
cd socfinder

# Запуск через Docker (включает загрузку данных)
docker-compose up -d

# Приложение доступно на http://localhost:3000
# API документация: http://localhost:8000/docs
```

### Команды для деплоя MVP
```bash
# На сервере
git clone <repo>
cd socfinder
docker-compose -f docker-compose.prod.yml up -d
```


## 7. Функциональность таблицы проектов

### Основные возможности
- **Отображение данных**: название, организация, регион, год, направление, сумма, статус
- **Сортировка**: по любому столбцу (возрастание/убывание)
- **Пагинация**: загрузка по 100-1000 проектов для производительности
- **Фильтрация**: применение тех же фильтров что и для карты
- **Поиск**: текстовый поиск по названию и организации

### Интеграция с картой
- **Синхронизация**: выделение в таблице = выделение на карте
- **Навигация**: клик по строке таблицы центрирует карту на проекте
- **Обновление**: фильтры применяются одновременно к карте и таблице

### Экспорт данных
- **Формат**: CSV файл с отфильтрованными данными
- **Содержимое**: все видимые в таблице проекты
- **Кодировка**: UTF-8 для корректного отображения кириллицы

## 8. Мониторинг и метрики

### Ключевые метрики
- Время отклика API (<200ms для простых запросов)
- Использование памяти БД
- Количество активных пользователей
- Ошибки 4xx/5xx
- Время загрузки карты
- Время загрузки таблицы

### Алерты
- API недоступен >1 минуты
- Использование диска >80%
- Время отклика >1 секунды
- Ошибки >5% от общего трафика

## 8. Безопасность

### Меры защиты
- Rate limiting для API (100 req/min на IP)
- CORS настройки
- SQL injection защита через ORM
- XSS защита через Content Security Policy
- HTTPS обязательно в продакшене
- Регулярные обновления зависимостей

### Переменные окружения
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/socfinder
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ENVIRONMENT=production
```

## 9. Бюджет и ресурсы

### Минимальные требования сервера
- **CPU**: 2 vCPU
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Bandwidth**: 1TB/месяц

### Примерная стоимость (месяц)
- VPS (DigitalOcean/Hetzner): $20-40
- Домен: $10-15/год
- SSL сертификат: бесплатно (Let's Encrypt)

**Итого**: $25-60/месяц

## 10. Текущий статус ✅ ГОТОВО К ИСПОЛЬЗОВАНИЮ

### Что работает прямо сейчас
- ✅ **Полная база данных**: 166,849 проектов в PostgreSQL
- ✅ **Корректная статистика**: 32,107 победителей, 71+ млрд рублей
- ✅ **Интерактивная карта**: все проекты на карте России
- ✅ **Мощная таблица**: поиск, сортировка, экспорт в CSV
- ✅ **Переключение режимов**: карта/таблица одним кликом
- ✅ **Docker развертывание**: `docker-compose up -d`

### Как запустить
```bash
# Клонировать репозиторий
git clone https://github.com/antisingle/socfinder
cd socfinder

# Запустить все сервисы
docker-compose up -d

# Открыть в браузере
open http://localhost:3000
```

### Доступ к сервисам
- **Frontend**: http://localhost:3000 (React приложение)
- **Backend API**: http://localhost:8001 (FastAPI документация: /docs)
- **PostgreSQL**: localhost:5432 (база данных)

### Следующие шаги развития
- Расширенные фильтры в таблице
- Улучшенная карта с кластеризацией
- Детальные страницы проектов
- Статистические дашборды
