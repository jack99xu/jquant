---
phase: 02-query-layer-mcp-server
plan: 01
subsystem: api
tags: [fastmcp, sqlite3, mcp, python, jq-knowledge-db]

# Dependency graph
requires:
  - phase: 01-scraper-schema
    provides: jq_knowledge.db SQLite database with api_docs, api_params, api_return_attrs, table_columns schema
provides:
  - FastMCP server (server.py) with 6 query tools for JoinQuant API documentation
  - Unit test suite (tests/test_server.py) covering all 6 tools
  - seeded_db pytest fixture for server integration tests
affects:
  - 02-02 (next plan in phase — depends on server.py for MCP host integration or further tooling)

# Tech tracking
tech-stack:
  added: [fastmcp==3.1.1, mcp==1.26.0]
  patterns:
    - Module-level _conn sentinel with _get_conn() lazy opener for test monkey-patching
    - sqlite3 URI mode=ro for read-only production DB connections
    - conn.row_factory=sqlite3.Row applied in _get_conn() for column-name access on any connection
    - Fuzzy suggestion fallback: prefix match -> all functions when no prefix match

key-files:
  created:
    - server.py
    - tests/test_server.py
    - .planning/phases/02-query-layer-mcp-server/deferred-items.md
  modified:
    - pyproject.toml
    - uv.lock
    - tests/conftest.py

key-decisions:
  - "row_factory=sqlite3.Row set in _get_conn() not _open_db() so monkey-patched test connections also get column-name access"
  - "Fuzzy suggestions fall back to all available functions (limited) when prefix match yields nothing — ensures not-found responses always include discovery hints"
  - "Pre-existing test_seed.py failure (missing chinese_name binding) deferred — out of scope for this plan"

patterns-established:
  - "MCP tool pattern: @mcp.tool decorator on module-level function, _get_conn() for DB access"
  - "Test monkey-patch pattern: monkeypatch.setattr(server, '_conn', seeded_db) + autouse fixture"
  - "Not-found response pattern: explicit 'not found' message + suggestions list"
  - "Section-filtered response pattern: list functions in section, fall back to available sections on miss"

requirements-completed: [MCP-01, MCP-02, MCP-03, MCP-04, MCP-05, MCP-06]

# Metrics
duration: 3min
completed: 2026-03-22
---

# Phase 2 Plan 01: FastMCP Server with 6 Query Tools Summary

**FastMCP server exposing lookup_function, search_docs, list_by_section, search_in_section, list_functions, and lookup_table_columns against a read-only SQLite jq_knowledge.db**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-22T15:29:55Z
- **Completed:** 2026-03-22T15:33:27Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Complete FastMCP server with all 6 MCP tools (MCP-01 through MCP-06) implemented and tested
- All 8 unit tests pass covering lookup, search, section listing, cross-section search, table columns, and read-only DB enforcement
- Read-only SQLite connection via `mode=ro` URI prevents any write operations at the database level
- seeded_db pytest fixture with realistic Chinese API documentation data for testing

## Task Commits

Each task was committed atomically:

1. **Task 1: Add fastmcp dependency and test scaffold with seeded fixtures** - `48376d0` (chore)
2. **Task 2: Implement server.py with all 6 MCP tools** - `f03c84e` (feat)

**Plan metadata:** (docs commit — see below)

_Note: Task 2 is the TDD GREEN phase — test scaffold (RED) was Task 1._

## Files Created/Modified
- `server.py` - FastMCP server with 6 tools, module-level _conn, read-only DB, fuzzy suggestions, startup validation
- `tests/test_server.py` - 8 unit tests covering all MCP requirements
- `tests/conftest.py` - Added seeded_db fixture with api_docs, api_params, api_return_attrs, table_columns test data
- `pyproject.toml` - Added fastmcp dependency
- `uv.lock` - Updated lockfile with fastmcp==3.1.1 and 59 transitive dependencies

## Decisions Made
- `row_factory=sqlite3.Row` is set in `_get_conn()` rather than only in `_open_db()` so that monkey-patched test connections (plain sqlite3 connections without row_factory) also get column-name access. This keeps test setup minimal.
- Fuzzy suggestions fall back to returning all available functions (up to 5) when prefix matching yields nothing. This ensures callers always get discovery hints for any not-found lookup.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] row_factory not applied to monkey-patched test connections**
- **Found during:** Task 2 (TDD GREEN — first test run)
- **Issue:** `_open_db()` sets `conn.row_factory = sqlite3.Row` but test fixture creates a plain `sqlite3.connect(":memory:")` without row_factory. When tests monkey-patch `server._conn = seeded_db`, column-name access via `row['function_name']` raised `TypeError: tuple indices must be integers or slices, not str`
- **Fix:** Moved row_factory assignment into `_get_conn()` — checks `if _conn.row_factory is not sqlite3.Row` and sets it, applied on every call including test-patched connections
- **Files modified:** server.py
- **Verification:** All 8 tests pass
- **Committed in:** f03c84e (Task 2 commit)

**2. [Rule 1 - Bug] Fuzzy suggestions returned empty for non-matching prefix**
- **Found during:** Task 2 (test_lookup_function_not_found)
- **Issue:** `_fuzzy_suggestions("nonexistent_xyz")` extracts prefix "none", which matches no function names in the test DB. Test asserts `"get_" in result` which failed with empty suggestions.
- **Fix:** Added fallback in `_fuzzy_suggestions` — when prefix match yields no results, return first N available function names from api_docs
- **Files modified:** server.py
- **Verification:** test_lookup_function_not_found passes; suggestions always non-empty when DB has functions
- **Committed in:** f03c84e (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 bugs)
**Impact on plan:** Both fixes necessary for test correctness. The row_factory fix is a minor plumbing detail absent from the plan spec. The fuzzy fallback improves usability — the plan said "fuzzy suggestions" which should always yield something discoverable. No scope creep.

## Issues Encountered
- Pre-existing `test_seed.py::test_upsert_api_doc_insert` failure (missing `chinese_name` binding) — confirmed pre-existing before Phase 02 work. Logged to deferred-items.md, excluded from verification run.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- server.py is complete and fully tested — ready for Plan 02 (MCP host integration, deployment, or additional tooling)
- DB connection requires `jq_knowledge.db` at project root or `JQ_DB_PATH` env var — populated by Phase 01 scraper pipeline
- Run with: `uv run python server.py` (stdio MCP transport for AI host integration)

---
*Phase: 02-query-layer-mcp-server*
*Completed: 2026-03-22*
