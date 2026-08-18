"""
Unit tests for API doc HTML parsing logic in scraper/api_docs.py.
Tests use hardcoded sample HTML strings that mimic the real JoinQuant DOM structure.
No browser required.
"""

import pytest
from scraper.api_docs import _parse_all_functions


# ---------------------------------------------------------------------------
# Sample HTML fixtures — wrapped in .help-api-right div to match real structure
# ---------------------------------------------------------------------------

def _wrap(body_html: str) -> str:
    """Wrap HTML content in the expected page structure."""
    return f'<html><body><div class="help-api-right">{body_html}</div></body></html>'


SAMPLE_SINGLE_FUNCTION_HTML = _wrap("""
<h2 id="获取股票数据">获取股票数据</h2>
<h4 id="get_security_info">获取股票基本信息</h4>
<p>获取股票/基金/指数的信息</p>
<p>调用方法</p>
<pre>get_security_info(code)</pre>
<p>参数</p>
<ul>
  <li>code: str - 证券代码, 必选</li>
</ul>
<p>返回值</p>
<p>SecurityUnitData对象</p>
<p>示例</p>
<pre>info = get_security_info('000001.XSHE')
print(info.display_name)</pre>
<h2 id="other-section">其他章节</h2>
""")

SAMPLE_PARAMS_TABLE_HTML = _wrap("""
<h2 id="获取股票数据">获取股票数据</h2>
<h4 id="get_price">获取历史数据</h4>
<p>获取一支或者多支股票的行情数据</p>
<p>调用方法</p>
<pre>get_price(security, start_date=None, end_date=None, frequency='daily')</pre>
<p>参数</p>
<table>
  <tr><th>参数</th><th>类型</th><th>说明</th></tr>
  <tr><td>security</td><td>str/list</td><td>股票代码或代码列表</td></tr>
  <tr><td>start_date</td><td>str</td><td>开始日期，格式YYYY-MM-DD</td></tr>
  <tr><td>end_date</td><td>str</td><td>结束日期，格式YYYY-MM-DD</td></tr>
</table>
<p>返回值</p>
<p>DataFrame对象</p>
<p>示例</p>
<pre>df = get_price('000001.XSHE', start_date='2020-01-01', end_date='2020-12-31')</pre>
<h2 id="other">其他</h2>
""")

SAMPLE_RETURN_ATTRS_HTML = _wrap("""
<h2 id="获取股票数据">获取股票数据</h2>
<h4 id="get_security_info">获取股票基本信息</h4>
<p>获取证券信息</p>
<p>调用方法</p>
<pre>get_security_info(code)</pre>
<p>参数</p>
<ul>
  <li>code - 证券代码</li>
</ul>
<p>返回值</p>
<table>
  <tr><th>属性</th><th>类型</th><th>说明</th></tr>
  <tr><td>display_name</td><td>str</td><td>股票名称</td></tr>
  <tr><td>name</td><td>str</td><td>股票缩写</td></tr>
  <tr><td>start_date</td><td>datetime.date</td><td>上市日期</td></tr>
</table>
<p>示例</p>
<pre>info = get_security_info('000001.XSHE')</pre>
""")

SAMPLE_NO_EXAMPLE_HTML = _wrap("""
<h2 id="获取股票数据">获取股票数据</h2>
<h4 id="get_index_stocks">获取指数成份股</h4>
<p>获取一个指数给定日期在平台可交易的成分股列表</p>
<p>调用方法</p>
<pre>get_index_stocks(index_symbol)</pre>
<p>参数</p>
<ul>
  <li>index_symbol: str - 指数代码</li>
</ul>
<p>返回值</p>
<p>list[str] 股票代码列表</p>
""")

SAMPLE_NO_RETURN_TYPE_HTML = _wrap("""
<h2 id="获取股票数据">获取股票数据</h2>
<h4 id="run_query">执行查询</h4>
<p>执行JQData查询</p>
<p>调用方法</p>
<pre>run_query(query)</pre>
<p>参数</p>
<ul>
  <li>query - SQLAlchemy查询对象</li>
</ul>
<p>示例</p>
<pre>df = run_query(query(Valuation).filter(Valuation.code == '000001.XSHE'))</pre>
""")

