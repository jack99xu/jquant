# Phase 2: Query Layer + MCP Server - Research

**Researched:** 2026-03-22
**Domain:** FastMCP server over stdio + SQLite read-only queries
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Tool design:**
- 4 focused tools mapping to requirements MCP-01~04: `lookup_function`, `search_docs`, `list_by_section`, `search_in_section`
- 1 additional discovery tool: list all function names grouped by section (~221 names, low token cost)
- 1 table column tool: `lookup_table_columns(table_name)` — returns all columns for a given table
- Total: 6 tools (4 core doc tools + 1 discovery + 1 table columns)
- All-in-one responses: `lookup_function` returns full doc + all params + return attrs + example code in a single response
- Bilingual tool descriptions: tool names and descriptions include both English and Chinese keywords

**Response format:**
- Structured text format: clean labeled sections with markdown
- Search results: summary list — function_name + chinese_name + one-line description + section per result
- Not-found handling: explicit "not found" message + fuzzy suggestions of similar function names + alternative search terms
- Example code: include when available in DB, skip the section cleanly when NULL

**Data coverage:**
- Core exposure: api_docs + api_params + api_return_attrs
- Table columns: exposed via dedicated `lookup_table_columns` tool
- Strategies: skip for v1 (EXT-02 in v2 scope)
- Search scope: LIKE search across ALL text fields — function_name, chinese_name, description, call_signature

**Connection & config:**
- Database path: default to `jq_knowledge.db` in project directory, with `JQ_DB_PATH` env var override
- Startup validation: check DB exists, verify expected tables exist, warn (not fail) if any table has 0 rows
- Database access: read-only mode (MCP-06) — no mutations exposed
- Claude Desktop config: include a ready-to-paste `claude_desktop_config.json` snippet

### Claude's Discretion

- Exact query SQL construction and optimization
- Fuzzy matching algorithm for not-found suggestions
- Internal module structure (single file vs split)
- Logging approach and verbosity levels

### Deferred Ideas (OUT OF SCOPE)

- Strategy code lookup via MCP — v2 (EXT-02)
- Strategy search by keyword — v2 (EXT-02)
- Natural language strategy generation — v2 (GEN-01~03)
- Additional API section scraping beyond Stock — v2 (EXT-01)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MCP-01 | MCP tool for exact function name lookup returning full documentation | FastMCP `@mcp.tool` decorator + JOIN query across api_docs, api_params, api_return_attrs |
| MCP-02 | MCP tool for keyword search across all API docs | LIKE search on function_name, chinese_name, description, call_signature columns |
| MCP-03 | MCP tool for filtering docs by API category/section | WHERE section = ? query using idx_api_docs_section index |
| MCP-04 | MCP tool for section-scoped search (search within a specific section) | Combine LIKE pattern with section filter in single WHERE clause |
| MCP-05 | All responses structured, token-efficient, with clear not-found signals | Return type str from tool functions; format as labeled markdown sections |
| MCP-06 | Database opened read-only, no mutations exposed | `sqlite3.connect("file:path?mode=ro", uri=True)` — OperationalError on any write attempt |
</phase_requirements>

---

## Summary

Phase 2 builds a FastMCP server running over stdio that exposes the SQLite database created in Phase 1 to AI hosts. The core pattern is straightforward: FastMCP 3.1.1 uses Python decorators to register tools, each tool is a Python function that queries the read-only SQLite connection and returns a formatted string, and Claude Desktop spawns the process via `uv run`. No HTTP server, no auth, no async complexity — the phase is dominated by SQL query design and response formatting choices.

The database schema is fully settled from Phase 1 (5 tables, 5 indexes, 221 api_docs rows, 2479 table_columns rows). The planner can write SQL queries directly against known column names without any discovery work. The only discretionary decisions are: SQL construction for each of the 6 tools, the fuzzy-match algorithm for not-found suggestions, and whether to split the implementation into one file or two (query layer + server layer).

FastMCP's decorator-based API is stable and well-documented. The pattern is `@mcp.tool` on a plain Python function — FastMCP auto-generates the JSON schema from type annotations and docstrings. Read-only SQLite access is a one-liner using the URI API: `sqlite3.connect("file:path.db?mode=ro", uri=True)`. Claude Desktop connects via a known `claude_desktop_config.json` format using `uv --directory ... run server.py`.

