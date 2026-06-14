"""
Loads config.yaml and builds the database + API connector registries.

config.yaml shape:
  databases:
    - name: local
      type: sqlite
      path: ./data/local.db
    - name: production
      type: postgresql
      host_env: PGHOST
      port_env: PGPORT
      user_env: PGUSER
      password_env: PGPASSWORD
      dbname_env: PGDATABASE

  allow_writes: false
  mask_extra_columns: []
"""

import os
import yaml
from core.adapters.sqlite_adapter import SQLiteAdapter
from core.adapters.postgres_adapter import PostgreSQLAdapter
from core.api.connector import OpenAPIConnector


def _require_env(var_name: str) -> str:
    """Read an env var or raise a clear error — never silently empty."""
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(
            f"Required env var '{var_name}' is not set. Add it to your .env file."
        )
    return value


def load_config(config_path: str = "config.yaml") -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Config file not found at '{config_path}'. "
            "Copy config.example.yaml to config.yaml and fill it in."
        )

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    databases: dict = {}
    for db_conf in raw.get("databases", []):
        name = db_conf["name"]
        db_type = db_conf["type"].lower()

        if db_type == "sqlite":
            databases[name] = SQLiteAdapter(path=db_conf["path"])

        elif db_type == "postgresql":
            databases[name] = PostgreSQLAdapter(
                host=_require_env(db_conf["host_env"]),
                port=int(os.getenv(db_conf.get("port_env", "PGPORT"), "5432")),
                user=_require_env(db_conf["user_env"]),
                password=_require_env(db_conf["password_env"]),
                dbname=_require_env(db_conf["dbname_env"]),
            )
        else:
            raise ValueError(f"Unknown db type '{db_type}' for '{name}'")

    apis: dict = {}
    for api_conf in raw.get("apis", []):
        name = api_conf["name"]
        api_key = None
        if "api_key_env" in api_conf:
            api_key = os.getenv(api_conf["api_key_env"])
        apis[name] = OpenAPIConnector(
            spec_url=api_conf["spec_url"],
            base_url=api_conf["base_url"],
            api_key=api_key,
        )

    return {
        "databases": databases,
        "apis": apis,
        "allow_writes": raw.get("allow_writes", False),
        "mask_extra_columns": raw.get("mask_extra_columns", []),
    }
