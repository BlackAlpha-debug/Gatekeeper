import os
import sys
import sqlite3
import tempfile

import pytest

# Ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


@pytest.fixture
def tmp_sqlite_db(tmp_path):
    """Create a temporary SQLite database with a users table."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE users "
        "(id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)"
    )
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@test.com', 'secret123')")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@test.com', 'hunter2')")
    conn.execute("INSERT INTO users VALUES (3, 'Charlie', 'charlie@test.com', 'pass789')")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def tmp_audit_db(tmp_path):
    """Return a path for a temporary audit database."""
    return str(tmp_path / "audit.db")


@pytest.fixture
def sample_rows():
    """Sample user rows for masker tests."""
    return [
        {"id": 1, "name": "Alice", "email": "alice@test.com", "password": "secret123"},
        {"id": 2, "name": "Bob", "email": "bob@test.com", "password": "hunter2"},
        {"id": 3, "name": "Charlie", "email": "charlie@test.com", "password": "pass789"},
    ]