**Primary recommendation:** Single `server.py` file is sufficient for 6 tools. Open DB connection once at module load with `mode=ro`. Return formatted strings from all tools — FastMCP converts str return to TextContent automatically.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastmcp | 3.1.1 | MCP server framework, tool registration, schema gen | Already in STACK.md; decorator API eliminates boilerplate; handles stdio transport automatically |
| sqlite3 | stdlib | Read-only database access | Built-in, zero deps, URI mode enables read-only enforcement |
| python-dotenv | 1.x | Load `JQ_DB_PATH` env var from `.env` | Already a project dependency; consistent with Phase 1 pattern |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib | stdlib | Resolve DB path relative to server.py location | Use for `Path(__file__).parent / "jq_knowledge.db"` default |
| os | stdlib | Read `JQ_DB_PATH` env var fallback | Use `os.environ.get("JQ_DB_PATH")` |
| logging | stdlib | Startup warnings for missing tables or 0-row tables | Use Python stdlib logging; write to stderr (FastMCP uses stdio for MCP protocol) |

### Alternatives NOT to Use

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| fastmcp 3.1.1 | Official mcp SDK 1.26.0 | Official SDK is lower-level; FastMCP already chosen in STACK.md |
| sqlite3 URI mode | `check_same_thread=False` only | URI mode provides OS-level read-only enforcement, not just Python-level |
| Formatted strings | JSON return | MCP clients handle plain text better for LLM consumption; JSON adds parsing overhead on the LLM side |

**Installation (fastmcp not yet in pyproject.toml):**
```bash
uv add fastmcp
```

---

## Architecture Patterns

### Recommended Project Structure

```
auto-jq-database/
├── server.py              # FastMCP server: tool definitions + startup
├── db/
│   ├── schema.py          # Existing — init_db() reusable for validation
│   ├── seed.py            # Existing — reference for column names
│   └── queries.py         # NEW: SQL query functions (optional split)
├── jq_knowledge.db        # Existing populated database
└── pyproject.toml         # Add fastmcp dependency
```

The planner may choose single-file (`server.py` contains both tools and queries) or two-file (query logic in `db/queries.py`). Both are valid; the two-file split is easier to test.

### Pattern 1: FastMCP Tool Definition

**What:** Register Python functions as MCP tools using `@mcp.tool` decorator with bilingual docstrings.
**When to use:** Every tool in this server.

```python
# Source: https://gofastmcp.com/servers/tools
from fastmcp import FastMCP

mcp = FastMCP("JoinQuant API Docs / 聚宽API文档")

@mcp.tool
def lookup_function(function_name: str) -> str:
    """Look up complete documentation for a JoinQuant API function by exact name.
    查询聚宽API函数的完整文档，包括参数列表、返回值和示例代码。

    Args:
        function_name: Exact function name (e.g. 'get_price', 'get_fundamentals')
    """
    # ... query DB, format response
    return formatted_string
```

### Pattern 2: Read-Only SQLite Connection at Module Load

**What:** Open the database once at import time in read-only mode; share across all tool calls.
**When to use:** MCP servers are single-process, single-threaded from stdio — one connection is correct.

```python
# Source: https://docs.python.org/3/library/sqlite3.html#sqlite3.connect
import sqlite3
import os
from pathlib import Path

_DEFAULT_DB = Path(__file__).parent / "jq_knowledge.db"
_DB_PATH = os.environ.get("JQ_DB_PATH", str(_DEFAULT_DB))

# Read-only: OS enforces no writes; raises OperationalError on any mutation attempt
conn = sqlite3.connect(f"file:{_DB_PATH}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row  # enables column name access: row["function_name"]
```

### Pattern 3: Startup Validation

**What:** Check DB exists and tables have data before accepting tool calls; warn, don't fail.
**When to use:** Server startup (module level or `lifespan` context if using FastMCP lifespan).

```python
import logging
import sys

logger = logging.getLogger(__name__)

def validate_db(conn: sqlite3.Connection) -> None:
    """Warn on empty tables; raise if DB is inaccessible."""
    expected_tables = ["api_docs", "api_params", "api_return_attrs", "table_columns"]
    for table in expected_tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if count == 0:
                logger.warning("Table %s has 0 rows — data may not be loaded", table)
        except sqlite3.OperationalError as e:
            logger.error("Table %s missing or inaccessible: %s", table, e)
```

### Pattern 4: Fuzzy Not-Found Suggestions

**What:** When exact lookup fails, return similar function names via LIKE prefix match.
**When to use:** `lookup_function` when exact match returns no rows.

```python
def _fuzzy_suggestions(conn, name: str, limit: int = 5) -> list[str]:
    """Return up to `limit` function names that share a prefix with `name`."""
    prefix = name[:4] if len(name) >= 4 else name
    rows = conn.execute(
        "SELECT function_name FROM api_docs WHERE function_name LIKE ? LIMIT ?",
        (f"{prefix}%", limit),
    ).fetchall()
    return [r["function_name"] for r in rows]
```

