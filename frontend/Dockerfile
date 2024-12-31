# Используем официальный образ Nginx
FROM nginx:alpine

# Копируем статические файлы Flutter Web в папку для раздачи
COPY build/web /usr/share/nginx/html

# Копируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Указываем порт для Nginx
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
