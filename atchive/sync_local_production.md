# План синхронизации локальной и продакшен версий SocFinder

## Цель
Синхронизировать изменения между сервером и локальной версией, настроить автоматизацию деплоя, предотвратить потерю времени в будущем.

---

## 1. ЗАФИКСИРОВАТЬ ИЗМЕНЕНИЯ НА СЕРВЕРЕ

### 1.1 Создать коммит с текущим состоянием:
```bash
# На сервере
cd /root/socfinder

# Добавить все изменения
git add .

# Создать коммит с описанием исправлений
git commit -m "fix: production deployment fixes

- Fix CORS settings for external domain
- Fix React environment variables for production
- Remove Docker volumes from production
- Fix PostgreSQL credentials mismatch
- Hardcode API_URL for production
- Update .env with production values"
```

### 1.2 Отправить изменения в репозиторий:
```bash
# Отправить в основную ветку
git push origin main
```

---

## 2. ОБНОВИТЬ ЛОКАЛЬНУЮ ВЕРСИЮ

### 2.1 Получить изменения с сервера:
```bash
# Локально
cd /Users/reznikov/crsr/pers/socfinder

# Получить последние изменения
git pull origin main
```

### 2.2 Проверить что получилось:
```bash
# Проверить статус
git status

# Посмотреть последние коммиты
git log --oneline -5
```

---

## 3. НАСТРОИТЬ ЛОКАЛЬНУЮ КОНФИГУРАЦИЮ

### 3.1 Создать .env.local для разработки:
```bash
# Создать файл для локальной разработки
cp .env .env.local

# Отредактировать для локальной работы
nano .env.local
```

**Содержимое .env.local:**
```env
# Database (локально)
POSTGRES_DB=socfinder
POSTGRES_USER=socfinder_user
POSTGRES_PASSWORD=правильный_пароль  # Тот же что на сервере
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Frontend (локально)
REACT_APP_API_URL=http://localhost:8001/api

# Django
SECRET_KEY=TObXfEs1c1ojHVLI87rv7yQQqyRmOKfkm+38XCW2k/8=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# Redis
REDIS_URL=redis://redis:6379

# Server
PORT=8000
HOST=0.0.0.0

# Static files
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# Logging
LOG_LEVEL=INFO
```

### 3.2 Создать .env.production для продакшена:
```bash
# Переименовать текущий .env в продакшен версию
mv .env .env.production
```

### 3.3 Создать базовый docker-compose.yml для репозитория:
```bash
nano docker-compose.yml
```

**Базовый docker-compose.yml (для всех сред):**
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=socfinder
      - POSTGRES_USER=socfinder_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U socfinder_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=${REACT_APP_API_URL}
    depends_on:
      - backend
    # Базовые volumes (пустые для продакшена)
    volumes: []

volumes:
  postgres_data:
```

### 3.4 Создать docker-compose.override.yml для локальной разработки:
```bash
nano docker-compose.override.yml
```

**docker-compose.override.yml (локальные переопределения):**
```yaml
# Локальные переопределения для разработки
services:
  frontend:
    environment:
      - REACT_APP_API_URL=http://localhost:8001/api
    volumes:
      - ./frontend/src:/app/src      # Монтирование кода для разработки
      - ./frontend/public:/app/public

  backend:
    volumes:
      - ./data:/app/data
      - ./backend:/app              # Монтирование кода для разработки
```

### 3.5 Создать docker-compose.prod.yml для продакшена:
```bash
nano docker-compose.prod.yml
```

**docker-compose.prod.yml (продакшен переопределения):**
```yaml
# Продакшен переопределения
services:
  frontend:
    environment:
      - REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api
    volumes: []  # Убрать все volumes для продакшена

  backend:
    volumes:
      - ./data:/app/data  # Только данные, не код
```

### 3.6 Обновить .gitignore для исключения override файлов:
```bash
nano .gitignore
```

**Добавить в .gitignore:**
```gitignore
# Docker override files
docker-compose.override.yml
docker-compose.prod.yml

# Environment files
.env.local
.env.production
.env
```

### 3.7 Стратегия работы с override файлами:

**Принцип работы:**
- `docker-compose.yml` - базовая конфигурация для всех сред (в репозитории)
- `docker-compose.override.yml` - локальные переопределения (НЕ в репозитории)
- `docker-compose.prod.yml` - продакшен переопределения (НЕ в репозитории)

**Автоматическое переключение:**
- Локально: `docker-compose up` → автоматически подхватит override
- На сервере: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up`

