"""
API documentation scraper for JoinQuant.

Extracts structured function records from ALL JoinQuant API doc pages at
https://www.joinquant.com/help/api/help?name=X

The docs are organized by topic (stock, fund, future, option, bond, index,
JQData, api, factor). Each page is a single-page app with a tree sidebar
(.am-tree) and content rendered in .help-api-right.

Content structure:
- H2: top-level sections (e.g., 获取股票数据, 获取融资融券标的列表)
- H3: sub-sections or standalone functions
- H4: individual functions within sub-sections
- pre: call signatures and example code
- p/ul/table: params, descriptions, return types

No login required — all pages are public.
"""

import sys
import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import BrowserContext

# ---------------------------------------------------------------------------
# All API doc pages to scrape
# ---------------------------------------------------------------------------

API_PAGES = [
    {"name": "stock", "label": "股票数据"},
    {"name": "fund", "label": "场内基金数据"},
    {"name": "future", "label": "期货数据"},
    {"name": "option", "label": "期权数据"},
    {"name": "bond", "label": "债券数据"},
    {"name": "index", "label": "指数数据"},
    {"name": "JQData", "label": "JQData使用说明"},
    {"name": "api", "label": "策略API"},
    {"name": "factor", "label": "因子分析"},
]

_BASE_URL = "https://www.joinquant.com/help/api/help?name="

# Content-proving selector
CONTENT_READY_SEL = "h2"

# Section markers used to identify blocks of content
_SECTION_MARKERS = {"调用方法", "参数", "返回值", "示例", "注意", "返回"}

# h5 markers within article-level function blocks
_H5_MARKERS = {"参数", "返回值", "注意", "示例"}


# ---------------------------------------------------------------------------
# Public scraping functions
# ---------------------------------------------------------------------------


def scrape_all_api_sections(context: BrowserContext) -> tuple[list[dict], list[dict]]:
    """Scrape ALL API doc pages and return function records + table column defs.

    Iterates over all API_PAGES, extracting every function from each page,
    plus any table column definitions (get_fundamentals tables and STK_/FINANCE_ fields).

    Returns:
        (api_records, table_column_records) where table_column_records is a list
        of {"table_name": str, "columns": list[dict]}.
    """
    all_records = []
    all_table_columns = []
    page = context.new_page()
    try:
        for i, page_info in enumerate(API_PAGES):
            if i > 0:
                time.sleep(random.uniform(2.0, 3.0))

            url = f"{_BASE_URL}{page_info['name']}"
            section_label = page_info["label"]

            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(3)  # wait for SPA content to render

            try:
                page.wait_for_selector(CONTENT_READY_SEL, timeout=10000)
            except Exception:
                print(
                    f"WARNING: Content not loaded for '{section_label}' ({url})",
                    file=sys.stderr,
                )
                continue

            html = page.content()
            records = _parse_all_functions(html, section_label)

            if len(records) == 0:
                print(
                    f"WARNING: 0 functions found on '{section_label}' -- check page structure",
                    file=sys.stderr,
                )
            else:
                print(f"  {section_label}: {len(records)} functions", file=sys.stderr)

            all_records.extend(records)

            # Extract table column definitions from this page
            table_cols = extract_table_columns(html)
            if table_cols:
                col_count = sum(len(tc["columns"]) for tc in table_cols)
                print(
                    f"  {section_label}: {len(table_cols)} table column defs ({col_count} columns)",
                    file=sys.stderr,
                )
                all_table_columns.extend(table_cols)
    finally:
        page.close()

    return all_records, all_table_columns


# ---------------------------------------------------------------------------
# Pure parsing functions (no browser — testable with sample HTML)
# ---------------------------------------------------------------------------


