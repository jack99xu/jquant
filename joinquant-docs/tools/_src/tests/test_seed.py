"""Upsert idempotency and null handling tests for all seed functions."""
import pytest
from db.seed import (
    upsert_api_doc,
    upsert_api_params,
    upsert_api_return_attrs,
    upsert_strategy,
)


# --- api_doc tests ---

def test_upsert_api_doc_insert(db_conn):
    """upsert_api_doc inserts a new record; row count = 1."""
    upsert_api_doc(db_conn, {
        "function_name": "get_security_info",
        "section": "获取股票数据",
        "call_signature": "get_security_info(code)",
        "description": "获取证券基本信息",
        "return_type": "SecurityUnitData",
        "example_code": "get_security_info('000001.XSHE')",
    })
    count = db_conn.execute("SELECT COUNT(*) FROM api_docs").fetchone()[0]
    assert count == 1


def test_upsert_api_doc_update(db_conn):
    """Upserting same function_name twice with different description keeps row count=1 and updates description."""
    upsert_api_doc(db_conn, {
        "function_name": "get_security_info",
        "section": "获取股票数据",
        "call_signature": "get_security_info(code)",
        "description": "原始描述",
        "return_type": None,
        "example_code": None,
    })
    upsert_api_doc(db_conn, {
        "function_name": "get_security_info",
        "section": "获取股票数据",
        "call_signature": "get_security_info(code)",
        "description": "更新后的描述",
        "return_type": None,
        "example_code": None,
    })

    count = db_conn.execute("SELECT COUNT(*) FROM api_docs").fetchone()[0]
    assert count == 1

    row = db_conn.execute(
        "SELECT description FROM api_docs WHERE function_name = ?",
        ("get_security_info",),
    ).fetchone()
    assert row[0] == "更新后的描述"


def test_upsert_api_doc_null_fields(db_conn):
    """upsert with return_type=None and example_code=None succeeds without error."""
    upsert_api_doc(db_conn, {
        "function_name": "get_price",
        "section": "获取股票数据",
        "call_signature": None,
        "description": None,
        "return_type": None,
        "example_code": None,
    })
    count = db_conn.execute("SELECT COUNT(*) FROM api_docs").fetchone()[0]
    assert count == 1


# --- api_params tests ---

def test_upsert_api_params(db_conn):
    """upsert_api_params inserts param rows linked to a function_name."""
    # Insert parent first
    upsert_api_doc(db_conn, {
        "function_name": "get_security_info",
        "section": "获取股票数据",
        "call_signature": None,
        "description": None,
        "return_type": None,
        "example_code": None,
    })

    params = [
        {"param_name": "code", "param_type": "str", "description": "证券代码", "is_required": 1},
        {"param_name": "date", "param_type": "str", "description": "查询日期", "is_required": 0},
    ]
    upsert_api_params(db_conn, "get_security_info", params)

    count = db_conn.execute(
        "SELECT COUNT(*) FROM api_params WHERE function_name = ?",
        ("get_security_info",),
    ).fetchone()[0]
    assert count == 2


def test_upsert_api_params_replace(db_conn):
    """Upserting params for the same function replaces (delete+insert) old params."""
    upsert_api_doc(db_conn, {
        "function_name": "get_security_info",
        "section": "获取股票数据",
        "call_signature": None,
        "description": None,
        "return_type": None,
        "example_code": None,
    })

    # Insert initial params (3 params)
    initial_params = [
        {"param_name": "code", "param_type": "str", "description": "证券代码", "is_required": 1},
        {"param_name": "date", "param_type": "str", "description": "查询日期", "is_required": 0},
        {"param_name": "extra", "param_type": "str", "description": "额外参数", "is_required": 0},
    ]
    upsert_api_params(db_conn, "get_security_info", initial_params)

    # Replace with fewer params (1 param)
    new_params = [
        {"param_name": "code", "param_type": "str", "description": "证券代码", "is_required": 1},
    ]
    upsert_api_params(db_conn, "get_security_info", new_params)

    count = db_conn.execute(
        "SELECT COUNT(*) FROM api_params WHERE function_name = ?",
        ("get_security_info",),
    ).fetchone()[0]
    assert count == 1


# --- api_return_attrs tests ---

def test_upsert_api_return_attrs(db_conn):
    """upsert_api_return_attrs inserts return attribute rows linked to function_name."""
    upsert_api_doc(db_conn, {
        "function_name": "get_security_info",
        "section": "获取股票数据",
        "call_signature": None,
        "description": None,
        "return_type": None,
        "example_code": None,
    })

    attrs = [
        {"attr_name": "display_name", "attr_type": "str", "description": "证券显示名称"},
        {"attr_name": "name", "attr_type": "str", "description": "证券名称"},
        {"attr_name": "start_date", "attr_type": "datetime.date", "description": "上市日期"},
    ]
    upsert_api_return_attrs(db_conn, "get_security_info", attrs)

    count = db_conn.execute(
        "SELECT COUNT(*) FROM api_return_attrs WHERE function_name = ?",
        ("get_security_info",),
    ).fetchone()[0]
    assert count == 3


# --- strategy tests ---

def test_upsert_strategy_insert(db_conn):
    """upsert_strategy inserts a new strategy; row count = 1."""
    upsert_strategy(db_conn, {
        "name": "均值回归策略",
        "category": "均值回归",
        "description": "基于均值回归原理的经典策略",
        "code_content": "def initialize(context):\n    pass",
    })
    count = db_conn.execute("SELECT COUNT(*) FROM strategies").fetchone()[0]
    assert count == 1


def test_upsert_strategy_update(db_conn):
    """Upserting same (name, category) with different code_content keeps row count=1 and updates code."""
    upsert_strategy(db_conn, {
        "name": "均值回归策略",
        "category": "均值回归",
        "description": "初始描述",
        "code_content": "def initialize(context):\n    pass",
    })
    upsert_strategy(db_conn, {
        "name": "均值回归策略",
        "category": "均值回归",
        "description": "更新描述",
        "code_content": "def initialize(context):\n    g.security = '000001.XSHE'",
    })

    count = db_conn.execute("SELECT COUNT(*) FROM strategies").fetchone()[0]
    assert count == 1

    row = db_conn.execute(
        "SELECT code_content FROM strategies WHERE name = ?",
        ("均值回归策略",),
    ).fetchone()
    assert "000001.XSHE" in row[0]


def test_upsert_strategy_null_description(db_conn):
    """upsert_strategy with description=None succeeds without error."""
    upsert_strategy(db_conn, {
        "name": "无描述策略",
        "category": "其他",
        "description": None,
        "code_content": "def initialize(context):\n    pass",
    })
    count = db_conn.execute("SELECT COUNT(*) FROM strategies").fetchone()[0]
    assert count == 1
