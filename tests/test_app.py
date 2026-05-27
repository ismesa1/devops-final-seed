import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import app as app_module  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test_tasks.db"

    app_module.DB_PATH = str(db_path)
    app_module.app.config["TESTING"] = True
    app_module.init_db()

    with app_module.app.test_client() as test_client:
        yield test_client


def test_get_db_returns_sqlite_connection(tmp_path):
    app_module.DB_PATH = str(tmp_path / "conn_test.db")
    connection = app_module.get_db()

    try:
        assert isinstance(connection, sqlite3.Connection)
        assert connection.row_factory == sqlite3.Row
    finally:
        connection.close()


def test_init_db_creates_tasks_table(tmp_path):
    app_module.DB_PATH = str(tmp_path / "init_test.db")

    app_module.init_db()

    connection = sqlite3.connect(app_module.DB_PATH)
    try:
        row = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
        ).fetchone()
        assert row is not None
    finally:
        connection.close()


def test_index_returns_api_metadata(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "name": "To-Do API",
        "version": "1.0.0",
        "endpoints": ["/tasks"],
    }


def test_list_tasks_returns_empty_list_initially(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task_success(client):
    payload = {"title": "Aprender pytest", "description": "Escribir pruebas unitarias"}

    response = client.post("/tasks", json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data["id"] > 0
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["completed"] == 0


def test_create_task_requires_title(client):
    response = client.post("/tasks", json={"description": "Sin titulo"})

    assert response.status_code == 400
    assert "title" in response.get_json()["error"]


def test_get_task_returns_existing_task(client):
    created = client.post("/tasks", json={"title": "Tarea A", "description": "Desc A"}).get_json()

    response = client.get(f"/tasks/{created['id']}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == created["id"]
    assert data["title"] == "Tarea A"


def test_get_task_returns_404_when_not_found(client):
    response = client.get("/tasks/9999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Tarea no encontrada"


def test_update_task_updates_fields(client):
    created = client.post("/tasks", json={"title": "Inicial", "description": "Pendiente"}).get_json()

    response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "Actualizada", "description": "Hecha", "completed": 1},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["title"] == "Actualizada"
    assert data["description"] == "Hecha"
    assert data["completed"] == 1


def test_update_task_requires_payload(client):
    created = client.post("/tasks", json={"title": "Inicial", "description": "Pendiente"}).get_json()

    response = client.put(f"/tasks/{created['id']}", json={})

    assert response.status_code == 400
    assert response.get_json()["error"] == "No se enviaron datos"


def test_update_task_returns_404_when_not_found(client):
    response = client.put("/tasks/9999", json={"title": "No existe"})

    assert response.status_code == 404
    assert response.get_json()["error"] == "Tarea no encontrada"


def test_delete_task_removes_task(client):
    created = client.post("/tasks", json={"title": "Eliminar", "description": "Temporal"}).get_json()

    delete_response = client.delete(f"/tasks/{created['id']}")
    get_response = client.get(f"/tasks/{created['id']}")

    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == "Tarea eliminada"
    assert get_response.status_code == 404


def test_delete_task_returns_404_when_not_found(client):
    response = client.delete("/tasks/9999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Tarea no encontrada"


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["database"] == "ok"


def test_metrics_endpoint_is_available(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.content_type
    assert "flask_exporter_info" in response.get_data(as_text=True)