SAMPLE_MULTIPLE_FUNCTIONS_HTML = _wrap("""
<h2 id="获取股票数据">获取股票数据</h2>
<h4 id="get_security_info">获取股票基本信息</h4>
<p>获取股票信息</p>
<p>调用方法</p>
<pre>get_security_info(code)</pre>
<p>参数</p>
<ul><li>code - 证券代码</li></ul>
<p>返回值</p>
<p>SecurityUnitData对象</p>
<p>示例</p>
<pre>info = get_security_info('000001.XSHE')</pre>
<h4 id="get_all_securities">获取所有标的信息</h4>
<p>获取平台支持的所有股票、基金、指数等标的信息</p>
<p>调用方法</p>
<pre>get_all_securities(types=[], date=None)</pre>
<p>参数</p>
<ul>
  <li>types: list - 标的类型列表</li>
  <li>date: str - 查询日期</li>
</ul>
<p>返回值</p>
<p>DataFrame对象</p>
<p>示例</p>
<pre>df = get_all_securities(types=['stock'])</pre>
""")

SAMPLE_CHINESE_CONTENT_HTML = _wrap("""
<h2 id="获取股票数据">获取股票数据</h2>
<h4 id="get_fundamentals">获取财务数据</h4>
<p>获取上市公司的财务数据，包括资产负债表、利润表和现金流量表中的数据</p>
<p>调用方法</p>
<pre>get_fundamentals(query_object, date=None, statDate=None)</pre>
<p>参数</p>
<ul>
  <li>query_object - 使用query函数生成的查询对象</li>
  <li>date: str - 查询的日期</li>
  <li>statDate: str - 财报统计的季度或年份</li>
</ul>
<p>返回值</p>
<p>pandas.DataFrame</p>
<p>示例</p>
<pre>df = get_fundamentals(query(Valuation).filter(Valuation.code == '000001.XSHE'))</pre>
""")

SAMPLE_ARTICLE_FUNCTION_HTML = _wrap("""
<h2 id="获取股票数据">获取股票数据</h2>
<article>
<pre>get_fundamentals(query_object, date=None, statDate=None)</pre>
<h5>参数</h5>
<ul>
  <li>query_object - 查询对象</li>
  <li>date - 查询日期</li>
</ul>
<h5>返回值</h5>
<p>pandas.DataFrame - 财务数据表格</p>
<h5>示例</h5>
<pre>df = get_fundamentals(query(Valuation))</pre>
</article>
""")

SAMPLE_MIXED_HTML = _wrap("""
<h2 id="获取股票数据">获取股票数据</h2>
<h4 id="get_security_info">获取股票基本信息</h4>
<p>获取证券信息</p>
<p>调用方法</p>
<pre>get_security_info(code)</pre>
<p>参数</p>
<ul><li>code - 代码</li></ul>
<p>返回值</p>
<p>SecurityUnitData</p>
<p>示例</p>
<pre>info = get_security_info('000001.XSHE')</pre>
<article>
<pre>get_fundamentals(query_object, date=None)</pre>
<h5>参数</h5>
<ul>
  <li>query_object - 查询对象</li>
  <li>date - 日期</li>
</ul>
<h5>返回值</h5>
<p>pandas.DataFrame</p>
<h5>示例</h5>
<pre>df = get_fundamentals(query(Valuation))</pre>
</article>
""")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_parse_single_function():
    """Sample HTML with one function block returns list with 1 dict containing required fields."""
    records = _parse_all_functions(SAMPLE_SINGLE_FUNCTION_HTML, page_label="测试")
    assert len(records) == 1
    r = records[0]
    assert "function_name" in r
    assert "call_signature" in r
    assert "description" in r
    assert "return_type" in r
    assert "example_code" in r
    assert "params" in r
    assert "return_attrs" in r
    assert r["function_name"] == "get_security_info"
    assert "get_security_info(code)" in r["call_signature"]
    assert r["description"] is not None


