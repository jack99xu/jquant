"""JoinQuant API Documentation MCP Server.

Exposes JoinQuant (聚宽) API documentation from jq_knowledge.db as MCP tools
for Claude and other AI assistants.

Install:
    claude mcp add jq-docs -- uvx jq-docs-mcp
    # or: pip install jq-docs-mcp && jq-docs-mcp
"""
import sqlite3
import os
import logging
from pathlib import Path
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP("JoinQuant API Docs / 聚宽API文档查询")

_DEFAULT_DB = Path(__file__).parent / "jq_knowledge.db"
_DB_PATH = os.environ.get("JQ_DB_PATH") or str(_DEFAULT_DB)


def _open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{_DB_PATH}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# Module-level connection — tests monkey-patch this
_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = _open_db()
    # Ensure row_factory is set even on monkey-patched test connections
    if _conn.row_factory is not sqlite3.Row:
        _conn.row_factory = sqlite3.Row
    return _conn


def _validate_db(conn: sqlite3.Connection) -> None:
    expected = ["api_docs", "api_params", "api_return_attrs", "table_columns"]
    for table in expected:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if count == 0:
                logger.warning("Table %s has 0 rows", table)
        except sqlite3.OperationalError as e:
            logger.error("Table %s missing: %s", table, e)


def _fuzzy_suggestions(name: str, limit: int = 5) -> list[str]:
    conn = _get_conn()
    prefix = name[:4] if len(name) >= 4 else name
    rows = conn.execute(
        "SELECT function_name FROM api_docs WHERE function_name LIKE ? LIMIT ?",
        (f"{prefix}%", limit),
    ).fetchall()
    if rows:
        return [r["function_name"] for r in rows]
    # Fall back to returning all available function names
    rows = conn.execute(
        "SELECT function_name FROM api_docs LIMIT ?",
        (limit,),
    ).fetchall()
    return [r["function_name"] for r in rows]


def _format_function_doc(row, params, return_attrs) -> str:
    lines = []
    lines.append(f"## Function: {row['function_name']}")
    if row["chinese_name"]:
        lines.append(f"**Chinese Name:** {row['chinese_name']}")
    lines.append(f"**Section:** {row['section']}")
    if row["call_signature"]:
        lines.append(f"\n### Signature\n`{row['call_signature']}`")
    if row["description"]:
        lines.append(f"\n### Description\n{row['description']}")
    if params:
        lines.append("\n### Parameters")
        lines.append("| Name | Type | Required | Description |")
        lines.append("|------|------|----------|-------------|")
        for p in params:
            req = "Yes" if p["is_required"] else "No"
            lines.append(f"| {p['param_name']} | {p['param_type'] or '-'} | {req} | {p['description'] or '-'} |")
    if row["return_type"]:
        lines.append(f"\n### Returns\n**Type:** {row['return_type']}")
    if return_attrs:
        lines.append("\n**Return Attributes:**")
        for a in return_attrs:
            lines.append(f"- `{a['attr_name']}` ({a['attr_type'] or '-'}): {a['description'] or '-'}")
    if row["example_code"]:
        lines.append(f"\n### Example\n```python\n{row['example_code']}\n```")
    return "\n".join(lines)


def _format_search_results(rows) -> str:
    lines = ["## Search Results", f"Found {len(rows)} result(s):", ""]
    for r in rows:
        lines.append(f"- **{r['function_name']}** ({r['chinese_name'] or '-'}) — {r['description'] or '-'} [{r['section']}]")
    return "\n".join(lines)


@mcp.tool
def lookup_function(function_name: str) -> str:
    """Look up complete documentation for a JoinQuant API function by exact name.
    查询聚宽API函数的完整文档，包括参数列表、返回值和示例代码。

    Args:
        function_name: Exact function name (e.g. 'get_price', 'get_fundamentals')
    """
    conn = _get_conn()
    row = conn.execute("SELECT * FROM api_docs WHERE function_name = ?", (function_name,)).fetchone()
    if row is None:
        suggestions = _fuzzy_suggestions(function_name)
        hint = f"\nSimilar functions: {', '.join(suggestions)}" if suggestions else ""
        return f"Function '{function_name}' not found.{hint}"
    params = conn.execute(
        "SELECT param_name, param_type, is_required, description FROM api_params WHERE function_name = ?",
        (function_name,)
    ).fetchall()
    return_attrs = conn.execute(
        "SELECT attr_name, attr_type, description FROM api_return_attrs WHERE function_name = ?",
        (function_name,)
    ).fetchall()
    return _format_function_doc(row, params, return_attrs)


