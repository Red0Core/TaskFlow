FROM ghcr.io/cirruslabs/flutter:latest

# Устанавливаем рабочую директорию
WORKDIR /frontend

# Копируем проект во временную директорию
COPY ./lib ./lib
COPY ./pubspec.yaml ./pubspec.yaml

RUN flutter create . --platforms web && flutter config --enable-web
# Устанавливаем зависимости и собираем веб-приложение
RUN flutter pub get && flutter build web --wasm

# Используем официальный образ Nginx
FROM nginx:alpine

# Копируем статические файлы Flutter Web в папку для раздачи
COPY --from=0 /frontend/build/web /usr/share/nginx/html

# Копируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Указываем порт для Nginx
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
