import pytest
from schemas import TaskCreate
from fastapi.testclient import TestClient

@pytest.fixture(scope="function")
def get_user_id_with_task(client, clean_database):
    """
    Фикстура для регистрации и авторизации пользователя.
    Возвращает токен для аутентифицированных запросов.
    """
    # Регистрация пользователя
    register_response = client.post(
        "/auth/register",
        json={"username": "test_user", "password": "secure_password"}
    )
    assert register_response.status_code == 201

    # Авторизация пользователя
    login_response = client.post(
        "/auth/login",
        json={"username": "test_user", "password": "secure_password"}
    )
    assert login_response.status_code == 200

    user_id = login_response.json()['id']
    
    response = client.post(
        f"/users/{user_id}/tasks",
        json={"title": "Test Task", "description": "This is a test task."},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"

    return user_id

def test_get_tasks(client: TestClient, get_user_id_with_task):
    user_id = get_user_id_with_task

    # Добавление новой задачи
    response = client.post(
        f"/users/{user_id}/tasks",
        json={"title": "Test Task2", "description": "This is another test task."}
    )
    assert response.status_code == 201

    # Получение всех задач пользователя
    response = client.get(f"/users/{user_id}/tasks")
    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 2

    # Проверка первой задачи
    assert tasks[0]['title'] == "Test Task"
    assert tasks[0]['description'] == "This is a test task."
    assert tasks[0]["is_completed"] is False

    # Проверка второй задачи
    assert tasks[1]['title'] == "Test Task2"
    assert tasks[1]['description'] == "This is another test task."
    assert tasks[1]["is_completed"] is False

def test_get_one_task(client: TestClient, get_user_id_with_task):
    user_id = get_user_id_with_task

    create_task = client.post(
        f"/users/{user_id}/tasks",
        json={"title": "Single Task", "description": "This is a single task."}
    )
    assert create_task.status_code == 201
    
    task_id = create_task.json()['id']
    response = client.get(url=f"/users/{user_id}/tasks/{task_id}")
    assert response.status_code == 200

    # Проверяем, что данные совпадают
    task = response.json()
    assert task["id"] == task_id
    assert task["title"] == "Single Task"
    assert task["description"] == "This is a single task."
    assert task["is_completed"] is False

def test_get_task_of_unexist_user(client, get_user_id_with_task):
    user_id = get_user_id_with_task

    # Попытка получить задачу несуществующего пользователя
    response = client.get(f"/users/-1/tasks/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_get_nonexistent_task(client, get_user_id_with_task):
    user_id = get_user_id_with_task

    # Попытка получить задачу несуществующего пользователя
    response = client.get(f"/users/{user_id}/tasks/-1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_patch_task(client: TestClient, get_user_id_with_task):
    user_id = get_user_id_with_task

    # Создание задачи
    response = client.post(
        f"/users/{user_id}/tasks",
        json={"title": "Initial Task", "description": "Task description"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    # Частичное обновление задачи
    patch_response = client.patch(
        f"/users/{user_id}/tasks/{task_id}",
        json={"title": "Updated Task Title", "is_completed": True}
    )
    assert patch_response.status_code == 200
    updated_task = patch_response.json()
    assert updated_task["title"] == "Updated Task Title"
    assert updated_task["description"] == "Task description"
    assert updated_task["is_completed"] is True

def test_put_task(client: TestClient, get_user_id_with_task):
    user_id = get_user_id_with_task

    # Создание задачи
    response = client.post(
        f"/users/{user_id}/tasks",
        json={"title": "Initial Task", "description": "Initial Description"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    # Полное обновление задачи
    put_response = client.put(
        f"/users/{user_id}/tasks/{task_id}",
        json={"title": "Updated Task", "description": "Updated Description", "is_completed": True}
    )
    assert put_response.status_code == 200
    updated_task = put_response.json()
    assert updated_task["title"] == "Updated Task"
    assert updated_task["description"] == "Updated Description"
    assert updated_task["is_completed"] is True

def test_get_completed_tasks(client: TestClient, get_user_id_with_task):
    user_id = get_user_id_with_task

    # Добавление новых задач
    for i in range(2, 5):
        response = client.post(
            f"/users/{user_id}/tasks",
            json={"title": f"Test Task{i}", "description": "This is another test task."}
        )
        assert response.status_code == 201
    
    # Частичное обновление последней задачи
    patch_response = client.patch(
        f"/users/{user_id}/tasks/{response.json()['id']}",
        json={"is_completed": True}
    )
    assert response.status_code == 201

    # Получаем все завершенные задачи
    response = client.get(
        f"/users/{user_id}/tasks",
        params={"is_completed": True}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    for task in response.json():
        assert task['is_completed'] == True

    # Получаем все незавершенные задачи
    response = client.get(
        f"/users/{user_id}/tasks",
        params={"is_completed": False}
    )
    assert response.status_code == 200
    assert len(response.json()) == 3  # Все задачи незавершённые
    for task in response.json():
        assert task['is_completed'] is False

def test_delete_task(client: TestClient, get_user_id_with_task):
    # Создание второй задачи
    response = client.post(
        f"/users/{get_user_id_with_task}/tasks",
        json={"title": "Initial Task", "description": "Initial Description"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]
    
    # Проверка что добавилось
    response = client.get(
        f"/users/{get_user_id_with_task}/tasks"
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

    
    response = client.delete(
        f"/users/{get_user_id_with_task}/tasks/{task_id}"
    )
    assert response.status_code == 204

    # Проверка на удаление
    response = client.get(
        f"/users/{get_user_id_with_task}/tasks"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Попытка удалить ту же задачу снова
    response = client.delete(f"/users/{get_user_id_with_task}/tasks/{task_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}