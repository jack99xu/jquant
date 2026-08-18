# Project Research Summary

**Project:** JoinQuant API & Strategy Knowledge Base (auto-jq-database)
**Domain:** Web scraper + SQLite knowledge base + MCP server (Chinese quant platform)
**Researched:** 2026-03-22
**Confidence:** HIGH (stack and architecture); MEDIUM (JoinQuant-specific behavior)

## Executive Summary

This project is a depth-first, static knowledge base that solves a specific gap: JoinQuant's Chinese-language quantitative trading API is not in any AI model's training data. The recommended approach is a two-process architecture — a one-time Playwright scraper that ingests docs and strategies into SQLite, and a persistent FastMCP server that exposes search tools to AI hosts via stdio. This pattern (ingestion separated from exposure) is the established standard for AI-queryable knowledge bases and avoids the primary failure modes of mixing scrape and serve logic. The stack is Python 3.12 + Playwright + FastMCP + sqlite3 stdlib, all with verified PyPI versions and no exotic dependencies.

The key insight from competitor analysis is that Context7 and Google's MCP server are breadth-first and always-current — this project must be the opposite: intentionally narrow (4 API sections + strategy list), depth-first (JoinQuant-specific schema fields), and static (one-time scrape, refresh on demand). That constraint eliminates entire categories of complexity (scheduling, real-time sync, embedding infrastructure) that would otherwise derail v1. The MCP server should expose 3-5 focused tools — not a generic SQL interface — with descriptions written from the LLM's perspective, not as developer documentation.

The top risk is JoinQuant's SPA rendering and login behavior. JoinQuant's frontend almost certainly renders via JavaScript, meaning naive `page.goto()` + `page.content()` will return empty shells. Every page navigation must wait for content-specific selectors, not just `networkidle`. The second risk is Chinese text search: SQLite's built-in FTS5 tokenizers cannot segment Chinese words, so v1 should use `LIKE '%keyword%'` queries on indexed columns — fast enough for hundreds of records — and defer FTS to v1.x only if search quality proves insufficient.

## Key Findings

### Recommended Stack

The stack is lean and dependency-minimal by design. Python 3.12 is the sweet spot: required by FastMCP (>=3.10) and the fastest stable release. Playwright is non-negotiable for JoinQuant — the site uses JavaScript-driven auth and dynamic content rendering that plain HTTP clients cannot handle. FastMCP 3.1.1 powers approximately 70% of deployed MCP servers and provides a higher-level decorator API than the official SDK without sacrificing protocol compatibility. SQLite stdlib handles FTS5, concurrent reads, and WAL mode — no ORM or external DB needed. uv replaces pip+venv+virtualenv as the 2025 community standard.

See `.planning/research/STACK.md` for version compatibility matrix and alternatives considered.

**Core technologies:**
- Python 3.12: Runtime — fastest stable release; required by FastMCP ecosystem
- Playwright 1.58.0: Browser automation — only tool that handles JoinQuant's SPA login and JS-rendered content
- FastMCP 3.1.1: MCP server framework — decorator-based tool registration, handles JSON Schema automatically
- sqlite3 (stdlib): Storage — zero deps, FTS5 support, WAL mode for concurrent reads, single-file portability
- uv (latest): Project management — 10-100x faster than pip, built-in lockfile, 2025 community standard
- beautifulsoup4 + lxml: HTML parsing — easier API than raw DOM for messy real-world markup; lxml backend gives 5-10x parse speedup
- python-dotenv: Credential management — keeps JoinQuant credentials out of source code

### Expected Features

The MVP is tightly scoped: API doc scraper (4 public sections, no login), Playwright login automation for the strategy section, SQLite schema for api_docs, FTS5 or LIKE-based keyword search, and three MCP tools (lookup_function, search_api_docs, list_sections). Read-only DB enforcement and explicit not-found responses are table stakes that must ship with v1. Strategy data is collected in v1 but not exposed via MCP — that deferred exposure is intentional to keep tool count low.

See `.planning/research/FEATURES.md` for full prioritization matrix and anti-feature rationale.

