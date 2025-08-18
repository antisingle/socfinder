# Анализ ошибок развертывания SocFinder

## Краткая сводка
**Время затрачено:** ~10 часов  
**Основная проблема:** Развертывание React/FastAPI приложения с Docker Compose на новом сервере  
**Результат:** Успешно развернуто и работает  

---

## 1. ОШИБКИ КОНФИГУРАЦИИ DOCKER COMPOSE

### 1.1 Неправильные учетные данные PostgreSQL
**Ошибка:**
```yaml
# В docker-compose.yml
POSTGRES_USER=socfinder          # ❌ Неправильно
POSTGRES_PASSWORD=другой_пароль  # ❌ Неправильно

# В .env файле  
POSTGRES_USER=socfinder_user     # ✅ Правильно
POSTGRES_PASSWORD=правильный_пароль   # ✅ Правильно - нужно это учесть при создании учётки локально и удалённо
```

**Проявление:**
- `role "socfinder_user" does not exist`
- Backend не мог подключиться к БД

**Решение:**
- Исправить docker-compose.yml чтобы соответствовал .env
- Удалить Docker volume: `docker volume rm socfinder_postgres_data`
- Пересоздать контейнеры

**Урок:** Всегда проверяй соответствие переменных окружения между файлами!

---

## 2. ПРОБЛЕМЫ С ПЕРЕМЕННЫМИ ОКРУЖЕНИЯ REACT

### 2.1 Отсутствующая переменная REACT_APP_API_URL
**Ошибка:**
```bash
grep REACT_APP .env
# Пустой результат - переменная отсутствовала
```

**Проявление:**
- `API_URL: ` (пустая строка в консоли браузера)
- Фронтенд делал запросы к себе (порт 3000) вместо бэкенда (порт 8001)

**Решение:**
```bash
echo "REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api" >> .env
```

### 2.2 Неправильный URL в переменной окружения
**Ошибка:**
```yaml
- REACT_APP_API_URL=http://antisingle.fvds.ru::8001/api  # ❌ Двойное двоеточие
```

**Решение:**
```yaml
- REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api   # ✅ Одно двоеточие
```

### 2.3 localhost vs внешний домен
**Ошибка:**
```yaml
- REACT_APP_API_URL=http://localhost:8001/api  # ❌ Не работает с внешним доменом
```

**Проявление:**
- Фронтенд работает на antisingle.fvds.ru:3000
- localhost ссылается на локальную машину пользователя, не на сервер

**Решение:**
```yaml
- REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api  # ✅ Полный URL сервера
```

**Урок:** В продакшене всегда используй полные URL, не localhost!

---

## 3. ПРОБЛЕМЫ С DOCKER VOLUMES

### 3.1 Volumes перезаписывают собранный образ
**Ошибка:**
```yaml
frontend:
  volumes:
    - ./frontend/src:/app/src      # ❌ Монтирует локальные файлы
    - ./frontend/public:/app/public # ❌ Поверх собранного образа
```

**Проявление:**
- Переменные окружения в контейнере правильные
- Но React не читает их, потому что использует локальные файлы
- `API_URL: ` остается пустым

**Решение:**
```yaml
frontend:
  volumes: []  # ✅ Убрать volumes или закомментировать
```

**Урок:** В продакшене не используй volumes с исходным кодом - они перезаписывают собранный образ!

---

## 4. ПРОБЛЕМЫ С REACT BUILD ARGS

### 4.1 Dockerfile не читает переменные окружения при сборке
**Ошибка:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
# Нет ARG и ENV для REACT_APP_API_URL
RUN npm run build  # ❌ React не видит переменные
```

**Проявление:**
- Переменные окружения есть в docker-compose.yml
- Но React читает их только при сборке, не во время выполнения
- `process.env.REACT_APP_API_URL` возвращает undefined

**Решение:**
```dockerfile
FROM node:18-alpine
ARG REACT_APP_API_URL           # ✅ Добавить ARG
ENV REACT_APP_API_URL=$REACT_APP_API_URL  # ✅ Добавить ENV
WORKDIR /app
RUN npm run build
```

### 4.2 --build-arg не работает с docker-compose
**Ошибка:**
```bash
docker-compose build --build-arg REACT_APP_API_URL=... frontend
# Не работает с docker-compose
```

**Решение (временное):**
```typescript
// Хардкод в коде
const API_URL = 'http://antisingle.fvds.ru:8001/api';
```

**Урок:** React переменные окружения - это сложно в Docker! Проще хардкодить в продакшене.

---

## 5. СИНТАКСИЧЕСКИЕ ОШИБКИ

### 5.1 Неправильный символ комментария
**Ошибка:**
```typescript
# const API_URL = process.env.REACT_APP_API_URL || '';  // ❌ # не комментарий в TS
```

**Проявление:**
```
Syntax error: Invalid character (28:undefined)
```

**Решение:**
```typescript
// const API_URL = process.env.REACT_APP_API_URL || '';  // ✅ Правильный комментарий
```

**Урок:** В TypeScript используй `//` для комментариев, не `#`!

