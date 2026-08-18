import sqlite3
import pytest
from db.schema import init_db


@pytest.fixture
def db_conn():
    """Create an in-memory SQLite connection with schema initialized."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def seeded_db():
    """Create an in-memory SQLite connection with schema initialized and seeded test data."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)

    # Seed api_docs (3 rows)
    conn.execute("""INSERT INTO api_docs (function_name, chinese_name, section, call_signature, description, return_type, example_code)
        VALUES ('get_price', '获取行情数据', '获取股票数据', 'get_price(security, start_date, end_date, frequency, fields, skip_paused, fq, count, panel, fill_paused)', '获取一支或者多支股票的行情数据', 'DataFrame', 'df = get_price("000001.XSHE", start_date="2015-01-01", end_date="2015-02-01")')""")
    conn.execute("""INSERT INTO api_docs (function_name, chinese_name, section, call_signature, description, return_type, example_code)
        VALUES ('get_fundamentals', '查询财务数据', '获取股票数据', 'get_fundamentals(query_object, date, statDate)', '查询财务数据', 'DataFrame', NULL)""")
    conn.execute("""INSERT INTO api_docs (function_name, chinese_name, section, call_signature, description, return_type, example_code)
        VALUES ('get_mtss', '获取融资融券信息', '获取融资融券标的列表', 'get_mtss(security, start_date, end_date, fields, count)', '获取一支或者多支股票在一个时间段内的融资融券信息', 'DataFrame', 'df = get_mtss("000001.XSHE")')""")

    # Seed api_params (3 rows for get_price)
    conn.execute("INSERT INTO api_params (function_name, param_name, param_type, description, is_required) VALUES ('get_price', 'security', 'str/list', '一支股票代码或者一个股票代码的list', 1)")
    conn.execute("INSERT INTO api_params (function_name, param_name, param_type, description, is_required) VALUES ('get_price', 'start_date', 'str/date', '开始时间', 0)")
    conn.execute("INSERT INTO api_params (function_name, param_name, param_type, description, is_required) VALUES ('get_price', 'end_date', 'str/date', '结束时间', 0)")

    # Seed api_return_attrs (1 row for get_price)
    conn.execute("INSERT INTO api_return_attrs (function_name, attr_name, attr_type, description) VALUES ('get_price', 'open', 'float', '时间段开始时价格')")

    # Seed table_columns (2 rows)
    conn.execute("INSERT INTO table_columns (table_name, column_name, column_type, meaning, description) VALUES ('balance_sheet', 'total_assets', 'float', '资产总计', '资产负债表-资产总计')")
    conn.execute("INSERT INTO table_columns (table_name, column_name, column_type, meaning, description) VALUES ('balance_sheet', 'total_liability', 'float', '负债合计', '资产负债表-负债合计')")

    conn.commit()

    yield conn
    conn.close()
