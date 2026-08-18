---
phase: 01-scraper-schema
plan: 01
subsystem: database
tags: [sqlite, python, uv, pytest, playwright, beautifulsoup4, lxml]

# Dependency graph
requires: []
provides:
  - "SQLite schema: 4 tables (api_docs, api_params, api_return_attrs, strategies) with FK cascades and 4 indexes"
  - "Seed functions: idempotent upserts using ON CONFLICT DO UPDATE and delete+insert pattern"
  - "Test suite: 17 passing tests covering columns, indexes, Chinese LIKE search, FK cascade, upsert idempotency"
  - "uv project: all dependencies installed (playwright, bs4, lxml, python-dotenv, rich, pytest)"
affects:
  - 01-scraper-schema
  - 02-mcp-server

# Tech tracking
tech-stack:
  added:
    - "uv 0.10.9 (project + dependency management)"
    - "Python 3.12"
    - "playwright 1.58.0 (browser automation)"
    - "beautifulsoup4 4.14.3 (HTML parsing)"
    - "lxml 6.0.2 (fast BS4 parser backend)"
    - "python-dotenv 1.2.2 (credential loading)"
    - "rich 14.3.3 (terminal output)"
    - "pytest 9.0.2 (test framework)"
    - "sqlite3 stdlib (database)"
  patterns:
    - "init_db: accepts Path (file DB) or sqlite3.Connection (in-memory for tests)"
    - "upsert_api_doc: ON CONFLICT(function_name) DO UPDATE pattern"
    - "upsert_api_params: delete-then-insert for full replacement idempotency"
    - "upsert_strategy: ON CONFLICT(name, category) DO UPDATE pattern"
    - "conftest fixture: in-memory SQLite with PRAGMA foreign_keys=ON"

key-files:
  created:
    - "db/schema.py — init_db() with 4 CREATE TABLE + 4 CREATE INDEX statements"
    - "db/seed.py — upsert_api_doc, upsert_api_params, upsert_api_return_attrs, upsert_strategy"
    - "tests/conftest.py — db_conn fixture with in-memory SQLite"
    - "tests/test_schema.py — 8 schema validation tests"
    - "tests/test_seed.py — 9 upsert idempotency and null handling tests"
    - "pyproject.toml — project config with pytest settings"
    - ".gitignore — excludes auth.json, .env, *.db"
    - ".env.example — credential template"
  modified: []

key-decisions:
  - "Separate api_params table (not JSON column) for per-parameter queryability (DB-03)"
  - "LIKE-based Chinese text search for v1 (not FTS5 + jieba) — sufficient for hundreds of records"
  - "delete+insert pattern for params/return_attrs upserts — cleanest idempotency guarantee"
  - "init_db accepts both file path and connection — enables in-memory testing without extra fixture complexity"

patterns-established:
  - "TDD: write conftest + failing tests first, then implement schema + seed, verify GREEN"
  - "FK cascades: api_params and api_return_attrs reference api_docs ON DELETE CASCADE"
  - "Upsert: ON CONFLICT for single-key tables; delete+insert for child tables with no surrogate conflict key"

requirements-completed: [DB-01, DB-02, DB-03, DB-04, DB-05, SCRP-08]

# Metrics
duration: 4min
completed: 2026-03-22
---

# Phase 1 Plan 01: Project Scaffolding and SQLite Schema Summary

**uv project with pytest-configured pyproject.toml, 4-table SQLite schema with FK cascades and indexes, and 17 passing TDD tests for schema structure and upsert idempotency**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-03-22T11:28:57Z
- **Completed:** 2026-03-22T11:31:28Z
- **Tasks:** 2
- **Files modified:** 12

## Accomplishments
- Initialized uv project with Python 3.12 and all required dependencies (playwright, beautifulsoup4, lxml, python-dotenv, rich, pytest)
- Created SQLite schema with 4 tables, 4 indexes, and FK CASCADE relationships between api_docs and its child tables
- Implemented idempotent upsert functions for all 4 tables using ON CONFLICT DO UPDATE (single-key tables) and delete+insert (child tables)
- Full test suite: 8 schema tests + 9 seed tests, all passing

## Task Commits

Each task was committed atomically:

1. **Task 1: Project scaffolding and dependency installation** - `27726a7` (chore)
2. **Task 2: SQLite schema and seed functions with full test suite** - `4d430c5` (feat)

## Files Created/Modified
- `pyproject.toml` — uv project config with all deps and pytest testpaths/pythonpath settings
- `.gitignore` — excludes auth.json, .env, *.db, __pycache__, .venv
- `.env.example` — credential template for JQ_USERNAME/JQ_PASSWORD
- `db/__init__.py` — empty package init
- `db/schema.py` — init_db() creating 4 tables + 4 indexes; accepts Path or Connection
- `db/seed.py` — upsert_api_doc, upsert_api_params, upsert_api_return_attrs, upsert_strategy
- `scraper/__init__.py` — empty package init
- `tests/__init__.py` — empty package init
- `tests/conftest.py` — db_conn fixture (in-memory SQLite + foreign_keys=ON + init_db)
- `tests/test_schema.py` — 8 tests: columns, indexes, Chinese LIKE, FK cascade
- `tests/test_seed.py` — 9 tests: insert, update, null fields, param replacement
- `uv.lock` — dependency lockfile

## Decisions Made
- Separate `api_params` table (not JSON column): enables `SELECT * FROM api_params WHERE param_name = 'code'` queries directly — required for DB-03 and MCP query friendliness
- LIKE-based Chinese text search (not FTS5): sufficient for hundreds of records; avoids CJK tokenizer complexity as confirmed in STATE.md
- delete+insert for child table upserts: cleanest idempotency guarantee — no need to track which rows changed
- `init_db` accepts both `Path` and `sqlite3.Connection`: makes in-memory testing trivial without adding fixture complexity

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed wrong column index in test_params_queryable assertion**
- **Found during:** Task 2 (TDD GREEN phase — first test run)
- **Issue:** Test asserted `rows[0][2] == "get_security_info"` but `SELECT *` on api_params returns `(id, function_name, param_name, ...)` — function_name is index 1, not 2
- **Fix:** Changed assertion to `rows[0][1] == "get_security_info"` and `rows[0][2] == "code"`
- **Files modified:** tests/test_schema.py
- **Verification:** All 17 tests pass after fix
- **Committed in:** 4d430c5 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug in test assertion)
**Impact on plan:** Trivial fix — wrong column index in test assertion. No scope creep. All requirements met.

## Issues Encountered
None beyond the column index bug documented above.

## User Setup Required
None — no external service configuration required for this plan. `.env` with JoinQuant credentials is created and gitignored (credentials are for scraping tasks in subsequent plans).

## Next Phase Readiness
- Database layer complete — schema and seed functions are the contract that scrapers write to and MCP server reads from
- Ready for Plan 02: login/session management and API doc scraper
- Blockers remain from STATE.md: JoinQuant DOM structure and selector stability unverified (requires headed Playwright discovery in Plan 02)

---
*Phase: 01-scraper-schema*
*Completed: 2026-03-22*
