# TaskFlow

**TaskFlow** — это приложение для управления задачами, демонстрирующее мои навыки разработки. Проект включает серверную часть (backend) на **FastAPI** и в будущем будет дополнен клиентским приложением (frontend) на **Flutter**.

---

## 📋 Функционал

- Аутентификация и авторизация с использованием JWT (включая refresh-токены).
- Полный набор операций CRUD для задач и пользователей.
- Возможность добавления мобильного и веб-приложения на **Flutter** (в разработке).

---

## 🛠 Используемые технологии

### Backend
- **FastAPI** — фреймворк для разработки API.
- **PostgreSQL** — для работы с базой данных (SQLite в режиме разработки).
- **Docker** — для контейнеризации приложения.
- **Pytest** — для написания тестов.

### Frontend
- **Flutter** — для разработки мобильного и веб-приложения.

### CI/CD (планируется)
- **GitHub Actions** — для автоматизации тестирования и деплоя.

---

### 🚀 Быстрый запуск через Docker Compose
Шаг 1: Подготовьте .env файл
- Создайте .env файл в директории backend, основываясь на backend/.env.example.
  
Шаг 2: Сборка и запуск контейнеров
- Убедитесь, что у вас установлен Docker и Docker Compose.
- Запустите `docker-compose up --build`
  
После запуска:
- Frontend: будет доступен по адресу http://localhost.
- Backend API: будет доступен по адресу http://localhost/api.
  
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
6. Запустить через ```uvicorn uvicorn main:app --reload```

---

## 🚀 Как запустить Frontend
### Требования
- Установленный [Flutter SDK](https://flutter.dev/docs/get-started/install).
- Подготовленный backend (можно запустить с помощью [Docker Compose](../backend/README.md)).
### Установка
1. Перейдите в папку `frontend`:
   ```bash
   cd frontend
2. Установить зависимости ```flutter pub get```
3. Запустить веб-сервер (Порт с учетом CORS) ```flutter run -d chrome --web-port=8080```
4. Открыть сайт http://localhost:8080

---

### Как настроить CORS

Откройте файл `main.py` и добавьте ваш домен в список разрешённых источников:

```python
allowed_origins = [
   "http://127.0.0.1:8080",
   "http://localhost:8080",  # Для локального тестирования
   "https://ваш-домен.com",  # Укажите свой домен
]
```

---

### **📈 Что дальше?**

1. ~~Frontend: Начать разработку клиентской части на Flutter.~~
2. PostgreSQL: Перенести проект с SQLite на PostgreSQL.
3. CI/CD: Настроить автоматическое тестирование и сборку через GitHub Actions.
4. Деплой: Развернуть проект на сервере (можно и сейчас, но только backend)
