# -*- coding: utf-8 -*-
"""导出器单元测试：使用内存 SQLite 构造最小数据，验证 Markdown 输出结构"""
import sqlite3
import pytest

from export_markdown import (
    load_api_docs, load_params, load_table_columns, classify_table,
    render_function, render_api_md, render_data_md, render_index_md,
)


@pytest.fixture
def conn():
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE api_docs (
        function_name TEXT PRIMARY KEY, section TEXT NOT NULL,
        call_signature TEXT, description TEXT, return_type TEXT,
        example_code TEXT, scraped_at TEXT, chinese_name TEXT)""")
    cur.execute("""CREATE TABLE api_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT, function_name TEXT NOT NULL,
        param_name TEXT NOT NULL, param_type TEXT, description TEXT,
        is_required INTEGER DEFAULT 1)""")
    cur.execute("""CREATE TABLE table_columns (
        id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT NOT NULL,
        column_name TEXT NOT NULL, column_type TEXT, meaning TEXT,
        description TEXT)""")
    cur.execute("INSERT INTO api_docs VALUES ('get_price','数据API > 行情数据','get_price(security, start_date, end_date)','获取历史行情','DataFrame',NULL,'','获取历史行情')")
    cur.execute("INSERT INTO api_docs VALUES ('order','交易函数 > 交易','order(security, amount)','下单','Order','print(order(\"000001.XSHE\", 100))','','下单')")
    cur.execute("INSERT INTO api_params VALUES (1,'get_price','security','str','标的代码',1)")
    cur.execute("INSERT INTO api_params VALUES (2,'get_price','count','int','数量',0)")
    cur.execute("INSERT INTO table_columns VALUES (1,'STK_AUDIT_OPINION','pub_date','DATE','发布日期','')")
    cur.execute("INSERT INTO table_columns VALUES (2,'FUND_INFO','name','VARCHAR','基金名称','')")
    conn.commit()
    return conn


@pytest.fixture
def conn_with_pipe(conn):
    """在基础 fixture 上追加一条签名含竖线的函数，用于验证表格转义"""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO api_docs VALUES (?,?,?,?,?,?,?,?)",
        ('基金列表', '数据API > 基金数据',
         'df[df.display_name.str.contains("指|增")]', '获取基金列表', 'DataFrame',
         None, '', '基金列表'),
    )
    conn.commit()
    return conn


@pytest.fixture
def conn_with_pipe_cols(conn):
    """在基础 fixture 上追加一列含义含竖线的字段，用于验证表格转义"""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO table_columns (table_name, column_name, column_type, meaning, description) "
        "VALUES (?,?,?,?,?)",
        ('STK_AUDIT_OPINION', 'audit_text', 'VARCHAR', '意见类型|补充', '含竖线'),
    )
    conn.commit()
    return conn


@pytest.fixture
def conn_with_newline_sig(conn):
    """在基础 fixture 上追加一条签名含换行的函数，用于验证换行展平"""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO api_docs VALUES (?,?,?,?,?,?,?,?)",
        ('get_mtss', '数据API > 行情数据',
         'from jqdata import *\nget_mtss(security, start_date, end_date)',
         '获取融资融券数据', 'DataFrame', None, '', '获取融资融券数据'),
    )
    conn.commit()
    return conn


@pytest.fixture
def conn_with_pipe_param(conn):
    """在基础 fixture 上追加一条说明含竖线的参数，用于验证参数表转义"""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO api_params (function_name, param_name, param_type, description, is_required) "
        "VALUES (?,?,?,?,?)",
        ('get_price', 'fields', 'list', '字段列表，如 ["open|close"]', 0),
    )
    conn.commit()
    return conn


def test_load_api_docs(conn):
    docs = load_api_docs(conn)
    assert len(docs) == 2
    assert docs[0]['name'] == 'get_price'


def test_load_params(conn):
    params = load_params(conn)
    assert len(params['get_price']) == 2
    assert params['get_price'][0]['required'] is True


def test_load_table_columns(conn):
    tables = load_table_columns(conn)
    assert set(tables.keys()) == {'STK_AUDIT_OPINION', 'FUND_INFO'}


def test_render_function_contains_signature(conn):
    docs = load_api_docs(conn)
    params = load_params(conn)
    md = render_function(docs[0], params)
    assert '### get_price' in md
    assert '`get_price(security, start_date, end_date)`' in md
    assert '| 参数名 | 类型 | 必填 | 说明 |' in md
    assert '| security | str | 是 | 标的代码 |' in md
    assert '| count | int | 否 | 数量 |' in md


def test_render_function_skips_null_example(conn):
    docs = load_api_docs(conn)
    params = load_params(conn)
    md = render_function(docs[0], params)
    assert '```python' not in md  # example_code 为 NULL 时不输出代码块


def test_render_function_includes_example(conn):
    docs = load_api_docs(conn)
    params = load_params(conn)
    md = render_function(docs[1], params)
    assert '```python' in md
    assert 'print(order("000001.XSHE", 100))' in md


def test_render_api_md_groups_by_section(conn):
    docs = load_api_docs(conn)
    params = load_params(conn)
    md = render_api_md(docs, params)
    assert '## 数据API > 行情数据' in md
    assert '## 交易函数 > 交易' in md
    # 章节保持首次出现顺序
    assert md.index('## 数据API > 行情数据') < md.index('## 交易函数 > 交易')


def test_classify_table():
    assert classify_table('STK_BASIC') == 'Stock.md'
    assert classify_table('FUND_INFO') == 'Fund.md'
    assert classify_table('FUT_PRICE') == 'Future.md'
    assert classify_table('INDEX_MEMBER') == 'Index.md'
    assert classify_table('OPT_XXX') == 'Option.md'
    assert classify_table('UNKNOWN_TABLE') == 'Other.md'


def test_render_data_md(conn):
    tables = load_table_columns(conn)
    out = render_data_md(tables)
    assert 'Stock.md' in out and 'Fund.md' in out
    assert '## STK_AUDIT_OPINION' in out['Stock.md']
    assert '| pub_date | DATE | 发布日期 |  |' in out['Stock.md']


def test_render_index_md(conn):
    docs = load_api_docs(conn)
    md = render_index_md(docs)
    assert '| get_price | 数据API > 行情数据 | `get_price(security, start_date, end_date)` |' in md
    assert '| order | 交易函数 > 交易 | `order(security, amount)` |' in md


def test_render_index_md_escapes_pipe(conn_with_pipe):
    docs = load_api_docs(conn_with_pipe)
    md = render_index_md(docs)
    # 签名中的竖线在表格单元格内必须转义为 \|
    escaped = 'df[df.display_name.str.contains("指\\|增")]'
    raw = 'df[df.display_name.str.contains("指|增")]'
    assert escaped in md
    assert raw not in md


def test_render_data_md_escapes_pipe(conn_with_pipe_cols):
    tables = load_table_columns(conn_with_pipe_cols)
    out = render_data_md(tables)
    # meaning/name 单元格内的竖线必须转义为 \|
    assert '| audit_text | VARCHAR | 意见类型\\|补充 | 含竖线 |' in out['Stock.md']


def test_render_index_md_flattens_newline(conn_with_newline_sig):
    docs = load_api_docs(conn_with_newline_sig)
    md = render_index_md(docs)
    row = next(l for l in md.splitlines() if 'get_mtss' in l)
    # 表格行必须是单行，签名中的换行被替换为空格
    assert 'from jqdata import * get_mtss(security, start_date, end_date)' in row


def test_render_function_signature_flattens_newline(conn_with_newline_sig):
    docs = load_api_docs(conn_with_newline_sig)
    params = load_params(conn_with_newline_sig)
    md = render_function(docs[0], params)
    sig_line = next(l for l in md.splitlines() if '**签名:**' in l)
    # 行内代码跨行会断裂，签名中的换行必须被替换为空格
    assert 'from jqdata import * get_mtss(security, start_date, end_date)' in sig_line


def test_render_function_escapes_param_cells(conn_with_pipe_param):
    docs = load_api_docs(conn_with_pipe_param)
    params = load_params(conn_with_pipe_param)
    md = render_function(docs[0], params)
    # 参数表单元格内的竖线必须转义为 \|
    assert '| fields | list | 否 | 字段列表，如 ["open\\|close"] |' in md
