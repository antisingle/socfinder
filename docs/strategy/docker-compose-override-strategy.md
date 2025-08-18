# Docker Compose Override Strategy в проекте SocFinder

## 🎯 Обзор стратегии

Проект использует **Docker Compose Override YAML** подход для управления конфигурациями разных сред (локальная разработка и продакшен). Это позволяет:

- ✅ Избежать дублирования базовой конфигурации
- ✅ Безопасно управлять секретными данными
- ✅ Легко переключаться между средами
- ✅ Автоматизировать деплой

---

## 📁 Структура файлов

### 1. **docker-compose.yml** (базовый)
- **Назначение**: Общие настройки для всех сред
- **Git статус**: ✅ В репозитории
- **Содержимое**: Базовая структура сервисов, health checks, зависимости

### 2. **docker-compose.override.yml** (локальная разработка)
- **Назначение**: Переопределения для локальной разработки
- **Git статус**: ❌ НЕ в репозитории (.gitignore)
- **Содержимое**: Монтирование кода, локальные URL, volumes для разработки

### 3. **docker-compose.prod.yml** (продакшен)
- **Назначение**: Переопределения для продакшена
- **Git статус**: ❌ НЕ в репозитории (.gitignore)
- **Содержимое**: Продакшен URL, убранные volumes, продакшен настройки

---

## 🔄 Принцип работы

### Автоматическое переключение:
```bash
# Локально - автоматически подхватит override
docker-compose up          # → docker-compose.yml + docker-compose.override.yml

# На сервере - явно указываем продакшен
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Приоритет файлов:
1. `docker-compose.yml` (базовый)
2. `docker-compose.override.yml` (локальный, если есть)
3. Явно указанные файлы (например, `docker-compose.prod.yml`)

---

## 📋 Конкретные настройки в проекте

### **docker-compose.yml** (базовый):
```yaml
services:
  frontend:
    volumes: []  # Пустые volumes по умолчанию
    environment:
      - REACT_APP_API_URL=${REACT_APP_API_URL}
  
  backend:
    environment:
      - DATABASE_URL=${DATABASE_URL}
```

### **docker-compose.override.yml** (локально):
```yaml
services:
  frontend:
    volumes:
      - ./frontend/src:/app/src      # Монтирование кода для разработки
      - ./frontend/public:/app/public
    environment:
      - REACT_APP_API_URL=http://localhost:8001/api
  
  backend:
    volumes:
      - ./data:/app/data
      - ./backend:/app              # Монтирование кода для разработки
```

### **docker-compose.prod.yml** (на сервере):
```yaml
services:
  frontend:
    volumes: []  # Убрать volumes для продакшена
    environment:
      - REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api
  
  backend:
    volumes:
      - ./data:/app/data  # Только данные, не код
```

---

## 🚀 Команды для работы

### Локальная разработка:
```bash
# Автоматически подхватит docker-compose.override.yml
docker-compose up -d

# Или явно указать
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Продакшен деплой:
```bash
# На сервере - явно указать продакшен override
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Или через скрипт деплоя
./deploy.sh
```

### Проверка конфигурации:
```bash
# Посмотреть итоговую конфигурацию (локально)
docker-compose config

# Посмотреть итоговую конфигурацию (продакшен)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml config
```

---

## 🔐 Управление секретами

### Переменные окружения:
- **Локально**: `.env.local` (НЕ в git)
- **Продакшен**: `.env.production` (НЕ в git)
- **Шаблон**: `.env.example` (в git)

### Передача переменных:
```bash
# Локально
export $(cat .env.local | sed '/^#/d')
docker-compose up

# Продакшен
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up
```

---

## ✅ Преимущества стратегии

1. **Безопасность**: Секретные данные не попадают в git
2. **Гибкость**: Легко переключаться между средами
3. **Автоматизация**: Docker Compose сам выбирает нужную конфигурацию
4. **Масштабируемость**: Можно добавлять новые среды (staging, testing)
5. **DRY принцип**: Нет дублирования базовой конфигурации
6. **Совместимость**: Работает с CI/CD системами

---

## 🎯 Практическое применение

### Для разработчиков:
- Работают локально с `docker-compose up`
- Автоматически получают правильную конфигурацию
- Не нужно помнить сложные команды

### Для DevOps:
- Деплойят на сервер с явным указанием продакшен конфигурации
- Могут использовать скрипты автоматизации
- Легко откатывают изменения

### Для CI/CD:
- Могут использовать свои override файлы
- Гибкая настройка для разных окружений
- Автоматизация деплоя

---

## 📚 Связанные файлы

- `docker-compose.yml` - базовая конфигурация
- `docker-compose.override.yml` - локальные переопределения
- `docker-compose.prod.yml` - продакшен переопределения
- `.env.local` - локальные переменные окружения
- `.env.production` - продакшен переменные окружения
- `.env.example` - шаблон переменных
- `deploy.sh` - скрипт автоматизации деплоя
- `Makefile` - команды для быстрой работы

---

## 🚨 Важные моменты

1. **НЕ коммитить** `.env.*` файлы в git
2. **НЕ коммитить** override файлы в git
3. **Всегда использовать** `--env-file` на продакшене
4. **Проверять** итоговую конфигурацию через `docker-compose config`
5. **Тестировать** локально перед деплоем

---

## 🔄 Обновление стратегии

При изменении базовой конфигурации:
1. Обновить `docker-compose.yml`
2. Проверить совместимость с override файлами
3. Обновить `.env.example` если добавлены новые переменные
4. Протестировать локально и на продакшене
5. Зафиксировать изменения в git

---

*Этот документ является основным руководством по архитектуре Docker Compose в проекте SocFinder.*
