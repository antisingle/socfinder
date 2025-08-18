# Команды для работы с удаленным сервером

## 🖥️ Подключение к серверу

### Базовое подключение:
```bash
ssh root@antisingle.fvds.ru
```

### Подключение с указанием порта (если нужен):
```bash
ssh -p 22 root@antisingle.fvds.ru
```

### Подключение с передачей команды (выполнить и выйти):
```bash
ssh root@antisingle.fvds.ru "команда"
```

---

## 📁 Навигация по серверу

### Переход в папку проекта:
```bash
cd /root/socfinder
```

### Проверка текущего пути:
```bash
pwd
```

### Просмотр содержимого папки:
```bash
ls -la
```

### Просмотр только определенных файлов:
```bash
ls -la | grep -E "(docker-compose|\.env|Makefile)"
```

---

## 🐳 Docker Compose команды

### Проверка статуса контейнеров:
```bash
docker-compose ps
```

### Запуск с продакшен конфигурацией:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d
```

### Остановка контейнеров:
```bash
docker-compose down
```

### Пересборка и запуск:
```bash
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d
```

### Просмотр логов:
```bash
# Все сервисы
docker-compose logs

# Конкретный сервис
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Последние строки
docker-compose logs --tail=20
docker-compose logs backend --tail=10
```

---

## 🔧 Git команды

### Проверка статуса:
```bash
git status
```

### Получение обновлений:
```bash
git pull origin main
```

### Просмотр последних коммитов:
```bash
git log --oneline -5
```

### Проверка ветки:
```bash
git branch
```

---

## 📊 Мониторинг и диагностика

### Проверка переменных окружения в контейнере:
```bash
# Backend
docker-compose exec backend env | grep DATABASE_URL

# Frontend
docker-compose exec frontend env | grep REACT_APP
```

### Проверка API вручную:
```bash
# Статистика
curl -s "http://localhost:8001/api/v1/stats/overview"

# Проекты
curl -s "http://localhost:8001/api/v1/projects?limit=3"

# Health check
curl -s "http://localhost:8001/health"
```

### Проверка базы данных:
```bash
# Подключение к PostgreSQL
docker-compose exec postgres psql -U socfinder_user -d socfinder

# Список пользователей
docker-compose exec postgres psql -U postgres -c '\du'
```

---

## 🚀 Автоматизация

### Использование скрипта деплоя:
```bash
./deploy.sh
```

### Использование Makefile:
```bash
make deploy
make health
make logs
```

### Создание .env.production:
```bash
cat > .env.production << 'EOF'
# Продакшен переменные окружения
POSTGRES_DB=socfinder
POSTGRES_USER=socfinder_user
POSTGRES_PASSWORD=Ant1$1ngleoe
REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api
DATABASE_URL=postgresql://socfinder_user:Ant1$1ngleoe@postgres:5432/socfinder
EOF
```

---

## 🔍 Отладка проблем

### Проверка здоровья контейнеров:
```bash
docker-compose ps | grep -v "healthy\|Up"
```

### Проверка использования ресурсов:
```bash
# Память
free -h

# Диск
df -h

# Процессы
top
```

### Проверка сетевых соединений:
```bash
# Открытые порты
netstat -tlnp

# Docker сети
docker network ls
```

---

## 📝 Часто используемые команды

### Полная перезагрузка с нуля:
```bash
# Остановить все
docker-compose down

# Удалить volume базы данных (если нужно пересоздать)
docker volume rm socfinder_postgres_data

# Запустить заново
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d
```

### Проверка что все работает:
```bash
# 1. Статус контейнеров
docker-compose ps

# 2. API отвечает
curl -f http://localhost:8001/api/v1/stats/overview

# 3. Фронтенд загружается
curl -f http://localhost:3000

# 4. Нет критических ошибок в логах
docker-compose logs --tail=10 | grep -i error
```

### Обновление и перезапуск:
```bash
# Получить изменения
git pull origin main

# Перезапустить
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d
```

---

## ⚠️ Важные моменты

### Переменные окружения:
- **Всегда используй** `--env-file .env.production` при запуске
- **Проверяй** что переменные передались в контейнеры
- **Не забывай** что .env файлы НЕ в git

### Docker Compose:
- **Локально**: `docker-compose up` (автоматически подхватит override)
- **На сервере**: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up`
- **Всегда указывай** продакшен override на сервере

### Безопасность:
- **Не коммить** .env файлы
- **Не коммить** override файлы
- **Используй** SSH ключи для подключения

---

## 🎯 Быстрые команды для копирования

### Полная проверка системы:
```bash
cd /root/socfinder && \
docker-compose ps && \
curl -s "http://localhost:8001/api/v1/stats/overview" | head -1 && \
echo "✅ Система работает"
```

### Быстрый перезапуск:
```bash
cd /root/socfinder && \
docker-compose down && \
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d
```

### Проверка логов:
```bash
cd /root/socfinder && \
docker-compose logs --tail=20 | grep -i error
```

---

*Этот документ содержит все необходимые команды для работы с удаленным сервером SocFinder.*
