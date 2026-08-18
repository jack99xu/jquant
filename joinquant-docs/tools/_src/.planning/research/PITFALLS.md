# Pitfalls Research

**Domain:** Web scraping + SQLite knowledge base + MCP server (JoinQuant/Chinese financial platform)
**Researched:** 2026-03-22
**Confidence:** MEDIUM — JoinQuant-specific internals unverifiable without live site inspection; general scraping and MCP pitfalls are HIGH confidence from official docs and community evidence.

---

## Critical Pitfalls

### Pitfall 1: Login State Lost Between Scraper Runs

**What goes wrong:**
The scraper logs in to JoinQuant at the start of each run, but session cookies are not persisted. Every re-run triggers a fresh login. JoinQuant (like many Chinese platforms) monitors login frequency and may rate-limit, CAPTCHA-gate, or silently block accounts that log in too often from automation.

**Why it happens:**
Playwright's default browser context does not persist storage between runs. Developers assume "login at the top of the script" is fine because it works in early testing when frequency is low.

**How to avoid:**
Use `context.storage_state(path="auth.json")` after the first successful login and load it with `browser.new_context(storage_state="auth.json")` on subsequent runs. Check whether the session is still valid before attempting re-login (e.g., look for a logged-in indicator element). Only re-authenticate when the session has actually expired.

**Warning signs:**
- Scraper makes a login request every time it runs
- Auth.json does not exist in the project
- Login requests visible in Playwright network logs on every execution

**Phase to address:** Phase 1 (scraper foundation) — before any scraping logic is written on top.

---

### Pitfall 2: JoinQuant Serves a JavaScript SPA — Content Is Not in Initial HTML

**What goes wrong:**
The strategy list and API documentation pages are almost certainly rendered by React/Vue on the client side. A naive `page.content()` call immediately after `page.goto()` returns the empty shell HTML, not the rendered content. Selectors find nothing; the scraper silently produces empty records.

**Why it happens:**
Developers use `page.goto(url)` and immediately try to extract content, without waiting for dynamic rendering to complete. Works fine on static pages, breaks completely on SPAs.

**How to avoid:**
Always use `page.wait_for_selector("[specific element that proves content is loaded]")` or `page.wait_for_load_state("networkidle")` after navigation. For the strategy list sidebar specifically, wait for the category tree elements to appear before iterating them. For API doc pages, wait for function signature elements to appear before extracting.

**Warning signs:**
- Extracted text is empty strings or placeholder content like "加载中"
- HTML dumps from `page.content()` show `<div id="app"></div>` with nothing inside
- Strategy count in the database is 0 or far below expected

**Phase to address:** Phase 1 (scraper foundation) — establish the right waiting strategy before building extraction logic.

---

### Pitfall 3: CSS Selectors Encoded Against JoinQuant's Current DOM Break Silently on Site Updates

**What goes wrong:**
Selectors like `.strategy-sidebar > ul > li:nth-child(2) > a` work at development time but break when JoinQuant updates their frontend. The scraper runs without errors, produces no output or partial output, and the knowledge base goes stale without any alert.

**Why it happens:**
Frontend code is deployed for users, not scrapers, and changes without backward compatibility or announcement. Auto-generated CSS class names (common in React/Next.js) change with every build — they look like `.sc-bdnxRM` or `.css-1a2b3c`.

**How to avoid:**
- Prefer semantic selectors: element tags + `data-*` attributes + stable class names with human-readable names
- Avoid chained position-based selectors like `:nth-child(N)`
- After extraction, validate row counts against a floor threshold (e.g., "we expect at least 10 strategies per category") and fail loudly rather than silently writing empty data
- Store the raw HTML of each page alongside extracted data so you can re-parse without re-scraping if the parser breaks

**Warning signs:**
- Database category has 0 entries after a run
- Extracted function names contain HTML artifacts or are null
- A run that previously took 5 minutes now completes in 10 seconds (nothing was found to iterate)

**Phase to address:** Phase 1 for selector strategy; Phase 2 for validation checks on extracted data.

---

### Pitfall 4: SQLite FTS5 Cannot Search Chinese Text Without a Custom Tokenizer

