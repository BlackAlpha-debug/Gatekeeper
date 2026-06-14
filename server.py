"""GateKeeper — run with: python server.py"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

from fastmcp import FastMCP
from dotenv import load_dotenv
from core.config_loader import load_config
from core.governance.audit import AuditLogger
from core.governance.validator import QueryValidator
from core.governance.masker import DataMasker

load_dotenv(os.path.join(BASE_DIR, ".env"))

config       = load_config(os.path.join(BASE_DIR, "config.yaml"))
databases    = config["databases"]
api_connectors = config["apis"]
audit        = AuditLogger(log_db_path=os.path.join(BASE_DIR, "data", "audit.db"))
validator    = QueryValidator(allow_writes=config["allow_writes"])
masker       = DataMasker(extra_columns=config["mask_extra_columns"])

mcp = FastMCP("GateKeeper")


@mcp.tool()
def list_databases() -> dict:
    """List all configured databases and their connection status."""
    try:
        return {"databases": [
            {"name": name, "connected": db.test_connection()}
            for name, db in databases.items()
        ]}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_schema(database_name: str) -> dict:
    """Return the table/column schema for a connected database."""
    try:
        if database_name not in databases:
            return {"error": f"Unknown db '{database_name}'. Available: {list(databases)}"}
        return {"schema": databases[database_name].get_schema()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def query_database(database_name: str, sql: str) -> dict:
    """
    Execute a SQL query with safety checks, audit logging,
    and automatic sensitive-column masking.
    """
    try:
        if database_name not in databases:
            return {"error": f"Unknown db '{database_name}'. Available: {list(databases)}"}

        is_valid, reason = validator.validate(sql)
        if not is_valid:
            audit.log(database_name, sql, row_count=0, blocked=True)
            return {"error": reason, "blocked": True}

        results = databases[database_name].execute(sql)
        safe    = masker.mask(results)
        audit.log(database_name, sql, row_count=len(safe))
        return {"rows": safe, "count": len(safe)}

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_audit_history(limit: int = 20) -> dict:
    """Return recent query audit log entries."""
    try:
        return {"history": audit.get_history(limit)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_api_connectors() -> dict:
    """List all configured API connectors."""
    try:
        return {"connectors": list(api_connectors.keys())}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_api_operations(connector_name: str) -> dict:
    """List all available operations for a given API connector."""
    try:
        if connector_name not in api_connectors:
            return {"error": f"Unknown connector '{connector_name}'"}
        return {"operations": api_connectors[connector_name].list_operations()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def call_api(connector_name: str, operation: str, params: dict = {}) -> dict:
    """Call an operation on a registered API connector."""
    try:
        if connector_name not in api_connectors:
            return {"error": f"Unknown connector '{connector_name}'"}
        result = api_connectors[connector_name].call(operation, params)
        audit.log(f"api:{connector_name}", operation, row_count=0)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def cross_source_query(plan: list) -> dict:
    """
    Execute a multi-step query across databases and APIs.
    plan = [
      {"step": 1, "source": "local", "sql": "SELECT id FROM users LIMIT 5"},
      {"step": 2, "source": "github", "operation": "getUser", "params": {}}
    ]
    """
    try:
        results = {}
        for step in plan:
            key    = f"step_{step.get('step', '?')}"
            source = step.get("source", "")

            if source in databases:
                sql = step.get("sql", "")
                is_valid, reason = validator.validate(sql)
                if not is_valid:
                    results[key] = {"error": reason, "blocked": True}
                    continue
                results[key] = masker.mask(databases[source].execute(sql))

            elif source in api_connectors:
                results[key] = api_connectors[source].call(
                    step.get("operation", ""),
                    step.get("params", {}),
                )
            else:
                results[key] = {"error": f"Unknown source '{source}'"}

        audit.log("cross_source", str(plan), row_count=0)
        return results
    except Exception as e:
        return {"error": str(e)}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