### Pattern 5: Claude Desktop Configuration

**What:** Ready-to-paste snippet users add to `~/Library/Application Support/Claude/claude_desktop_config.json`.
**When to use:** Include as a comment block or in project README; document in server.py header.

```json
{
  "mcpServers": {
    "jq-docs": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/auto-jq-database",
        "run",
        "server.py"
      ]
    }
  }
}
```

Note: `uv` must be the full path on some systems. User runs `which uv` to confirm.

### Anti-Patterns to Avoid

- **Opening a new DB connection per tool call:** Expensive and unnecessary. Open once at module level.
- **Using `conn.row_factory = None` and accessing rows by index:** Fragile — column order changes break queries. Always use `sqlite3.Row`.
- **Async tool functions without need:** FastMCP supports both sync and async. SQLite is synchronous; sync tool functions are simpler and correct here.
- **Raising bare Python exceptions from tools:** Use `raise ToolError("message")` from `fastmcp.exceptions` — these transmit cleanly to the LLM; raw exceptions may expose stack traces.
- **Writing to stderr with `print()`:** MCP stdio uses stdout for protocol. All logging must go to stderr via Python's `logging` module (default handler writes to stderr).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON schema for tool parameters | Manual schema dict | FastMCP `@mcp.tool` decorator | FastMCP generates from type annotations automatically |
| stdio transport framing | Custom stdin/stdout reader | `mcp.run(transport="stdio")` or just `mcp.run()` | MCP protocol framing is non-trivial; FastMCP handles it |
| Tool error serialization | Try/except + return error string | `raise ToolError("msg")` from fastmcp.exceptions | ToolError messages are transmitted correctly to LLM; strings returned from except blocks can confuse routing |
| Bilingual keyword matching | Custom tokenizer | SQL `LIKE '%term%'` across multiple columns | For 221 rows LIKE is instant; FTS5+jieba is overengineering (see Out of Scope in REQUIREMENTS.md) |

**Key insight:** FastMCP's value is eliminating all MCP protocol boilerplate. Every line of custom plumbing code is a mistake in this context.

---

## Common Pitfalls

### Pitfall 1: stdout Contamination

**What goes wrong:** Server appears to connect but tools return garbled/empty results.
**Why it happens:** `print()` statements write to stdout, corrupting the MCP protocol stream which Claude Desktop reads from the same stdout.
**How to avoid:** Replace every `print()` with `logging.getLogger(__name__).info()` or `logger.debug()`. Python's logging default handler writes to stderr.
**Warning signs:** Claude Desktop shows connection but tool calls fail silently or return JSON parse errors.

### Pitfall 2: SQLite URI Mode Not Enabled

**What goes wrong:** `sqlite3.connect("file:path.db?mode=ro")` opens the file in read-write mode and ignores the URI params.
**Why it happens:** The `uri=True` keyword argument is required — without it, the connection string is treated as a literal filename.
**How to avoid:** Always pass `uri=True` as a keyword argument alongside the URI-format path.
**Warning signs:** Writing to the "read-only" DB succeeds; or the file `file:path.db?mode=ro` is created as a new empty database file.

### Pitfall 3: DB Path Resolution at Import Time

**What goes wrong:** Server works when run from the project directory but fails when Claude Desktop spawns it from a different working directory.
**Why it happens:** `"jq_knowledge.db"` is relative to cwd, which is not guaranteed when Claude Desktop launches the process.
**How to avoid:** Always resolve the path relative to `__file__`: `Path(__file__).parent / "jq_knowledge.db"`.
**Warning signs:** "no such file or directory" errors only when launched via Claude Desktop, not from terminal.

### Pitfall 4: row_factory Not Set

**What goes wrong:** `row["function_name"]` raises `TypeError: tuple indices must be integers`.
**Why it happens:** Default sqlite3 rows are tuples; column name access requires `conn.row_factory = sqlite3.Row`.
**How to avoid:** Set `conn.row_factory = sqlite3.Row` immediately after opening the connection.

### Pitfall 5: Empty Result vs Not-Found Confusion

**What goes wrong:** Tool returns empty string or Python `None` when a function doesn't exist.
**Why it happens:** `fetchone()` returns `None` on no match; unhandled this becomes `NoneType` error or empty response.
**How to avoid:** Explicitly check `if row is None: return f"Function '{name}' not found. Did you mean: {suggestions}"`.
**Warning signs:** Success criteria #4 fails — querying nonexistent function returns empty or exception.

### Pitfall 6: fastmcp Not in pyproject.toml

