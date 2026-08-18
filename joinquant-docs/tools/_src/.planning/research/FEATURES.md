# Feature Research

**Domain:** API documentation knowledge base with MCP server for quantitative trading platform
**Researched:** 2026-03-22
**Confidence:** HIGH (for table stakes and MCP patterns); MEDIUM (for differentiators specific to JoinQuant use case)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users (AI assistants and developers) assume exist. Missing these = the tool is not useful.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Function name lookup | Primary use case: AI needs exact function signature before writing code | LOW | Direct SQL query on `function_name` column |
| Keyword / full-text search across docs | Users don't always know exact function name; search by topic | MEDIUM | SQLite FTS5 virtual table on `description`, `parameters`, `examples` columns |
| Return structured data per function | AI needs parameters, types, return value, description in one response | LOW | Schema design decision; JSON or flat columns |
| Search by category / topic | JoinQuant docs are organized by section (e.g., 获取股票数据); users navigate this way | LOW | `category` column with indexed lookup |
| Return code examples alongside docs | Without examples, AI still guesses usage patterns | MEDIUM | Scraper must extract example blocks from HTML; store as text |
| MCP tool with clear input schema | MCP clients reject tools without proper JSON Schema input definitions | LOW | FastMCP / MCP SDK handles this declaratively |
| Read-only enforcement | MCP exposes a knowledge base, not a writable database; mutations must be blocked | LOW | SQLite authorizer callback or open DB in read-only mode |
| Graceful error on unknown function | When function is not in database, tool must return a clear "not found" signal, not silence | LOW | Explicit not-found response vs empty list |
| One-time scrape → persistent DB | Data collected once and stored; server reads from .db file at startup | LOW | This is the core architecture decision already validated |
| Login automation for gated content | JoinQuant strategy section requires authentication; scraper must handle this | MEDIUM | Playwright storageState for session persistence after initial login |

### Differentiators (Competitive Advantage)

Features that set this knowledge base apart from generic doc tools or context-stuffing approaches.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| JoinQuant-specific schema | Fields matched to JoinQuant's doc structure (function_name, parameters, return_type, examples in Chinese) | LOW | Generic doc tools use generic schemas; this one maps exactly to JoinQuant's format |
| Exact parameter-level search | Search "get_price start_date parameter" and retrieve that specific parameter's description | MEDIUM | Requires storing parameters as structured data (JSON array or separate table), not a blob |
| Strategy code cross-reference | Link API functions to real strategy code that uses them | HIGH | Not in v1 scope per PROJECT.md; mentioned as future |
| Rebuild script idempotency | Scraper can be re-run to refresh DB without data duplication | MEDIUM | Upsert on primary key (function_name); scraper deletes+reinserts by section |
| Chinese-language FTS | FTS5 tokenizer must handle Chinese characters (unicode61 or ICU tokenizer) | MEDIUM | Default FTS5 tokenizer does not properly segment Chinese; ICU tokenizer or trigram tokenization required |
| Compact tool output (token-efficient) | MCP responses count against context window; terse structured output beats verbose prose | LOW | Return only the fields the AI needs; avoid redundant nesting |
| Section-scoped search | Search within a specific API section (e.g., "only in 获取股票数据") | LOW | Filter by `section` column; avoids irrelevant results from other sections |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time sync with JoinQuant | "Always current docs" sounds appealing | JoinQuant may block automated traffic; scrape frequency risks account ban; adds scheduling complexity with no clear benefit for stable API docs | One-time scrape; re-run manually when docs change |
| Strategy search via MCP (v1) | Strategies are in the DB; why not expose them? | Adds surface area without solving the core problem (incorrect API usage); dilutes tool purpose; AI gets confused by too many tools | Keep MCP focused on API doc lookup; strategy search is v2 if validated |
| Semantic / vector search | "Smarter search" sounds better | Adds embedding model dependency (OpenAI/Ollama), infrastructure complexity, and latency; SQLite FTS5 is sufficient for structured API doc lookup with known terminology | FTS5 with BM25 ranking; add vector search only if FTS5 proves insufficient |
| Web UI for browsing docs | Nice for humans to explore | Out of scope; the consumer is an AI model, not a human browser; adds frontend build complexity | Claude / Cursor can read MCP responses directly |
| Automatic schema migration | "Future proof" | Over-engineering for a single-user local tool; the DB is a disposable cache | Drop and rebuild the DB file when schema changes |
| Multi-user authentication on MCP | Seems like good practice | This is a local tool running on developer's machine via stdio transport; auth adds complexity with no security benefit in this context | Keep as local stdio MCP server; no HTTP transport needed for v1 |
| Coverage of all JoinQuant API sections | More complete = better | Scope creep; the 4 target sections cover the most commonly confused APIs; adding futures/options sections before v1 is validated wastes time | Start with 4 sections; add more only after validating the MCP server is used |

