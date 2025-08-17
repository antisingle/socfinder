#!/bin/bash
# Скрипт для создания дампа базы данных PostgreSQL

echo "🔍 Проверяем статус контейнеров..."
docker-compose -f docker-compose.minimal.yml ps

echo "📦 Создаем дамп базы данных..."
mkdir -p data/dumps

# Создаем дамп базы данных
docker-compose -f docker-compose.minimal.yml exec -T postgres pg_dump -U socfinder -Fc --clean --if-exists socfinder > data/dumps/socfinder_dump.sql

# Проверяем размер дампа
DUMP_SIZE=$(du -h data/dumps/socfinder_dump.sql | cut -f1)
echo "✅ Дамп успешно создан: data/dumps/socfinder_dump.sql"
echo "📊 Размер дампа: $DUMP_SIZE"

# Обновляем Dockerfile для использования дампа
echo "🔧 Обновляем Dockerfile для использования дампа..."
cat > backend/Dockerfile.dump << EOF
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Запускаем восстановление из дампа и FastAPI
CMD ["sh", "-c", "python data/scripts/restore_from_dump.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
EOF

echo "✅ Создан файл backend/Dockerfile.dump"
echo ""
echo "🚀 Для использования дампа вместо Excel файла:"
echo "1. Переименуйте backend/Dockerfile.dump в backend/Dockerfile"
echo "2. Пересоберите образ: docker-compose -f docker-compose.minimal.yml build backend"
echo "3. Запустите контейнеры: docker-compose -f docker-compose.minimal.yml up -d"
echo ""
echo "✅ Готово!"
