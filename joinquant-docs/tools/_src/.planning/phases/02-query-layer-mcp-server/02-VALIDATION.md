---
phase: 2
slug: query-layer-mcp-server
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (already in `[dependency-groups] dev`) |
| **Config file** | `pyproject.toml` — `[tool.pytest.ini_options]` with `testpaths = ["tests"]`, `pythonpath = ["."]` |
| **Quick run command** | `uv run pytest tests/test_server.py -x` |
| **Full suite command** | `uv run pytest tests/ -x` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_server.py -x`
- **After every plan wave:** Run `uv run pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | MCP-06 | unit | `uv run pytest tests/test_server.py::test_db_read_only -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | MCP-01 | unit | `uv run pytest tests/test_server.py::test_lookup_function_returns_full_doc -x` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | MCP-01 | unit | `uv run pytest tests/test_server.py::test_lookup_function_not_found -x` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | MCP-02 | unit | `uv run pytest tests/test_server.py::test_search_docs_chinese_keyword -x` | ❌ W0 | ⬜ pending |
| 02-01-05 | 01 | 1 | MCP-02 | unit | `uv run pytest tests/test_server.py::test_search_docs_no_results -x` | ❌ W0 | ⬜ pending |
| 02-01-06 | 01 | 1 | MCP-03 | unit | `uv run pytest tests/test_server.py::test_list_by_section -x` | ❌ W0 | ⬜ pending |
| 02-01-07 | 01 | 1 | MCP-04 | unit | `uv run pytest tests/test_server.py::test_search_in_section_scoped -x` | ❌ W0 | ⬜ pending |
| 02-01-08 | 01 | 1 | MCP-05 | unit | `uv run pytest tests/test_server.py::test_response_format -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_server.py` — stubs for MCP-01 through MCP-06 (8 test functions)
- [ ] `tests/conftest.py` update — add `seeded_db_conn` fixture with sample api_docs + api_params + api_return_attrs + table_columns rows
- [ ] `uv add fastmcp` — dependency not yet in pyproject.toml

*Wave 0 must complete before any implementation tasks begin.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Claude Desktop connects to MCP server | MCP-06 | Requires Claude Desktop running | 1. Add server config to `claude_desktop_config.json` 2. Restart Claude Desktop 3. Verify connection in logs |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