def _parse_all_functions(html: str, page_label: str) -> list[dict]:
    """Parse ALL function blocks from a help API page.

    Walks the .help-api-right content area, finding all H2 sections and
    extracting functions from H3/H4 headings and article elements within each.

    Each function gets a section label like "股票数据 > 获取股票概况" to
    indicate where it lives in the hierarchy.
    """
    soup = BeautifulSoup(html, "lxml")
    records = []
    seen_names = set()

    # Find the main content area
    content = soup.find(class_="help-api-right")
    if content is None:
        # Fallback to body
        content = soup.body or soup

    # Get all H2 elements as section boundaries
    h2s = content.find_all("h2")

    for h2_idx, h2 in enumerate(h2s):
        h2_text = h2.get_text(strip=True)
        if not h2_text:
            continue

        # Collect elements between this H2 and the next H2
        section_elements = []
        el = h2
        while True:
            el = el.find_next_sibling()
            if el is None:
                break
            if hasattr(el, "name") and el.name == "h2":
                break
            section_elements.append(el)

        # Build section label
        section = f"{page_label} > {h2_text}"

        # Extract functions from this section
        _extract_from_section(section_elements, section, records, seen_names)

    return records


def _extract_from_section(elements: list, section: str, records: list, seen_names: set):
    """Extract function records from a list of section elements.

    Handles three patterns:
    1. <article> elements (complex functions with h5 sub-structure)
    2. <section> containers with nested <article> elements
    3. Direct H3/H4 headings (simple functions)
    """
    for i, el in enumerate(elements):
        if not hasattr(el, "name"):
            continue

        if el.name == "article":
            record = _parse_article_function(el, section)
            if record and record["function_name"] not in seen_names:
                seen_names.add(record["function_name"])
                records.append(record)

        elif el.name == "section":
            for nested in el.find_all("article"):
                record = _parse_article_function(nested, section)
                if record and record["function_name"] not in seen_names:
                    seen_names.add(record["function_name"])
                    records.append(record)

        elif el.name == "h3":
            # H3 can be a sub-section label or a function heading
            # If followed by a pre with a call signature, it's a function
            record = _parse_heading_function(el, elements, section, "h3")
            if record and record["function_name"] not in seen_names:
                seen_names.add(record["function_name"])
                records.append(record)

        elif el.name == "h4":
            record = _parse_heading_function(el, elements, section, "h4")
            if record and record["function_name"] not in seen_names:
                seen_names.add(record["function_name"])
                records.append(record)


def _parse_heading_function(heading, all_elements: list, section: str, heading_tag: str) -> dict | None:
    """Parse a function block anchored by an H3 or H4 heading.

    Collects siblings until the next heading of same or higher level.
    Looks for a call signature in the first <pre> element.
    """
    # Find index in all_elements
    try:
        idx = all_elements.index(heading)
    except ValueError:
        return None

    # Determine stop tags
    stop_tags = {"h2"}
    if heading_tag == "h3":
        stop_tags.add("h3")
    elif heading_tag == "h4":
        stop_tags.update({"h3", "h4"})

    # Collect siblings
    siblings = []
    for el in all_elements[idx + 1:]:
        if hasattr(el, "name") and el.name in stop_tags:
            break
        siblings.append(el)

    if not siblings:
        return None

    # Look for call signature
    call_signature = None

    # Method 1: labeled "调用方法" paragraph followed by pre
    call_signature = _extract_by_label(siblings, "调用方法", preceding_label=True)

    # Method 2: first <pre> element
    if not call_signature:
        for sib in siblings:
            if hasattr(sib, "name") and sib.name == "pre":
                text = sib.get_text(strip=True)
                if text and "(" in text:
                    call_signature = text
                    break

    # Extract function name
    function_name = None
    if call_signature:
        function_name = _extract_function_name(call_signature)
    if not function_name:
        # Try heading id attribute
        h_id = heading.get("id", "").strip()
        if h_id and not any("\u4e00" <= c <= "\u9fff" for c in h_id) and h_id.isidentifier():
            function_name = h_id
    if not function_name:
        # For headings with a pre block (i.e. they document something), use
        # the heading text as the function name. This captures data table
        # sections like "十大股东", "合并利润表" etc.
        if call_signature:
            heading_text = heading.get_text(strip=True)
            if heading_text:
                function_name = heading_text
        else:
            # No call signature at all — skip, this is a section label
            return None
    if not function_name:
        return None

    # Chinese name: use the heading text as the Chinese interface name
    heading_text = heading.get_text(strip=True)
    chinese_name = None
    if heading_text and heading_text != function_name:
        # Only use if it contains Chinese characters (not "示例", section markers etc.)
        has_chinese = any("\u4e00" <= c <= "\u9fff" for c in heading_text)
        if has_chinese and heading_text not in _SECTION_MARKERS and heading_text != "示例":
            chinese_name = heading_text

    description = _extract_description(heading, siblings)
    return_type = _extract_return_type(siblings)
    example_code = _extract_by_label(siblings, "示例", preceding_label=True)
    params = _extract_params_from_siblings(siblings)
    return_attrs = _extract_return_attrs_from_siblings(siblings)

    return {
        "function_name": function_name,
        "chinese_name": chinese_name,
        "section": section,
        "call_signature": call_signature,
        "description": description,
        "return_type": return_type,
        "example_code": example_code,
        "params": params,
        "return_attrs": return_attrs,
    }


