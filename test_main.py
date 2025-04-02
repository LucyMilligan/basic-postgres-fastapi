# info: https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#override-a-dependency

# given this is a practice repo - only tests for users endpoint are included below
# to practice testing the sqlmodels and endpoints. Tests for checking the field constraints
# also included

import pytest  
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session
from models import Activity, User


@pytest.fixture(name="session")  
def session_fixture():  
    """fixture to create the custom engine for testing purposes, 
    create the tables, and create the session.
    SQLite used rather than Postgres for ease/speed of testing, as the
    database can be stored in-memory"""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """fixture to tell fastAPI to use get_session_override (test session) instead of
    get_session (production session). After the test function is done, pytest will
    come back to execute the rest of the code after yield"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client 
    app.dependency_overrides.clear()


class TestCreateUser:
    def test_create_user_valid_request_body(self, client: TestClient):
        user_test = {"name": "Test", "email": "test email"}
        response = client.post("/users/", json=user_test)
        data = response.json()

        assert response.status_code == 200
        assert data["name"] == "Test"
        assert data["user_id"] is not None
        assert data["email"] == "test email"

    def test_create_user_incomplete_request_body(self, client: TestClient):
        user_test = {"name": "Test"}
        response = client.post("/users/", json=user_test)
        assert response.status_code == 422

    def test_create_user_invalid_request_body(self, client: TestClient):
        user_test = {"name": "Test", "email": 57864587}
        response = client.post("/users/", json=user_test)
        assert response.status_code == 422


class TestGetUsers:
    def test_get_users(self, session: Session, client: TestClient):
        #add users to the empty database
        user_1 = User(name="test_1", email="test email 1")
        user_2 = User(name="test_2", email="test email 2")
        session.add(user_1)
        session.add(user_2)
        session.commit()

        #test the endpoint
        response = client.get("/users/")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 2
        assert data[0]["name"] == user_1.name
        assert data[1]["name"] == user_2.name
        for user in data:
            assert "email" not in user
            assert user["user_id"] is not None


class TestGetUserByUserId:
    def test_get_user_by_user_id(self, session: Session, client: TestClient):
        user_1 = User(name="test_1", email="test email 1")
        session.add(user_1)
        session.commit()

        response = client.get("/users/1")
        data = response.json()

        assert response.status_code == 200
        assert data["name"] == user_1.name
        assert data["user_id"] == 1

    def test_get_user_by_user_id_raises_exception(self, session: Session, client: TestClient):
        user_1 = User(name="test_1", email="test email 1")
        session.add(user_1)
        session.commit()

        response = client.get("/users/3")
        data = response.json()

        assert response.status_code == 404
        assert data["detail"] == "User not found"


class TestUpdateUser:
    def test_update_user_updates_user(self, session: Session, client: TestClient):
        user_1 = User(name="test_1", email="test email 1")
        session.add(user_1)
        session.commit()

        response = client.patch("/users/1", json={"name": "updated"})
        data = response.json()

        assert response.status_code == 200
        assert data["name"] == "updated"
        assert data["user_id"] == user_1.user_id
        assert "email" not in data


class TestDeleteUser:
    def test_delete_user_deletes_user(self, session: Session, client: TestClient):
        user_1 = User(name="test_1", email="test email 1")
        session.add(user_1)
        session.commit()

        response = client.delete("/users/1")
        data = response.json()
        users_in_db = session.get(User, 1)

        assert response.status_code == 200
        assert users_in_db is None
        assert data == {"message": "User_id 1 deleted"}


class TestCreateActivity:
    def test_create_activity_raises_422_for_incorrect_date_field(self, session: Session, client: TestClient):
        activity_test = {
            "user_id": 1,
            "date": "25 March 25", #incorrect format
            "time": "17:30",
            "activity": "run",
            "activity_type": "trail",
            "moving_time": "00:00:30",
            "distance_km": 5,
            "perceived_effort": 5,
            "elevation_m": 5
        }
        response = client.post("/activities/", json=activity_test)
        data = response.json()
        assert response.status_code == 422
        assert "Format of data incorrect:" and "date" in data["detail"]

    def test_create_activity_raises_422_for_multiple_incorrect_fields(self, session: Session, client: TestClient):
        activity_test = {
            "user_id": 1,
            "date": "25 March 25", #incorrect format
            "time": "7.30pm", #incorrect format
            "activity": "running", #incorrect format
            "activity_type": "trail",
            "moving_time": "30mins 5secs", #incorrect format
            "distance_km": 5,
            "perceived_effort": 100, #incorrect format
            "elevation_m": 5
        }
        response = client.post("/activities/", json=activity_test)
        data = response.json()
        assert response.status_code == 422
        assert "Format of data incorrect:" in data["detail"]
        assert "date" in data["detail"]
        assert "time" in data["detail"]
        assert "activity" in data["detail"]
        assert "moving_time" in data["detail"]
        assert "perceived_effort" in data["detail"]


class TestUpdateActivity:
    def test_update_activity_raises_422_for_incorrect_fields(self, session: Session, client: TestClient):
        activity_test = Activity(
            user_id= 1,
            date="2025/03/04",
            time="17:30",
            activity="run",
            activity_type="trail",
            moving_time="00:00:30",
            distance_km=5,
            perceived_effort=5,
            elevation_m=5
        )

        activity_update = {
            "date": "25 March 2024",
            "time": "5pm",
            "perceived_effort": 15
        }

        session.add(activity_test)
        session.commit()

        response = client.patch("/activities/1", json=activity_update)
        data = response.json()["detail"]

        assert response.status_code == 422
        assert data[0]["type"] == "string_pattern_mismatch"
        assert "date" in data[0]["loc"]
        assert "time" in data[1]["loc"]
        assert "perceived_effort" in data[2]["loc"]