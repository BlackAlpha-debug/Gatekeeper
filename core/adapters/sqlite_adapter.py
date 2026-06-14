import sqlite3
from .base import DatabaseAdapter


class SQLiteAdapter(DatabaseAdapter):

    def __init__(self, path: str):
        self.path = path

    def execute(self, sql: str) -> list[dict]:
        conn = sqlite3.connect(self.path)
        try:
            cursor = conn.execute(sql)
            if cursor.description is None:
                return []
            columns = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()

    def get_schema(self) -> dict:
        conn = sqlite3.connect(self.path)
        try:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            schema = {}
            for (table,) in tables:
                cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
                schema[table] = [col[1] for col in cols]
            return schema
        finally:
            conn.close()

    def test_connection(self) -> bool:
        try:
            conn = sqlite3.connect(self.path)
            conn.close()
            return True
        except Exception:
            return False
