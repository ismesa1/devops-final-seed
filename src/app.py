import json
import logging
import os
import sqlite3
import sys
import time

from flask import Flask, g, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "tasks.db")
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        optional_fields = {
            "http_method": getattr(record, "http_method", None),
            "path": getattr(record, "path", None),
            "status_code": getattr(record, "status_code", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "task_id": getattr(record, "task_id", None),
        }

        for key, value in optional_fields.items():
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)


def configure_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)


configure_logging()
logger = logging.getLogger("todo_api")
metrics = PrometheusMetrics(app)
metrics.info("app_info", "Application info", version=APP_VERSION)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


@app.before_request
def on_request_start():
    g.started_at = time.perf_counter()


@app.after_request
def on_request_end(response):
    elapsed_ms = round((time.perf_counter() - g.started_at) * 1000, 2)
    logger.info(
        "http_request",
        extra={
            "http_method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": elapsed_ms,
        },
    )
    return response


@app.route("/", methods=["GET"])
def index():
    return jsonify({"name": "To-Do API", "version": APP_VERSION, "endpoints": ["/tasks"]})


@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        return jsonify({"status": "ok", "database": "ok", "version": APP_VERSION}), 200
    except sqlite3.Error:
        logger.exception("healthcheck_failed")
        return jsonify({"status": "error", "database": "error", "version": APP_VERSION}), 503


@app.route("/tasks", methods=["GET"])
def list_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(t) for t in tasks])


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    if not data or "title" not in data:
        return jsonify({"error": "El campo 'title' es obligatorio"}), 400

    title = data["title"]
    description = data.get("description", "")

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (title, description),
    )
    task_id = cursor.lastrowid
    conn.commit()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    logger.info("task_created", extra={"task_id": task_id})
    return jsonify(dict(task)), 201


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify(dict(task))


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Tarea no encontrada"}), 404

    title = data.get("title", task["title"])
    description = data.get("description", task["description"])
    completed = data.get("completed", task["completed"])

    conn.execute(
        "UPDATE tasks SET title=?, description=?, completed=? WHERE id=?",
        (title, description, completed, task_id),
    )
    conn.commit()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    logger.info("task_updated", extra={"task_id": task_id})
    return jsonify(dict(task))


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Tarea no encontrada"}), 404

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    logger.info("task_deleted", extra={"task_id": task_id})
    return jsonify({"message": "Tarea eliminada"}), 200


if __name__ == "__main__":  # pragma: no cover
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port)