**Must have (table stakes):**
- Function name lookup (exact match) — primary use case for AI code assistance
- Keyword / full-text search across doc fields — users rarely know exact function names
- Structured return: parameters, types, return value, description, examples — AI needs all fields in one response
- Login automation for strategy section — required to access gated content
- Read-only DB enforcement in MCP server — prevents mutations from AI hosts
- Explicit not-found responses — no silent empty results

**Should have (differentiators):**
- JoinQuant-specific schema fields — generic tools use generic schemas; this maps exactly to JoinQuant's structure
- Chinese-language search (LIKE-based for v1, jieba-tokenized FTS for v1.x) — core language of the docs
- Section-scoped search — filter results to one API section to reduce noise
- Parameter-level search — find functions by parameter name, not just function name
- Rebuild script idempotency — upsert on re-run; required for any repeated use

**Defer (v2+):**
- Strategy MCP tool — validate API lookup value first; keep tool count low in v1
- Semantic / vector search — FTS + LIKE is sufficient for hundreds of records; adds embedding infrastructure for marginal gain
- Additional API sections (futures, options, index) — scope creep before v1 is validated
- Web UI for doc browsing — consumer is an AI model, not a human

### Architecture Approach

The architecture is a strict two-process system: an offline ingestion pipeline (Playwright scraper → transformer → SQLite INSERT) and an always-on MCP server (SQLite SELECT → tool formatter → AI host). These must never be combined. The MCP server opens SQLite in read-only mode; the scraper runs as a separate CLI script (`run_scrape.py`) and exits on completion. All SQL lives in a `db/queries.py` module — MCP tools call query functions, never write raw SQL. Each MCP tool does exactly two things: call a query function, then format results as structured markdown text.

See `.planning/research/ARCHITECTURE.md` for component diagram, data flow, and build order dependency graph.

**Major components:**
1. Browser Launcher + Page Navigator (Playwright) — manages session lifecycle, login flow, SPA content waiting
2. Content Extractor + Transformer — pulls DOM content, parses HTML into typed records, validates structure
3. SQLite DB (api_docs + strategies tables) — persistent document store; FTS5 virtual table or indexed columns for search
4. MCP Server (FastMCP, stdio) — exposes 3-5 focused tools; thin formatting layer over db/queries.py

**Build order (architecture-mandated):**
1. DB schema (no dependencies)
2. DB query functions (depends on schema)
3. Scraper: browser, auth, extract, transform (independent of DB)
4. Seed script (depends on queries + transform output)
5. Full scrape run — verify data in DB before touching MCP
6. MCP tools (depends on populated DB)
7. MCP server entry point (registers tools)

### Critical Pitfalls

1. **JoinQuant SPA content not rendered before extraction** — Always use `page.wait_for_selector("[content-specific element]")` after navigation; never assume content is ready after `page.goto()` or `networkidle`. Empty strings and `加载中` in extracted data are the warning sign.

2. **Login state lost between scraper runs** — Persist session with `context.storage_state(path="auth.json")` after first successful login; load it on all subsequent runs. Never re-login on every run — JoinQuant monitors login frequency and may rate-limit or CAPTCHA-gate the account.

3. **CSS selectors break silently on JoinQuant site updates** — Prefer semantic selectors (element tags, `data-*` attributes, human-readable class names); avoid chained `:nth-child()` selectors. Assert minimum row counts after each scrape section; fail loudly rather than writing empty data.

4. **SQLite FTS5 cannot tokenize Chinese text** — Use `LIKE '%keyword%'` queries for v1; the knowledge base will have hundreds of records, well within LIKE performance bounds. If FTS is added later, pre-tokenize with `jieba` before inserting into the FTS index.

5. **MCP tool descriptions written for humans, not LLMs** — Tool descriptions are the primary signal an LLM uses to decide which tool to call. Write from the LLM's perspective: when to use it, example input format, what it returns. A vague `"Search API docs"` description causes the LLM to call wrong tools or none at all.