**Преимущества:**
- ✅ Безопасность: секретные данные не попадают в git
- ✅ Гибкость: легко переключаться между средами
- ✅ Автоматизация: Docker Compose сам выбирает нужную конфигурацию
- ✅ Масштабируемость: можно добавлять новые среды (staging, testing)

### 3.8 Практические команды для работы:

**Локальная разработка:**
```bash
# Автоматически подхватит docker-compose.override.yml
docker-compose up -d

# Или явно указать
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

**Продакшен деплой:**
```bash
# На сервере - явно указать продакшен override
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Или через скрипт деплоя
./deploy.sh
```

**Проверка конфигурации:**
```bash
# Посмотреть итоговую конфигурацию (локально)
docker-compose config

# Посмотреть итоговую конфигурацию (продакшен)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml config
```

---

## 4. ИСПРАВИТЬ FRONTEND/SRC/APP.TSX

### 4.1 Вернуть переменные окружения вместо хардкода:
```bash
nano frontend/src/App.tsx
```

**Заменить:**
```typescript
// Было (хардкод для продакшена):
const API_URL = 'http://antisingle.fvds.ru:8001/api';

// На (переменные окружения):
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';
```

### 4.2 Исправить CORS в backend/app/main.py:
```bash
nano backend/app/main.py
```

**Обновить CORS для обеих сред:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Локальная разработка
        "http://localhost:3001", 
        "http://localhost:8080",
        "http://antisingle.fvds.ru:3000"   # Продакшен
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 5. СОЗДАТЬ DOCKER-COMPOSE.PROD.YML

### 5.1 Создать override файл для продакшена:
```bash
nano docker-compose.prod.yml
```

**Содержимое docker-compose.prod.yml:**
```yaml
# Переопределения для продакшена
services:
  frontend:
    environment:
      - REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api
    volumes: []  # Убрать volumes в продакшене

  backend:
    volumes:
      - ./data:/app/data  # Только данные, не код
```

---

## 6. СОЗДАТЬ СКРИПТЫ АВТОМАТИЗАЦИИ

### 6.1 Создать deploy.sh для сервера:
```bash
nano deploy.sh
chmod +x deploy.sh
```

**Содержимое deploy.sh:**
```bash
#!/bin/bash
# deploy.sh - скрипт деплоя на продакшен

echo "🚀 Деплой SocFinder на продакшен..."

# 1. Остановить старые контейнеры
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# 2. Получить последние изменения
git pull origin main

# 3. Пересобрать с нуля (избежать кэша)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# 4. Запустить с продакшен конфигурацией
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Проверить статус
echo "📊 Статус контейнеров:"
docker-compose ps

# 6. Проверить что API работает
echo "🔍 Проверка API..."
curl -s http://localhost:8001/health | grep -q "healthy" && echo "✅ API работает" || echo "❌ API не работает"

echo "🎯 Деплой завершен! Проверь: http://antisingle.fvds.ru:3000"
```

### 6.2 Создать Makefile:
```bash
nano Makefile
```

**Содержимое Makefile:**
```makefile
# Локальная разработка
dev:
	docker-compose down
	docker-compose up -d
	@echo "🏠 Локально: http://localhost:3000"

# Продакшен деплой
deploy:
	./deploy.sh

# Полная перезагрузка
rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Проверка здоровья
health:
	@echo "🔍 Проверка API..."
	@curl -s http://localhost:8001/health || echo "❌ API недоступен"
	@echo "🔍 Проверка фронтенда..."
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Фронтенд работает" || echo "❌ Фронтенд недоступен"

# Логи
logs:
	docker-compose logs --tail=50

# Очистка
clean:
	docker-compose down --rmi all --volumes
	docker system prune -f
```

---

## 7. ОБНОВИТЬ .GITIGNORE

### 7.1 Добавить файлы окружения:
```bash
nano .gitignore
```

**Добавить:**
```gitignore
# Environment files
.env.local
.env.production
.env

