# 🚀 Быстрое развертывание SocFinder

## Подготовка сервера (5 минут)

### 1. Подключение к серверу
```bash
ssh root@your-server-ip
```

### 2. Установка Docker (Ubuntu/Debian)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 3. Установка Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 4. Перелогинивание
```bash
exit
ssh root@your-server-ip
```

## Развертывание приложения (2 минуты)

### 1. Клонирование репозитория
```bash
git clone https://github.com/antisingle/socfinder.git
cd socfinder
```

### 2. Настройка окружения
```bash
cp env.prod.example .env
nano .env
```

Отредактируйте `.env`:
```bash
# Установите надежный пароль
POSTGRES_PASSWORD=your_very_secure_password_2025

# Обновите URL API (замените на ваш домен)
API_URL=http://your-server-ip/api
```

### 3. Запуск приложения
```bash
./deploy.sh
```

## Проверка (1 минута)

Откройте в браузере:
- **Приложение**: `http://your-server-ip`
- **API**: `http://your-server-ip/api/v1/stats/overview`

## Настройка домена (опционально)

### 1. Настройка DNS
Добавьте A-запись: `your-domain.com -> your-server-ip`

### 2. Обновите .env
```bash
API_URL=http://your-domain.com/api
```

### 3. Перезапуск
```bash
docker-compose -f docker-compose.prod.yml restart
```

## SSL сертификат (опционально)

### 1. Установка Certbot
```bash
sudo apt install certbot
```

### 2. Получение сертификата
```bash
sudo certbot certonly --standalone -d your-domain.com
```

### 3. Копирование сертификатов
```bash
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*
```

### 4. Обновление nginx.conf
Раскомментируйте HTTPS секцию в `nginx/nginx.conf`

### 5. Перезапуск
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

## Управление

```bash
# Просмотр статуса
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f

# Перезапуск
docker-compose -f docker-compose.prod.yml restart

# Остановка
docker-compose -f docker-compose.prod.yml down
```

## Troubleshooting

### Проблема: Не загружаются данные
```bash
# Проверить логи backend
docker-compose -f docker-compose.prod.yml logs backend

# Перезагрузить данные
docker-compose -f docker-compose.prod.yml down
docker volume rm socfinder_postgres_data
docker-compose -f docker-compose.prod.yml up -d
```

### Проблема: 502 Bad Gateway
```bash
# Проверить статус всех сервисов
docker-compose -f docker-compose.prod.yml ps

# Перезапустить все
docker-compose -f docker-compose.prod.yml restart
```

### Проблема: Нет доступа извне
```bash
# Открыть порты в firewall
sudo ufw allow 80
sudo ufw allow 443
```

## Резервное копирование

### Создание backup
```bash
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U socfinder socfinder > backup_$(date +%Y%m%d).sql
```

### Восстановление
```bash
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U socfinder -d socfinder < backup_file.sql
```

---

**Время развертывания: ~8 минут**
**Поддержка**: [GitHub Issues](https://github.com/antisingle/socfinder/issues)
