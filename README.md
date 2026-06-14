# GateKeeper

Enterprise governance layer for MCP database and API access.

## Features
- **Query Validation** — blocks DROP, DELETE, INSERT, UPDATE and SQL injection patterns
- **Data Masking** — auto-hides sensitive columns (password, email, SSN, tokens)
- **Audit Logging** — every query logged with timestamp and blocked status
- **Multi-Database** — SQLite and PostgreSQL via adapter pattern
- **OpenAPI Connector** — auto-generates tools from any OpenAPI spec
- **Cross-Source Queries** — query databases and APIs in a single request

## Quick Start

```bash
# Clone and enter
git clone <your-repo-url>
cd MCP-Governance-Suite

# Set up Python environment
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install
pip install -e .

# Configure
cp .env.example .env           # fill in your database credentials
cp config.example.yaml config.yaml  # configure databases and APIs

# Run
python server.py
```

## Claude Desktop Setup

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gatekeeper": {
      "command": "/path/to/env/bin/python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop. The server starts automatically.

## MCP Tools

| Tool | Description |
|------|-------------|
| `list_databases` | List configured databases with connection status |
| `get_schema` | Return table/column schema for a database |
| `query_database` | Execute SQL with validation, masking, and audit |
| `get_audit_history` | View recent query log entries |
| `list_api_connectors` | List configured API connectors |
| `list_api_operations` | List operations for an API connector |
| `call_api` | Call an API operation |
| `cross_source_query` | Multi-step query across databases and APIs |

## Configuration

### config.yaml

```yaml
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

apis:
  - name: petstore
    spec_url: https://petstore3.swagger.io/api/v3/openapi.json
    base_url: https://petstore3.swagger.io/api/v3

allow_writes: false
mask_extra_columns: []
```

### .env

```
PGHOST=db.xxxx.supabase.co
PGPORT=5432
PGUSER=postgres
PGPASSWORD=your-password
PGDATABASE=postgres
GITHUB_TOKEN=
```

## License

MIT
