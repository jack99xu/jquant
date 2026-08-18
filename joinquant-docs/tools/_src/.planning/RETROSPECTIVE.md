# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-22
**Phases:** 2 | **Plans:** 7 | **Sessions:** ~3

### What Was Built
- Playwright-based scraper for JoinQuant API docs (221 functions, 2479 table columns from 9 help pages)
- Strategy scraper with auth session persistence and CAPTCHA-gated login helper
- SQLite database with 4 tables, structured per-parameter storage, idempotent upserts
- FastMCP server with 6 query tools over stdio transport
- End-to-end Claude Desktop/Code integration

### What Worked
- Discovery spike (Phase 1, Plan 02) before committing to selectors saved significant rework — JoinQuant DOM structure and auth flow were not predictable
- Separating API doc scraping (public) from strategy scraping (auth-gated) allowed Phase 2 to proceed without valid phone credentials
- TDD approach for server tools caught the row_factory issue early
- Single HTML file discovery (all 4 API sections in 635KB) simplified scraper architecture

### What Was Inefficient
- Strategy scraper required multiple rewrites due to auth/CAPTCHA blocking — could have deprioritized earlier
- Gap closure plan (01-05) addressed real DOM parsing issues but was triggered by verification, not caught in initial implementation
- Thread safety issue (check_same_thread) only surfaced during real MCP integration, not unit tests

### Patterns Established
- `gen_auth.py` headed browser helper for CAPTCHA-gated sessions
- Module-level `_conn` with monkey-patching for test isolation
- Section-boundary scoping to prevent cross-section duplication in single-page HTML parsing

### Key Lessons
1. JoinQuant web login requires phone number, not API key — document auth requirements early when scraping Chinese platforms
2. Always test SQLite connections with `check_same_thread=False` when used in MCP/async contexts
3. Public API doc pages can be scraped without authentication — separate auth-dependent and auth-independent work

### Cost Observations
- Model mix: ~10% opus (orchestration), ~90% sonnet (execution)
- Sessions: ~3
- Notable: Entire project from zero to shipped MCP server in a single day

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | ~3 | 2 | First milestone — established scraper + MCP server pattern |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | 25 | ~80% | 2 (fastmcp, playwright) |

### Top Lessons (Verified Across Milestones)

1. Discovery spikes before committing to scraping selectors save significant rework
2. Separate auth-dependent from auth-independent work paths for resilient pipelines
