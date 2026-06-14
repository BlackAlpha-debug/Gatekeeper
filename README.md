<p align="center">
  <h1 align="center">GateKeeper</h1>
  <p align="center">
    <strong>MCP Governance Suite</strong>
  </p>
  <p align="center">
    A lightweight, enterprise-grade governance layer that sits between AI agents and your databases — validating queries, masking sensitive data, and logging every interaction before it ever touches production.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastMCP-3.4-green?style=flat-square" alt="FastMCP">
  <img src="https://img.shields.io/badge/databases-SQLite%20%7C%20PostgreSQL-orange?style=flat-square" alt="Databases">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/tests-66%20passed-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/status-production--ready-brightgreen?style=flat-square" alt="Status">
</p>

---

## The Problem

AI agents like Claude can now execute SQL queries directly against your databases through the Model Context Protocol (MCP). But with great power comes great risk:

- What stops an AI from running `DROP TABLE users`?
- Who ensures passwords and emails aren't leaked in query results?
- How do you audit every query an AI agent makes against your data?

**GateKeeper solves all three.** It acts as a governance middleware — every query passes through validation, masking, and audit logging before results are returned. Your data stays safe, your compliance stays intact, and you have a full paper trail of every interaction.

---

## Core Features

- **Query Validation** — Blocks destructive operations (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`) and SQL injection patterns using word-boundary regex that won't false-positive on column names like `created_at`
- **Automatic Data Masking** — Detects and redacts sensitive columns (`password`, `email`, `ssn`, `token`, `credit_card`) in query results before they reach the AI agent
- **Complete Audit Trail** — Every query is logged to a dedicated audit database with timestamp, source, row count, and blocked status
- **Multi-Database Support** — Seamlessly switch between SQLite (local/testing) and PostgreSQL (production) through the adapter pattern
- **OpenAPI Auto-Discovery** — Point it at any OpenAPI spec URL and it auto-generates callable tools — no manual endpoint setup
- **Cross-Source Queries** — Execute multi-step query plans spanning databases and APIs in a single request, with partial failure handling

---

## Architecture & Tech Stack

```
                    Claude Desktop
                         |
                    [MCP Protocol]
                         |
                   +-----+-----+
                   | GateKeeper |
                   |  server.py |
                   +-----+-----+
                         |
          +--------------+--------------+
          |              |              |
    [Validator]    [Data Masker]   [Audit Logger]
          |              |              |
          +--------------+--------------+
                         |
              +----------+----------+
              |                     |
      [SQLite Adapter]    [PostgreSQL Adapter]
              |                     |
         local.db            Supabase Cloud
```

| Layer | Technology | Why |
|-------|-----------|-----|
| **Server Framework** | FastMCP 3.4 | Native MCP protocol support with tool registration |
| **Language** | Python 3.11+ | Rich ecosystem for database drivers and API clients |
| **Local Database** | SQLite | Zero-config testing and audit log storage |
| **Production Database** | PostgreSQL (Supabase) | Scalable cloud database with connection pooling |
| **Configuration** | YAML + dotenv | Separation of structure (config.yaml) from secrets (.env) |
| **Design Patterns** | Adapter Pattern, Abstract Base Classes | Database-agnostic query execution — swap backends without touching business logic |

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/BlackAlpha-debug/Gatekeeper.git
cd Gatekeeper

# Set up the virtual environment
python -m venv env
.\env\Scripts\Activate.ps1       # Windows
# source env/bin/activate        # macOS/Linux

# Install dependencies
pip install -e .

# Configure the environment
cp .env.example .env             # Add your database credentials
cp config.example.yaml config.yaml  # Configure databases & APIs

# Run the server
python server.py
```

### Connect to Claude Desktop

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gatekeeper": {
      "command": "path/to/env/Scripts/python.exe",
      "args": ["path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop. A green badge in **Settings > Developer** confirms the server is running.

---

## MCP Tools

GateKeeper exposes **8 tools** to Claude through MCP:

| Tool | Description |
|------|-------------|
| `list_databases` | List all configured databases with live connection status |
| `get_schema` | Inspect table and column structure for any connected database |
| `query_database` | Execute SQL with full governance pipeline (validate > execute > mask > audit) |
| `get_audit_history` | Retrieve the audit log — see every query, who ran it, and whether it was blocked |
| `list_api_connectors` | List all registered OpenAPI connectors |
| `list_api_operations` | Discover available operations on any API connector |
| `call_api` | Execute an API operation with automatic audit logging |
| `cross_source_query` | Run multi-step query plans across databases and APIs in one call |

---

## Usage Examples

### Governance in Action

```python
from core.governance.validator import QueryValidator
from core.governance.masker import DataMasker

validator = QueryValidator(allow_writes=False)
masker = DataMasker()

# Safe query passes validation
validator.validate("SELECT * FROM users")
# => (True, "OK")

# Dangerous query is blocked
validator.validate("DROP TABLE users")
# => (False, "Write operation 'DROP' is blocked. Server is in read-only mode.")

# Sensitive columns are automatically masked
rows = [{"id": 1, "name": "Alice", "email": "alice@test.com", "password": "secret123"}]
masker.mask(rows)
# => [{"id": 1, "name": "Alice", "email": "***MASKED***", "password": "***MASKED***"}]
```

### Database Adapter Pattern

```python
from core.adapters.sqlite_adapter import SQLiteAdapter
from core.adapters.postgres_adapter import PostgreSQLAdapter

# Same interface, different backends
local = SQLiteAdapter(path="./data/local.db")
prod = PostgreSQLAdapter(host="db.xxx.supabase.co", port=5432,
                         user="postgres", password="***", dbname="postgres")

# Both respond to the same methods
local.test_connection()   # => True
local.get_schema()        # => {"users": ["id", "name", "email", "password"]}
local.execute("SELECT * FROM users LIMIT 3")
```

### Cross-Source Query

```python
# Query your database AND an API in a single request
plan = [
    {"step": 1, "source": "local", "sql": "SELECT id, name FROM users LIMIT 3"},
    {"step": 2, "source": "petstore", "operation": "getInventory", "params": {}},
]

# Results from both steps, with governance applied to database results
# If step 1 fails, step 2 still executes (partial failure handling)
```

---

## Configuration

### config.yaml

```yaml
databases:
  - name: local
    type: sqlite
    path: ./data/local.db

  - name: production
    type: postgresql
    host_env: PGHOST        # References env var name, not the value
    port_env: PGPORT
    user_env: PGUSER
    password_env: PGPASSWORD
    dbname_env: PGDATABASE

apis:
  - name: petstore
    spec_url: https://petstore3.swagger.io/api/v3/openapi.json
    base_url: https://petstore3.swagger.io/api/v3

allow_writes: false          # Set to true to allow INSERT/UPDATE/DELETE
mask_extra_columns: []       # Add custom column names to mask
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

> **Security Note:** Database credentials are referenced by env var *name* in `config.yaml`, never by value. Passwords never appear in config files, logs, or audit trails.

---

## Testing

GateKeeper has a comprehensive test suite with **66 tests** covering every governance component:

```bash
# Run the full suite
python -m pytest tests -v
```

```
tests/test_validator.py      17 passed   — keyword blocking, word-boundary safety, injection patterns, write mode
tests/test_masker.py         14 passed   — all sensitive patterns, extra columns, mutation safety, edge cases
tests/test_audit.py           8 passed   — logging, retrieval, ordering, limits, timestamps, auto-increment
tests/test_sqlite_adapter.py 11 passed   — connection, queries, schema, error handling, dict format
tests/test_config_loader.py   7 passed   — env vars, missing config, type validation, end-to-end loading

66 passed in 1.70s
```

| Module | Tests | What's Verified |
|--------|-------|-----------------|
| **Validator** | 17 | All 7 blocked keywords, word-boundary regex (`created_at` not blocked), case insensitivity, 5 SQL injection patterns, write mode toggle |
| **Masker** | 14 | password, email, ssn, credit_card, api_key, token, phone, dob detection, custom extra columns, original data immutability |
| **Audit Logger** | 8 | DB auto-creation, log/retrieve cycle, blocked flag, DESC ordering, limit enforcement, timestamp presence |
| **SQLite Adapter** | 11 | Connection, SELECT/WHERE/COUNT/LIMIT, dict output format, non-SELECT returns empty, bad table raises, schema extraction |
| **Config Loader** | 7 | Env var validation (missing/empty), missing config error, SQLite/unknown type handling, flag passthrough, end-to-end wiring |

---

## Project Structure

```
GateKeeper/
├── server.py                   # MCP server entry point (8 tools)
├── pyproject.toml              # Package metadata & dependencies
├── config.example.yaml         # Configuration template
├── .env.example                # Credentials template
├── README.md
│
├── core/
│   ├── config_loader.py        # YAML config parser & adapter builder
│   ├── adapters/
│   │   ├── base.py             # Abstract DatabaseAdapter interface
│   │   ├── sqlite_adapter.py   # SQLite implementation
│   │   └── postgres_adapter.py # PostgreSQL implementation
│   ├── governance/
│   │   ├── validator.py        # Query validation & SQL injection blocking
│   │   ├── masker.py           # Sensitive column auto-detection & redaction
│   │   └── audit.py            # Query audit logging to SQLite
│   └── api/
│       └── connector.py        # OpenAPI spec parser & HTTP caller
│
├── tests/
│   ├── conftest.py             # Shared fixtures (temp DBs, sample data)
│   ├── test_validator.py       # 17 tests — query validation & injection blocking
│   ├── test_masker.py          # 14 tests — sensitive column masking
│   ├── test_audit.py           #  8 tests — audit logging & retrieval
│   ├── test_sqlite_adapter.py  # 11 tests — SQLite adapter operations
│   └── test_config_loader.py   #  7 tests — config loading & env vars
│
└── data/
    ├── local.db                # SQLite test database
    └── audit.db                # Audit log database (auto-created)
```

---

## Roadmap

- [ ] Role-based access control (RBAC) — different masking rules per user role
- [ ] Async database connections for improved throughput
- [ ] Advanced regex-based masking strategies (partial redaction, tokenization)
- [ ] Real-time audit dashboard with query analytics
- [ ] Rate limiting per database to prevent query floods
- [ ] Support for MySQL and MongoDB adapters
- [ ] GitHub Actions CI/CD pipeline with automated governance tests

---

## License

MIT

---

<p align="center">
  Built with Python, FastMCP, and a healthy distrust of unvalidated SQL.
</p>