---

## 6. ПРОБЛЕМЫ С CORS

### 6.1 Отсутствующий домен в allow_origins
**Ошибка:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ❌ Только localhost
)
```

**Проявление:**
```
Access to XMLHttpRequest has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header
```

**Решение:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://antisingle.fvds.ru:3000"  # ✅ Добавить внешний домен
    ],
)
```

**Урок:** В CORS настройках добавляй все домены, с которых будут запросы!

---

## 7. ПРОБЛЕМЫ С КЭШИРОВАНИЕМ

### 7.1 Браузер кэширует старый JavaScript
**Ошибка:**
```
Status Code: 304 Not Modified
if-none-match: "старый_etag"
```

**Проявление:**
- Фронтенд пересобран с новыми переменными
- Но браузер использует старый кэшированный код
- Запросы все еще идут к старым URL

**Решение:**
- `Ctrl + F5` (жесткая перезагрузка)
- `Cmd + Shift + R` (Mac)
- Или очистить кэш в DevTools

### 7.2 Docker кэширует старые слои
**Проблема:**
- `docker-compose build` использует кэшированные слои
- Новые переменные окружения не применяются

**Решение:**
```bash
docker-compose build --no-cache frontend  # ✅ Принудительная пересборка
```

**Урок:** При проблемах с переменными окружения всегда используй --no-cache!

---

## 8. ПРОБЛЕМЫ С БАЗОЙ ДАННЫХ

### 8.1 Неправильные пути импорта в коде
**Ошибка:**
```python
from app.database import engine  # ❌ Неправильный путь
```

**Проявление:**
```
ModuleNotFoundError: No module named 'app.database'
```

**Решение:**
```python
from app.core.database import engine  # ✅ Правильный путь
```

### 8.2 Неправильный разделитель в CSV
**Ошибка:**
```sql
\copy projects FROM 'file.csv' WITH CSV HEADER;  -- ❌ Разделитель по умолчанию ','
```

**Проявление:**
```
ERROR: invalid input syntax for type integer: "А жизнь продолжается!"
```

**Решение:**
```sql
\copy projects(name,contest,year,...) FROM 'file.csv' WITH CSV HEADER DELIMITER ';';  -- ✅ Правильный разделитель
```

---

## 9. ЭФФЕКТИВНЫЕ МЕТОДЫ ОТЛАДКИ

### 9.1 Проверка переменных окружения
```bash
# В контейнере
docker-compose exec frontend env | grep REACT_APP

# В консоли браузера
console.log('API_URL:', API_URL);
```

### 9.2 Проверка Network вкладки в DevTools
- Request URL - куда идут запросы
- Status Code - успешность запросов  
- Headers - CORS заголовки

### 9.3 Проверка Docker логов
```bash
docker-compose logs frontend
docker-compose logs backend
```

### 9.4 Проверка API вручную
```bash
curl http://localhost:8001/api/v1/stats/overview
```

---

## 10. РЕКОМЕНДАЦИИ ДЛЯ БУДУЩЕГО

### 10.1 Чек-лист для развертывания React + FastAPI

**Переменные окружения:**
- [ ] REACT_APP_* переменные есть в .env
- [ ] URL используют полные домены, не localhost
- [ ] Нет опечаток в URL (двойные двоеточия, etc.)

**Docker:**
- [ ] Нет volumes с исходным кодом в продакшене
- [ ] Dockerfile имеет ARG/ENV для React переменных
- [ ] Используй --no-cache при проблемах с переменными

**CORS:**
- [ ] Все домены добавлены в allow_origins
- [ ] Включены localhost для разработки и внешние домены для продакшена

**База данных:**
- [ ] Учетные данные совпадают между .env и docker-compose.yml
- [ ] Правильные пути импорта в коде
- [ ] Правильные разделители в CSV файлах

### 10.2 Порядок отладки

