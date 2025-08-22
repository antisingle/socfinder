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

# Пакетная обработка грантов
process-1h:
	@echo "🚀 Запуск обработки на 1 час (60 минут)..."
	@source ./venv/bin/activate && cd data/scripts && python time_batch_processing.py 60

process-6h:
	@echo "🚀 Запуск обработки на 6 часов (360 минут)..."
	@source ./venv/bin/activate && cd data/scripts && python time_batch_processing.py 360

process-24h:
	@echo "🚀 Запуск обработки на 24 часа (1440 минут)..."
	@source ./venv/bin/activate && cd data/scripts && python time_batch_processing.py 1440

process-custom:
	@echo "🚀 Запуск обработки на заданное время..."
	@echo "Использование: make process-custom MINUTES=<количество_минут>"
	@echo "Пример: make process-custom MINUTES=120"
	@if [ -z "$(MINUTES)" ]; then echo "❌ Укажите MINUTES=<количество_минут>"; exit 1; fi
	@source ./venv/bin/activate && cd data/scripts && python time_batch_processing.py $(MINUTES)

# Мониторинг обработки
monitor-processing:
	@echo "📊 Мониторинг процесса обработки..."
	@cd data/scripts && tail -f time_batch_processing.log

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
	@echo ""
	@echo "🔍 Пакетная обработка грантов:"
	@echo "  make process-1h        - обработка на 1 час"
	@echo "  make process-6h        - обработка на 6 часов"
	@echo "  make process-24h       - обработка на 24 часа"
	@echo "  make process-custom MINUTES=120 - обработка на 120 минут"
	@echo "  make monitor-processing - мониторинг процесса"
