from fastapi.testclient import TestClient

def test_create_task(client, clean_database, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/tasks",
        json={"title": "Test Task", "description": "This is a test task."},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
    assert response.json()["description"] == "This is a test task."
    assert response.json()["is_completed"] is False

    fail_response = client.post(
        "/tasks",
        json={"description": "This is a test task."},
        headers=headers,
    )
    assert fail_response.status_code == 422

    fail_response = client.post(
        "/tasks",
        json={"title": "This is a test title."},
        headers=headers,
    )
    assert fail_response.status_code == 422

def test_get_tasks(client, clean_database, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Создаём задачу
    client.post(
        "/tasks",
        json={"title": "Task 1", "description": "Description 1"},
        headers=headers,
    )
    client.post(
        "/tasks",
        json={"title": "Task 2", "description": "Description 2"},
        headers=headers,
    )

    # Получаем все задачи
    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 1"
    assert tasks[1]["title"] == "Task 2"


def test_get_one_task(client: TestClient, clean_database, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Создаём задачу
    create_task = client.post(
        "/tasks",
        json={"title": "Task 1", "description": "Description 1"},
        headers=headers,
    )
    assert create_task.status_code == 201
    
    task_id = create_task.json()['id']
    response = client.get(
        f"/tasks/{task_id}",
        headers=headers    
    )
    assert response.status_code == 200

    # Проверяем, что данные совпадают
    task = response.json()
    assert task["id"] == task_id
    assert task["title"] == "Task 1"
    assert task["description"] == "Description 1"
    assert task["is_completed"] is False

def test_get_nonexistent_task(client, clean_database, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Попытка получить задачу несуществующего пользователя
    response = client.get(f"/tasks/-1", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}

def test_patch_task(client: TestClient, clean_database, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Создаём задачу
    create_task = client.post(
        "/tasks",
        json={"title": "Task 1", "description": "Description 1"},
        headers=headers,
    )
    assert create_task.status_code == 201
    task_id = create_task.json()['id']

    # Частичное обновление задачи
    patch_response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated Task Title", "is_completed": True},
        headers=headers
    )
    assert patch_response.status_code == 200
    updated_task = patch_response.json()
    assert updated_task["title"] == "Updated Task Title"
    assert updated_task["description"] == "Description 1"
    assert updated_task["is_completed"] is True

def test_update_task(client, clean_database, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Создаём задачу
    create_response = client.post(
        "/tasks",
        json={"title": "Old Title", "description": "Old Description"},
        headers=headers
    )
    task_id = create_response.json()["id"]

    # Обновляем задачу
    update_response = client.put(
        f"/tasks/{task_id}",
        json={"title": "New Title", "description": "New Description", "is_completed": True},
        headers=headers
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "New Title"
    assert updated_task["description"] == "New Description"
    assert updated_task["is_completed"] is True


def test_get_completed_tasks(client: TestClient, clean_database, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Добавление новых задач
    for i in range(2, 5):
        response = client.post(
            f"/tasks",
            json={"title": f"Test Task{i}", "description": "This is another test task."},
            headers=headers
        )
        assert response.status_code == 201
    
    # Частичное обновление последней задачи
    patch_response = client.patch(
        f"/tasks/{response.json()['id']}",
        json={"is_completed": True},
        headers=headers
    )
    assert response.status_code == 201

    # Получаем все завершенные задачи
    response = client.get(
        f"/tasks",
        params={"is_completed": True},
        headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    for task in response.json():
        assert task['is_completed'] == True

    # Получаем все незавершенные задачи
    response = client.get(
        f"/tasks",
        params={"is_completed": False},
        headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 2  # Все задачи незавершённые
    for task in response.json():
        assert task['is_completed'] is False

def test_delete_task(client, clean_database, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Создаём задачу
    create_response = client.post(
        "/tasks",
        json={"title": "Task to delete", "description": "Will be deleted"},
        headers=headers
    )
    task_id = create_response.json()["id"]

    # Удаляем задачу
    delete_response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204

    # Проверяем, что задача удалена
    get_response = client.get(f"/tasks/{task_id}", headers=headers)
    assert get_response.status_code == 404

    # Проверяем, что их нет теперь вообще
    get_response = client.get("/tasks", headers=headers)
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

def test_get_tasks_unauthorized(client):
    response = client.get("/tasks")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_tasks_invalid_token(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/tasks", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