---

## Feature Dependencies

```
[Login automation (Playwright + storageState)]
    └──required by──> [Strategy page scraping]
                          └──feeds──> [SQLite strategy table]

[API page scraping (public, no login)]
    └──feeds──> [SQLite api_docs table]
                    └──required by──> [MCP search tools]
                                          └──requires──> [FTS5 index on api_docs]
                                          └──requires──> [Category index on api_docs]
                                          └──requires──> [Function name index on api_docs]

[Chinese-language FTS tokenizer]
    └──enhances──> [FTS5 full-text search]
    (without proper tokenizer, Chinese search quality degrades significantly)

[Structured parameter storage (JSON or table)]
    └──enables──> [Parameter-level search] (differentiator)
    └──conflicts──> [Single blob storage for parameters] (simpler but not searchable)
```

### Dependency Notes

- **Login automation requires Playwright session persistence:** A single login at scrape time saves cookies to `storageState.json`; subsequent page loads reuse this state without re-authenticating.
- **FTS5 index requires schema decision upfront:** FTS5 virtual tables are defined at schema creation; retrofitting FTS5 onto an existing table requires dropping and recreating the virtual table.
- **Chinese FTS tokenizer must be chosen before schema creation:** Switching tokenizers later requires dropping and rebuilding the FTS5 table and all indexed content.
- **MCP tool input schema requires knowing the search axes:** Tool parameters (`function_name`, `keyword`, `category`, `section`) must be defined before implementation; adding new search axes later means updating tool definitions and potentially breaking MCP client caches.
- **Compact tool output conflicts with verbose prose storage:** Store full Chinese doc text in DB; MCP tools select and truncate on output, not at storage time.

---

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate that AI models write better JoinQuant code.

- [ ] **Playwright scraper with login** — Accesses gated strategy section; required to collect strategy examples
- [ ] **API doc scraper (no login)** — Collects 4 target sections from joinquant.com/help/api/help
- [ ] **SQLite schema: api_docs table** — Stores function_name, section, parameters (structured), return_type, description, examples
- [ ] **FTS5 virtual table on api_docs** — Enables keyword search across function descriptions and examples
- [ ] **MCP tool: lookup_function** — Exact match by function name; returns full structured record
- [ ] **MCP tool: search_api_docs** — FTS5 keyword search; returns list of matching functions with short descriptions
- [ ] **MCP tool: list_sections** — Returns available API sections so AI can orient itself
- [ ] **Read-only DB enforcement** — Open SQLite in read-only mode in MCP server process
- [ ] **Not-found responses** — Explicit signal when function is not in DB (not empty list)

### Add After Validation (v1.x)

Features to add once AI models are actually using the MCP server and gaps are identified.

