import sqlite3
from datetime import datetime


class AuditLogger:

    def __init__(self, log_db_path: str = "data/audit.db"):
        self.db = log_db_path
        self._setup()

    def _setup(self):
        conn = sqlite3.connect(self.db)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT    NOT NULL,
                    database  TEXT    NOT NULL,
                    sql       TEXT    NOT NULL,
                    row_count INTEGER NOT NULL,
                    blocked   INTEGER NOT NULL DEFAULT 0
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def log(self, database: str, sql: str,
            row_count: int, blocked: bool = False):
        conn = sqlite3.connect(self.db)
        try:
            conn.execute(
                "INSERT INTO audit_log (timestamp,database,sql,row_count,blocked) "
                "VALUES (?,?,?,?,?)",
                (datetime.now().isoformat(), database, sql,
                 row_count, 1 if blocked else 0),
            )
            conn.commit()
        finally:
            conn.close()

    def get_history(self, limit: int = 50) -> list[dict]:
        conn = sqlite3.connect(self.db)
        try:
            cursor = conn.execute(
                "SELECT id,timestamp,database,sql,row_count,blocked "
                "FROM audit_log ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
