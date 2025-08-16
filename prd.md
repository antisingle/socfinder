# PRD: Интерактивная карта грантов - Техническая реализация

## 1. Техническая архитектура

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **База данных**: SQLite (для MVP), PostgreSQL (для продакшена)
- **ORM**: SQLAlchemy (без миграций в MVP)
- **Обработка данных**: Pandas
- **Валидация**: Pydantic

### Frontend
- **Framework**: React 18 + TypeScript
- **Карты**: Leaflet + React-Leaflet
- **Сборка**: Create React App (для MVP)
- **Стили**: CSS Modules

### DevOps
- **Контейнеризация**: Docker + Docker Compose
- **Веб-сервер**: Nginx (reverse proxy)

## 2. Структура проекта

```
socfinder/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── migrations/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── stores/
│   │   └── types/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── data/
│   ├── raw/
│   ├── processed/
│   └── scripts/
├── docker-compose.yml
├── nginx.conf
└── README.md
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
    # ... остальные поля
```

## 4. Последовательность разработки (1 день - MVP)

### Утро (4 часа): Подготовка данных и Backend
**Задачи**:
1. Простой скрипт загрузки Excel в SQLite (вместо PostgreSQL)
2. Минимальная очистка данных
3. Статичная база координат регионов (JSON файл)
4. FastAPI с базовыми эндпоинтами: `/projects`, `/regions`, `/stats`
5. Без тестов, без миграций - только рабочий API

**Результат**: Работающий API с данными

### День (4 часа): Frontend MVP
**Задачи**:
1. Create React App с TypeScript (без Vite для простоты)
2. Простая Leaflet карта с точками
3. Базовые фильтры: регион, год (без UI библиотек)
4. Axios для API запросов
5. Минимальная верстка

**Результат**: Работающий фронтенд с картой

### Вечер (4 часа): Интеграция и деплой
**Задачи**:
1. Связать фронт с бэком
2. Простая кластеризация точек
3. Базовые карточки проектов
4. Docker Compose файл
5. Деплой на VPS

**Результат**: Работающий MVP в продакшене

## 4.1. Упрощения для MVP
- SQLite вместо PostgreSQL (без настройки сервера БД)
- Статичные координаты регионов (без геокодирования)
- Без Redis кэширования
- Минимальный UI (без Ant Design)
- Без тестов
- Фиксированный набор фильтров

## 5. Варианты деплоя

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


## 7. Мониторинг и метрики

### Ключевые метрики
- Время отклика API (<200ms для простых запросов)
- Использование памяти БД
- Количество активных пользователей
- Ошибки 4xx/5xx
- Время загрузки карты

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