6. **Too many MCP tools causes LLM tool selection failure** — Target 3-5 tools. LLM accuracy collapses past 15-20 tools. Combine overlapping functionality (e.g., one `search_api_docs` tool that handles keyword, function name, and category lookup via optional parameters) rather than creating separate tools per search axis.

## Implications for Roadmap

Based on the architecture's build order dependency graph and pitfall phase mappings, a 3-phase structure is optimal.

### Phase 1: Scraper Foundation + DB Schema

**Rationale:** Architecture research mandates schema-first; nothing else can be built without knowing the data shape. The scraper is the riskiest component (site-specific, external dependency, SPA rendering, login behavior) and must be validated before the MCP server is built — there is nothing to serve until data is in the DB.

**Delivers:** Working Playwright scraper with session persistence, validated data in SQLite for all target pages, raw HTML backup stored per page, extraction validated with row count assertions.

**Addresses features:** Login automation (Playwright), API doc scraper (4 sections), SQLite schema (api_docs), strategy page scraper, scrape run tracking.

**Avoids pitfalls:** SPA content wait (Pitfall 2), login state persistence (Pitfall 1), brittle CSS selectors (Pitfall 3), credentials in source (security).

**Research flag:** Needs deeper research during planning — JoinQuant's actual DOM structure, selector stability, and login flow cannot be verified without live site inspection. Plan a discovery spike at the start of this phase.

### Phase 2: Database Layer + Search

**Rationale:** With data validated in SQLite, this phase locks the query API that the MCP server will depend on. The Chinese search decision (LIKE vs FTS5 + jieba) must be made here — it affects schema design and cannot be retrofitted easily.

**Delivers:** db/queries.py with typed query functions, LIKE-based search on indexed columns for v1 (search_by_function_name, search_by_keyword, list_sections), SQLite WAL mode enabled, read-only connection configuration.

**Addresses features:** FTS5 index or LIKE search on api_docs, category index, function name index, section lookup, read-only DB enforcement.

**Avoids pitfalls:** Chinese FTS tokenization failure (Pitfall 4), SQLite concurrent access locking (WAL mode), raw HTML blob storage (data must be structured).

**Research flag:** Standard patterns — SQLite query functions and WAL mode are well-documented. No deep research needed; follow PITFALLS.md guidance directly.

### Phase 3: MCP Server + Tool Surface

**Rationale:** Built last because it has no value until the DB is populated and queryable. Tool surface design (3-5 tools, LLM-oriented descriptions) must be planned before implementation to avoid retrofitting.

**Delivers:** FastMCP server with stdio transport, 3-5 focused tools (lookup_function, search_api_docs, list_sections at minimum), LLM-oriented tool descriptions, explicit not-found responses, Claude Desktop integration config.

**Addresses features:** MCP tools (lookup_function, search_api_docs, list_sections), compact token-efficient output, graceful not-found responses, read-only enforcement (DB opened read-only in server process).

**Avoids pitfalls:** Tool descriptions too vague for LLMs (Pitfall 5), too many tools (Pitfall 6), raw SQL rows returned to AI (anti-pattern), monolithic query tool (anti-pattern).

**Research flag:** FastMCP patterns are well-documented; standard patterns apply. The tool description writing is judgment-driven — test with Claude after implementation and iterate.

### Phase Ordering Rationale

- The architecture's build order dependency graph directly determines phase order: schema → scraper → verify DB → MCP. There is no phase reordering that avoids this dependency chain.
- Pitfall phase mappings from PITFALLS.md align exactly: Pitfalls 1-3 are Phase 1 concerns, Pitfall 4 is Phase 2, Pitfalls 5-6 are Phase 3.
- The strategy table is collected in Phase 1 but the strategy MCP tool is deferred to v2 — this keeps Phase 3 tool count below the 5-8 recommended ceiling and lets v1 validate API doc lookup value before expanding scope.
- Chinese FTS tokenization (jieba) is a Phase 2 stretch goal, not a blocker. LIKE-based search ships in v1 and is sufficient for the expected dataset size.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** JoinQuant's DOM structure, selector strategy, and login flow are unverifiable without live site access. Start Phase 1 with a discovery spike: open the site in Playwright, dump `page.content()` after navigation, and identify stable selectors before writing extraction logic.