def test_parse_params():
    """Sample HTML with params table — params list contains dicts with param_name, param_type, description."""
    records = _parse_all_functions(SAMPLE_PARAMS_TABLE_HTML, page_label="测试")
    assert len(records) >= 1
    r = records[0]
    assert r["function_name"] == "get_price"
    params = r["params"]
    assert isinstance(params, list)
    assert len(params) >= 1
    for p in params:
        assert "param_name" in p
        assert "param_type" in p
        assert "description" in p
    security_param = next((p for p in params if p["param_name"] == "security"), None)
    assert security_param is not None
    assert security_param["param_type"] is not None


def test_parse_return_attrs():
    """Sample HTML with return attributes table — return_attrs list contains dicts."""
    records = _parse_all_functions(SAMPLE_RETURN_ATTRS_HTML, page_label="测试")
    assert len(records) >= 1
    r = records[0]
    return_attrs = r["return_attrs"]
    assert isinstance(return_attrs, list)
    assert len(return_attrs) >= 1
    for a in return_attrs:
        assert "attr_name" in a
        assert "attr_type" in a
        assert "description" in a
    display_name_attr = next((a for a in return_attrs if a["attr_name"] == "display_name"), None)
    assert display_name_attr is not None
    assert display_name_attr["attr_type"] == "str"


def test_parse_missing_example():
    """Function block with no example code — example_code is None."""
    records = _parse_all_functions(SAMPLE_NO_EXAMPLE_HTML, page_label="测试")
    assert len(records) >= 1
    r = records[0]
    assert r["function_name"] == "get_index_stocks"
    assert r["example_code"] is None


def test_parse_missing_return_type():
    """Function block with no return type — return_type is None."""
    records = _parse_all_functions(SAMPLE_NO_RETURN_TYPE_HTML, page_label="测试")
    assert len(records) >= 1
    r = records[0]
    assert r["function_name"] == "run_query"
    assert r["return_type"] is None


def test_parse_multiple_functions():
    """Sample HTML with 2 function blocks — returns list of length 2."""
    records = _parse_all_functions(SAMPLE_MULTIPLE_FUNCTIONS_HTML, page_label="测试")
    assert len(records) == 2
    names = [r["function_name"] for r in records]
    assert "get_security_info" in names
    assert "get_all_securities" in names


def test_parse_chinese_content():
    """Function with Chinese description — description contains Chinese characters."""
    records = _parse_all_functions(SAMPLE_CHINESE_CONTENT_HTML, page_label="测试")
    assert len(records) >= 1
    r = records[0]
    assert r["description"] is not None
    assert any("\u4e00" <= c <= "\u9fff" for c in r["description"])
    assert "财务数据" in r["description"]


def test_parse_article_function():
    """Article-level complex function block is parsed correctly."""
    records = _parse_all_functions(SAMPLE_ARTICLE_FUNCTION_HTML, page_label="测试")
    assert len(records) >= 1
    r = records[0]
    assert "get_fundamentals" in r["function_name"]
    assert r["call_signature"] is not None
    assert "get_fundamentals" in r["call_signature"]
    assert r["example_code"] is not None


def test_parse_mixed_h4_and_article():
    """HTML with both h4 and article function blocks — all are extracted."""
    records = _parse_all_functions(SAMPLE_MIXED_HTML, page_label="测试")
    assert len(records) == 2
    names = [r["function_name"] for r in records]
    assert "get_security_info" in names
    assert "get_fundamentals" in names


def test_section_is_stored_on_all_records():
    """Section name is stored on every record in the list."""
    records = _parse_all_functions(SAMPLE_MULTIPLE_FUNCTIONS_HTML, page_label="测试页面")
    for r in records:
        assert "测试页面" in r["section"]


def test_empty_html_returns_empty_list():
    """Empty HTML input returns empty list — never raises."""
    records = _parse_all_functions('<html><body><div class="help-api-right"></div></body></html>', page_label="")
    assert records == []


def test_partial_data_stored_as_none():
    """Fields that cannot be extracted are stored as None, not skipped."""
    records = _parse_all_functions(SAMPLE_NO_EXAMPLE_HTML, page_label="测试")
    assert len(records) >= 1
    r = records[0]
    assert "example_code" in r
    assert r["example_code"] is None
    for key in ("function_name", "section", "call_signature", "description",
                "return_type", "example_code", "params", "return_attrs"):
        assert key in r