**What goes wrong:**
If you add full-text search using SQLite's FTS5 extension (for keyword search across API doc text), the built-in `unicode61` tokenizer treats the entire Chinese sentence as a single token because Chinese has no whitespace word boundaries. Searching for `获取股票` fails to match a document containing `获取股票数据`. FTS returns zero results for Chinese queries.

**Why it happens:**
FTS5's tokenizers are designed for space-delimited languages. This is a known, documented limitation — the official SQLite FTS5 docs note CJK is not handled by built-in tokenizers.

**How to avoid:**
For v1, skip FTS entirely and use SQLite `LIKE '%keyword%'` on indexed text columns. This is slower for large datasets but the knowledge base will contain hundreds, not millions, of records. If FTS becomes necessary, use the `jieba` Python library to pre-tokenize Chinese text into space-separated tokens before inserting into the FTS index.

**Warning signs:**
- MCP search tool returns empty results for Chinese-language queries that should match
- English keyword searches work but Chinese ones don't

**Phase to address:** Phase 2 (database schema design) — decide upfront whether to use FTS or LIKE, and design schema accordingly.

---

### Pitfall 5: MCP Tool Descriptions Are Written for Humans, Not for LLMs

**What goes wrong:**
Tool descriptions like `"Search API docs"` give the LLM no signal about when to use the tool, what query format to use, or what to expect back. The LLM either ignores the tool or calls it with wrong argument formats. A 2025 study found 97.1% of MCP tool descriptions in the wild have at least one quality issue, with 56% having unclear purpose statements.

**Why it happens:**
Tool descriptions are treated as documentation strings for human developers reading the code, not as the primary decision surface an LLM uses to choose between tools.

**How to avoid:**
Write tool descriptions from the LLM's perspective: "Use this tool when the user asks about a JoinQuant API function by name or wants to know what parameters `get_price()` accepts. Input: function name (e.g., 'get_price') or keyword (e.g., 'dividend'). Returns: function signature, parameters, return type, description, and code examples." Include: when to use it, example input format, what it returns.

**Warning signs:**
- LLM calls the wrong tool for a query, or calls no tool when one should apply
- LLM invents parameter names not in the schema
- Claude answers "I don't know the JoinQuant API signature" despite the knowledge base being populated

**Phase to address:** Phase 3 (MCP server) — treat tool descriptions as production copy, not code comments.

---

### Pitfall 6: Too Many MCP Tools Causes LLM Tool Selection Failures

**What goes wrong:**
Adding separate tools for every operation (search by name, search by category, search by keyword, list all functions, get examples, get parameters...) causes the LLM's tool selection accuracy to collapse. Research shows LLM performance falls off a cliff past 15-20 tools; at 107 tools, both large and small models fail completely.

**Why it happens:**
Developers model MCP tools like REST API endpoints — one tool per resource/action. LLMs work differently: they need focused, clearly differentiated tools.

**How to avoid:**
Design 3-5 tools maximum for this project. A single `search_api_docs(query, type)` tool that handles name lookup, keyword search, and category browsing is better than three separate tools. Keep the tool count to 5-8 and combine overlapping functionality. Official MCP guidance recommends 5-8 tools per server.

**Warning signs:**
- Tool count in server exceeds 10
- LLM calls the wrong search tool for a query
- LLM conflates parameters between different search tools