# Data files
data/dumps/*.*
data/raw/*.*
*.csv
*.sql

# Docker
.dockerignore
```

---

## 8. СОЗДАТЬ .ENV.EXAMPLE

### 8.1 Создать шаблон переменных:
```bash
nano .env.example
```

**Содержимое .env.example:**
```env
# Database
POSTGRES_DB=socfinder
POSTGRES_USER=socfinder_user
POSTGRES_PASSWORD=your_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Frontend (локально используй localhost, на сервере - полный домен)
REACT_APP_API_URL=http://localhost:8001/api

# Django
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# Redis
REDIS_URL=redis://redis:6379

# Server
PORT=8000
HOST=0.0.0.0

# Static files
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# Logging
LOG_LEVEL=INFO
```

---

## 9. ЗАФИКСИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ

### 9.1 Добавить новые файлы:
```bash
git add .env.example
git add docker-compose.prod.yml
git add deploy.sh
git add Makefile
git add .gitignore
```

### 9.2 Зафиксировать изменения в коде:
```bash
git add frontend/src/App.tsx
git add backend/app/main.py
git add docker-compose.yml
```

### 9.3 Создать коммит:
```bash
git commit -m "feat: add environment management and deployment automation

- Add .env.example template
- Add docker-compose.prod.yml for production overrides  
- Add deploy.sh script for automated deployment
- Add Makefile for common commands
- Revert App.tsx to use environment variables instead of hardcode
- Update CORS to support both local and production domains
- Update docker-compose.yml for local development
- Update .gitignore to exclude environment files"
```

### 9.4 Отправить в репозиторий:
```bash
git push origin main
```

---

## 10. ТЕСТИРОВАНИЕ

### 10.1 Тестировать локально:
```bash
# Запустить локально
make dev

# Проверить что работает
make health

# Открыть http://localhost:3000
```

### 10.2 Деплой на сервер:
```bash
# На сервере
cd /root/socfinder
git pull origin main
./deploy.sh
```

---

## 11. ЧЕК-ЛИСТ ВЫПОЛНЕНИЯ

### 11.1 На сервере:
- [ ] Создать коммит с текущими изменениями
- [ ] Отправить в git репозиторий
- [ ] Проверить что изменения зафиксированы

### 11.2 Локально:
- [ ] Получить изменения с сервера
- [ ] Создать .env.local для локальной разработки
- [ ] Создать .env.production для продакшена
- [ ] Обновить docker-compose.yml для локальной работы
- [ ] Исправить App.tsx (вернуть переменные окружения)
- [ ] Обновить CORS настройки
- [ ] Создать docker-compose.prod.yml
- [ ] Создать deploy.sh скрипт
- [ ] Создать Makefile
- [ ] Обновить .gitignore
- [ ] Создать .env.example
- [ ] Зафиксировать все изменения в git

### 11.3 Проверка:
- [ ] Локальная версия работает (make dev, make health)
- [ ] Продакшен версия работает (./deploy.sh)
- [ ] Все файлы зафиксированы в git

---

## 12. РЕЗУЛЬТАТ

После выполнения всех шагов у тебя будет:

✅ **Синхронизированные версии** между локальной и продакшен  
✅ **Автоматизированный деплой** через `./deploy.sh`  
✅ **Разделение конфигураций** через docker-compose.prod.yml  
✅ **Быстрые команды** через Makefile  
✅ **Документированные переменные** в .env.example  
✅ **Предотвращение потери времени** в будущем  

**Следующие деплои займут 2 минуты вместо 10 часов!** 🎯

---

## 13. КОМАНДЫ ДЛЯ БЫСТРОГО КОПИРОВАНИЯ

### 13.1 Создание файлов окружения:
```bash
# Создать .env.local
cp .env .env.local

# Создать .env.production  
mv .env .env.production

# Создать .env.example
nano .env.example
```

### 13.2 Создание скриптов:
```bash
# Создать deploy.sh
nano deploy.sh
chmod +x deploy.sh

# Создать Makefile
nano Makefile

# Создать docker-compose.prod.yml
nano docker-compose.prod.yml
```

### 13.3 Git команды:
```bash
# Добавить все файлы
git add .

# Создать коммит
git commit -m "feat: add environment management and deployment automation"

# Отправить в репозиторий
git push origin main
```

### 13.4 Тестирование:
```bash
# Локально
make dev
make health

# На сервере
./deploy.sh
```