**What goes wrong:** `uv run server.py` from Claude Desktop fails with `ModuleNotFoundError: No module named 'fastmcp'`.
**Why it happens:** fastmcp is not yet listed as a project dependency (pyproject.toml only has playwright, beautifulsoup4, etc.).
**How to avoid:** Run `uv add fastmcp` before implementing. This is a Wave 0 prerequisite.
**Warning signs:** Import error in Claude Desktop logs at `~/Library/Logs/Claude/mcp*.log`.

---

## Code Examples

Verified patterns from official sources:

### Full Tool Function with Not-Found Handling

```python
# Source: https://gofastmcp.com/servers/tools + https://docs.python.org/3/library/sqlite3.html
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
import sqlite3

mcp = FastMCP("JoinQuant API Docs / 聚宽API文档查询")

@mcp.tool
def lookup_function(function_name: str) -> str:
    """Look up full documentation for a JoinQuant API function.
    查询聚宽API函数的完整文档（参数、返回值、示例代码）。

    Args:
        function_name: Exact function name (e.g. 'get_price', 'get_fundamentals')
    """
    row = conn.execute(
        "SELECT * FROM api_docs WHERE function_name = ?",
        (function_name,)
    ).fetchone()

    if row is None:
        suggestions = _fuzzy_suggestions(conn, function_name)
        hint = f"\nSimilar functions: {', '.join(suggestions)}" if suggestions else ""
        return f"Function '{function_name}' not found.{hint}"

    params = conn.execute(
        "SELECT param_name, param_type, is_required, description FROM api_params WHERE function_name = ?",
        (function_name,)
    ).fetchall()

    return _format_function_doc(row, params)
```

### Read-Only Connection with Row Factory

```python
# Source: https://docs.python.org/3/library/sqlite3.html#sqlite3.connect
import sqlite3, os
from pathlib import Path

_DB_PATH = os.environ.get("JQ_DB_PATH") or str(Path(__file__).parent / "jq_knowledge.db")
conn = sqlite3.connect(f"file:{_DB_PATH}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
```

### Server Entrypoint

```python
# Source: https://modelcontextprotocol.io/quickstart/server (official MCP quickstart)
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### LIKE Search Across Multiple Columns

```python
# Source: https://www.sqlite.org/lang_expr.html (LIKE operator)
def search_docs(keyword: str) -> str:
    """Search API docs / 搜索API文档。Search by keyword (English or Chinese / 英文或中文)."""
    pattern = f"%{keyword}%"
    rows = conn.execute(
        """SELECT function_name, chinese_name, description, section
           FROM api_docs
           WHERE function_name LIKE ?
              OR chinese_name LIKE ?
              OR description LIKE ?
              OR call_signature LIKE ?
           LIMIT 20""",
        (pattern, pattern, pattern, pattern)
    ).fetchall()
    if not rows:
        return f"No results found for '{keyword}'."
    return _format_search_results(rows)
