import psycopg2
from .base import DatabaseAdapter


class PostgreSQLAdapter(DatabaseAdapter):

    def __init__(self, host: str, port: int, user: str,
                 password: str, dbname: str):
        self._conn_params = {
            "host": host, "port": port, "user": user,
            "password": password, "dbname": dbname,
            "connect_timeout": 10,
        }

    def _connect(self):
        return psycopg2.connect(**self._conn_params)

    def execute(self, sql: str) -> list[dict]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            if cursor.description is None:
                return []
            columns = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()

    def get_schema(self) -> dict:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)
            schema: dict = {}
            for table, column in cursor.fetchall():
                schema.setdefault(table, []).append(column)
            return schema
        finally:
            conn.close()

    def test_connection(self) -> bool:
        try:
            conn = self._connect()
            conn.close()
            return True
        except Exception:
            return False
