import pytest
from core.governance.validator import QueryValidator


class TestReadOnlyMode:
    """Validator with allow_writes=False (default)."""

    def setup_method(self):
        self.v = QueryValidator(allow_writes=False)

    def test_select_allowed(self):
        ok, msg = self.v.validate("SELECT * FROM users")
        assert ok is True
        assert msg == "OK"

    def test_select_with_where_allowed(self):
        ok, msg = self.v.validate("SELECT name FROM users WHERE id = 1")
        assert ok is True

    def test_drop_blocked(self):
        ok, msg = self.v.validate("DROP TABLE users")
        assert ok is False
        assert "DROP" in msg

    def test_delete_blocked(self):
        ok, msg = self.v.validate("DELETE FROM users WHERE id = 1")
        assert ok is False
        assert "DELETE" in msg

    def test_insert_blocked(self):
        ok, msg = self.v.validate("INSERT INTO users VALUES (4, 'Dave', 'dave@test.com', 'pw')")
        assert ok is False
        assert "INSERT" in msg

    def test_update_blocked(self):
        ok, msg = self.v.validate("UPDATE users SET name = 'X' WHERE id = 1")
        assert ok is False
        assert "UPDATE" in msg

    def test_truncate_blocked(self):
        ok, msg = self.v.validate("TRUNCATE TABLE users")
        assert ok is False
        assert "TRUNCATE" in msg

    def test_alter_blocked(self):
        ok, msg = self.v.validate("ALTER TABLE users ADD COLUMN age INTEGER")
        assert ok is False
        assert "ALTER" in msg

    def test_create_blocked(self):
        ok, msg = self.v.validate("CREATE TABLE evil (id INTEGER)")
        assert ok is False
        assert "CREATE" in msg

    def test_created_at_not_blocked(self):
        """'CREATE' inside 'created_at' must NOT trigger the block."""
        ok, msg = self.v.validate("SELECT created_at FROM logs")
        assert ok is True
        assert msg == "OK"

    def test_updated_at_not_blocked(self):
        """'UPDATE' inside 'updated_at' must NOT trigger the block."""
        ok, msg = self.v.validate("SELECT updated_at FROM records")
        assert ok is True
        assert msg == "OK"

    def test_case_insensitive(self):
        ok, msg = self.v.validate("drop table users")
        assert ok is False
        assert "DROP" in msg

    def test_lowercase_select(self):
        ok, msg = self.v.validate("select * from users")
        assert ok is True


class TestDangerousPatterns:
    """SQL injection pattern detection."""

    def setup_method(self):
        self.v = QueryValidator()

    def test_double_dash_comment(self):
        ok, msg = self.v.validate("SELECT * FROM users -- a comment")
        assert ok is False
        assert "Dangerous" in msg

    def test_semicolon_dash(self):
        ok, msg = self.v.validate("SELECT 1;-- injection")
        assert ok is False

    def test_block_comment_open(self):
        ok, msg = self.v.validate("SELECT /* malicious */ * FROM users")
        assert ok is False

    def test_block_comment_close(self):
        ok, msg = self.v.validate("SELECT */ FROM users")
        assert ok is False

    def test_xp_underscore(self):
        ok, msg = self.v.validate("EXEC xp_cmdshell 'dir'")
        assert ok is False

    def test_clean_query_no_patterns(self):
        ok, msg = self.v.validate("SELECT id, name FROM users WHERE id > 0")
        assert ok is True


class TestWriteMode:
    """Validator with allow_writes=True."""

    def setup_method(self):
        self.v = QueryValidator(allow_writes=True)

    def test_insert_allowed(self):
        ok, msg = self.v.validate("INSERT INTO users VALUES (4, 'Dave', 'd@t.com', 'pw')")
        assert ok is True

    def test_update_allowed(self):
        ok, msg = self.v.validate("UPDATE users SET name = 'X'")
        assert ok is True

    def test_drop_allowed(self):
        ok, msg = self.v.validate("DROP TABLE users")
        assert ok is True

    def test_injection_still_blocked(self):
        """Dangerous patterns are blocked even in write mode."""
        ok, msg = self.v.validate("SELECT * FROM users -- comment")
        assert ok is False
        assert "Dangerous" in msg
