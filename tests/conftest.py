import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db

# Настройка тестовой базы данных
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_todo.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Фикстура для тестовой базы данных
@pytest.fixture(scope="function")
def db_session():
    """Создаёт новую сессию базы данных для теста и очищает её после выполнения."""
    # Пересоздаём таблицы перед каждым тестом
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Переопределяем get_db для использования тестовой базы
@pytest.fixture(scope="function", autouse=True)
def override_get_db(db_session):
    """Переопределяет зависимость get_db для использования фикстуры db_session."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db

# Фикстура для TestClient
@pytest.fixture(scope="function")
def client():
    """Клиент для тестирования приложения FastAPI."""
    return TestClient(app)

# Автоматическая очистка базы данных
@pytest.fixture(scope="function", autouse=True)
def clean_database(db_session):
    """
    Очищает таблицы базы данных перед каждым тестом.
    """
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
