# 🚀 Быстрый запуск SocFinder Internal LLM

## ⚡ За 5 минут от 0 до работающего анализа

### 1️⃣ Проверить, что установлено
```bash
# Python 3.8+
python --version

# Docker
docker --version

# Ollama
ollama --version
```

### 2️⃣ Установить недостающее
```bash
# Если нет Ollama
brew install ollama  # macOS
# или скачать с ollama.ai

# Если нет Docker
# скачать с docker.com
```

### 3️⃣ Запустить Ollama
```bash
# В отдельном терминале
ollama serve

# Скачать модель (в новом терминале)
ollama pull llama3.1:8b
```

### 4️⃣ Запустить базу данных
```bash
docker-compose up -d
```

### 5️⃣ Активировать Python
```bash
source venv/bin/activate
cd data/scripts
```

### 6️⃣ Запустить тест
```bash
python test_2_examples.py
```

## ✅ Готово!

Если видите:
- "✅ Грант обработан"
- "✅ Результаты сохранены в БД"

**Система работает!** 🎉

## 🔄 Что дальше?

### Тест на 10 минут
```bash
python test_10_minutes_fixed.py
```

### Полный анализ (4 часа)
```bash
# Скорость: ~1.4 гранта/мин
# Результат: ~336 грантов
# Прогресс: 1.05% от всех победителей
```

## 🆘 Если что-то не работает

### LLM не отвечает
```bash
# Проверить Ollama
ollama list
ollama serve
```

### База недоступна
```bash
# Проверить Docker
docker ps
docker-compose up -d
```

### Python ошибки
```bash
# Активировать окружение
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Мониторинг

### Проверить прогресс
```bash
python -c "
from postgres_manager import PostgresManager
pg = PostgresManager()
print(pg.get_analysis_summary())
"
```

### Посмотреть результаты
```bash
# Последние 5 грантов
python -c "
from postgres_manager import PostgresManager
pg = PostgresManager()
conn = pg.get_connection()
cursor = conn.cursor()
cursor.execute('SELECT grant_id, COUNT(*) FROM problems GROUP BY grant_id ORDER BY COUNT(*) DESC LIMIT 5')
print(cursor.fetchall())
conn.close()
"
```

---

**Время чтения:** 2 минуты  
**Время запуска:** 5 минут  
**Результат:** Работающий анализ грантов! 🚀
