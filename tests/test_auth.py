from database import User
from fastapi.testclient import TestClient

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

# Тест успешного логина
def test_login_user(client: TestClient, db_session, clean_database):
    # Регистрация пользователя
    client.post("/auth/register", json={"username": "test_user", "password": "secure_password"})
    
    response = client.post(
        "/auth/login",
        json={"username": "test_user", "password": "secure_password"}
    )
    assert response.status_code == 200
    user = db_session.query(User).filter(User.username == "test_user").first()
    assert response.json()['id'] == user.id

# Тест логина с неверным паролем
def test_login_invalid_password(client: TestClient, clean_database):
    # Регистрация пользователя
    client.post("/auth/register", json={"username": "test_user", "password": "secure_password"})
 
    response = client.post(
        "/auth/login",
        json={"username": "test_user", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}

def test_register_empty_body(client: TestClient):
    response = client.post("/auth/register", json={})
    assert response.status_code == 422