**Phase to address:** Phase 3 (MCP server design) — plan tool surface before implementation.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcode category names from sidebar instead of scraping them dynamically | Faster initial build | Breaks when JoinQuant adds/renames categories | Never — scrape the category list dynamically |
| Skip validation of extracted data (assume scrape worked) | Less code | Silent empty database, broken knowledge base | Never |
| Store raw HTML blobs in SQLite instead of parsed structured data | Easier ingestion | MCP queries become HTML parsing in query time | Never for primary storage; acceptable as a backup column |
| Re-login on every scraper run instead of persisting session | Simpler code | Account rate-limiting or CAPTCHA lock | MVP only, must be fixed before any repeated use |
| Use `LIKE` search without indexes | Simpler schema | Query times grow linearly with record count | Acceptable for <1000 rows (this project) |
| Skip scraper run tracking (no record of which pages were visited) | Less code | Cannot resume interrupted runs or detect missing pages | Never — add a `scrape_runs` table even in v1 |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| JoinQuant login | POST credentials directly to the login form action URL | Use Playwright to fill and submit the actual form — the site likely uses CSRF tokens and JavaScript-driven auth flows that raw HTTP requests cannot replicate |
| JoinQuant strategy pages | Navigate directly to strategy URLs | The strategy content may only load after sidebar navigation triggers client-side state; navigate via the UI, not direct URLs |
| SQLite from MCP server | Open a new connection per tool call | Use a module-level connection pool or singleton with WAL mode enabled; MCP servers handle concurrent calls and SQLite connections are not free to create |
| Playwright storage state | Store `auth.json` in the repo | Add `auth.json` to `.gitignore` immediately — it contains live session cookies that can impersonate the JoinQuant account |
| MCP server tool returns | Return raw SQLite Row objects | Serialize to plain dicts/JSON before returning; MCP protocol requires JSON-serializable outputs |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Scraping all strategies in a single synchronous loop with no delay | Works in dev, gets rate-limited or IP-blocked in full run | Add 1-3 second delay between page navigations; respect server pacing | At ~50+ consecutive pages |
| Loading entire SQLite database into memory for each MCP query | Fine for 100 rows, slow for 10,000 | Use parameterized SQL queries with LIMIT; never `SELECT *` without a WHERE | At ~5,000+ rows |
| Re-running the full scraper to update one changed page | Acceptable once, becomes a problem at scale | Track `last_scraped_at` per page; implement incremental re-scrape | Whenever re-scraping is needed |
| `page.wait_for_load_state("networkidle")` timeout | Playwright throws on complex pages | Set explicit timeouts and use targeted `wait_for_selector` instead | On pages with persistent polling/websockets |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| JoinQuant credentials hardcoded in source code | Credential exposure if repo is shared or made public | Load credentials from environment variables; never commit credentials |
| `auth.json` (Playwright storage state) committed to git | Live session cookies leaked; account compromise | Add `auth.json` and `*.json` auth files to `.gitignore` immediately |
| MCP server has no authentication | Any local process can call the MCP server and query the database | For local-only use this is acceptable; if server is ever networked, add auth header validation |
| SQLite file stored in a web-accessible directory | Knowledge base data exposed via HTTP | Store `.db` file outside any web root; this is a local tool so less critical, but establish the habit |

---

## UX Pitfalls (LLM Consumer Experience)

| Pitfall | LLM Consumer Impact | Better Approach |
|---------|---------------------|-----------------|
| MCP tool returns raw SQL column names as keys (`func_nm`, `ret_typ`) | LLM has to guess what fields mean; response is harder to reason about | Return human-readable keys (`function_name`, `return_type`) in tool output |
| Tool returns entire database row including internal IDs and timestamps | Adds noise to LLM context | Filter output to only fields useful for code generation: name, signature, parameters, description, examples |
| No fallback message when search returns empty | LLM silently fails and may hallucinate | Return a structured message like `{"found": false, "suggestion": "Try searching by keyword instead of function name"}` |
| Search is exact-match only | Searches like `get_price` fail if user types `getprice` or `get price` | Use SQLite `LIKE '%{query}%'` for fuzzy matching; normalize input before querying |

---

## "Looks Done But Isn't" Checklist

