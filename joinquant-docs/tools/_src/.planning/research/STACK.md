# Stack Research

**Domain:** Web scraper + SQLite storage + MCP server (Chinese quant platform)
**Researched:** 2026-03-22
**Confidence:** HIGH (core stack verified against PyPI/official docs)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12 | Runtime | Sweet spot: 3.10 required by mcp/fastmcp, 3.12 is fastest stable release, 3.13 still too new for ecosystem stability |
| playwright | 1.58.0 | Browser automation for login + scraping | Only tool that reliably handles SPAs, cookie-based auth, and dynamic JS rendering — essential for JoinQuant's authenticated content |
| fastmcp | 3.1.1 | MCP server framework | FastMCP powers ~70% of all MCP servers across languages; higher-level API than official SDK with decorator-based tool registration, handles schema gen automatically |
| sqlite3 | stdlib | Database storage | Built-in, zero deps, FTS5 support for keyword search, perfect for single-file portable knowledge bases |
| uv | latest | Package + project management | 10-100x faster than pip, built-in lockfile, replaces pip+venv+virtualenv with one tool; 2025 standard |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| beautifulsoup4 | 4.12.x | HTML parsing after Playwright renders page | Use when extracting structured content from rendered HTML; easier API than lxml for navigating messy real-world markup |
| lxml | 5.x | Fast HTML/XML parser backend for BS4 | Install alongside BS4; specify `html.parser="lxml"` for 5-10x parse speedup on large documents |
| python-dotenv | 1.x | Load credentials from .env file | Required to keep JoinQuant credentials out of source code |
| rich | 13.x | Terminal output formatting | Progress indicators and structured logging during long scrape runs — not required but eliminates print() debugging |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Project init, dependency management, venv creation | `uv init`, `uv add playwright fastmcp beautifulsoup4 lxml python-dotenv` |
| playwright install | Download browser binaries | `uv run playwright install chromium` — only Chromium needed, reduces download size |
| sqlite3 CLI | Database inspection during development | Built into macOS, use to verify schema and query data manually |
| ruff | Linting + formatting | Single tool replacing black + flake8 + isort; fast, zero config needed |

## Installation

```bash
# Init project with uv
uv init auto-jq-database
cd auto-jq-database

# Core dependencies
uv add playwright fastmcp beautifulsoup4 lxml python-dotenv

# Dev dependencies
uv add --dev ruff

# Install Playwright browser binaries (Chromium only — smaller footprint)
uv run playwright install chromium
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| fastmcp 3.1.1 | Official mcp SDK 1.26.0 | Use official SDK only if you need maximum protocol-level control or are building MCP infrastructure (not a tool server) |
| Playwright | Selenium | Never for new projects in 2026 — Playwright has better async support, auto-waiting, and session state APIs |
| Playwright | requests + httpx | Only if JoinQuant served static HTML with no JS rendering — it doesn't; login sets JS-managed session state |
| sqlite3 stdlib | SQLAlchemy | Use SQLAlchemy only if you need to support multiple databases or plan to migrate to PostgreSQL; adds indirection with no benefit here |
| sqlite3 stdlib | Peewee ORM | Peewee is lightweight but FTS5 support is awkward through ORM; raw sqlite3 is simpler for this use case |
| BeautifulSoup4 + lxml | selectolax | Selectolax is faster but has smaller ecosystem and less documentation; BS4 + lxml backend closes the performance gap enough |
| uv | pip + venv | pip+venv works but uv is now the community standard; lockfile reproducibility matters for a scraper that should re-run reliably |
| Python | Node.js | Node.js + Playwright is Playwright's "native" environment, but Python is more ergonomic for SQLite and MCP tool development; performance difference is irrelevant for a one-time scrape |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Scrapy | Built for crawling link graphs, not targeted authenticated scraping of known pages; massive overhead for 4 API doc pages + strategy list | Playwright directly |
| Puppeteer | Node.js only; would require two language ecosystems for a single project | Playwright (Python) |
| Selenium | Auto-wait is manual (explicit/implicit waits), session state saving requires third-party libraries, no first-class async support, slower than Playwright | Playwright |
| requests / httpx alone | JoinQuant login sets cookies via JavaScript; plain HTTP clients can't execute JS and will get redirect loops or empty responses | Playwright for login, then optionally save cookies for static pages |
| SQLAlchemy for FTS5 | No native FTS5 ORM support; you end up writing raw SQL anyway, so SQLAlchemy adds a dependency with zero benefit for this schema | sqlite3 stdlib + raw SQL |
| Poetry | Slower than uv, larger footprint, overlapping concerns with modern uv; still viable but no longer the default choice in 2025 | uv |
| mcp-server-sqlite (PyPI package) | The official Anthropic SQLite MCP reference is archived/deprecated, not maintained | Build a custom FastMCP server exposing your specific tools |

## Stack Patterns by Variant

**If JoinQuant adds Cloudflare Bot Protection (unlikely — they use Alibaba Cloud infra):**
- Use Playwright with `--channel=chrome` to use real Chrome binary instead of Chromium
- Add `playwright.chromium.launch(channel="chrome")` — requires Google Chrome installed locally
- Do NOT use undetected-chromedriver (Selenium only) or FlareSolverr (Docker overhead)

**If scraping needs to run repeatedly on a schedule (v2+):**
- Add session state persistence: save `context.storage_state()` to `auth_state.json` after first login
- Reload on subsequent runs with `browser.new_context(storage_state="auth_state.json")`
- This avoids re-login on every run without storing passwords in memory

**If the MCP server needs to be used from Claude Desktop (most likely use case):**
- FastMCP stdio transport is the right choice (default)
- No HTTP server needed — Claude Desktop spawns the process directly
- `fastmcp run server.py` or `uv run python server.py` in Claude Desktop config

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| fastmcp 3.1.1 | Python >=3.10 | Requires mcp >=1.2.0 as a transitive dependency |
| mcp 1.26.0 | Python >=3.10 | Automatically installed by fastmcp |
| playwright 1.58.0 | Python >=3.9 | No conflict with Python 3.12 target |
| beautifulsoup4 4.12.x | lxml 5.x | Use `BeautifulSoup(html, "lxml")` parser string to activate lxml backend |

## Sources

- https://pypi.org/project/fastmcp/ — Version 3.1.1, released 2026-03-14, Python >=3.10 (verified)
- https://pypi.org/project/mcp/ — Version 1.26.0, released 2026-01-24, Python >=3.10 (verified)
- https://pypi.org/project/playwright/ — Version 1.58.0, released 2026-01-30, Python >=3.9 (verified)
- https://github.com/modelcontextprotocol/python-sdk — Official MCP Python SDK repo
- https://gofastmcp.com/ — FastMCP official documentation
- https://playwright.dev/python/docs/auth — Playwright session/cookie persistence patterns
- https://realpython.com/python-uv/ — uv vs pip/venv comparison (MEDIUM confidence, community source)
- https://dev.to/dmitriiweb/beautifulsoup-vs-lxml-a-practical-performance-comparison-1l0a — BS4 vs lxml benchmarks (MEDIUM confidence)
- https://www.sqlite.org/fts5.html — SQLite FTS5 official docs

---
*Stack research for: JoinQuant API & Strategy Knowledge Base (web scraper + SQLite + MCP server)*
*Researched: 2026-03-22*