1. **Проверить переменные окружения** в контейнере
2. **Проверить консоль браузера** на ошибки JavaScript
3. **Проверить Network вкладку** на правильность запросов
4. **Проверить Docker логи** на ошибки сервера
5. **Тестировать API вручную** с curl
6. **Использовать --no-cache** при проблемах с кэшем

### 10.3 Альтернативные подходы

**Для переменных окружения React:**
- Хардкод в коде для продакшена (проще)
- Использование .env файлов вместо Docker переменных
- Передача конфигурации через API endpoint

**Для CORS:**
- Использование прокси в nginx
- Wildcard origins для разработки (небезопасно в продакшене)

---

## ИТОГИ

**Основные причины потери времени:**
1. **Переменные окружения React** - самая сложная часть (4+ часа)
2. **Docker volumes** перезаписывали собранный образ (2+ часа)
3. **CORS настройки** для внешнего домена (1+ час)
4. **Несоответствие учетных данных БД** (1+ час)
5. **Кэширование браузера** и Docker (1+ час)

**Самые эффективные методы отладки:**
1. Проверка консоли браузера
2. Network вкладка в DevTools  
3. Проверка переменных в контейнере
4. Тестирование API с curl
5. Docker логи

**Ключевые уроки:**
- React переменные окружения работают только при сборке
- В продакшене не используй volumes с исходным кодом
- Всегда проверяй соответствие переменных между файлами
- CORS должен включать все домены
- Используй --no-cache при проблемах с переменными
- Полные URL вместо localhost в продакшене

---

## 11. СИНХРОНИЗАЦИЯ ЛОКАЛЬНОЙ И ПРОДАКШЕН ВЕРСИЙ

### 11.1 Текущие различия между версиями

**Локальная версия:**
```env
POSTGRES_PASSWORD=старый_пароль
REACT_APP_API_URL=http://localhost:8001/api
```

**Продакшен версия:**
```env  
POSTGRES_PASSWORD=правильный_пароль
REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api
```

**Проблема:** Разные конфигурации приводят к ошибкам при переносе между средами.

### 11.2 Стратегии синхронизации

#### Вариант 1: Отдельные .env файлы
```bash
.env.local          # Для локальной разработки
.env.production     # Для продакшена
.env.example        # Шаблон с описанием переменных
```

**Docker-compose:**
```yaml
# Локально
env_file: .env.local

# На сервере  
env_file: .env.production
```

#### Вариант 2: Условные переменные
```env
# Общий .env файл
NODE_ENV=development  # или production

# Локально
POSTGRES_PASSWORD=локальный_пароль
API_HOST=localhost

# На сервере переопределить только нужные:
POSTGRES_PASSWORD=продакшен_пароль  
API_HOST=antisingle.fvds.ru
```

#### Вариант 3: Docker Compose override
```yaml
# docker-compose.yml (базовая конфигурация)
services:
  frontend:
    environment:
      - REACT_APP_API_URL=http://localhost:8001/api

# docker-compose.prod.yml (переопределения для продакшена)
services:
  frontend:
    environment:
      - REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api
```

**Запуск:**
```bash
# Локально
docker-compose up

# На сервере
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

---

## 12. РЕКОМЕНДАЦИИ ДЛЯ БЫСТРОГО ТЕСТИРОВАНИЯ

### 12.1 Чек-лист перед коммитом

**Локальное тестирование:**
- [ ] `docker-compose down && docker-compose up -d` - полный перезапуск
- [ ] Открыть http://localhost:3000 - фронтенд работает
- [ ] Проверить консоль браузера - нет ошибок
- [ ] `curl http://localhost:8001/api/v1/stats/overview` - API отвечает
- [ ] Проверить что данные загружаются в UI

**Подготовка к деплою:**
- [ ] Обновить .env.production с правильными URL
- [ ] Проверить CORS настройки в backend/app/main.py
- [ ] Убедиться что volumes закомментированы в docker-compose.yml
- [ ] Зафиксировать изменения в git

### 12.2 Быстрый деплой на сервер

**Скрипт деплоя:**
```bash
#!/bin/bash
# deploy.sh

echo "🚀 Деплой SocFinder..."

# 1. Остановить старые контейнеры
docker-compose down

# 2. Получить последние изменения
git pull origin main

# 3. Пересобрать с нуля (избежать кэша)
docker-compose build --no-cache

# 4. Запустить
docker-compose up -d

# 5. Проверить статус
echo "📊 Статус контейнеров:"
docker-compose ps

# 6. Проверить что API работает
echo "🔍 Проверка API..."
curl -s http://localhost:8001/health | grep -q "healthy" && echo "✅ API работает" || echo "❌ API не работает"

# 7. Показать логи если есть проблемы
echo "📋 Логи (последние 20 строк):"
docker-compose logs --tail=20

echo "🎯 Деплой завершен! Проверь: http://antisingle.fvds.ru:3000"
```

