# 🚀 Развертывание SocFinder на сервере

## Быстрый старт

### 1. Подготовка сервера

#### Минимальные требования
- **CPU**: 2 vCPU
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+

#### Установка Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Перелогиньтесь после добавления в группу docker
```

#### Установка Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Развертывание приложения

#### Клонирование репозитория
```bash
git clone https://github.com/antisingle/socfinder.git
cd socfinder
```

#### Настройка окружения
```bash
# Скопировать пример конфигурации
cp env.prod.example .env

# Отредактировать конфигурацию
nano .env
```

#### Запуск деплоя
```bash
# Запустить автоматический деплой
./deploy.sh
```

### 3. Проверка развертывания

После успешного деплоя проверьте:
- Frontend: http://your-server-ip
- API: http://your-server-ip/api
- Health check: http://your-server-ip/health

## Детальная настройка

### Переменные окружения (.env)

```bash
# База данных
POSTGRES_PASSWORD=your_secure_password_here

# URL API (замените на ваш домен)
API_URL=https://your-domain.com/api

# SSL сертификаты (опционально)
SSL_CERT_PATH=./nginx/ssl/cert.pem
SSL_KEY_PATH=./nginx/ssl/key.pem
```

### Настройка домена и SSL

#### 1. Настройка DNS
Добавьте A-запись в DNS:
```
your-domain.com -> YOUR_SERVER_IP
```

#### 2. Получение SSL сертификата (Let's Encrypt)
```bash
# Установка certbot
sudo apt install certbot

# Получение сертификата
sudo certbot certonly --standalone -d your-domain.com

# Копирование сертификатов
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*
```

#### 3. Обновление конфигурации для HTTPS
Раскомментируйте HTTPS секцию в `nginx/nginx.conf` и обновите домен.

#### 4. Перезапуск с HTTPS
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

### Настройка брандмауэра

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## Управление приложением

### Основные команды

```bash
# Просмотр статуса
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f

# Перезапуск сервиса
docker-compose -f docker-compose.prod.yml restart [service_name]

# Остановка
docker-compose -f docker-compose.prod.yml down

# Полная перезагрузка
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Мониторинг

#### Проверка здоровья сервисов
```bash
# Backend health check
curl http://localhost/health

# Database connection
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U socfinder

# Frontend
curl -I http://localhost/
```

#### Мониторинг ресурсов
```bash
# Использование Docker контейнерами
docker stats

# Использование диска
df -h
docker system df
```

### Резервное копирование

#### Создание backup базы данных
```bash
# Создание backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U socfinder socfinder > backup_$(date +%Y%m%d_%H%M%S).sql

# Автоматический backup (добавить в crontab)
0 2 * * * cd /path/to/socfinder && docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U socfinder socfinder > data/backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

#### Восстановление из backup
```bash
# Восстановление
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U socfinder -d socfinder < backup_file.sql
```

## Обновление приложения

### Обновление кода
```bash
# Получить последние изменения
git pull origin main

# Пересобрать и перезапустить
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Обновление данных
Данные автоматически загружаются при первом запуске. Для перезагрузки:
```bash
# Удалить данные и перезагрузить
docker-compose -f docker-compose.prod.yml down
docker volume rm socfinder_postgres_data
docker-compose -f docker-compose.prod.yml up -d
```

## Устранение неполадок

### Проблемы с запуском

#### PostgreSQL не запускается
```bash
# Проверить логи
docker-compose -f docker-compose.prod.yml logs postgres

# Проверить права доступа к volume
docker volume inspect socfinder_postgres_data
```

#### Backend не отвечает
```bash
# Проверить логи
docker-compose -f docker-compose.prod.yml logs backend

# Проверить подключение к базе
docker-compose -f docker-compose.prod.yml exec backend python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://socfinder:password@postgres:5432/socfinder')
print('Connection test:', engine.execute('SELECT 1').scalar())
"
```

#### Nginx ошибки
```bash
# Проверить конфигурацию
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Проверить логи
docker-compose -f docker-compose.prod.yml logs nginx
```

### Производительность

#### Оптимизация PostgreSQL
```bash
# Подключиться к базе
docker-compose -f docker-compose.prod.yml exec postgres psql -U socfinder -d socfinder

# Проверить размер таблиц
SELECT schemaname,tablename,attname,n_distinct,correlation FROM pg_stats WHERE tablename = 'projects';

# Создать дополнительные индексы при необходимости
CREATE INDEX idx_projects_region ON projects(region);
CREATE INDEX idx_projects_year ON projects(year);
```

## Мониторинг и алерты

### Простой мониторинг
```bash
# Создать скрипт мониторинга
cat > monitor.sh << 'EOF'
#!/bin/bash
if ! curl -f http://localhost/health > /dev/null 2>&1; then
    echo "$(date): SocFinder is DOWN" >> monitor.log
    # Отправить уведомление (email, Telegram, Slack)
fi
EOF

# Добавить в crontab (проверка каждые 5 минут)
*/5 * * * * /path/to/monitor.sh
```

### Логирование
```bash
# Настроить ротацию логов
sudo nano /etc/logrotate.d/docker-containers

# Содержимое файла:
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
```

## Безопасность

### Рекомендации
1. **Изменить пароли** в .env файле
2. **Настроить firewall** - открыть только необходимые порты
3. **Обновлять систему** регулярно
4. **Мониторить логи** на подозрительную активность
5. **Настроить автоматические обновления** безопасности

### Дополнительная защита
```bash
# Fail2ban для защиты от брутфорса
sudo apt install fail2ban

# Настроить SSH ключи вместо паролей
# Отключить root login
# Изменить стандартный SSH порт
```

## Поддержка

При возникновении проблем:
1. Проверьте логи всех сервисов
2. Убедитесь что все порты открыты
3. Проверьте DNS настройки
4. Создайте issue в GitHub репозитории
