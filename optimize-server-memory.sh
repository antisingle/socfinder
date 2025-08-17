#!/bin/bash
# Скрипт для оптимизации памяти на сервере с 1GB RAM

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔧 Оптимизация памяти для сервера с 1GB RAM${NC}"
echo "======================================================"

# Проверяем, запущен ли скрипт от root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}❌ Этот скрипт должен быть запущен от root!${NC}"
  echo "Выполните: sudo bash $0"
  exit 1
fi

# Проверяем текущую память
echo -e "${YELLOW}📊 Текущее состояние памяти:${NC}"
free -h
echo ""

# Проверяем текущий swap
echo -e "${YELLOW}📊 Текущий swap:${NC}"
swapon --show
echo ""

# Создаем swap файл размером 4GB
echo -e "${YELLOW}💾 Создаем swap файл размером 4GB...${NC}"
if [ -f /swapfile ]; then
  echo -e "${YELLOW}⚠️ Swap файл уже существует. Удаляем его...${NC}"
  swapoff /swapfile
  rm -f /swapfile
fi

# Создаем новый swap файл
echo -e "${YELLOW}📝 Создаем новый swap файл...${NC}"
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Добавляем swap в fstab для автоматического монтирования при загрузке
if ! grep -q "/swapfile" /etc/fstab; then
  echo -e "${YELLOW}📝 Добавляем swap в /etc/fstab...${NC}"
  echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
fi

# Оптимизируем параметры ядра для работы с swap
echo -e "${YELLOW}🔧 Оптимизируем параметры ядра...${NC}"

# Настраиваем swappiness (насколько активно система будет использовать swap)
# Значение 10 означает, что система будет использовать swap только когда RAM заполнена на 90%
sysctl vm.swappiness=10

# Настраиваем cache pressure (насколько активно система будет очищать кэш)
# Значение 50 - баланс между производительностью и использованием памяти
sysctl vm.vfs_cache_pressure=50

# Сохраняем параметры ядра
echo "vm.swappiness=10" >> /etc/sysctl.conf
echo "vm.vfs_cache_pressure=50" >> /etc/sysctl.conf

# Применяем параметры
sysctl -p

# Проверяем результаты
echo -e "${YELLOW}📊 Новое состояние памяти:${NC}"
free -h
echo ""

echo -e "${YELLOW}📊 Новый swap:${NC}"
swapon --show
echo ""

echo -e "${GREEN}✅ Оптимизация памяти завершена!${NC}"
echo -e "${GREEN}✅ Теперь у вас есть 4GB swap файл и оптимизированные параметры ядра.${NC}"
echo -e "${GREEN}✅ Это должно помочь с загрузкой большого Excel файла.${NC}"
echo ""
echo -e "${YELLOW}📋 Рекомендации:${NC}"
echo "1. Перезапустите Docker: sudo systemctl restart docker"
echo "2. Запустите контейнеры: docker-compose -f docker-compose.minimal.yml up -d"
echo "3. Следите за использованием памяти: htop или docker stats"
echo ""
