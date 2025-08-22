#!/bin/bash

echo "🚀 Быстрый экспорт данных SocFinder в Excel"
echo "=============================================="

# Проверяем, запущен ли Docker
if ! docker ps | grep -q "postgres"; then
    echo "❌ Контейнер PostgreSQL не запущен!"
    echo "Запустите: docker-compose up -d"
    exit 1
fi

echo "✅ PostgreSQL контейнер запущен"

# Переходим в директорию скриптов
cd "$(dirname "$0")"

# Устанавливаем зависимости если нужно
if ! python3 -c "import pandas, psycopg2, openpyxl" 2>/dev/null; then
    echo "📦 Устанавливаю зависимости..."
    pip3 install -r requirements_export.txt
fi

# Запускаем экспорт
echo "📤 Запускаю экспорт данных..."
python3 export_to_excel.py

echo "✅ Готово! Проверьте папку exports/"
