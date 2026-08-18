# Phase 1: Scraper + Schema - Research

**Researched:** 2026-03-22
**Domain:** Playwright browser automation, SQLite schema design, Python scraping pipeline
**Confidence:** HIGH (core stack verified against official docs and prior stack research)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Scraping approach:**
- Run Playwright headed for discovery/debugging, switch to headless once selectors are stable
- If login fails (wrong password, CAPTCHA, rate limit): fail fast with clear error message and exit
- Try direct URL navigation for strategy pages first; fall back to clicking through sidebar if direct URLs don't work
- Polite scraping: 2-3 second delay between page navigations to avoid rate limiting
- Session persistence via `auth.json` (Playwright `storageState`) — second run should not re-login

**API doc extraction:**
- One database row per callable API function (e.g., `get_security_info`, `get_price`) — not per section heading
- Extract code examples alongside function signatures — helps LLMs see usage patterns
- Store partial data when fields are missing (null for missing examples, return types, etc.) — never skip a function
- Example structure: function name, 调用方法, 参数 list, 返回值 attributes, 示例 code

**Schema design:**
- Must support: function name lookup, parameter-level queries, Chinese text LIKE search, category filtering
- Reference example: `get_security_info(code)` with params (code: 证券代码), return attributes (display_name, name, start_date, end_date, type, parent), and example code

