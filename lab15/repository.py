from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import json
from matrix import Matrix
from memento import SessionSnapshot


class SessionRepository(ABC):
    @abstractmethod
    def save(self, name, snapshot):
        pass

    @abstractmethod
    def list_all(self):
        pass

    @abstractmethod
    def get(self, session_id):
        pass

    @abstractmethod
    def delete(self, session_id):
        pass


class SqliteSessionRepository(SessionRepository):
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, data TEXT NOT NULL)""")

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def save(self, name, snapshot):
        if not name.strip():
            raise ValueError("Введите название сеанса.")
        data = {"a": snapshot.a_text, "b": snapshot.b_text,
                "operation": snapshot.operation,
                "scalar": snapshot.scalar_text, "result": snapshot.result}
        text = json.dumps(data, ensure_ascii=False, allow_nan=False)
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO sessions(name, data) VALUES (?, ?)",
                (name.strip(), text))
            return cursor.lastrowid

    def list_all(self):
        with self.connect() as connection:
            return connection.execute(
                "SELECT id, name FROM sessions ORDER BY id").fetchall()

    def get(self, session_id):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT data FROM sessions WHERE id = ?",
                (session_id,)).fetchone()
        if row is None:
            raise ValueError("Сеанс не найден.")
        try:
            data = json.loads(row[0])
            values = [data[key] for key in ("a", "b", "operation", "scalar")]
            if any(not isinstance(value, str) for value in values):
                raise ValueError("Поля сеанса должны быть строками.")
            result = data["result"]
            if result is not None:
                matrix = Matrix(result)
                result = tuple(tuple(row) for row in matrix.data)
            return SessionSnapshot(*values, result)
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError("Неверные данные сохранённого сеанса.") from error

    def delete(self, session_id):
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0
