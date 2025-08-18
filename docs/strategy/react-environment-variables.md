# React переменные окружения в Docker: важные нюансы

## 🚨 Ключевая проблема

**React переменные окружения (`REACT_APP_*`) работают только при СБОРКЕ, а не при ЗАПУСКЕ контейнера!**

## 🔍 Что происходило

### Неправильный подход (который не работал):
```bash
# 1. Сборка без build args
docker-compose build --no-cache

# 2. Запуск с env файлом
docker-compose --env-file .env.production up -d
```

**Результат:** фронтенд собран с `REACT_APP_API_URL=http://localhost:8001/api` (из локального .env), но запущен на сервере.

### Правильный подход (который работает):
```bash
# 1. Сборка С build args
docker-compose build --no-cache --build-arg REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api

# 2. Запуск с env файлом
docker-compose --env-file .env.production up -d
```

**Результат:** фронтенд собран с правильным URL и работает корректно.

## 🏗️ Как работают React переменные

### При сборке (build time):
- React считывает `REACT_APP_*` переменные
- Встраивает их в JavaScript код
- Создает production build

### При запуске (runtime):
- Переменные уже "зашиты" в код
- Изменить их нельзя без пересборки

## 🔧 Решение в deploy.sh

```bash
# ВАЖНО: --build-arg нужен для React переменных
docker-compose build --no-cache --build-arg REACT_APP_API_URL=http://antisingle.fvds.ru:8001/api

# --env-file только для runtime переменных (DATABASE_URL, POSTGRES_PASSWORD)
docker-compose --env-file .env.production up -d
```

## 📋 Чек-лист для деплоя

### ✅ Обязательно:
- [ ] `--build-arg REACT_APP_API_URL=...` при сборке фронтенда
- [ ] `--env-file .env.production` при запуске
- [ ] `--no-cache` для избежания кэширования

### ❌ Не делать:
- [ ] Сборка без build args
- [ ] Запуск без env файла
- [ ] Использование кэша при проблемах с переменными

## 🎯 Вывод

**Всегда используй `--build-arg` для React переменных в Docker!**

Без этого фронтенд будет работать с неправильными URL, даже если переменные окружения в контейнере правильные.