- [ ] **Section-scoped search** — Add `section` filter parameter to `search_api_docs` tool; add only when users report irrelevant cross-section results
- [ ] **Parameter-level search** — Add when users report needing to find functions by parameter name; requires structured parameter storage (JSON array per function)
- [ ] **SQLite schema: strategies table** — Add only after v1 MCP server is validated; strategy code cross-reference is a separate feature
- [ ] **Rebuild script idempotency** — Upsert instead of insert; add when second scrape run is needed

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Strategy MCP tool** — Expose strategy code lookup via MCP; defer until API doc lookup is validated as valuable
- [ ] **Additional API sections** — Expand beyond 4 Stock sections (futures, options, index); defer until users request specific missing sections
- [ ] **Chinese semantic search** — Add embedding-based similarity search; defer unless FTS5 proves insufficient for real queries

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| API doc scraper (4 sections) | HIGH | LOW | P1 |
| SQLite schema: api_docs | HIGH | LOW | P1 |
| FTS5 index on api_docs | HIGH | LOW | P1 |
| MCP tool: lookup_function | HIGH | LOW | P1 |
| MCP tool: search_api_docs | HIGH | LOW | P1 |
| Login automation (Playwright) | HIGH | MEDIUM | P1 |
| Strategy page scraper | MEDIUM | MEDIUM | P1 (required for strategy table, even if MCP not exposed) |
| Read-only enforcement | HIGH | LOW | P1 |
| Not-found responses | HIGH | LOW | P1 |
| MCP tool: list_sections | MEDIUM | LOW | P1 |
| Chinese FTS tokenizer (ICU/trigram) | MEDIUM | MEDIUM | P2 |
| Section-scoped search | MEDIUM | LOW | P2 |
| Parameter-level search | MEDIUM | MEDIUM | P2 |
| Rebuild idempotency | LOW | LOW | P2 |
| Strategy MCP tool | MEDIUM | LOW | P3 |
| Additional API sections | MEDIUM | LOW | P3 |
| Semantic vector search | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

---

## Competitor Feature Analysis

| Feature | Context7 (9000+ libraries) | Google Dev Knowledge MCP | This Project (JoinQuant KB) |
|---------|---------------------------|--------------------------|------------------------------|
| Source | Indexed public docs from npm/GitHub | Official Google developer docs | Scraped JoinQuant docs (Chinese) |
| Search | Semantic + keyword | search_documents + get_documents two-step | FTS5 keyword + exact function name |
| Coverage | Breadth (thousands of libraries) | Depth (Google ecosystem) | Depth (JoinQuant API only) |
| Language | English-first | English | Chinese (docs are in Chinese) |
| Real-time | Yes (indexed, updated) | Yes (re-indexed within 24h) | No (one-time scrape, intentional) |
| Login-gated content | No | No | Yes (strategies require login) |
| Code examples | Sometimes | Yes | Yes (extracted from doc pages) |
| Parameter structure | Varies | Varies | Explicit (JoinQuant has clear parameter tables) |

**Key insight:** Context7 and Google's MCP are breadth-first, always-current tools. This project is intentionally depth-first and static — it solves a specific gap (JoinQuant APIs not in any training data) that general-purpose tools cannot fill.

---

## Sources

- MCP specification — tools concept: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- MCP server build guide: https://modelcontextprotocol.io/docs/develop/build-server
- Google Developer Knowledge MCP tools: https://developers.google.com/knowledge/mcp
- SQLite as AI-queryable cache (MCP pattern): https://dev.to/queelius/the-mcp-pattern-sqlite-as-the-ai-queryable-cache-34g6
- Context7 MCP features: https://upstash.com/blog/context7-mcp
- Docs MCP Server (arabold, open-source alternative to Context7): https://github.com/arabold/docs-mcp-server
- Playwright authentication / session persistence: https://playwright.dev/docs/auth
- SQLite FTS5 documentation: https://www.sqlite.org/fts5.html
- MCP best practices 2026: https://www.cdata.com/blog/mcp-server-best-practices-2026

---
*Feature research for: JoinQuant API & Strategy Knowledge Base (MCP doc server)*
*Researched: 2026-03-22*