### Claude's Discretion
- Exact SQLite table design (separate params table vs JSON column — pick what's best for MCP queries)
- CSS selector strategy for JoinQuant pages (discovered during implementation)
- Strategy categorization scheme (based on what the sidebar reveals)
- Error handling and logging approach

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCRP-01 | System can log in to JoinQuant via Playwright with stored credentials | Playwright form fill + session establishment; credentials: e8244388-e273-4aec-a9ff-856943866238 |
| SCRP-02 | System persists login session to avoid repeated authentication | `context.storage_state(path="auth.json")` after login; `browser.new_context(storage_state="auth.json")` on reload |
| SCRP-03 | System scrapes all strategy names, categories, and code from "经典策略学习" sidebar | Playwright + `wait_for_selector` for sidebar tree; may require UI navigation vs direct URL |
| SCRP-04 | System scrapes API docs from 获取股票数据 page | Public page; `page.goto()` + wait for function entries; BeautifulSoup for extraction |
| SCRP-05 | System scrapes API docs from 获取单季度年度财务数据 page | Same pattern as SCRP-04 |
| SCRP-06 | System scrapes API docs from 上市公司概况 page | Same pattern as SCRP-04 |
| SCRP-07 | System scrapes API docs from 获取融资融券标的列表 page | Same pattern as SCRP-04 |
| SCRP-08 | Scraper can be re-run idempotently without data duplication | `INSERT OR REPLACE` / `ON CONFLICT DO UPDATE` with function_name as unique key |
| DB-01 | SQLite schema stores API docs with function name, parameters, return type, description, and examples | `api_docs` table + separate `api_params` table for structured parameter rows |
| DB-02 | SQLite schema stores strategy code with name, category, code content, and description | `strategies` table with category column indexed |
| DB-03 | Parameters stored as structured data (searchable per-parameter, not blob) | Separate `api_params` table with function_name FK; enables `SELECT * FROM api_params WHERE type = ?` |
| DB-04 | Chinese text searchable via LIKE-based queries | LIKE '%keyword%' on indexed text columns; no FTS5 for v1 (avoids CJK tokenizer complexity) |
| DB-05 | Category/section column indexed for fast filtering | `CREATE INDEX idx_api_docs_section ON api_docs(section)` and `CREATE INDEX idx_strategies_category ON strategies(category)` |

</phase_requirements>

---

## Summary

Phase 1 is a standalone data ingestion pipeline: log in to JoinQuant once, scrape 4 API doc pages and all classic strategy pages, and deposit the results into a structured SQLite database. The deliverable is a populated, verified `.db` file that Phase 2 reads. Nothing in this phase depends on any prior work — this is the foundation.

The technical challenge is threefold. First, JoinQuant is a JavaScript SPA, so all page content must be waited for after navigation — naive `page.content()` calls return empty shells. Second, the strategy section requires a valid login session, which must be persisted to `auth.json` to avoid triggering rate-limiting on repeated runs. Third, the schema must be designed for LLM query friendliness from the start — parameters as structured rows (not a blob), LIKE-indexed text columns for Chinese keyword search, and category indexes for section filtering.

The recommended approach is a four-module Python pipeline: `auth.py` (session management), `scraper/api_docs.py` (API page extraction), `scraper/strategies.py` (strategy page extraction), and `db/schema.py` + `db/seed.py` (storage). These are orchestrated by `run_scrape.py` with a discovery spike as Wave 0 to verify selectors before committing to extraction logic.

**Primary recommendation:** Build the SQLite schema and seed functions first, then the scraper modules that populate them. Wire together in `run_scrape.py`. Run headed initially to discover selectors, then switch to headless.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12 | Runtime | Required by fastmcp (>=3.10); 3.12 is fastest stable release |
| playwright | 1.58.0 | Browser automation for login + scraping | Handles SPAs, cookie auth, dynamic JS rendering |
| beautifulsoup4 | 4.12.x | HTML parsing after Playwright renders pages | Easier than lxml for messy real-world markup |
| lxml | 5.x | Fast parser backend for BeautifulSoup4 | 5-10x parse speedup; use as BS4 parser string |
| sqlite3 | stdlib | Database storage | Built-in, zero deps, FTS5 support if needed later |
| python-dotenv | 1.x | Load credentials from .env | Keeps credentials out of source code |
| uv | latest | Project + dependency management | 10-100x faster than pip; 2025/2026 standard |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| rich | 13.x | Terminal output during long scrape runs | Progress indicators replace print() debugging |
| pytest | 8.x | Test framework | Integration tests on extracted data, schema tests |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| beautifulsoup4 + lxml | selectolax | selectolax faster but smaller ecosystem; BS4+lxml closes gap |
| separate `api_params` table | JSON column for parameters | JSON column simpler to write; separate table enables `SELECT` per-parameter (required by DB-03) |
| LIKE-based search | FTS5 | FTS5 faster at scale but CJK tokenizer broken for Chinese without jieba; LIKE is correct for v1 |

**Installation:**
```bash
uv add playwright beautifulsoup4 lxml python-dotenv rich
uv add --dev pytest
uv run playwright install chromium
```

---

## Architecture Patterns

### Recommended Project Structure

```
auto-jq-database/
├── run_scrape.py           # CLI entry: orchestrates full ingestion pipeline
├── auth.py                 # Session management: login + storageState load/save
├── scraper/
│   ├── __init__.py
│   ├── api_docs.py         # Extract API functions from /help/api/help pages
│   └── strategies.py       # Extract strategies from 经典策略学习 sidebar
├── db/
│   ├── __init__.py
│   ├── schema.py           # CREATE TABLE statements, index definitions
│   └── seed.py             # Upsert functions: write records to SQLite
├── tests/
│   ├── conftest.py         # Shared fixtures (in-memory SQLite, sample records)
│   ├── test_schema.py      # Schema creation, index existence, column types
│   ├── test_seed.py        # Upsert idempotency, null field handling
│   └── test_extraction.py  # Unit tests for HTML parsing logic (no browser needed)
├── auth.json               # Playwright storageState (gitignored)
├── .env                    # JoinQuant credentials (gitignored)
├── .gitignore
└── pyproject.toml
```

### Pattern 1: Session Check Before Login

**What:** On each run, check whether `auth.json` exists and whether the session is still valid (navigate to an authenticated endpoint and confirm logged-in state) before executing login.

**When to use:** Every scraper run. Avoids repeated login attempts that trigger rate-limiting.

**Example:**
```python
# auth.py
import os
from pathlib import Path
from playwright.sync_api import BrowserContext

AUTH_FILE = Path("auth.json")

def ensure_authenticated(context: BrowserContext) -> None:
    """Load existing session or perform fresh login."""
    page = context.new_page()
    try:
        page.goto("https://www.joinquant.com/algorithm/index/list", timeout=15000)
        # If redirected to login page, session is expired or absent
        if "login" in page.url or page.query_selector(".login-form") is not None:
            _do_login(page)
            context.storage_state(path=str(AUTH_FILE))
        # else: session valid, no login needed
    finally:
        page.close()

def _do_login(page) -> None:
    """Fill and submit JoinQuant login form."""
    page.goto("https://www.joinquant.com/login")
    page.fill('input[name="username"]', os.environ["JQ_USERNAME"])
    page.fill('input[name="password"]', os.environ["JQ_PASSWORD"])
    page.click('button[type="submit"]')
    page.wait_for_url("**/algorithm/**", timeout=30000)
```

### Pattern 2: Headed Discovery Spike

**What:** Run Playwright in headed mode on the first pass to inspect DOM structure, identify stable selectors, and confirm content loads correctly.

**When to use:** Wave 0 of Phase 1 — before any extraction code is committed to.

**Example:**
```python
# Headed mode for discovery
browser = playwright.chromium.launch(headless=False, slow_mo=500)
# Once selectors confirmed:
browser = playwright.chromium.launch(headless=True)
```

### Pattern 3: Wait-Then-Extract SPA Pattern

**What:** After `page.goto()`, always wait for a selector that proves the dynamic content has rendered before calling `page.content()` or extracting DOM nodes.

**When to use:** Every page navigation. JoinQuant is a React/Vue SPA — the initial HTML is an empty shell.

**Example:**
```python
# scraper/api_docs.py
def scrape_api_section(page, url: str) -> list[dict]:
    page.goto(url)
    # Wait for actual API function entries to appear — NOT networkidle
    page.wait_for_selector(".api-function-block, h3.func-title", timeout=20000)
    html = page.content()
    soup = BeautifulSoup(html, "lxml")
    return _parse_api_functions(soup)
```

### Pattern 4: Upsert for Idempotency (SCRP-08)

**What:** Use `INSERT OR REPLACE INTO` (or `INSERT ... ON CONFLICT DO UPDATE`) keyed on `function_name` for API docs and `(name, category)` for strategies.

**When to use:** Every write to SQLite. Guarantees second run produces identical row counts.

**Example:**
```python
# db/seed.py
def upsert_api_doc(conn, record: dict) -> None:
    conn.execute("""
        INSERT INTO api_docs (function_name, section, call_signature, description, return_type, example_code)
        VALUES (:function_name, :section, :call_signature, :description, :return_type, :example_code)
        ON CONFLICT(function_name) DO UPDATE SET
            section = excluded.section,
            call_signature = excluded.call_signature,
            description = excluded.description,
            return_type = excluded.return_type,
            example_code = excluded.example_code
    """, record)
```

### Pattern 5: Polite Scraping Delay

**What:** Sleep 2-3 seconds between page navigations.

**When to use:** Between every `page.goto()` call after the first.

**Example:**
```python
import time
import random

def polite_goto(page, url: str, min_delay: float = 2.0, max_delay: float = 3.0) -> None:
    time.sleep(random.uniform(min_delay, max_delay))
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
```

### Anti-Patterns to Avoid

- **Immediate `page.content()` after `page.goto()`:** Returns the empty SPA shell. Always wait for a content-proving selector first.
- **Re-login every run:** Triggers JoinQuant rate-limiting. Always check session validity and load `auth.json` first.
- **Storing parameters as a single text blob:** Violates DB-03. Parameters must be rows in `api_params`, not a concatenated string.
- **Direct URL navigation for strategy pages without fallback:** User decision states to try direct URLs first, fall back to sidebar click if they don't work. Do not assume either always works.
- **Committing `auth.json` or `.env` to git:** Contains live session cookies and credentials.

---

## SQLite Schema Design

### Recommended Schema (Claude's Discretion — Optimized for MCP Query Friendliness)

**Recommendation: Separate `api_params` table** (not JSON column)

**Rationale:** DB-03 requires parameters to be "searchable per-parameter" — this means `SELECT * FROM api_params WHERE name = 'start_date'` or `WHERE type = 'str'` must work. A JSON column requires `json_extract()` calls that are less intuitive for the MCP query layer. A separate table enables simple SQL that maps cleanly to MCP tool inputs.

```sql
-- schema.py

CREATE TABLE IF NOT EXISTS api_docs (
    function_name   TEXT PRIMARY KEY,       -- e.g., "get_security_info"
    section         TEXT NOT NULL,          -- e.g., "获取股票数据"
    call_signature  TEXT,                   -- e.g., "get_security_info(code)"
    description     TEXT,                   -- Chinese description from docs
    return_type     TEXT,                   -- e.g., "SecurityUnitData"
    example_code    TEXT,                   -- Code block from 示例 section
    scraped_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS api_params (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name   TEXT NOT NULL REFERENCES api_docs(function_name) ON DELETE CASCADE,
    param_name      TEXT NOT NULL,          -- e.g., "code"
    param_type      TEXT,                   -- e.g., "str"
    description     TEXT,                   -- Chinese description of the param
    is_required     INTEGER DEFAULT 1       -- 1=required, 0=optional (if determinable)
);

CREATE TABLE IF NOT EXISTS api_return_attrs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name   TEXT NOT NULL REFERENCES api_docs(function_name) ON DELETE CASCADE,
    attr_name       TEXT NOT NULL,          -- e.g., "display_name"
    attr_type       TEXT,                   -- e.g., "str"
    description     TEXT                    -- Chinese description of the return attribute
);

CREATE TABLE IF NOT EXISTS strategies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,          -- Strategy name from sidebar
    category        TEXT NOT NULL,          -- Sidebar category (e.g., "均值回归")
    description     TEXT,                   -- Brief description if available
    code_content    TEXT NOT NULL,          -- Full Python strategy code
    scraped_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(name, category)
);

-- Indexes for DB-05
CREATE INDEX IF NOT EXISTS idx_api_docs_section ON api_docs(section);
CREATE INDEX IF NOT EXISTS idx_strategies_category ON strategies(category);
CREATE INDEX IF NOT EXISTS idx_api_params_function ON api_params(function_name);
CREATE INDEX IF NOT EXISTS idx_api_return_function ON api_return_attrs(function_name);
```

**Note on DB-04 (Chinese LIKE search):** No FTS5 virtual table is needed for v1. LIKE-based search on `api_docs.description`, `api_docs.example_code`, and `strategies.code_content` is sufficient for hundreds of records. The decision in STATE.md confirmed: "LIKE-based Chinese text search for v1 (not FTS5 + jieba)."

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Browser session management | Custom cookie persistence | Playwright `context.storage_state()` | storageState captures cookies + localStorage + IndexedDB atomically |
| HTML parsing | Custom regex-based parser | BeautifulSoup4 + lxml | Real JoinQuant HTML will be nested, malformed, and mixed Chinese/English — regex breaks silently |
| SPA content waiting | `time.sleep(N)` fixed delays | `page.wait_for_selector(selector)` | Fixed sleeps are fragile and slow; event-driven waiting is both faster and more reliable |
| Upsert logic | Manual SELECT+INSERT/UPDATE | `INSERT ... ON CONFLICT DO UPDATE` | SQLite's native upsert is atomic and eliminates race conditions |
| Test database setup | Copying the production `.db` file | In-memory SQLite + `conftest.py` fixture | Tests must be hermetic; never run tests against live scraped data |

**Key insight:** The scraping domain has solved all the hard problems (browser automation, HTML parsing, session persistence) at the library level. Custom implementations of any of these are worse in every dimension.

---

## Common Pitfalls

### Pitfall 1: SPA Empty Shell — Content Not Loaded at `page.goto()` Return

**What goes wrong:** `page.content()` immediately after `page.goto()` returns `<div id="app"></div>` — the React/Vue shell with no content. Extracted text is empty or "加载中".

**Why it happens:** JoinQuant renders content client-side. `page.goto()` resolves when the network response arrives, not when JS has finished rendering.

**How to avoid:** Always call `page.wait_for_selector("[selector-proving-content-exists]", timeout=20000)` before extraction. Use a selector that only appears after the actual data has rendered (e.g., a function name heading, not a generic container).

**Warning signs:** Extracted text is empty strings; database row count is 0; scrape completes unusually fast (nothing iterated).

### Pitfall 2: Login Rate-Limiting From Repeated Full Logins

**What goes wrong:** JoinQuant detects repeated login events from the same automation fingerprint and triggers CAPTCHA or temporary block.

**Why it happens:** Storing no session state means every scraper run logs in fresh.

**How to avoid:** Save `auth.json` after the first successful login. On subsequent runs: check if `auth.json` exists AND navigate to an authenticated page to confirm session is live. Only call the login flow if the session test fails.

**Warning signs:** Scraper works the first 2-3 times then fails; login page appears mid-scrape; CAPTCHA elements detected in DOM.

### Pitfall 3: Brittle CSS Selectors From Auto-Generated Class Names

**What goes wrong:** Selectors like `.css-1a2b3c` or `.sc-bdnxRM` stop working after JoinQuant deploys a frontend update. Scraper runs silently with 0 results.

**Why it happens:** React/Next.js with CSS Modules generates unique class names per build. These are not stable.

**How to avoid:** Prefer selectors based on element semantics: element tags, `data-*` attributes, stable human-readable class names, text content matching. Add post-extraction row count assertions: if a section produces 0 rows, fail loudly rather than writing an empty database.

**Warning signs:** Scrape completes very fast; all extracted fields are null; row count is 0 or far below previous run.

### Pitfall 4: Strategy Page Requires Sidebar Navigation, Not Direct URL

**What goes wrong:** Direct URL navigation to a strategy page may not load the content if JoinQuant uses client-side routing that requires the sidebar to be initialized first.

**Why it happens:** SPA state management — strategy detail pages may only render correctly when reached via the sidebar navigation that sets up the parent category state.

**How to avoid:** Try direct URL first (per user decision). If the strategy content selector is not found within timeout, fall back to sidebar click navigation. Implement the fallback path before the first full scrape run.

**Warning signs:** Direct URL navigation lands on the page but `code_content` is empty; other page elements render but the strategy code block is missing.

### Pitfall 5: `auth.json` Committed to Git

**What goes wrong:** Live session cookies (capable of full account access) are in version control history permanently.

**Why it happens:** The file is created by the scraper in the project root and developers forget to `.gitignore` it.

**How to avoid:** Add `auth.json` and `.env` to `.gitignore` before the first `git add`. Verify with `git status` before every commit.

**Warning signs:** `git status` shows `auth.json` as a new untracked file; `git log --all -- auth.json` shows prior commits.

---

## Code Examples

Verified patterns from official Playwright Python documentation:

### Session Save After Login
```python
# Source: https://playwright.dev/python/docs/auth
# After successful login:
context.storage_state(path="auth.json")
```

### Session Load on Subsequent Runs
```python
# Source: https://playwright.dev/python/docs/auth
# On next run, before navigating to any page:
context = browser.new_context(storage_state="auth.json")
```

### Full Scraper Entry Point Pattern
```python
# run_scrape.py
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from auth import ensure_authenticated
from scraper.api_docs import scrape_all_api_sections
from scraper.strategies import scrape_all_strategies
from db.schema import init_db
from db.seed import upsert_api_doc, upsert_api_params, upsert_strategy

AUTH_FILE = Path("auth.json")
DB_FILE = Path("jq_knowledge.db")

def main():
    conn = init_db(DB_FILE)

    with sync_playwright() as p:
        storage = str(AUTH_FILE) if AUTH_FILE.exists() else None
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage)

        ensure_authenticated(context)  # Login if needed, save auth.json

        # Scrape API docs (public pages, no login needed but use same context)
        api_records = scrape_all_api_sections(context)
        for record in api_records:
            upsert_api_doc(conn, record)
            upsert_api_params(conn, record["function_name"], record["params"])

        # Scrape strategies (requires authenticated session)
        strategy_records = scrape_all_strategies(context)
        for record in strategy_records:
            upsert_strategy(conn, record)

        browser.close()

    conn.close()
    print(f"Done. API docs: {count_rows(DB_FILE, 'api_docs')}, Strategies: {count_rows(DB_FILE, 'strategies')}")
```

### BeautifulSoup HTML Extraction Pattern
```python
# scraper/api_docs.py
from bs4 import BeautifulSoup

def _parse_api_functions(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    records = []

    # Selector TBD from discovery spike — placeholder structure
    for func_block in soup.select(".api-function-block"):
        name_el = func_block.select_one(".func-name")
        if not name_el:
            continue  # Never skip — per user decision, store partial data

        record = {
            "function_name": name_el.get_text(strip=True),
            "call_signature": _extract_text(func_block, ".call-method"),
            "description": _extract_text(func_block, ".description"),
            "return_type": _extract_text(func_block, ".return-type"),
            "example_code": _extract_text(func_block, ".example-code"),
            "params": _extract_params(func_block),
        }
        records.append(record)

    return records

def _extract_text(soup_el, selector: str) -> str | None:
    el = soup_el.select_one(selector)
    return el.get_text(strip=True) if el else None

def _extract_params(func_block) -> list[dict]:
    params = []
    for row in func_block.select(".param-row"):
        params.append({
            "param_name": _extract_text(row, ".param-name"),
            "param_type": _extract_text(row, ".param-type"),
            "description": _extract_text(row, ".param-desc"),
        })
    return params
```

**Note:** Selectors above are placeholders. The Wave 0 discovery spike must identify actual JoinQuant DOM structure before these are finalized.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Selenium for browser automation | Playwright | ~2021, accelerated 2023+ | Auto-waiting, better async, native storageState |
| pip + venv | uv | 2024-2025 | 10-100x faster installs, lockfile by default |
| requests alone for authenticated scraping | Playwright for login + optional requests | 2020+ | JavaScript-managed auth requires a real browser |
| FTS5 with unicode61 for Chinese | LIKE-based search (v1) / jieba pre-tokenization (v2+) | Known limitation since FTS5 introduction | Correct approach for Chinese at v1 scale |

---

## Open Questions

1. **JoinQuant DOM structure for API docs pages**
   - What we know: Pages at `joinquant.com/help/api/help#Stock:...` are SPA-rendered; they contain structured function documentation with parameters, return values, and examples
   - What's unclear: Exact CSS selectors, whether content is in the initial DOM or loaded via XHR after hash navigation, whether each function has a consistent wrapper element
   - Recommendation: Wave 0 discovery spike — open browser headed, navigate to each of the 4 target pages, use browser DevTools to inspect the DOM structure before writing any extraction code

2. **Strategy sidebar navigation structure**
   - What we know: "经典策略学习" uses a sidebar menu with categories; strategies may be reachable via direct URL or may require sidebar click
   - What's unclear: How many categories exist, whether category names are stable text or rendered from JS state, whether each strategy has a stable identifier in the URL
   - Recommendation: Part of Wave 0 spike — navigate to the strategies section while logged in and inspect the sidebar DOM

3. **Login form selectors on JoinQuant**
   - What we know: Standard form fill with username/password; submit button; session confirmed by redirect to authenticated page
   - What's unclear: Whether JoinQuant uses CSRF tokens, whether the login form is rendered client-side or server-side, whether there's a slide CAPTCHA on first automated login
   - Recommendation: Test login manually in headed Playwright at Wave 0 before scripting it

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | `pyproject.toml` — `[tool.pytest.ini_options]` (Wave 0 task) |
| Quick run command | `uv run pytest tests/ -x -q` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCRP-08 | Second upsert produces same row counts, no duplicates | unit | `pytest tests/test_seed.py::test_upsert_idempotency -x` | Wave 0 |
| DB-01 | api_docs table has correct columns (function_name, section, call_signature, description, return_type, example_code) | unit | `pytest tests/test_schema.py::test_api_docs_columns -x` | Wave 0 |
| DB-02 | strategies table has correct columns (name, category, code_content, description) | unit | `pytest tests/test_schema.py::test_strategies_columns -x` | Wave 0 |
| DB-03 | api_params table allows SELECT by param_name | unit | `pytest tests/test_schema.py::test_params_queryable -x` | Wave 0 |
| DB-04 | LIKE query on description returns Chinese-matching rows | unit | `pytest tests/test_schema.py::test_chinese_like_search -x` | Wave 0 |
| DB-05 | Index exists on api_docs.section and strategies.category | unit | `pytest tests/test_schema.py::test_indexes_exist -x` | Wave 0 |
| SCRP-01–07 | Extracted records from live pages contain non-null function_name | smoke (manual) | Run `python run_scrape.py` and check row counts | manual |
| SCRP-02 | Second run loads auth.json, does not re-execute login | smoke (manual) | Run scraper twice; confirm second run skips login flow | manual |

**Note on live scraping tests:** SCRP-01 through SCRP-07 require live browser access to JoinQuant and cannot be automated in a standard pytest run. These are validated manually by running `python run_scrape.py` and inspecting the resulting SQLite database.

### Sampling Rate

- **Per task commit:** `uv run pytest tests/ -x -q`
- **Per wave merge:** `uv run pytest tests/ -v`
- **Phase gate:** Full suite green + manual smoke test confirming non-zero row counts before Phase 2

### Wave 0 Gaps

- [ ] `tests/conftest.py` — in-memory SQLite fixture, sample `api_docs` and `strategies` records
- [ ] `tests/test_schema.py` — schema creation, column presence, index existence, LIKE search
- [ ] `tests/test_seed.py` — upsert idempotency, null field handling, ON CONFLICT behavior
- [ ] `tests/test_extraction.py` — HTML parsing unit tests (sample HTML strings, no browser required)
- [ ] `pyproject.toml` — pytest configuration, test path settings
- [ ] Framework install: `uv add --dev pytest`

---

## Sources

### Primary (HIGH confidence)
- [Playwright Python Auth Docs](https://playwright.dev/python/docs/auth) — storageState save/load patterns (verified 2026-03-22)
- [SQLite JSON Functions](https://sqlite.org/json1.html) — JSON column vs separate table tradeoffs
- [SQLite FTS5](https://www.sqlite.org/fts5.html) — confirmed CJK tokenizer limitation
- `.planning/research/STACK.md` — verified stack: Python 3.12, Playwright 1.58.0, beautifulsoup4 4.12.x, lxml 5.x, uv
- `.planning/research/PITFALLS.md` — SPA rendering, session persistence, selector brittleness pitfalls

### Secondary (MEDIUM confidence)
- [JSON and Virtual Columns in SQLite](https://antonz.org/json-virtual-columns/) — practical JSON vs relational column comparison
- [Playwright Scraping Guide 2026](https://oxylabs.io/blog/playwright-web-scraping) — `wait_for_selector` best practices
- `.planning/research/ARCHITECTURE.md` — component separation pattern (ingestion vs exposure layers)

### Tertiary (LOW confidence — needs live validation)
- JoinQuant DOM structure and CSS selectors: unverifiable without headed browser session; must be confirmed in Wave 0 discovery spike
- JoinQuant login flow details (CSRF, CAPTCHA behavior): inferred from common Chinese platform patterns; must be confirmed during Wave 0

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified against PyPI/official docs in prior research (STACK.md)
- Schema design: HIGH — SQLite schema recommendations are standard SQL; separate params table decision grounded in DB-03 requirements
- Playwright patterns: HIGH — from official Playwright Python documentation
- JoinQuant-specific DOM/selectors: LOW — cannot be verified without live browser access; Wave 0 discovery spike required before extraction code is written
- Pitfalls: HIGH for general Playwright/SQLite pitfalls; MEDIUM for JoinQuant-specific behavior

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (Playwright APIs are stable; JoinQuant DOM may change on any deploy)