def _parse_article_function(article, section: str) -> dict | None:
    """Parse a complex function block in an <article> element.

    The article contains h5 sub-headings (参数, 返回值, 注意, 示例) that mark sections.
    The first <pre> element is the call signature.
    """
    first_pre = article.find("pre")
    if first_pre is None:
        return None

    call_signature = first_pre.get_text(strip=True) or None

    function_name = None
    if call_signature:
        function_name = _extract_function_name(call_signature)
    if not function_name:
        return None

    # Organize children by h5 section labels
    sections: dict[str, list] = {}
    current_h5 = None
    for child in article.children:
        if not hasattr(child, "name"):
            continue
        if child.name == "h5":
            current_h5 = child.get_text(strip=True)
            sections.setdefault(current_h5, [])
        elif current_h5 is not None:
            sections[current_h5].append(child)

    # Description: first non-pre, non-h5 child before any h5
    description = None
    for child in article.children:
        if not hasattr(child, "name"):
            continue
        if child.name == "h5":
            break
        if child.name in ("p",) and child != first_pre:
            text = child.get_text(strip=True)
            if text:
                description = text
                break

    # Extract return type from 返回值 section
    return_type = None
    for el in sections.get("返回值", sections.get("返回", [])):
        if hasattr(el, "name") and el.name in ("p", "ul", "ol"):
            text = el.get_text(strip=True)
            if text:
                return_type = text
                break

    # Extract example code from 示例 section
    example_code = None
    for el in sections.get("示例", []):
        if hasattr(el, "name") and el.name == "pre":
            example_code = el.get_text(strip=True) or None
            break

    # Extract params from 参数 section
    params = []
    for el in sections.get("参数", []):
        if hasattr(el, "name"):
            if el.name == "table":
                params = _extract_params_from_table(el)
                break
            elif el.name == "ul":
                params = _extract_params_from_ul(el)
                break

    # Extract return attributes from 返回值 section
    return_attrs = []
    for el in sections.get("返回值", sections.get("返回", [])):
        if hasattr(el, "name") and el.name == "table":
            return_attrs = _extract_return_attrs_from_table(el)
            break

    # Chinese name: look for the h3/h4 heading that directly precedes this article
    chinese_name = _find_article_chinese_name(article, function_name)

    # Fallback: derive chinese_name from description if not found from heading
    if not chinese_name and description:
        chinese_name = _chinese_name_from_description(description)

    return {
        "function_name": function_name,
        "chinese_name": chinese_name,
        "section": section,
        "call_signature": call_signature,
        "description": description,
        "return_type": return_type,
        "example_code": example_code,
        "params": params,
        "return_attrs": return_attrs,
    }


# ---------------------------------------------------------------------------
# Helper: function name extraction
# ---------------------------------------------------------------------------


