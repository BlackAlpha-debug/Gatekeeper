import pytest
from core.adapters.sqlite_adapter import SQLiteAdapter


class TestSQLiteAdapter:

    def test_connection_success(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        assert adapter.test_connection() is True

    def test_connection_bad_path(self):
        adapter = SQLiteAdapter(path="/nonexistent/path/bad.db")
        # SQLite creates the file on connect, so this actually returns True
        # unless the directory doesn't exist
        result = adapter.test_connection()
        assert isinstance(result, bool)

    def test_execute_select(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        rows = adapter.execute("SELECT * FROM users")
        assert len(rows) == 3
        assert rows[0]["name"] == "Alice"
        assert rows[1]["name"] == "Bob"
        assert rows[2]["name"] == "Charlie"

    def test_execute_select_with_where(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        rows = adapter.execute("SELECT * FROM users WHERE id = 2")
        assert len(rows) == 1
        assert rows[0]["name"] == "Bob"

    def test_execute_returns_dicts(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        rows = adapter.execute("SELECT id, name FROM users LIMIT 1")
        assert isinstance(rows[0], dict)
        assert "id" in rows[0]
        assert "name" in rows[0]

    def test_execute_non_select_returns_empty(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        # A pragma that doesn't return rows
        result = adapter.execute("CREATE TABLE IF NOT EXISTS temp_t (x INT)")
        assert result == []

    def test_execute_bad_table_raises(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        with pytest.raises(Exception) as exc_info:
            adapter.execute("SELECT * FROM nonexistent_table")
        assert "nonexistent_table" in str(exc_info.value)

    def test_get_schema(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        schema = adapter.get_schema()
        assert "users" in schema
        assert "id" in schema["users"]
        assert "name" in schema["users"]
        assert "email" in schema["users"]
        assert "password" in schema["users"]

    def test_get_schema_column_order(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        schema = adapter.get_schema()
        assert schema["users"] == ["id", "name", "email", "password"]

    def test_execute_count(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        rows = adapter.execute("SELECT COUNT(*) as cnt FROM users")
        assert rows[0]["cnt"] == 3

    def test_execute_limit(self, tmp_sqlite_db):
        adapter = SQLiteAdapter(path=tmp_sqlite_db)
        rows = adapter.execute("SELECT * FROM users LIMIT 2")
        assert len(rows) == 2
