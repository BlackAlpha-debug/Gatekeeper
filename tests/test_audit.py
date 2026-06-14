import pytest
from core.governance.audit import AuditLogger


class TestAuditLogger:

    def test_creates_db_on_init(self, tmp_audit_db):
        logger = AuditLogger(log_db_path=tmp_audit_db)
        import os
        assert os.path.exists(tmp_audit_db)

    def test_log_and_retrieve(self, tmp_audit_db):
        logger = AuditLogger(log_db_path=tmp_audit_db)
        logger.log("testdb", "SELECT * FROM users", row_count=3)
        history = logger.get_history(limit=10)
        assert len(history) == 1
        assert history[0]["database"] == "testdb"
        assert history[0]["sql"] == "SELECT * FROM users"
        assert history[0]["row_count"] == 3
        assert history[0]["blocked"] == 0

    def test_blocked_flag(self, tmp_audit_db):
        logger = AuditLogger(log_db_path=tmp_audit_db)
        logger.log("testdb", "DROP TABLE users", row_count=0, blocked=True)
        history = logger.get_history(limit=10)
        assert history[0]["blocked"] == 1

    def test_multiple_entries_ordered_desc(self, tmp_audit_db):
        logger = AuditLogger(log_db_path=tmp_audit_db)
        logger.log("db1", "SELECT 1", row_count=1)
        logger.log("db2", "SELECT 2", row_count=2)
        logger.log("db3", "SELECT 3", row_count=3)
        history = logger.get_history(limit=10)
        assert len(history) == 3
        # Most recent first
        assert history[0]["database"] == "db3"
        assert history[2]["database"] == "db1"

    def test_limit_respected(self, tmp_audit_db):
        logger = AuditLogger(log_db_path=tmp_audit_db)
        for i in range(10):
            logger.log("db", f"SELECT {i}", row_count=i)
        history = logger.get_history(limit=3)
        assert len(history) == 3

    def test_empty_history(self, tmp_audit_db):
        logger = AuditLogger(log_db_path=tmp_audit_db)
        history = logger.get_history()
        assert history == []

    def test_timestamp_is_present(self, tmp_audit_db):
        logger = AuditLogger(log_db_path=tmp_audit_db)
        logger.log("db", "SELECT 1", row_count=1)
        history = logger.get_history(limit=1)
        assert "timestamp" in history[0]
        assert len(history[0]["timestamp"]) > 0

    def test_id_auto_increments(self, tmp_audit_db):
        logger = AuditLogger(log_db_path=tmp_audit_db)
        logger.log("db", "Q1", row_count=0)
        logger.log("db", "Q2", row_count=0)
        history = logger.get_history(limit=10)
        ids = [h["id"] for h in history]
        assert 1 in ids
        assert 2 in ids