def _chinese_name_from_description(description: str) -> str | None:
    """Extract a short Chinese name from the first sentence of a description.

    Takes the first clause (before 。，,. or newline) if it's short enough
    and contains Chinese characters.
    """
    import re
    if not description:
        return None
    # Take first sentence/clause
    first = re.split(r'[。，,.\n]', description)[0].strip()
    # Must contain Chinese, be reasonable length for a name
    if not first or len(first) > 40:
        return None
    has_chinese = any("\u4e00" <= c <= "\u9fff" for c in first)
    if not has_chinese:
        return None
    return first


def _find_article_chinese_name(article, function_name: str) -> str | None:
    """Find the Chinese heading that directly precedes an article element.

    Walks backwards from the article through its preceding siblings to find
    the nearest h3/h4 heading. Skips non-heading elements but stops at
    other articles or section boundaries.
    """
    el = article.find_previous_sibling()
    lookback = 5
    while el is not None and lookback > 0:
        if hasattr(el, "name"):
            if el.name in ("h3", "h4"):
                text = el.get_text(strip=True)
                if text and text != function_name:
                    has_chinese = any("\u4e00" <= c <= "\u9fff" for c in text)
                    if has_chinese and text not in _SECTION_MARKERS and text != "示例":
                        return text
                break
            if el.name in ("article", "h2"):
                break
        el = el.find_previous_sibling()
        lookback -= 1
    return None


def _extract_function_name(call_signature: str) -> str | None:
    """Extract a clean Python function name from a call signature string.

    Handles:
    - Leading import statements: "from jqdata import *\\nget_valuation(..."
    - Leading comment lines: "# 获取行业板块成分股get_industry_stocks(..."
    - Multi-line code blocks
    - Method calls: "obj.method(" -> "method"
    - finance.run_query(query(finance.TABLE_NAME...)) -> "TABLE_NAME"
      These are data table queries, not function calls. The table name
      (e.g., STK_SHAREHOLDER_TOP10) is the meaningful identifier.
    """
    if not call_signature:
        return None

    # Special case: finance.run_query(query(finance.TABLE_NAME...))
    # Extract the table name as the identifier
    import re
    table_match = re.search(r'finance\.(\w+)\)', call_signature)
    if table_match and 'run_query' in call_signature:
        table_name = table_match.group(1)
        if table_name not in ('run_query',) and _is_valid_python_name(table_name):
            return table_name

    lines = call_signature.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("from ", "import ", "# ")):
            continue
        if "(" not in stripped:
            continue
        candidate = stripped.split("(")[0].strip()
        candidate = candidate.lstrip("#").strip()
        # Handle method calls like finance.run_query
        if "." in candidate:
            candidate = candidate.rsplit(".", 1)[-1]
        if not candidate:
            continue
        if _is_valid_python_name(candidate):
            return candidate

    return None


def _is_valid_python_name(name: str) -> bool:
    """Return True if name is a valid Python identifier with no Chinese characters."""
    if not name:
        return False
    if any("\u4e00" <= c <= "\u9fff" for c in name):
        return False
    return name.isidentifier()


# ---------------------------------------------------------------------------
# Helper: sibling-traversal extractors
# ---------------------------------------------------------------------------


def _extract_description(heading, siblings: list) -> str | None:
    """Extract function description: first <p> sibling that is not a section label."""
    for el in siblings:
        if not hasattr(el, "name"):
            continue
        if el.name == "p":
            text = el.get_text(strip=True)
            if text and text not in _SECTION_MARKERS:
                return text
    return None


def _extract_by_label(siblings: list, label: str, preceding_label: bool = True) -> str | None:
    """Extract the <pre> element that immediately follows a <p> with the given label text."""
    found_label = False
    for el in siblings:
        if not hasattr(el, "name"):
            continue
        if el.name == "p" and el.get_text(strip=True) == label:
            found_label = True
            continue
        if found_label and el.name == "pre":
            return el.get_text(strip=True) or None
        if found_label and el.name == "p" and el.get_text(strip=True) in _SECTION_MARKERS:
            break
    return None


