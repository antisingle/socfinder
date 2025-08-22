# 🧪 Тестирование Backend API

## 📋 Описание

Тесты для API endpoints проблем и решений, включающие:
- Unit тесты для каждого endpoint
- Интеграционные тесты
- Тесты производительности
- Тесты обработки ошибок

## 🚀 Запуск тестов

### Установка зависимостей
```bash
cd backend
pip install -r requirements-test.txt
```

### Запуск всех тестов
```bash
# Из корня проекта
make test-backend

# Или напрямую
cd backend
python -m pytest tests/ -v
```

### Запуск конкретных тестов
```bash
# Только тесты проблем
python -m pytest tests/test_problems_solutions_api.py::TestProblemsAPI -v

# Только тесты решений
python -m pytest tests/test_problems_solutions_api.py::TestSolutionsAPI -v

# Только интеграционные тесты
python -m pytest tests/test_problems_solutions_api.py::TestIntegration -v
```

## 📊 Структура тестов

### TestProblemsAPI
- `test_get_problems()` - получение списка проблем
- `test_get_problems_count()` - подсчет проблем
- `test_get_problems_by_grant()` - проблемы по grant_id
- `test_search_problems()` - поиск проблем

### TestSolutionsAPI
- `test_get_solutions()` - получение списка решений
- `test_get_solutions_by_grants()` - решения по списку grant_ids
- `test_get_solutions_by_grant()` - решения по grant_id
- `test_search_solutions()` - поиск решений

### TestIntegration
- `test_problem_solution_relationship()` - связь проблем и решений
- `test_empty_grant_ids_request()` - обработка пустых запросов

## 🔧 Настройка тестовой базы

Тесты используют SQLite базу данных для изоляции:
- Автоматическое создание/удаление таблиц
- Тестовые данные создаются перед каждым тестом
- Очистка после каждого теста

## 📈 Метрики тестирования

- **Покрытие:** Все основные endpoints
- **Время выполнения:** < 5 секунд для полного набора
- **Изоляция:** Каждый тест независим
- **Данные:** Реалистичные тестовые данные

## 🚨 Известные проблемы

- Тесты требуют SQLAlchemy модели
- Некоторые тесты могут падать при изменении схемы БД
- Производительность зависит от размера тестовых данных

## 💡 Рекомендации

1. **Запускайте тесты перед деплоем**
2. **Добавляйте тесты для новых endpoints**
3. **Обновляйте тесты при изменении API**
4. **Используйте CI/CD для автоматического тестирования**
