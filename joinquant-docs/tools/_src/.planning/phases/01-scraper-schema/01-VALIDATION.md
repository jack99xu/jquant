---
phase: 1
slug: scraper-schema
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pyproject.toml` — `[tool.pytest.ini_options]` (Wave 0 installs) |
| **Quick run command** | `uv run pytest tests/ -x -q` |
| **Full suite command** | `uv run pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x -q`
- **After every plan wave:** Run `uv run pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 0 | DB-01 | unit | `pytest tests/test_schema.py::test_api_docs_columns -x` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 0 | DB-02 | unit | `pytest tests/test_schema.py::test_strategies_columns -x` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 0 | DB-03 | unit | `pytest tests/test_schema.py::test_params_queryable -x` | ❌ W0 | ⬜ pending |
| 01-01-04 | 01 | 0 | DB-04 | unit | `pytest tests/test_schema.py::test_chinese_like_search -x` | ❌ W0 | ⬜ pending |
| 01-01-05 | 01 | 0 | DB-05 | unit | `pytest tests/test_schema.py::test_indexes_exist -x` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | SCRP-08 | unit | `pytest tests/test_seed.py::test_upsert_idempotency -x` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 2 | SCRP-01 | smoke | Run `python run_scrape.py` — check login succeeds | manual | ⬜ pending |
| 01-03-02 | 03 | 2 | SCRP-02 | smoke | Run scraper twice — second run skips login | manual | ⬜ pending |
| 01-04-01 | 04 | 2 | SCRP-03–07 | smoke | Run `python run_scrape.py` — check non-zero row counts | manual | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` — in-memory SQLite fixture, sample `api_docs` and `strategies` records
- [ ] `tests/test_schema.py` — schema creation, column presence, index existence, LIKE search
- [ ] `tests/test_seed.py` — upsert idempotency, null field handling, ON CONFLICT behavior
- [ ] `tests/test_extraction.py` — HTML parsing unit tests (sample HTML strings, no browser required)
- [ ] `pyproject.toml` — pytest configuration under `[tool.pytest.ini_options]`
- [ ] Framework install: `uv add --dev pytest`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Login succeeds with stored credentials | SCRP-01 | Requires live JoinQuant access | Run `python run_scrape.py` headed; confirm browser logs in and redirects to authenticated page |
| Session persists across runs | SCRP-02 | Requires live auth.json from prior login | Run scraper twice; second run should not show login form interaction |
| API doc pages scraped correctly | SCRP-04–07 | Requires live JoinQuant pages | Run scraper; inspect `api_docs` table for non-zero rows with non-null function_name |
| Strategy pages scraped correctly | SCRP-03 | Requires live JoinQuant login + sidebar | Run scraper; inspect `strategies` table for non-zero rows with code_content populated |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
