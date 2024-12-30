from fastapi.testclient import TestClient
import jwt
import os

# Тест регистрации
def test_register_user(client: TestClient, clean_database):
    response = client.post(
        "/auth/register",
        json={"username": "test_user", "password": "secure_password"}
    )
    assert response.status_code == 201
    assert response.json() == {"username": "test_user"}

# Тест регистрации с уже существующим пользователем
def test_register_existing_user(client: TestClient, clean_database):
    # Регистрация пользователя
    client.post("/auth/register", json={"username": "test_user", "password": "secure_password"})

    response = client.post(
        "/auth/register",
        json={"username": "test_user", "password": "secure_password"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists"}

# Тест регистрации с уже существующим пользователем
def test_register_existing_user_with_different_password(client: TestClient, clean_database):
    # Регистрация пользователя
    client.post("/auth/register", json={"username": "test_user", "password": "secure_password"})

    response = client.post(
        "/auth/register",
        json={"username": "test_user", "password": "another_password"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists"}

# Тест регистрации с недостаточной длиной пароля
def test_register_existing_user_minpassword(client: TestClient, clean_database):
    # Регистрация пользователя
    response = client.post("/auth/register", json={"username": "test_user", "password": "1234567"})

    assert response.status_code == 422

# Тест логина через токен
def test_login_success(client, create_test_user, clean_database):
    create_test_user(username="testuser", password="testpassword")
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Расшифровываем токен для проверки структуры
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    for decoded_token in [
        jwt.decode(response.json()['access_token'], SECRET_KEY, algorithms=[ALGORITHM]),
        jwt.decode(response.json()['refresh_token'], SECRET_KEY, algorithms=[ALGORITHM]),
    ]:
        # Проверяем содержимое payload
        assert "sub" in decoded_token, "Payload не содержит 'sub'"
        assert isinstance(decoded_token["sub"], str), "Поле 'sub' должно быть строкой"
        assert decoded_token["sub"].isdigit(), "Поле 'sub' должно быть строковым числом"

        assert "exp" in decoded_token, "Payload не содержит 'exp'"
        assert isinstance(decoded_token["exp"], int), "Поле 'exp' должно быть числом"
        assert decoded_token["exp"] > 0, "Поле 'exp' должно быть положительным"

# Тест логина неизвестного пользователя
def test_login_invalid_user(client, clean_database):
    response = client.post(
        "/token",
        data={"username": "invaliduser", "password": "invalidpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# Тест пустой регистрации
def test_register_empty_body(client: TestClient):
    response = client.post("/auth/register", json={})
    assert response.status_code == 422


def test_refresh_access_token(client: TestClient, auth_token):
    refresh_token = auth_token["refresh_token"]
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "access_token" != auth_token["access_token"]

def test_refresh_token_validity(client: TestClient, auth_token):
    """Тестирует валидность нового access_token, полученного из /auth/refresh."""
    refresh_token = auth_token["refresh_token"]
    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == 200, "Ошибка при обновлении токена"

    access_token = refresh_response.json()["access_token"]
    assert access_token, "Access token отсутствует в ответе"

    # Расшифровываем токен для проверки структуры
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])

    # Проверяем содержимое payload
    assert "sub" in decoded_token, "Payload не содержит 'sub'"
    assert isinstance(decoded_token["sub"], str), "Поле 'sub' должно быть строкой"
    assert decoded_token["sub"].isdigit(), "Поле 'sub' должно быть строковым числом"

    assert "exp" in decoded_token, "Payload не содержит 'exp'"
    assert isinstance(decoded_token["exp"], int), "Поле 'exp' должно быть числом"
    assert decoded_token["exp"] > 0, "Поле 'exp' должно быть положительным"

def test_logout(client, auth_token):
    refresh_token = auth_token["refresh_token"]
    response = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert response.json()["detail"] == "Successfully logged out"
