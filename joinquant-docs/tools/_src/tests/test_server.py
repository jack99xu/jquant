import pytest
import server


@pytest.fixture(autouse=True)
def patch_db(seeded_db, monkeypatch):
    monkeypatch.setattr(server, "_conn", seeded_db)


def test_lookup_function_returns_full_doc():
    result = server.lookup_function("get_price")
    assert "get_price" in result
    assert "security" in result          # param name present
    assert "str/list" in result           # param type present
    assert "open" in result               # return attr present
    assert 'get_price("000001.XSHE"' in result  # example code present
    assert "获取行情数据" in result         # chinese_name present


def test_lookup_function_not_found():
    result = server.lookup_function("nonexistent_xyz")
    assert "not found" in result.lower()
    assert "get_" in result  # fuzzy suggestion present (prefix match)


def test_search_docs_chinese_keyword():
    result = server.search_docs("融资融券")
    assert "get_mtss" in result
    assert "获取融资融券标的列表" in result  # section present


def test_search_docs_no_results():
    result = server.search_docs("totally_absent_xyz")
    assert "no" in result.lower() and ("found" in result.lower() or "result" in result.lower())


def test_list_by_section():
    result = server.list_by_section("获取股票数据")
    assert "get_price" in result
    assert "get_fundamentals" in result
    assert "get_mtss" not in result  # different section


def test_search_in_section_scoped():
    result = server.search_in_section("price", "获取股票数据")
    assert "get_price" in result
    # get_mtss also matches 'price' in signature but wrong section
    assert "get_mtss" not in result


def test_response_format():
    result = server.lookup_function("get_price")
    assert isinstance(result, str)
    assert len(result) > 50  # non-trivial response
    # Should have labeled sections
    assert any(label in result for label in ["Function", "Parameters", "Returns", "Signature"])


def test_db_read_only():
    import sqlite3
    # The production DB connection should be read-only
    # Test that seeded_db (which is rw) can write but a ro conn cannot
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    try:
        from db.schema import init_db
        rw_conn = sqlite3.connect(tmp.name)
        init_db(rw_conn)
        rw_conn.close()
        ro_conn = sqlite3.connect(f"file:{tmp.name}?mode=ro", uri=True)
        with pytest.raises(sqlite3.OperationalError):
            ro_conn.execute("INSERT INTO api_docs (function_name, section) VALUES ('test', 'test')")
        ro_conn.close()
    finally:
        os.unlink(tmp.name)
