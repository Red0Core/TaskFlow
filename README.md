# TaskFlow

**TaskFlow** — это приложение для управления задачами, демонстрирующее мои навыки разработки. Проект включает серверную часть (backend) на **FastAPI** и ~~в будущем будет дополнен~~ клиентским приложением (frontend) на **Flutter**.

---

## 📋 Функционал

- Аутентификация и авторизация с использованием JWT (включая refresh-токены).
- Полный набор операций CRUD для задач и пользователей.
- Frontend на **Flutter**.

---

## 🛠 Используемые технологии

### Backend
- **FastAPI** — фреймворк для разработки API.
- **PostgreSQL** — для работы с базой данных (SQLite в режиме разработки).
- **Docker** — для контейнеризации приложения.
- **Pytest** — для написания тестов.

### Frontend
- **Flutter** — для разработки мобильного и веб-приложения.

### Деплой
- **Vercel** билдится flutter через каждый коммит на бесплатном тарифе
- **Render** содержится Backend на бесплатном тарифе, который билдится через Docker
- **Supabase** используется для PostgreSQL, к которому обращается backend на **Render**

### CI/CD
- **GitHub Actions**: Сделано для автоматизации тестирования. Больше применения не нашел пока что

---

### 🚀 Быстрый запуск через Docker Compose
Шаг 1: Подготовьте .env файл
- Создайте .env файл в директории backend, основываясь на backend/.env.example.
  
Шаг 2: Сборка и запуск контейнеров
- Убедитесь, что у вас установлен Docker и Docker Compose.
- Запустите `docker-compose up --build`
  
После запуска:
- Frontend: будет доступен по адресу http://localhost:8080.
- Backend API: будет доступен по адресу http://localhost:8080/api (перенаправление через nginx) или же http://localhost:8000/api.
  
---

## 🚀 Как запустить Backend

*Перед запуском приложения убедитесь, что в папке `backend` существует файл `.env`. Если его нет:*
1. Скопируйте шаблон `.env.example` в `.env`:
   ```bash
   cp backend/.env.example backend/.env
2. Заполните необходимые переменные в файле .env.
   
### Через Docker
1. Убедитесь, что Docker установлен и работает.
2. Запустите проект:
   ```bash
   docker-compose up --build

### Локально
1. Перейдите в папку backend
2. Создайте виртуальное окружение
   ```bash
   python -m venv venv
   source venv/bin/activate    # Для Linux/macOS
   venv\Scripts\activate       # Для Windows
4. Установите зависимости:
   ```bash
   pip install -r backend/requirements.txt
5. Если хотите проверить тесты, то ```pytest```
6. Запустить через ```uvicorn main:app --reload```

#### Как настроить CORS
Если требуется разрешить запросы с определенных доменов, отредактируйте файл `main.py`, добавив нужные домены в список разрешённых:
```python
allowed_origins = [
   "http://127.0.0.1:8080",
   "http://localhost:8080",  # Для локального тестирования
   "https://ваш-домен.com",  # Укажите свой домен
]
```

---

## 🚀 Как запустить Frontend
### Требования
- Установленный [Flutter SDK](https://flutter.dev/docs/get-started/install).
- Запущенный backend
### Запуск вручную
1. Перейдите в папку `frontend`:
   ```bash
   cd frontend
2. Установить зависимости ```flutter pub get```
3. Запустить веб-сервер (Порт с учетом CORS) ```flutter run -d chrome --web-port=8080```
4. Открыть сайт http://localhost:8080

---

## Как настроить API URL в Flutter

Ваше приложение взаимодействует с API, и вам нужно указать базовый URL для запросов во Flutter.
Если к API можно обратиться через тот же домен (your-domain.com/api), то ничего менять не надо!
Иначе в `frontend/lib/main.dart` вам надо явно написать ваш домен
```dart
final apiClient = ApiClient(baseUrl: "Ваш домен");
```

---

### **📈 Что дальше?**

1. ~~Frontend: Начать разработку клиентской части на Flutter.~~
2. ~~PostgreSQL: Перенести проект с SQLite на PostgreSQL.~~
3. ~~CI/CD: Настроить автоматическое тестирование и сборку через GitHub Actions.~~
4. ~~Деплой: Развернуть проект на сервере (можно и сейчас, но только backend)~~