### 12.3 Автоматизация тестирования

**Makefile для быстрых команд:**
```makefile
# Локальная разработка
dev:
	docker-compose down
	docker-compose up -d
	@echo "🏠 Локально: http://localhost:3000"

# Полная перезагрузка с пересборкой
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

### 12.4 Мониторинг после деплоя

**Быстрая проверка (30 секунд):**
```bash
# 1. Статус контейнеров
docker-compose ps | grep -v "healthy\|Up"

# 2. API отвечает
curl -f http://antisingle.fvds.ru:8001/api/v1/stats/overview

# 3. Фронтенд загружается
curl -f http://antisingle.fvds.ru:3000

# 4. Нет критических ошибок в логах
docker-compose logs --tail=10 | grep -i error
```

**Детальная проверка (2 минуты):**
1. Открыть http://antisingle.fvds.ru:3000
2. Проверить что статистика загрузилась (не нули)
3. Проверить что таблица проектов заполнена
4. Открыть DevTools → Console - нет ошибок
5. Открыть Network → обновить - запросы идут к :8001
6. Проверить что CORS работает (нет CORS ошибок)

---

## 13. ПРЕДОТВРАЩЕНИЕ ПОТЕРИ ВРЕМЕНИ

### 13.1 Документирование изменений

**Ведение CHANGELOG.md:**
```markdown
# Changelog

## [1.1.0] - 2025-08-17
### Исправлено
- CORS настройки для внешнего домена
- React переменные окружения в продакшене
- Docker volumes убраны из продакшена

### Изменено  
- POSTGRES_PASSWORD обновлен на сервере
- API_URL использует полный домен вместо localhost

### Конфигурация
- .env.local: API_URL=http://localhost:8001/api
- .env.production: API_URL=http://antisingle.fvds.ru:8001/api
```

### 13.2 Стандартизация процессов

**Правило: "Если работает локально, должно работать на сервере"**

**Обязательные проверки:**
1. Нет hardcode localhost в коде
2. Все переменные окружения документированы
3. CORS включает все нужные домены
4. Docker volumes не перезаписывают prod код
5. База данных имеет одинаковую схему

**Правило: "Один источник правды для конфигурации"**
- Все переменные описаны в .env.example
- Различия между средами минимальны
- Секреты (пароли) не коммитятся в git

### 13.3 Быстрая диагностика проблем

**Алгоритм поиска проблем (5 минут):**

1. **Контейнеры запущены?**
   ```bash
   docker-compose ps
   ```

2. **API отвечает?**
   ```bash
   curl http://antisingle.fvds.ru:8001/health
   ```

3. **Фронтенд показывает ошибки?**
   - Открыть DevTools → Console
   - Искать красные ошибки

4. **Переменные окружения правильные?**
   ```bash
   docker-compose exec frontend env | grep REACT_APP
   ```

5. **CORS работает?**
   - Network вкладка → искать CORS ошибки
   - Проверить allow_origins в backend/app/main.py

6. **База данных доступна?**
   ```bash
   docker-compose exec backend python -c "from app.core.database import engine; print('DB OK')"
   ```

**Если проблема не найдена за 5 минут:**
- Проверить логи: `docker-compose logs`
- Сравнить с последней рабочей версией
- Откатиться к предыдущему коммиту

---

## 14. ИТОГОВЫЕ РЕКОМЕНДАЦИИ

### 14.1 Золотые правила

1. **"Паритет разработки и продакшена"** - максимально похожие конфигурации
2. **"Fail fast"** - автоматические проверки перед деплоем  
3. **"Одна команда деплоя"** - весь процесс в одном скрипте
4. **"Мониторинг после деплоя"** - обязательная проверка работоспособности
5. **"Документируй различия"** - все изменения между средами записаны

### 14.2 Экономия времени

**Вместо 10 часов отладки:**
- 30 минут на настройку автоматизации
- 5 минут на каждый деплой
- 2 минуты на проверку работоспособности

**Инвестиция времени:**
- Создать .env.example с описанием всех переменных
- Написать deploy.sh скрипт
- Настроить Makefile с частыми командами
- Документировать различия между средами

**Результат:**
- Деплой за 5 минут вместо часов отладки
- Уверенность что все работает
- Легкое переключение между средами
- Новые разработчики могут быстро развернуть проект
