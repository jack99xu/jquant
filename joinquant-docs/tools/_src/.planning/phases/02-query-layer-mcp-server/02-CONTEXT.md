# Phase 2: Query Layer + MCP Server - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a FastMCP server running over stdio that exposes JoinQuant API documentation from the SQLite database to AI hosts (Claude Desktop). The server provides focused, LLM-oriented tools for looking up function signatures, searching docs by keyword, filtering by section, and querying table column definitions. Strategy lookup is deferred to v2.

</domain>

<decisions>
## Implementation Decisions

### Tool design
- **4 focused tools** mapping to requirements MCP-01~04: `lookup_function`, `search_docs`, `list_by_section`, `search_in_section`
- **1 additional discovery tool**: list all function names grouped by section — lets LLMs scan available functions before searching (~221 names, low token cost)
- **1 table column tool**: `lookup_table_columns(table_name)` — returns all columns for a given table (critical for `get_fundamentals` queries where LLMs need exact column names)
- **Total: 6 tools** (4 core doc tools + 1 discovery + 1 table columns)
- **All-in-one responses**: `lookup_function` returns the full doc + all params + return attrs + example code in a single response — one round-trip for a complete answer
- **Bilingual tool descriptions**: Tool names and descriptions include both English and Chinese keywords (e.g., "Search API docs / 搜索API文档") to improve routing for Chinese-language queries

### Response format
- **Structured text** format: clean labeled sections with markdown (Function, Signature, Parameters table, Returns, Example). Human-readable, token-efficient, LLM-friendly
- **Search results**: summary list format — function_name + chinese_name + one-line description + section per result. LLM calls `lookup_function` for full detail on the one it wants
- **Not-found handling**: explicit "not found" message + fuzzy suggestions of similar function names + alternative search terms. Helps LLMs self-correct
- **Example code**: include when available in DB, skip the section cleanly when NULL. No placeholder text for missing data

### Data coverage
- **Core exposure**: api_docs + api_params + api_return_attrs (via function lookup tools)
- **Table columns**: exposed via dedicated `lookup_table_columns` tool (2,479 column definitions across 180 tables)
- **Strategies**: skip for v1 — only 7 rows, marked as v2 scope (EXT-02) in PROJECT.md
- **Search scope**: LIKE search across ALL text fields — function_name, chinese_name, description, and call_signature for broadest match coverage

### Connection & config
- **Database path**: default to `jq_knowledge.db` in project directory, with `JQ_DB_PATH` env var override
- **Startup validation**: check DB exists, verify expected tables exist, warn (not fail) if any table has 0 rows. Server still starts but logs warnings
- **Database access**: read-only mode (MCP-06) — no mutations exposed
- **Claude Desktop config**: include a ready-to-paste `claude_desktop_config.json` snippet for easy setup

### Claude's Discretion
- Exact query SQL construction and optimization
- Fuzzy matching algorithm for not-found suggestions
- Internal module structure (single file vs split)
- Logging approach and verbosity levels

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project context
- `.planning/PROJECT.md` — Project vision, core value, constraints
- `.planning/REQUIREMENTS.md` — MCP-01~06 requirements for this phase
- `.planning/ROADMAP.md` — Phase 2 success criteria (5 observable outcomes)

### Database schema (Phase 1 output)
- `db/schema.py` — Complete SQLite schema: 5 tables (api_docs, api_params, api_return_attrs, table_columns, strategies), indexes, foreign keys
- `db/seed.py` — Upsert functions showing exact column names and types for each table

### Phase 1 context
- `.planning/phases/01-scraper-schema/01-CONTEXT.md` — Phase 1 decisions: LIKE-based search, separate params table, LLM-friendly schema design
- `.planning/phases/01-scraper-schema/.continue-here.md` — Final database stats: 221 api_docs, 83 api_params, 5 api_return_attrs, 2479 table_columns, 7 strategies

### Stack
- `.planning/research/STACK.md` — Python 3.12, FastMCP 3.1.1, sqlite3 stdlib, uv

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `db/schema.py` — `init_db()` accepts Path or Connection, can be reused for read-only DB opening
- `db/seed.py` — column names and table structures documented via upsert functions (reference for query construction)
- `jq_knowledge.db` — populated database file (221 API docs, 2479 table columns)

### Established Patterns
- Python 3.12 with uv for dependency management
- `pyproject.toml` for project config, `requirements.txt` not used
- sqlite3 stdlib for database access
- rich for console output (used in run_scrape.py)

### Integration Points
- `jq_knowledge.db` is the database file the MCP server reads
- `db/schema.py` defines the schema the query layer queries against
- FastMCP 3.1.1 already in `.planning/research/STACK.md` as chosen framework
- Claude Desktop connects via stdio transport

</code_context>

<specifics>
## Specific Ideas

- User wants the MCP server optimized for "方便让其他的LLM或者MCP去开放给其他的模型调用" — LLM-friendliness is the primary design criterion
- Success criteria #2 is the key test: asking "what parameters does get_price take?" should trigger the lookup tool and return correct params from the DB, not a hallucinated answer
- Table column lookup is specifically important for `get_fundamentals` usage where LLMs need exact column names like `total_operating_revenue`, `net_profit` etc.

</specifics>

<deferred>
## Deferred Ideas

- Strategy code lookup via MCP — v2 (EXT-02)
- Strategy search by keyword — v2 (EXT-02)
- Natural language strategy generation — v2 (GEN-01~03)
- Additional API section scraping beyond Stock — v2 (EXT-01)

</deferred>

---

*Phase: 02-query-layer-mcp-server*
*Context gathered: 2026-03-22*
