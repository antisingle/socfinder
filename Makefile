# Makefile для SocFinder - упрощение команд разработки

# Локальная разработка
dev:
	docker-compose down
	docker-compose up -d
	@echo "🏠 Локально: http://localhost:3000"

# Продакшен деплой
deploy:
	@echo "🚀 Деплой на продакшен..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✅ Продакшен запущен: http://antisingle.fvds.ru:3000"

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

# Проверка конфигурации
config:
	@echo "📋 Локальная конфигурация:"
	@docker-compose config

config-prod:
	@echo "📋 Продакшен конфигурация:"
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml config

# Помощь
help:
	@echo "🎯 SocFinder - команды разработки:"
	@echo "  make dev        - запуск локально"
	@echo "  make deploy     - деплой на продакшен"
	@echo "  make rebuild    - полная пересборка"
	@echo "  make health     - проверка здоровья"
	@echo "  make logs       - просмотр логов"
	@echo "  make clean      - полная очистка"
	@echo "  make config     - проверка локальной конфигурации"
	@echo "  make config-prod - проверка продакшен конфигурации"