```

### Claude Desktop Config (macOS)

```json
{
  "mcpServers": {
    "jq-docs": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/USERNAME/Desktop/ai-project/auto-jq-database",
        "run",
        "server.py"
      ]
    }
  }
}
```

Config file location: `~/Library/Application Support/Claude/claude_desktop_config.json`

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual MCP protocol framing in Python | FastMCP `@mcp.tool` decorator | 2024-2025 | Eliminates ~200 lines of protocol boilerplate |
| `mcp.run()` defaults to stdio | Same — stdio is still the default for local servers | FastMCP 3.x | No change needed; `mcp.run()` without args uses stdio |
| Separate query/server files as "clean architecture" | Single `server.py` is acceptable for ≤10 tools | FastMCP community norm | Less overhead for small servers |

**Deprecated/outdated:**
- `mcp-server-sqlite` (PyPI): Official Anthropic SQLite MCP reference is archived/not maintained. Do not use.
- `from mcp.server.fastmcp import FastMCP`: This import path (from official MCP SDK) works but the standalone `fastmcp` package (`from fastmcp import FastMCP`) is the current standard for FastMCP 3.x.

---

## Open Questions

1. **`mcp.run()` vs `mcp.run(transport="stdio")` in FastMCP 3.1.1**
   - What we know: Official MCP quickstart uses `mcp.run(transport="stdio")` explicitly
   - What's unclear: Whether FastMCP 3.1.1 defaults to stdio when no transport given (the gofastmcp welcome page implies it does)
   - Recommendation: Use explicit `mcp.run(transport="stdio")` to be unambiguous — zero cost, eliminates any ambiguity

2. **ToolError import path in FastMCP 3.1.1**
   - What we know: `fastmcp.exceptions.ToolError` is documented in the tools page
   - What's unclear: Whether this is available in the exact 3.1.1 release or a later patch
   - Recommendation: Implement tools to return error strings as fallback if import fails; add a Wave 0 verification step

---

## Validation Architecture

> `nyquist_validation` is `true` in `.planning/config.json` — this section is required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already in `[dependency-groups] dev`) |
| Config file | `pyproject.toml` — `[tool.pytest.ini_options]` with `testpaths = ["tests"]`, `pythonpath = ["."]` |
| Quick run command | `uv run pytest tests/test_server.py -x` |
| Full suite command | `uv run pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MCP-01 | `lookup_function("get_price")` returns params + return attrs in one response | unit | `uv run pytest tests/test_server.py::test_lookup_function_returns_full_doc -x` | Wave 0 |
| MCP-01 | `lookup_function("nonexistent")` returns explicit not-found + suggestions | unit | `uv run pytest tests/test_server.py::test_lookup_function_not_found -x` | Wave 0 |
| MCP-02 | `search_docs("融资融券")` returns matching rows with all structured fields | unit | `uv run pytest tests/test_server.py::test_search_docs_chinese_keyword -x` | Wave 0 |
| MCP-02 | `search_docs("totally_absent_xyz")` returns explicit not-found message | unit | `uv run pytest tests/test_server.py::test_search_docs_no_results -x` | Wave 0 |
| MCP-03 | `list_by_section("获取股票数据")` returns only functions from that section | unit | `uv run pytest tests/test_server.py::test_list_by_section -x` | Wave 0 |
| MCP-04 | `search_in_section(keyword, section)` returns only results from that section | unit | `uv run pytest tests/test_server.py::test_search_in_section_scoped -x` | Wave 0 |
| MCP-05 | All tool outputs are non-empty strings with labeled sections | unit | `uv run pytest tests/test_server.py::test_response_format -x` | Wave 0 |
| MCP-06 | DB connection rejects any write operation | unit | `uv run pytest tests/test_server.py::test_db_read_only -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_server.py -x`
- **Per wave merge:** `uv run pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Test Strategy Notes

Tests for tool functions must use an in-memory database seeded with known fixture data — not the live `jq_knowledge.db`. The existing `conftest.py::db_conn` fixture (in-memory SQLite with schema) is the right model. New tests need a version of this fixture that also seeds sample api_docs, api_params, and table_columns rows.

The tool functions must accept an optional `conn` parameter (or be refactored to use a module-level variable that tests can swap) to enable testing without the live database.

### Wave 0 Gaps

- [ ] `tests/test_server.py` — covers MCP-01 through MCP-06 (8 test functions listed above)
- [ ] `tests/conftest.py` update — add `seeded_db_conn` fixture with sample api_docs + api_params + api_return_attrs + table_columns rows
- [ ] `uv add fastmcp` — dependency not yet in pyproject.toml; required before any import of fastmcp works

---

## Sources

### Primary (HIGH confidence)

- `https://gofastmcp.com/servers/tools` — FastMCP 3.x `@mcp.tool` decorator syntax, parameter typing, error handling, return values
- `https://gofastmcp.com/getting-started/welcome` — FastMCP server structure and `mcp.run()` entrypoint
- `https://modelcontextprotocol.io/quickstart/server` — Official MCP quickstart: Claude Desktop config format, `claude_desktop_config.json` structure, stdio transport setup
- `https://docs.python.org/3/library/sqlite3.html#sqlite3.connect` — `sqlite3.connect()` with `uri=True` and `mode=ro`, `check_same_thread`, `row_factory`
- `db/schema.py` — Exact table names, column names, and indexes (PRIMARY source for all SQL)
- `db/seed.py` — Column names and types for all 5 tables (secondary reference for SQL construction)
- `.planning/research/STACK.md` — fastmcp 3.1.1 chosen stack, verified against PyPI 2026-03-14

### Secondary (MEDIUM confidence)

- `tests/conftest.py`, `tests/test_schema.py` — Established test patterns: `db_conn` fixture, in-memory SQLite, pytest structure

### Tertiary (LOW confidence)

- None — all critical claims verified against official docs or project source files

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — FastMCP 3.1.1 already confirmed in STACK.md against PyPI; sqlite3 URI mode verified against Python 3.12 official docs
- Architecture: HIGH — Tool decorator pattern verified against gofastmcp.com; Claude Desktop config verified against official MCP quickstart
- Pitfalls: HIGH — stdout contamination and URI mode pitfalls verified by direct documentation reading; path resolution is a known MCP server issue documented in official quickstart

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (FastMCP is active development; re-verify if > 30 days)
