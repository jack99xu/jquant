# Phase 1: Scraper + Schema - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Log in to JoinQuant, scrape all strategy code from "经典策略学习" and API documentation from 4 specified Stock API pages, and store everything in a structured SQLite database. The database is the deliverable — the MCP server that reads it is Phase 2.

</domain>

<decisions>
## Implementation Decisions

### Scraping approach
- Run Playwright **headed for discovery/debugging**, switch to **headless once selectors are stable**
- If login fails (wrong password, CAPTCHA, rate limit): **fail fast with clear error message and exit**
- Try **direct URL navigation** for strategy pages first; fall back to clicking through sidebar if direct URLs don't work
- **Polite scraping**: 2-3 second delay between page navigations to avoid rate limiting
- Session persistence via `auth.json` (Playwright `storageState`) — second run should not re-login

### API doc extraction
- One database row per **callable API function** (e.g., `get_security_info`, `get_price`) — not per section heading
- **Extract code examples** alongside function signatures — helps LLMs see usage patterns
- Store **partial data** when fields are missing (null for missing examples, return types, etc.) — never skip a function
- Example structure from user (get_security_info): function name, 调用方法, 参数 list, 返回值 attributes, 示例 code

### Schema design
- Claude's discretion on exact schema structure — optimize for MCP/LLM query friendliness
- Must support: function name lookup, parameter-level queries, Chinese text LIKE search, category filtering
- Reference example: `get_security_info(code)` with params (code: 证券代码), return attributes (display_name, name, start_date, end_date, type, parent), and example code

### Claude's Discretion
- Exact SQLite table design (separate params table vs JSON column — pick what's best for MCP queries)
- CSS selector strategy for JoinQuant pages (discovered during implementation)
- Strategy categorization scheme (based on what the sidebar reveals)
- Error handling and logging approach

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project context
- `.planning/PROJECT.md` — Project vision, credentials, target API pages
- `.planning/REQUIREMENTS.md` — SCRP-01~08, DB-01~05 requirements for this phase
- `.planning/ROADMAP.md` — Phase 1 success criteria (5 observable outcomes)

### Research findings
- `.planning/research/STACK.md` — Python 3.12, Playwright 1.58.0, FastMCP 3.1.1, sqlite3 stdlib, uv
- `.planning/research/ARCHITECTURE.md` — Three-layer architecture, build order, component boundaries
- `.planning/research/PITFALLS.md` — SPA rendering pitfalls, Chinese FTS limitations, selector brittleness
- `.planning/research/FEATURES.md` — Feature dependencies, Chinese tokenization challenges

### Target pages (scraping targets)
- JoinQuant 经典策略学习: requires login, sidebar navigation with strategy categories
- `https://www.joinquant.com/help/api/help#Stock:获取股票数据`
- `https://www.joinquant.com/help/api/help#Stock:获取单季度年度财务数据`
- `https://www.joinquant.com/help/api/help#Stock:上市公司概况`
- `https://www.joinquant.com/help/api/help#Stock:获取融资融券标的列表`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — greenfield project, no existing code

### Established Patterns
- None — patterns will be established in this phase

### Integration Points
- SQLite database file is the output artifact consumed by Phase 2 (MCP server)
- `auth.json` session file persisted by scraper, reused across runs

</code_context>

<specifics>
## Specific Ideas

- User provided a concrete API doc example (get_security_info) showing the structure: 调用方法, 参数, 返回值 attributes with types, 示例 code — this is the extraction target format
- User explicitly wants the schema to be optimized for "方便让其他的LLM或者MCP去开放给其他的模型调用" — LLM-friendliness is the primary schema design criterion
- Credentials for JoinQuant login: e8244388-e273-4aec-a9ff-856943866238 (both username and password)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-scraper-schema*
*Context gathered: 2026-03-22*
