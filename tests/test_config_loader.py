import os
import pytest
import yaml
from core.config_loader import load_config, _require_env
from core.adapters.sqlite_adapter import SQLiteAdapter


class TestRequireEnv:

    def test_existing_var(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "hello")
        assert _require_env("TEST_VAR") == "hello"

    def test_missing_var_raises(self, monkeypatch):
        monkeypatch.delenv("TEST_VAR", raising=False)
        with pytest.raises(EnvironmentError) as exc_info:
            _require_env("TEST_VAR")
        assert "TEST_VAR" in str(exc_info.value)

    def test_empty_var_raises(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "")
        with pytest.raises(EnvironmentError):
            _require_env("TEST_VAR")


class TestLoadConfig:

    def test_missing_config_file(self, tmp_path):
        with pytest.raises(FileNotFoundError) as exc_info:
            load_config(str(tmp_path / "nonexistent.yaml"))
        assert "not found" in str(exc_info.value)

    def test_sqlite_only_config(self, tmp_path, tmp_sqlite_db):
        config_data = {
            "databases": [
                {"name": "testdb", "type": "sqlite", "path": tmp_sqlite_db}
            ],
            "apis": [],
            "allow_writes": False,
            "mask_extra_columns": [],
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        result = load_config(str(config_file))

        assert "testdb" in result["databases"]
        assert isinstance(result["databases"]["testdb"], SQLiteAdapter)
        assert result["allow_writes"] is False
        assert result["mask_extra_columns"] == []
        assert result["apis"] == {}

    def test_allow_writes_flag(self, tmp_path, tmp_sqlite_db):
        config_data = {
            "databases": [
                {"name": "db", "type": "sqlite", "path": tmp_sqlite_db}
            ],
            "apis": [],
            "allow_writes": True,
            "mask_extra_columns": ["salary"],
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        result = load_config(str(config_file))
        assert result["allow_writes"] is True
        assert result["mask_extra_columns"] == ["salary"]

    def test_unknown_db_type_raises(self, tmp_path):
        config_data = {
            "databases": [
                {"name": "bad", "type": "mongodb", "path": "x"}
            ],
            "apis": [],
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ValueError) as exc_info:
            load_config(str(config_file))
        assert "mongodb" in str(exc_info.value)

    def test_empty_databases_ok(self, tmp_path):
        config_data = {"databases": [], "apis": []}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        result = load_config(str(config_file))
        assert result["databases"] == {}

    def test_sqlite_adapter_works_from_config(self, tmp_path, tmp_sqlite_db):
        config_data = {
            "databases": [
                {"name": "local", "type": "sqlite", "path": tmp_sqlite_db}
            ],
            "apis": [],
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        result = load_config(str(config_file))
        db = result["databases"]["local"]
        assert db.test_connection() is True
        rows = db.execute("SELECT * FROM users")
        assert len(rows) == 3