- [ ] **Login automation:** Does the scraper verify it is actually logged in (check for a logged-in element) before proceeding, rather than assuming login succeeded?
- [ ] **Session persistence:** Is `auth.json` being saved after login and loaded on subsequent runs?
- [ ] **Content wait:** Does the scraper wait for actual content elements (not just `networkidle`) before extracting?
- [ ] **Extraction validation:** After each page scrape, does the code assert that extracted data is non-empty and structurally valid?
- [ ] **Chinese text search:** Have you manually tested searching for a Chinese keyword in the MCP tool and confirmed it returns results?
- [ ] **Tool descriptions:** Have you tested each MCP tool by asking Claude to use it for a realistic user query and confirming it selects the right tool?
- [ ] **Credentials security:** Is `auth.json` in `.gitignore`? Are credentials loaded from environment variables, not source code?
- [ ] **SQLite WAL mode:** Is WAL mode enabled (`PRAGMA journal_mode=WAL`) to allow concurrent reads from the MCP server without locking?
- [ ] **Scrape run tracking:** Is there a record of which pages were successfully scraped (for resumability and detecting coverage gaps)?

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Login rate-limited or account flagged | MEDIUM | Wait 24-48 hours before retrying; implement session persistence to prevent re-triggering |
| CSS selectors broke after JoinQuant site update | MEDIUM | Re-inspect DOM via Playwright `page.content()`, update selectors, re-run scraper for affected pages; raw HTML backup allows re-parse without re-scraping |
| SQLite FTS search returns empty for Chinese queries | LOW | Drop FTS table, switch to `LIKE`-based search, reindex; data is not lost |
| Database populated with empty or malformed records | MEDIUM | Identify via count queries; delete and re-scrape affected categories; add validation checks to prevent recurrence |
| MCP tool descriptions cause LLM to call wrong tools | LOW | Rewrite descriptions (server-side only, no client changes needed); deploy and re-test |
| Auth state file committed to git with credentials | HIGH | Rotate JoinQuant account password immediately; add `auth.json` to `.gitignore`; remove from git history with `git filter-branch` or BFG |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Login state lost between runs | Phase 1: Scraper foundation | Run scraper twice in a row; confirm second run loads `auth.json` and does not trigger login |
| SPA content not loaded before extraction | Phase 1: Scraper foundation | Inspect extracted HTML — confirm it contains actual strategy text, not "加载中" |
| Brittle CSS selectors break silently | Phase 1 (selector strategy) + Phase 2 (extraction validation) | After scrape, assert row count meets minimum threshold; alert on zero-result categories |
| Chinese FTS tokenization failure | Phase 2: Database schema | Search for a Chinese term that exists in the data; confirm results return |
| MCP tool descriptions too vague | Phase 3: MCP server | Ask Claude to look up `get_price` parameters; confirm it calls the right tool with the right argument |
| Too many MCP tools | Phase 3: MCP server design | Count tools before implementation; refuse to add tool N+1 without removing or merging an existing one |
| Credentials in source code | Phase 1 (setup) | `git grep` for credential values before first commit |
| SQLite concurrent access locking | Phase 3: MCP server | Run two simultaneous tool calls; confirm neither throws a database locked error |

---

## Sources

- [Playwright Authentication — Official Docs](https://playwright.dev/docs/auth) — storageState persistence patterns (HIGH confidence)
- [SQLite FTS5 Extension — Official Docs](https://www.sqlite.org/fts5.html) — CJK tokenizer limitations (HIGH confidence)
- [GRDB Issue #413: FTS5 Tokenizers and Chinese](https://github.com/groue/GRDB.swift/issues/413) — community confirmation of unicode61 CJK failure (MEDIUM confidence)
- [MCP Tool Design: Why Your AI Agent Is Failing](https://dev.to/aws-heroes/mcp-tool-design-why-your-ai-agent-is-failing-and-how-to-fix-it-40fc) — tool description quality research (MEDIUM confidence)
- [Real Faults in MCP Software: Comprehensive Taxonomy (arXiv)](https://arxiv.org/html/2603.05637) — 97.1% of MCP tool descriptions have quality issues (MEDIUM confidence)
- [MCP Best Practices — Phil Schmid](https://www.philschmid.de/mcp-best-practices) — 5-8 tool recommendation, tool count cliff (MEDIUM confidence)
- [Fixing Claude Code Concurrent Session Problem with SQLite WAL](https://dev.to/daichikudo/fixing-claude-codes-concurrent-session-problem-implementing-memory-mcp-with-sqlite-wal-mode-o7k) — WAL mode in MCP context (MEDIUM confidence)
- [The Problem With XPath, CSS Selectors, and Keeping Your Scraper Alive](https://extractdata.substack.com/p/why-xpath-css-selectors-break-scrapers) — selector brittleness (MEDIUM confidence)
- [Stop Getting Blocked: 10 Common Web-Scraping Mistakes](https://www.firecrawl.dev/blog/web-scraping-mistakes-and-fixes) — silent failure without monitoring (MEDIUM confidence)
- [JoinQuant jqdatasdk GitHub](https://github.com/JoinQuant/jqdatasdk) — confirms JoinQuant has a Python SDK (jqdatasdk) as an alternative access method (HIGH confidence)

---
*Pitfalls research for: JoinQuant API & Strategy Knowledge Base (web scraping + SQLite + MCP)*
*Researched: 2026-03-22*
