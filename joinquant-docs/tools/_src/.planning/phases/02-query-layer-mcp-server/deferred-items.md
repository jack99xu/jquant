# Deferred Items

## Out-of-scope issues discovered during Phase 02 Plan 01

### 1. Pre-existing test_seed.py failure (test_upsert_api_doc_insert)

- **Discovered during:** Task 2 full test suite run
- **Issue:** `tests/test_seed.py::test_upsert_api_doc_insert` fails with `sqlite3.ProgrammingError: You did not supply a value for binding parameter :chinese_name`
- **Root cause:** The test passes a dict without `chinese_name` key but `db/seed.py` `upsert_api_doc` uses `:chinese_name` binding in the SQL query without defaulting missing keys to `None`
- **Pre-existing:** Confirmed — failure reproduces on commit before Phase 02 Plan 01 work
- **Impact:** None on new server.py functionality
- **Suggested fix:** Either add `chinese_name=None` defaults to test fixture dict, or use `record.get('chinese_name')` in `upsert_api_doc`
