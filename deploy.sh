#!/bin/bash
# deploy.sh - скрипт деплоя SocFinder на продакшен

echo "🚀 Деплой SocFinder на продакшен..."

# 1. Остановить старые контейнеры
echo "📴 Останавливаю старые контейнеры..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# 2. Получить последние изменения (если есть git)
if [ -d ".git" ]; then
    echo "📥 Получаю последние изменения из git..."
    git pull origin main
fi

# 3. Пересобрать с нуля (избежать кэша)
echo "🔨 Пересобираю контейнеры..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# 4. Запустить с продакшен конфигурацией
echo "🚀 Запускаю продакшен..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Проверить статус
echo "📊 Статус контейнеров:"
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# 6. Проверить что API работает
echo "🔍 Проверка API..."
sleep 10  # Дать время на запуск
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "✅ API работает"
else
    echo "❌ API не работает"
    echo "📋 Логи backend:"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs backend --tail=20
fi

# 7. Проверить фронтенд
echo "🔍 Проверка фронтенда..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Фронтенд работает"
else
    echo "❌ Фронтенд не работает"
    echo "📋 Логи frontend:"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs frontend --tail=20
fi

echo "🎯 Деплой завершен! Проверь: http://antisingle.fvds.ru:3000"
echo "📋 Для просмотра логов: make logs"
echo "📋 Для проверки здоровья: make health"