def _extract_return_type(siblings: list) -> str | None:
    """Extract return type from the 返回值/返回 section."""
    found_label = False
    for el in siblings:
        if not hasattr(el, "name"):
            continue
        text = el.get_text(strip=True) if el.name == "p" else ""
        if el.name == "p" and text in ("返回值", "返回"):
            found_label = True
            continue
        if found_label:
            if el.name == "p":
                if text and text not in _SECTION_MARKERS:
                    return text
                if text in _SECTION_MARKERS:
                    break
            elif el.name == "table":
                break
            elif el.name in ("ul", "ol"):
                t = el.get_text(strip=True)
                return t or None
    return None


def _extract_params_from_siblings(siblings: list) -> list[dict]:
    """Extract parameters from sibling elements after a heading."""
    found_label = False
    for el in siblings:
        if not hasattr(el, "name"):
            continue
        if el.name == "p" and el.get_text(strip=True) == "参数":
            found_label = True
            continue
        if found_label:
            if el.name == "table":
                return _extract_params_from_table(el)
            elif el.name == "ul":
                return _extract_params_from_ul(el)
            elif el.name == "p" and el.get_text(strip=True) in _SECTION_MARKERS:
                break
    return []


def _extract_return_attrs_from_siblings(siblings: list) -> list[dict]:
    """Extract return attributes from a table in the 返回值 section."""
    found_label = False
    for el in siblings:
        if not hasattr(el, "name"):
            continue
        text = el.get_text(strip=True) if el.name == "p" else ""
        if el.name == "p" and text in ("返回值", "返回"):
            found_label = True
            continue
        if found_label:
            if el.name == "table":
                return _extract_return_attrs_from_table(el)
            elif el.name == "p" and text in _SECTION_MARKERS:
                break
    return []


def _extract_params_from_table(table) -> list[dict]:
    """Extract params from a <table> element."""
    params = []
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 0:
            continue
        params.append({
            "param_name": cells[0].get_text(strip=True) or None,
            "param_type": cells[1].get_text(strip=True) if len(cells) > 1 else None,
            "description": cells[2].get_text(strip=True) if len(cells) > 2 else None,
        })
    return params


def _extract_params_from_ul(ul) -> list[dict]:
    """Extract params from a <ul> element."""
    params = []
    for li in ul.find_all("li"):
        text = li.get_text(strip=True)
        if not text:
            continue
        param_name, param_type, description = _parse_param_li_text(text)
        params.append({
            "param_name": param_name,
            "param_type": param_type,
            "description": description,
        })
    return params


def _extract_return_attrs_from_table(table) -> list[dict]:
    """Extract return attributes from a <table> element."""
    attrs = []
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 0:
            continue
        attrs.append({
            "attr_name": cells[0].get_text(strip=True) or None,
            "attr_type": cells[1].get_text(strip=True) if len(cells) > 1 else None,
            "description": cells[2].get_text(strip=True) if len(cells) > 2 else None,
        })
    return attrs


