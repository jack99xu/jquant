---
phase: 01-scraper-schema
plan: 03
subsystem: scraper
tags: [playwright, beautifulsoup4, lxml, sqlite, python, chinese, html-parsing, tdd]

# Dependency graph
requires:
  - phase: 01-scraper-schema/01-02
    provides: SELECTORS.md with confirmed CSS selectors and DOM structure for JoinQuant API docs
  - phase: 01-scraper-schema/01-01
    provides: db/seed.py upsert functions (upsert_api_doc, upsert_api_params, upsert_api_return_attrs)

provides:
  - scraper/api_docs.py — scrape_all_api_sections, scrape_api_section, _parse_api_functions
  - tests/test_extraction.py — 12 unit tests validating HTML parsing with sample HTML (no browser)

affects: [run_scrape.py, phase-02-mcp-server]

# Tech tracking
tech-stack:
  added: []  # beautifulsoup4, lxml, playwright already installed in plan 01
  patterns:
    - "h4-sibling traversal: collect siblings until next h2/h3/h4, extract by paragraph label text"
    - "article-h5 extraction: organize article children by h5 section label, extract by key"
    - "function_name derived from call_signature pre element (text before first '('), not h4 text"
    - "partial data stored as None, never skipped"
    - "polite delay: time.sleep(random.uniform(2.0, 3.0)) between page navigations"

key-files:
  created:
    - scraper/api_docs.py
    - tests/test_extraction.py
  modified: []

key-decisions:
  - "Function name extracted from call_signature pre element (text before '('), not h4 heading text — h4 contains Chinese section labels, not Python function names"
  - "Two parsing strategies: h4-sibling traversal for simple functions, article-h5 structure for complex functions (get_fundamentals etc.)"
  - "Return type extracted from text paragraph after '返回值' label; return_attrs extracted from table after same label — mutually exclusive patterns"
  - "Params extracted from both table and ul formats (real JoinQuant pages use both)"

patterns-established:
  - "Pattern: Parse h4 function blocks by collecting siblings until next heading, then extract by paragraph label marker"
  - "Pattern: Parse article blocks by organizing children by h5 section header text"
  - "Pattern: Derive function_name from call signature (pre element), fall back to h4 id, then h4 text"
  - "Pattern: All extraction helpers return None for missing data (never raise, never omit key)"

requirements-completed: [SCRP-04, SCRP-05, SCRP-06, SCRP-07]

# Metrics
duration: 4min
completed: 2026-03-22
---

# Phase 1 Plan 03: API Docs Scraper Summary

**JoinQuant API doc scraper using h4-sibling traversal and article-h5 extraction, with 12 pytest unit tests validating all parsing behaviors against sample HTML (no browser required)**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-03-22T11:55:04Z
- **Completed:** 2026-03-22T11:59:00Z
- **Tasks:** 1 (TDD)
- **Files modified:** 2

## Accomplishments

- `scraper/api_docs.py` — full extraction module with `scrape_all_api_sections`, `scrape_api_section`, `_parse_api_functions`, and all helper functions
- `tests/test_extraction.py` — 12 unit tests covering single function, params table, return attrs, missing fields, multiple functions, Chinese content, article blocks, mixed h4+article, empty HTML, and partial data
- All 29 project tests pass (12 extraction + 8 schema + 9 seed)
- Real selectors from SELECTORS.md used throughout (no placeholders)
- Polite 2-3 second random delay between page navigations

## Task Commits

Each task was committed atomically:

1. **Task 1: API docs extraction module with unit tests** - `6762ab7` (feat)

## Files Created/Modified

- `scraper/api_docs.py` — API doc scraper with two DOM parsing strategies (h4-sibling + article-h5), polite delays, content-ready wait, and 0-record warning
- `tests/test_extraction.py` — 12 unit tests validating all parsing behaviors using sample HTML strings that mirror the real JoinQuant DOM structure

## Decisions Made

- **Function name from call signature**: The h4 heading text is a Chinese section label (e.g., "获取股票基本信息"), not the Python function name. Function name is extracted by splitting the call signature pre element on `(`. Falls back to h4 `id` attribute (which in the real DOM often contains the English function name), then h4 text as last resort.
- **Two parsing strategies**: SELECTORS.md documented two distinct DOM patterns. h4-level for most functions (p/pre/ul siblings), article-level for complex functions (get_fundamentals, etc.) with h5 sub-structure. Both are handled.
- **Params in both ul and table formats**: Real JoinQuant pages use both formats. Both `_extract_params_from_ul` and `_extract_params_from_table` are implemented and chosen based on which element appears in the params section.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Function name extraction from call signature instead of h4 text**
- **Found during:** Task 1 (GREEN phase — first test run)
- **Issue:** Initial implementation used h4 text as function_name, but h4 contains Chinese section labels. Tests asserting `r["function_name"] == "get_security_info"` failed with `'获取股票基本信息'`.
- **Fix:** Derive function_name by splitting the call signature pre element text on `(`. Added fallback to h4 id attribute (often contains English function name) then h4 text.
- **Files modified:** scraper/api_docs.py
- **Verification:** All 12 extraction tests pass with correct function names
- **Committed in:** 6762ab7

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug)
**Impact on plan:** Essential fix for correct function_name extraction. No scope creep.

## Issues Encountered

- Initial parsing assumed h4 text == function name. Real DOM has Chinese headings in h4 text; English function names come from call signatures or h4 id attributes. Fixed during GREEN phase.

## Next Phase Readiness

- `scraper/api_docs.py` is ready to be called from `run_scrape.py` to populate the SQLite database
- Record format matches exactly what `db/seed.py` `upsert_api_doc`, `upsert_api_params`, and `upsert_api_return_attrs` expect
- Phase 1 Plan 04 (run_scrape.py orchestration) can now be executed

## Self-Check: PASSED

All created files verified present. All commits verified in git log.

---
*Phase: 01-scraper-schema*
*Completed: 2026-03-22*
