FROM node:18-alpine

# Добавить аргументы для переменных окружения
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

WORKDIR /app

# Копируем package.json
COPY package.json ./

# Устанавливаем зависимости
RUN npm install 

# Копируем исходный код
COPY . .

# Собираем production build
RUN npm run build

# Устанавливаем serve для раздачи статики
RUN npm install -g serve

# Открываем порт
EXPOSE 3000

# Запускаем приложение
CMD ["serve", "-s", "build", "-l", "3000"]