Phases with standard patterns (skip research-phase):
- **Phase 2:** SQLite query functions, WAL mode, and LIKE-based search are fully documented and straightforward. Follow PITFALLS.md guidance directly.
- **Phase 3:** FastMCP tool registration with stdio transport is well-documented at gofastmcp.com. The only non-standard element is tool description quality — validate with real Claude queries after implementation.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All package versions verified against PyPI; FastMCP, Playwright, sqlite3 are the correct tools for this use case with no credible alternatives |
| Features | HIGH (table stakes) / MEDIUM (differentiators) | MCP tool patterns are well-established; JoinQuant-specific schema fields depend on actual doc structure not yet inspected |
| Architecture | HIGH | MCP architecture from official docs; two-process ingestion/exposure pattern is universal for this system type |
| Pitfalls | HIGH (general scraping/MCP) / MEDIUM (JoinQuant-specific) | FTS5 CJK limitation is documented officially; login rate-limiting behavior is inferred from general knowledge of Chinese platforms, not JoinQuant-specific evidence |

**Overall confidence:** HIGH for tech decisions; MEDIUM for JoinQuant-specific behavior. The unknowns are all discoverable in Phase 1's discovery spike.

### Gaps to Address

- **JoinQuant DOM structure:** Cannot be verified without live site inspection. Resolve in Phase 1 discovery spike — open pages in headed Playwright, inspect sidebar structure, confirm login flow uses form fields (not OAuth or CAPTCHA) before committing to selector strategy.
- **JoinQuant login rate-limiting behavior:** Assumed to be present based on general patterns for Chinese platforms; actual throttle threshold is unknown. Mitigation (session persistence) is correct regardless — implement it in Phase 1 regardless of whether rate-limiting is confirmed.
- **Strategy section content structure:** The strategy listing sidebar navigation pattern is assumed (navigate via UI, not direct URLs). Confirm in Phase 1 whether strategies load from direct URLs or require sidebar traversal to trigger client-side state.
- **Chinese search quality at v1 scope:** LIKE-based search is assumed sufficient for hundreds of records. If the scraped dataset is larger than expected (>2,000 rows), consider jieba tokenization for FTS at Phase 2 rather than deferring to v1.x.

## Sources

### Primary (HIGH confidence)
- https://pypi.org/project/fastmcp/ — FastMCP 3.1.1, Python >=3.10, release date verified
- https://pypi.org/project/playwright/ — Playwright 1.58.0, Python >=3.9, release date verified
- https://modelcontextprotocol.io/docs/learn/architecture — MCP architecture patterns
- https://modelcontextprotocol.io/specification/2025-06-18/server/tools — MCP tools spec
- https://www.sqlite.org/fts5.html — SQLite FTS5, CJK tokenizer limitations
- https://playwright.dev/docs/auth — Playwright storageState session persistence

### Secondary (MEDIUM confidence)
- https://dev.to/aws-heroes/mcp-tool-design-why-your-ai-agent-is-failing-and-how-to-fix-it-40fc — tool description quality (97.1% defect rate finding)
- https://www.philschmid.de/mcp-best-practices — 5-8 tool count recommendation
- https://scrapingant.com/blog/web-scraping-playwright-python-part-3 — Playwright + SQLite pattern
- https://upstash.com/blog/context7-mcp — Context7 MCP feature comparison
- https://dev.to/queelius/the-mcp-pattern-sqlite-as-the-ai-queryable-cache-34g6 — SQLite as AI-queryable cache pattern

### Tertiary (LOW confidence / needs validation)
- JoinQuant login rate-limiting behavior — inferred from general Chinese platform patterns; validate in Phase 1 discovery spike
- JoinQuant DOM structure and selector stability — not inspectable without live site access; validate in Phase 1

---
*Research completed: 2026-03-22*
*Ready for roadmap: yes*
