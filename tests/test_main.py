from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from todo.main import app, get_session

from todo import settings


def test_read_main():
    client = TestClient(app=app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == ['Hello World']


def test_write_main():

    connection_string = str(settings.DATABASE_URL)

    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        client = TestClient(app=app)

        todo_content = "test todo"

        response = client.post("/todos/", json={"content": todo_content})

        data = response.json()

        assert response.status_code == 200
        assert data["content"] == todo_content


def test_read_list_main():

    connection_string = str(settings.DATABASE_URL)

    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app=app)

        response = client.get("/todos/")
        assert response.status_code == 200
