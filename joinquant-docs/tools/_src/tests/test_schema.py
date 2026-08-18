"""Schema validation tests for all 4 SQLite tables and indexes."""
import sqlite3
import pytest


def get_columns(conn, table_name):
    """Return list of column names for a table."""
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [row[1] for row in rows]


def get_indexes(conn, table_name):
    """Return list of index names for a table."""
    rows = conn.execute(f"PRAGMA index_list({table_name})").fetchall()
    return [row[1] for row in rows]


def test_api_docs_columns(db_conn):
    """api_docs table has all required columns."""
    columns = get_columns(db_conn, "api_docs")
    assert "function_name" in columns
    assert "section" in columns
    assert "call_signature" in columns
    assert "description" in columns
    assert "return_type" in columns
    assert "example_code" in columns
    assert "scraped_at" in columns


def test_api_params_columns(db_conn):
    """api_params table has all required columns."""
    columns = get_columns(db_conn, "api_params")
    assert "id" in columns
    assert "function_name" in columns
    assert "param_name" in columns
    assert "param_type" in columns
    assert "description" in columns
    assert "is_required" in columns


def test_api_return_attrs_columns(db_conn):
    """api_return_attrs table has all required columns."""
    columns = get_columns(db_conn, "api_return_attrs")
    assert "id" in columns
    assert "function_name" in columns
    assert "attr_name" in columns
    assert "attr_type" in columns
    assert "description" in columns


def test_strategies_columns(db_conn):
    """strategies table has all required columns and UNIQUE constraint."""
    columns = get_columns(db_conn, "strategies")
    assert "id" in columns
    assert "name" in columns
    assert "category" in columns
    assert "description" in columns
    assert "code_content" in columns
    assert "scraped_at" in columns

    # Verify UNIQUE(name, category) constraint by attempting duplicate insert
    db_conn.execute(
        "INSERT INTO strategies (name, category, code_content) VALUES (?, ?, ?)",
        ("test_strat", "test_cat", "code"),
    )
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO strategies (name, category, code_content) VALUES (?, ?, ?)",
            ("test_strat", "test_cat", "other_code"),
        )


def test_indexes_exist(db_conn):
    """All four required indexes exist on their respective tables."""
    api_docs_indexes = get_indexes(db_conn, "api_docs")
    assert "idx_api_docs_section" in api_docs_indexes

    strategies_indexes = get_indexes(db_conn, "strategies")
    assert "idx_strategies_category" in strategies_indexes

    api_params_indexes = get_indexes(db_conn, "api_params")
    assert "idx_api_params_function" in api_params_indexes

    api_return_indexes = get_indexes(db_conn, "api_return_attrs")
    assert "idx_api_return_function" in api_return_indexes


def test_chinese_like_search(db_conn):
    """Chinese text is findable via LIKE queries on the description column."""
    db_conn.execute(
        """INSERT INTO api_docs (function_name, section, description)
           VALUES (?, ?, ?)""",
        ("get_security_info", "获取股票数据", "获取证券的详细信息，包括证券代码和名称"),
    )
    db_conn.commit()

    rows = db_conn.execute(
        "SELECT function_name FROM api_docs WHERE description LIKE ?",
        ("%证券%",),
    ).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "get_security_info"


def test_params_queryable(db_conn):
    """Parameters in api_params are queryable as individual rows by param_name."""
    # First insert the parent api_docs row
    db_conn.execute(
        "INSERT INTO api_docs (function_name, section) VALUES (?, ?)",
        ("get_security_info", "获取股票数据"),
    )
    db_conn.commit()

    # Insert params
    db_conn.execute(
        """INSERT INTO api_params (function_name, param_name, param_type, is_required)
           VALUES (?, ?, ?, ?)""",
        ("get_security_info", "code", "str", 1),
    )
    db_conn.commit()

    rows = db_conn.execute(
        "SELECT * FROM api_params WHERE param_name = ?",
        ("code",),
    ).fetchall()
    assert len(rows) == 1
    assert rows[0][1] == "get_security_info"  # function_name column (index 1: id, function_name, param_name, ...)
    assert rows[0][2] == "code"  # param_name column (index 2)


def test_foreign_key_cascade(db_conn):
    """DELETE from api_docs cascades to api_params and api_return_attrs."""
    # Insert parent row
    db_conn.execute(
        "INSERT INTO api_docs (function_name, section) VALUES (?, ?)",
        ("get_price", "获取股票数据"),
    )
    db_conn.commit()

    # Insert child rows
    db_conn.execute(
        "INSERT INTO api_params (function_name, param_name) VALUES (?, ?)",
        ("get_price", "code"),
    )
    db_conn.execute(
        "INSERT INTO api_return_attrs (function_name, attr_name) VALUES (?, ?)",
        ("get_price", "close"),
    )
    db_conn.commit()

    # Verify children exist
    assert db_conn.execute(
        "SELECT COUNT(*) FROM api_params WHERE function_name = ?", ("get_price",)
    ).fetchone()[0] == 1
    assert db_conn.execute(
        "SELECT COUNT(*) FROM api_return_attrs WHERE function_name = ?", ("get_price",)
    ).fetchone()[0] == 1

    # Delete parent — should cascade
    db_conn.execute("DELETE FROM api_docs WHERE function_name = ?", ("get_price",))
    db_conn.commit()

    # Children should be gone
    assert db_conn.execute(
        "SELECT COUNT(*) FROM api_params WHERE function_name = ?", ("get_price",)
    ).fetchone()[0] == 0
    assert db_conn.execute(
        "SELECT COUNT(*) FROM api_return_attrs WHERE function_name = ?", ("get_price",)
    ).fetchone()[0] == 0