@mcp.tool
def search_docs(keyword: str) -> str:
    """Search JoinQuant API docs by keyword (English or Chinese).
    搜索API文档，支持英文和中文关键词搜索（函数名、中文名、描述、调用签名）。

    Args:
        keyword: Search term in English or Chinese
    """
    conn = _get_conn()
    pattern = f"%{keyword}%"
    rows = conn.execute(
        """SELECT function_name, chinese_name, description, section
           FROM api_docs
           WHERE function_name LIKE ?
              OR chinese_name LIKE ?
              OR description LIKE ?
              OR call_signature LIKE ?
           LIMIT 20""",
        (pattern, pattern, pattern, pattern)
    ).fetchall()
    if not rows:
        return f"No results found for '{keyword}'."
    return _format_search_results(rows)


@mcp.tool
def list_by_section(section: str) -> str:
    """List all API functions in a specific documentation section.
    列出某个文档分类下的所有API函数。

    Args:
        section: Section name (e.g. '获取股票数据', '获取融资融券标的列表')
    """
    conn = _get_conn()
    rows = conn.execute(
        "SELECT function_name, chinese_name, description FROM api_docs WHERE section = ?",
        (section,)
    ).fetchall()
    if not rows:
        sections = conn.execute("SELECT DISTINCT section FROM api_docs").fetchall()
        available = ", ".join(r["section"] for r in sections)
        return f"No functions found in section '{section}'.\nAvailable sections: {available}"
    lines = [f"## Section: {section}", f"Found {len(rows)} function(s):", ""]
    for r in rows:
        lines.append(f"- **{r['function_name']}** ({r['chinese_name'] or '-'}) — {r['description'] or '-'}")
    return "\n".join(lines)


@mcp.tool
def search_in_section(keyword: str, section: str) -> str:
    """Search API docs within a specific section only.
    在指定文档分类中搜索API函数。

    Args:
        keyword: Search term in English or Chinese
        section: Section name to search within (e.g. '获取股票数据')
    """
    conn = _get_conn()
    pattern = f"%{keyword}%"
    rows = conn.execute(
        """SELECT function_name, chinese_name, description, section
           FROM api_docs
           WHERE section = ?
             AND (function_name LIKE ?
                  OR chinese_name LIKE ?
                  OR description LIKE ?
                  OR call_signature LIKE ?)
           LIMIT 20""",
        (section, pattern, pattern, pattern, pattern)
    ).fetchall()
    if not rows:
        return f"No results found for '{keyword}' in section '{section}'."
    return _format_search_results(rows)


@mcp.tool
def list_functions() -> str:
    """List all available JoinQuant API function names, grouped by section.
    列出所有可用的聚宽API函数名，按文档分类分组。

    Use this to discover what functions are available before looking up specific ones.
    """
    conn = _get_conn()
    rows = conn.execute("SELECT function_name, section FROM api_docs ORDER BY section, function_name").fetchall()
    if not rows:
        return "No functions found in database."
    grouped: dict[str, list[str]] = {}
    for r in rows:
        grouped.setdefault(r["section"], []).append(r["function_name"])
    lines = ["## Available Functions"]
    for section, names in grouped.items():
        lines.append(f"\n### {section} ({len(names)})")
        for name in names:
            lines.append(f"- {name}")
    lines.append(f"\n**Total: {len(rows)} functions**")
    return "\n".join(lines)


@mcp.tool
def lookup_table_columns(table_name: str) -> str:
    """Look up all column definitions for a JoinQuant data table.
    查询聚宽数据表的所有字段定义（字段名、类型、含义）。

    Critical for get_fundamentals queries where exact column names are needed.

    Args:
        table_name: Table name (e.g. 'balance_sheet', 'income_statement')
    """
    conn = _get_conn()
    rows = conn.execute(
        "SELECT column_name, column_type, meaning, description FROM table_columns WHERE table_name = ? ORDER BY column_name",
        (table_name,)
    ).fetchall()
    if not rows:
        tables = conn.execute("SELECT DISTINCT table_name FROM table_columns ORDER BY table_name LIMIT 20").fetchall()
        available = ", ".join(r["table_name"] for r in tables)
        return f"Table '{table_name}' not found.\nAvailable tables (first 20): {available}"
    lines = [f"## Table: {table_name}", f"{len(rows)} column(s):", ""]
    lines.append("| Column | Type | Meaning | Description |")
    lines.append("|--------|------|---------|-------------|")
    for r in rows:
        lines.append(f"| {r['column_name']} | {r['column_type'] or '-'} | {r['meaning'] or '-'} | {r['description'] or '-'} |")
    return "\n".join(lines)


def main():
    global _conn
    _conn = _open_db()
    _validate_db(_conn)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