def extract_table_columns(html: str) -> list[dict]:
    """Extract table column definitions from a help API page.

    Finds two patterns:
    1. get_fundamentals tables: "表名: XXX" followed by a table with
       headers 列名|列的含义|解释
    2. STK_/FINANCE_ field tables: table following query(finance.XXX) code
       with headers 字段名称|中文名称|字段类型|含义

    Returns a list of dicts with: table_name, columns (list of column defs).
    """
    import re
    soup = BeautifulSoup(html, "lxml")
    content = soup.find(class_="help-api-right")
    if content is None:
        content = soup.body or soup

    results = []
    seen_tables = set()

    # Pattern 1: "表名: XXX" + column definition table
    # These are for get_fundamentals tables (valuation, balance, income, etc.)
    for text_node in content.find_all(string=re.compile(r'表名[:：]\s*\w+')):
        match = re.search(r'表名[:：]\s*(\w+)', text_node)
        if not match:
            continue
        table_name = match.group(1)
        if table_name in seen_tables:
            continue

        # Find the next <table> sibling after this text
        parent = text_node.parent
        tbl = None
        el = parent
        for _ in range(5):
            el = el.find_next_sibling()
            if el is None:
                break
            if hasattr(el, "name") and el.name == "table":
                tbl = el
                break
        # Also check if table is a child of the parent's next sibling
        if tbl is None:
            tbl = parent.find_next("table")

        if tbl is None:
            continue

        columns = _parse_column_def_table(tbl, style="fundamentals")
        if columns:
            seen_tables.add(table_name)
            results.append({"table_name": table_name, "columns": columns})

    # Pattern 2: query(finance.XXX) + field definition table
    # These are for STK_/FINANCE_ tables
    for pre in content.find_all("pre"):
        text = pre.get_text(strip=True)
        match = re.search(r'finance\.(\w+)\)', text)
        if not match or 'run_query' not in text:
            continue
        table_name = match.group(1)
        if table_name in ('run_query',) or table_name in seen_tables:
            continue

        # Find the next <table> after this pre
        tbl = pre.find_next("table")
        if tbl is None:
            continue

        # Verify this table has field definition headers
        first_row = tbl.find("tr")
        if first_row is None:
            continue
        header_text = first_row.get_text(strip=True)
        if '字段名称' not in header_text and '字段名' not in header_text and '列名' not in header_text:
            continue

        columns = _parse_column_def_table(tbl, style="stk")
        if columns:
            seen_tables.add(table_name)
            results.append({"table_name": table_name, "columns": columns})

    return results


def _parse_column_def_table(table, style: str = "fundamentals") -> list[dict]:
    """Parse a column definition HTML table into structured records.

    style="fundamentals": headers are 列名|列的含义|解释
    style="stk": headers are 字段名称|中文名称|字段类型|含义
    """
    columns = []
    rows = table.find_all("tr")

    # Skip header row(s)
    start = 0
    for i, row in enumerate(rows):
        ths = row.find_all("th")
        if ths:
            start = i + 1
            continue
        # Some tables use first td row as header
        tds = row.find_all("td")
        if tds:
            first_cell = tds[0].get_text(strip=True)
            if first_cell in ('列名', '字段名称', '字段名'):
                start = i + 1
                continue
            break

    for row in rows[start:]:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        col_name = cells[0].get_text(strip=True)
        if not col_name:
            continue

        if style == "fundamentals":
            columns.append({
                "column_name": col_name,
                "column_type": None,
                "meaning": cells[1].get_text(strip=True) if len(cells) > 1 else None,
                "description": cells[2].get_text(strip=True) if len(cells) > 2 else None,
            })
        else:  # stk
            columns.append({
                "column_name": col_name,
                "column_type": cells[2].get_text(strip=True) if len(cells) > 2 else None,
                "meaning": cells[1].get_text(strip=True) if len(cells) > 1 else None,
                "description": cells[-1].get_text(strip=True) if len(cells) > 3 else None,
            })

    return columns


def _parse_param_li_text(text: str) -> tuple[str | None, str | None, str | None]:
    """Parse a parameter list item text into (name, type, description)."""
    param_name = None
    param_type = None
    description = None

    if ": " in text:
        parts = text.split(": ", 1)
        param_name = parts[0].strip()
        rest = parts[1]
        if " - " in rest:
            type_part, desc_part = rest.split(" - ", 1)
            param_type = type_part.strip() or None
            description = desc_part.strip() or None
        elif "/" in rest and len(rest.split("/")[0]) < 20:
            param_type = rest.strip() or None
        else:
            description = rest.strip() or None
    elif " - " in text:
        parts = text.split(" - ", 1)
        param_name = parts[0].strip()
        description = parts[1].strip() or None
    else:
        param_name = text.strip()

    return param_name or None, param_type, description
