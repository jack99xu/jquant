# JoinQuant API & Strategy Knowledge Base

## What This Is

A local knowledge base that scrapes JoinQuant (聚宽) API documentation from all 9 help pages, stores structured data (221 functions, 2479 table columns) in SQLite, and exposes it via a FastMCP server over stdio. AI models query exact API signatures, parameters, return values, and examples instead of guessing.

## Core Value

AI models can query accurate JoinQuant API documentation (function signatures, parameters, return values, examples) so they write correct JoinQuant code on the first try.

## Requirements

### Validated

- ✓ Automated browser scraping of JoinQuant API docs (all 9 help pages) — v1.0
- ✓ SQLite database schema for API docs (function name, parameters, return type, description, examples) — v1.0
- ✓ SQLite database schema for strategy code (name, category, code content, description) — v1.0
- ✓ Parameters stored as structured per-parameter records, not blobs — v1.0
- ✓ MCP server with 6 tools (lookup, search, section filter, section-scoped search, list functions, table columns) — v1.0
- ✓ Login automation with session persistence and CAPTCHA helper — v1.0
- ✓ Read-only database access, no mutations exposed — v1.0
- ✓ Chinese text searchable via LIKE queries — v1.0
- ✓ Idempotent scraper (re-run produces identical data, no duplicates) — v1.0

### Active

- [ ] Natural language strategy generation: user describes strategy → system uses stored API docs as context → outputs correct JoinQuant strategy Python file
- [ ] Strategy examples searchable via MCP (not just API docs)
- [ ] Scrape additional JoinQuant API sections (期货、期权、指数 etc)

### Out of Scope

- Real-time sync with JoinQuant — API docs are stable; manual re-scrape sufficient
- Semantic/vector search — LIKE sufficient for structured API docs with known terminology
- Web UI for browsing docs — consumer is AI models, not humans
- Multi-user auth on MCP — local stdio server on developer's machine

## Context

Shipped v1.0 with 2,665 LOC Python. Tech stack: Python, uv, Playwright, BeautifulSoup4, SQLite, FastMCP.

- JoinQuant (聚宽) is a Chinese quantitative trading platform with its own Python SDK
- AI models frequently guess JoinQuant API signatures incorrectly because the docs aren't in their training data
- API docs are publicly accessible at joinquant.com/help/api/help (single 635KB HTML file)
- Strategy content requires phone number login with jigsaw CAPTCHA — gen_auth.py provides headed browser helper
- Database contains 221 API functions and 2,479 table column definitions

## Constraints

- **Storage**: SQLite — simple, portable, no server setup required
- **Scraping**: Playwright headed browser for login, public pages for API docs
- **MCP Transport**: stdio only (local developer machine)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| SQLite over PostgreSQL | Simplicity, portability, easy to share the .db file | ✓ Good |
| Automated scraping over manual | Too many strategies to copy manually, reproducible | ✓ Good |
| API doc lookup only (no strategy search in MCP) | Core problem is incorrect API usage, not finding strategies | ✓ Good — validated by usage |
| LIKE-based Chinese search (not FTS5 + jieba) | Sufficient for hundreds of records, avoids tokenizer complexity | ✓ Good |
| Separate api_params table (not JSON column) | Per-parameter queryability for MCP tools | ✓ Good |
| check_same_thread=False for SQLite | MCP stdio transport dispatches on different thread; read-only is safe | ✓ Good |
| OpenAI API for code generation | User wants LLM-powered strategy generation using stored docs as context | — Pending (v2) |

---
*Last updated: 2026-03-23 after v1.0 milestone*
