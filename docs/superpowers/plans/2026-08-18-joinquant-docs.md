# 聚宽文档本地化整理 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `D:\jack99xu\opencodetest\810\joinquant-docs\` 下生成一份可供 AI 助手 grep/read 检索的聚宽知识库（api.md + 数据字典 + FAQ 索引 + README）。

**Architecture:** 复用 jq-docs-mcp 仓库（github.com/jiaweizhang1995/jq-docs-mcp）的抓取管线与内置 SQLite 数据库（`jq_knowledge.db`：api_docs 221 函数 / api_params 83 参数 / table_columns 2479 字段），新写零第三方依赖的导出器 `export_markdown.py` 将 SQLite 转为结构化 Markdown。抓取重跑为可选增强，失败不阻塞（使用内置 db）。

**Tech Stack:** Python 3.12（仅标准库 sqlite3/os/argparse）、pytest（测试）、git（获取源码）、pip（抓取依赖，可选）。

**已核实事实（2026-08-18 实测内置 db）：**
- 表结构：
  - `api_docs(function_name PK, section, call_signature, description, return_type, example_code, scraped_at, chinese_name)` — 221 行
  - `api_params(function_name, param_name, param_type, description, is_required)` — 83 行（参数覆盖率低，属预期，签名仍完整）
  - `api_return_attrs` — 5 行，抓取内容错误，**不导出**
  - `strategies` — 7 行社区策略，**不导出**
  - `table_columns(table_name, column_name, column_type, meaning, description)` — 2479 行，meaning 含中文含义
- 内置 db 中 example_code 多为 NULL；section 形如「数据API > 数据API大全」（含层级，用 ` > ` 分隔）

## Global Constraints

- 输出目录固定为 `D:\jack99xu\opencodetest\810\joinquant-docs\`；工具与中间产物放 `joinquant-docs\tools\`
- 所有生成文件编码 UTF-8（Python 打开文件必须显式 `encoding='utf-8'`）
- 导出器仅依赖 Python 标准库（sqlite3、os、argparse）；pytest 仅测试用
- 代码注释用中文；变量命名语义化英文
- 不导出 `api_return_attrs` 与 `strategies` 表
- 不执行 git commit（用户未要求版本管理）
- 每步验证失败必须停止并报告，不得跳过验证继续

---

### Task 1: 获取 jq-docs-mcp 源码与内置数据库

**Files:**
- Create: `joinquant-docs/tools/_src/`（git clone 目标）
- Create: `joinquant-docs/tools/jq_knowledge.db`（复制自 _src）

**Interfaces:**
- Produces: `joinquant-docs/tools/jq_knowledge.db` — Task 2 抓取与 Task 3 导出器的输入

- [ ] **Step 1: 创建工作区目录并克隆仓库**

```powershell
New-Item -ItemType Directory -Path "D:\jack99xu\opencodetest\810\joinquant-docs\tools" -Force
git clone --depth 1 https://github.com/jiaweizhang1995/jq-docs-mcp.git "D:\jack99xu\opencodetest\810\joinquant-docs\tools\_src"
```

Expected: clone 成功（耗时可能 1-3 分钟，网络慢时允许重试；之前实测该仓库可克隆成功）。

- [ ] **Step 2: 复制内置数据库到 tools/**

```powershell
Copy-Item "D:\jack99xu\opencodetest\810\joinquant-docs\tools\_src\jq_knowledge.db" "D:\jack99xu\opencodetest\810\joinquant-docs\tools\jq_knowledge.db"
```

- [ ] **Step 3: 验证 db 可用且表结构正确**

```powershell
python -c "import sqlite3; c=sqlite3.connect(r'D:\jack99xu\opencodetest\810\joinquant-docs\tools\jq_knowledge.db'); print(c.execute('SELECT COUNT(*) FROM api_docs').fetchone()[0], c.execute('SELECT COUNT(*) FROM table_columns').fetchone()[0], c.execute('SELECT DISTINCT section FROM api_docs LIMIT 20').fetchall())"
```

Expected: 输出 `221 2479` 开头，随后列出约 20 个 section 值（乱码可接受，utf-8 环境下正常）。若表不存在或计数异常（<100），停止并报告。

- [ ] **Step 4: 记录实际 section 值清单（供 Task 3 人工核对）**

```powershell
python -c "import sqlite3; c=sqlite3.connect(r'D:\jack99xu\opencodetest\810\joinquant-docs\tools\jq_knowledge.db'); [print(r[0]) for r in c.execute('SELECT DISTINCT section FROM api_docs')]"
```

Expected: 输出全部 section 值。将输出记录在任务笔记中，Task 3 的 api.md 章节结构以此为准。

---

### Task 2: 尝试重跑抓取获取最新数据（可选增强，失败不阻塞）

**Files:**
- Modify: `joinquant-docs/tools/jq_knowledge.db`（若抓取成功则被覆盖为新数据）

**Interfaces:**
- Consumes: `joinquant-docs/tools/_src/`（含 run_scrape.py 与 pyproject.toml）
- Produces: 最新的 `joinquant-docs/tools/jq_knowledge.db`（或维持内置版本）

- [ ] **Step 1: 查看抓取脚本的依赖声明**

```powershell
Get-Content "D:\jack99xu\opencodetest\810\joinquant-docs\tools\_src\pyproject.toml"
```

Expected: 看到 [project] dependencies 列表（大概率含 requests/beautifulsoup4 等）。

- [ ] **Step 2: 安装依赖**

```powershell
pip install -e "D:\jack99xu\opencodetest\810\joinquant-docs\tools\_src"
```

Expected: 安装成功或提示已安装。若 `-e` 安装失败（如 pyproject 结构问题），改为按 Step 1 看到的依赖清单逐个 `pip install <包名>`。

- [ ] **Step 3: 运行抓取**

```powershell
python "D:\jack99xu\opencodetest\810\joinquant-docs\tools\_src\run_scrape.py"
```

Expected: 脚本联网抓取聚宽官网帮助页并写入 `_src\jq_knowledge.db`。若报错（官网改版/反爬/超时），**记录错误信息后继续 Task 3**（保留内置 db），不得反复重试超过 2 次。

- [ ] **Step 4: 判断抓取结果并决定 db 来源**

```powershell
python -c "import sqlite3; c=sqlite3.connect(r'D:\jack99xu\opencodetest\810\joinquant-docs\tools\_src\jq_knowledge.db'); print('api_docs', c.execute('SELECT COUNT(*) FROM api_docs').fetchone()[0]); print('api_params', c.execute('SELECT COUNT(*) FROM api_params').fetchone()[0])"
```

- 若 api_docs ≥ 200 且 api_params 明显多于 83：抓取成功，执行 `Copy-Item _src\jq_knowledge.db → tools\jq_knowledge.db` 覆盖内置版
- 否则：保留内置 db（api_docs 221 / api_params 83），记录「抓取未改善，使用内置 db」

---

### Task 3: TDD 编写导出器 export_markdown.py

**Files:**
- Create: `joinquant-docs/tools/export_markdown.py`
- Create: `joinquant-docs/tools/test_export.py`（pytest，与脚本同目录便于直接运行）

**Interfaces:**
- Consumes: `joinquant-docs/tools/jq_knowledge.db`（schema 见 Global Constraints）
- Produces: 以下函数供 main 与测试使用，Task 4 调用：
  - `load_api_docs(conn) -> list[dict]`，dict 键：name/section/signature/description/return_type/example/chinese_name
  - `load_params(conn) -> dict[str, list[dict]]`，外层键为函数名，内层 dict 键：name/type/desc/required
  - `load_table_columns(conn) -> dict[str, list[dict]]`，外层键为表名，内层 dict 键：name/type/meaning/desc
  - `classify_table(table_name) -> str`（返回文件名如 'Stock.md'）
  - `render_function(doc, params) -> str`
  - `render_api_md(docs, params) -> str`
  - `render_data_md(tables) -> dict[str, str]`（文件名 → 文件内容）
  - `render_index_md(docs) -> str`

- [ ] **Step 1: 写失败测试**

创建 `joinquant-docs/tools/test_export.py`：

```python
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
```

- [ ] **Step 2: 运行测试确认失败**

```powershell
python -m pytest "D:\jack99xu\opencodetest\810\joinquant-docs\tools\test_export.py" -v
```

Expected: 全部失败，报 `ModuleNotFoundError: No module named 'export_markdown'`。

- [ ] **Step 3: 编写导出器实现**

创建 `joinquant-docs/tools/export_markdown.py`：

```python
# -*- coding: utf-8 -*-
"""聚宽知识库导出器：从 jq_knowledge.db 导出结构化 Markdown

用法:
    python export_markdown.py --db tools/jq_knowledge.db --out ..
输出:
    api.md          策略 API 全文（按官网章节组织）
    index.md        函数速查表（函数名 | 章节 | 签名）
    data/*.md       数据字典（按表名前缀分类：Stock/Fund/Future/Index/Option/Other）
"""
import argparse
import os
import sqlite3

DATA_HEADER = (
    "# 聚宽数据字典\n\n"
    "> 数据来源：聚宽官方数据文档，字段含义以 meaning 列为准。\n\n"
    "---\n\n"
)


def load_api_docs(conn):
    """读取 api_docs 全部函数，按章节+函数名排序"""
    cur = conn.cursor()
    cur.execute("""
        SELECT function_name, section, call_signature, description,
               return_type, example_code, chinese_name
        FROM api_docs ORDER BY section, function_name
    """)
    return [
        {
            'name': row[0], 'section': row[1] or '', 'signature': row[2] or '',
            'description': row[3] or '', 'return_type': row[4] or '',
            'example': row[5] or '', 'chinese_name': row[6] or '',
        }
        for row in cur.fetchall()
    ]


def load_params(conn):
    """读取 api_params，按函数名分组"""
    cur = conn.cursor()
    cur.execute("""
        SELECT function_name, param_name, param_type, description, is_required
        FROM api_params
    """)
    params = {}
    for row in cur.fetchall():
        params.setdefault(row[0], []).append({
            'name': row[1] or '', 'type': row[2] or '',
            'desc': row[3] or '', 'required': bool(row[4]),
        })
    return params


def load_table_columns(conn):
    """读取 table_columns，按表名分组"""
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name, column_name, column_type, meaning, description
        FROM table_columns ORDER BY table_name, column_name
    """)
    tables = {}
    for row in cur.fetchall():
        tables.setdefault(row[0], []).append({
            'name': row[1] or '', 'type': row[2] or '',
            'meaning': row[3] or '', 'desc': row[4] or '',
        })
    return tables


def classify_table(table_name):
    """按表名前缀归入数据字典分类文件"""
    up = table_name.upper()
    if up.startswith('STK'):
        return 'Stock.md'
    if up.startswith('FUND') or up.startswith('FND'):
        return 'Fund.md'
    if up.startswith('FUT'):
        return 'Future.md'
    if up.startswith('IND') or 'INDEX' in up:
        return 'Index.md'
    if up.startswith('OPT'):
        return 'Option.md'
    return 'Other.md'


def render_function(doc, params):
    """单个函数渲染为 Markdown 小节"""
    lines = [f"### {doc['name']}（{doc['chinese_name']}）", ""]
    lines.append(f"**签名:** `{doc['signature']}`")
    if doc['section']:
        lines.append(f"**章节:** {doc['section']}")
    if doc['description']:
        lines.append(f"**说明:** {doc['description']}")
    param_list = params.get(doc['name'], [])
    if param_list:
        lines.append("")
        lines.append("**参数:**")
        lines.append("")
        lines.append("| 参数名 | 类型 | 必填 | 说明 |")
        lines.append("|--------|------|------|------|")
        for p in param_list:
            req = '是' if p['required'] else '否'
            lines.append(f"| {p['name']} | {p['type']} | {req} | {p['desc']} |")
    if doc['return_type']:
        lines.append("")
        lines.append(f"**返回值:** {doc['return_type']}")
    if doc['example']:
        lines.append("")
        lines.append("**示例代码:**")
        lines.append("")
        lines.append("```python")
        lines.append(doc['example'])
        lines.append("```")
    return "\n".join(lines)


def render_api_md(docs, params):
    """全部函数按章节分组渲染为 api.md 内容"""
    lines = [
        "# 聚宽策略 API 文档", "",
        "> 数据来源：聚宽官方 API 文档（joinquant.com/help/api/help），由 jq-docs-mcp 抓取入库后导出。",
        "> 参数信息来自官方页面提取，部分函数可能缺失参数明细，以**签名**为准。",
        "", "---", "",
    ]
    sections = {}
    for doc in docs:
        sections.setdefault(doc['section'], []).append(doc)
    for section, section_docs in sections.items():
        lines.append(f"## {section}")
        lines.append("")
        for doc in section_docs:
            lines.append(render_function(doc, params))
            lines.append("")
            lines.append("---")
            lines.append("")
    return "\n".join(lines)


def render_data_md(tables):
    """数据字典按分类文件渲染；返回 {文件名: 内容}"""
    grouped = {}
    for table_name, cols in tables.items():
        grouped.setdefault(classify_table(table_name), []).append((table_name, cols))
    out = {}
    for fname, table_list in grouped.items():
        lines = [DATA_HEADER]
        for table_name, cols in table_list:
            lines.append(f"## {table_name}")
            lines.append("")
            lines.append("| 字段名 | 类型 | 含义 | 说明 |")
            lines.append("|--------|------|------|------|")
            for c in cols:
                lines.append(f"| {c['name']} | {c['type']} | {c['meaning']} | {c['desc']} |")
            lines.append("")
        out[fname] = "\n".join(lines)
    return out


def render_index_md(docs):
    """函数速查表：函数名 | 章节 | 签名"""
    lines = [
        "# 聚宽 API 函数速查表", "",
        "| 函数名 | 章节 | 签名 |",
        "|--------|------|------|",
    ]
    for d in docs:
        lines.append(f"| {d['name']} | {d['section']} | `{d['signature']}` |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='聚宽知识库导出器')
    parser.add_argument('--db', default='tools/jq_knowledge.db', help='SQLite 数据库路径')
    parser.add_argument('--out', default='.', help='输出目录（joinquant-docs 根目录）')
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    docs = load_api_docs(conn)
    params = load_params(conn)
    tables = load_table_columns(conn)
    conn.close()
    print(f"加载: 函数 {len(docs)} | 参数 {sum(len(v) for v in params.values())} | 数据表 {len(tables)}")

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, 'api.md'), 'w', encoding='utf-8') as f:
        f.write(render_api_md(docs, params))
    with open(os.path.join(args.out, 'index.md'), 'w', encoding='utf-8') as f:
        f.write(render_index_md(docs))
    data_out = render_data_md(tables)
    data_dir = os.path.join(args.out, 'data')
    os.makedirs(data_dir, exist_ok=True)
    for fname, content in data_out.items():
        with open(os.path.join(data_dir, fname), 'w', encoding='utf-8') as f:
            f.write(content)
    print(f"完成: api.md, index.md, data/ 下 {len(data_out)} 个分类文件")


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: 运行测试确认通过**

```powershell
python -m pytest "D:\jack99xu\opencodetest\810\joinquant-docs\tools\test_export.py" -v
```

Expected: 9 个测试全部 PASS。若有失败，修复实现代码（不得修改测试）后重跑，直至全绿。

---

### Task 4: 运行导出器生成知识库文件

**Files:**
- Create: `joinquant-docs/api.md`
- Create: `joinquant-docs/index.md`
- Create: `joinquant-docs/data/Stock.md`、`Fund.md`、`Future.md`、`Index.md`、`Option.md`、`Other.md`（按实际分类，可能缺少数个）

**Interfaces:**
- Consumes: `joinquant-docs/tools/jq_knowledge.db`、`joinquant-docs/tools/export_markdown.py`（Task 3 产物）

- [ ] **Step 1: 运行导出器**

```powershell
python "D:\jack99xu\opencodetest\810\joinquant-docs\tools\export_markdown.py" --db "D:\jack99xu\opencodetest\810\joinquant-docs\tools\jq_knowledge.db" --out "D:\jack99xu\opencodetest\810\joinquant-docs"
```

Expected: 输出 `加载: 函数 221 | 参数 83 | 数据表 N` 与 `完成: api.md, index.md, data/ 下 M 个分类文件`（M ≤ 6）。

- [ ] **Step 2: 验证计数与文件存在**

```powershell
python -c "
import re
api = open(r'D:\jack99xu\opencodetest\810\joinquant-docs\api.md', encoding='utf-8').read()
idx = open(r'D:\jack99xu\opencodetest\810\joinquant-docs\index.md', encoding='utf-8').read()
import os
data_dir = r'D:\jack99xu\opencodetest\810\joinquant-docs\data'
print('api.md 函数小节数:', api.count('### '))
print('index.md 函数行数:', idx.count('| ') - 2)
print('data 文件:', os.listdir(data_dir))
"
```

Expected: 函数小节数 = 221（容差 ±10%，若重跑抓取成功则以实际计数为准并记录）；index 行数 = 221；data 目录含 1-6 个 .md 文件。

- [ ] **Step 3: 抽查数据字典含中文含义**

```powershell
python -c "
import glob
ok = 0
for p in glob.glob(r'D:\jack99xu\opencodetest\810\joinquant-docs\data\*.md'):
    lines = [l for l in open(p, encoding='utf-8') if l.startswith('| ') and '含义' not in l]
    with_meaning = [l for l in lines if len(l.split('|')) >= 4 and l.split('|')[3].strip()]
    ok += len(with_meaning)
    print(p.split(chr(92))[-1], '字段行:', len(lines), '含含义:', len(with_meaning))
print('总计含中文含义的字段行:', ok)
"
```

Expected: 每个文件「含含义」> 0，总计 ≥ 2000（2479 字段大多有 meaning；若明显偏少，检查 meaning 列是否被其他列挤占，必要时调整渲染模板）。

---

### Task 5: 获取 FAQ / 平台规则文档

**Files:**
- Create: `joinquant-docs/faq.md`

**Interfaces:**
- Consumes: 无（外部数据源）
- Produces: `joinquant-docs/faq.md` — Task 6 README 引用

**背景:** jq-docs-mcp 数据库不含 FAQ 页面数据（其 9 个页面聚焦 API 与数据字典）。FAQ 内容取自第三方仓库 lzwme/finance-quant-skills（其 joinquant-docs 目录从聚宽官方 FAQ 页面离线同步）。

- [ ] **Step 1: 尝试 webfetch 获取 faq.md（主 URL）**

```powershell
# 用 webfetch 抓取 raw 文件（若失败换 Step 2 备用 URL）
```

用 webfetch 工具请求：`https://raw.githubusercontent.com/lzwme/finance-quant-skills/main/skills/joinquant-docs/faq.md`
Expected: 返回 Markdown 内容（含"常见问题"、"复权"、"更新频率"等章节）。将内容写入 `joinquant-docs/faq.md`（UTF-8）。

- [ ] **Step 2: 主 URL 失败时用备用分支 URL**

用 webfetch 工具请求：`https://raw.githubusercontent.com/lzwme/finance-quant-skills/master/skills/joinquant-docs/faq.md`
Expected: 同上。若仍失败（仓库已删/网络不可达），创建 `joinquant-docs/faq.md` 写入以下说明并继续：

```markdown
# 聚宽平台规则与 FAQ

> 本文件未能自动获取。官方 FAQ 地址：https://www.joinquant.com/help/api/help?name=faq
> 建议手动导出该页面内容后替换本文件。
```

- [ ] **Step 3: 验证 faq.md 非空且为有效 Markdown**

```powershell
python -c "content = open(r'D:\jack99xu\opencodetest\810\joinquant-docs\faq.md', encoding='utf-8').read(); print('字节数:', len(content.encode('utf-8')), '| 标题数:', content.count('# ')); print('包含FAQ标记:', 'FAQ' in content or '常见问题' in content)"
```

Expected: 字节数 > 1000（说明文件真实抓取成功）；若为手动占位说明，字节数可较小但必须包含官方 FAQ 链接。

---

### Task 6: 编写 README.md 总索引

**Files:**
- Create: `joinquant-docs/README.md`

**Interfaces:**
- Consumes: Task 4 生成的实际文件名与计数

- [ ] **Step 1: 写入 README.md**

创建 `joinquant-docs/README.md`：

```markdown
# 聚宽（JoinQuant）平台知识库

> 供 AI 助手与本人查阅的本地化文档。数据来自聚宽官方帮助页面，由 jq-docs-mcp 抓取入库后导出为 Markdown。
> 生成日期：{YYYY-MM-DD（以实际执行为准）}；函数 {实际函数数} 个，数据字段 {实际字段数} 个。

## 文件清单

| 文件 | 内容 | 何时查阅 |
|------|------|----------|
| `api.md` | 策略 API 全文：架构、设置、数据获取、交易、对象，按官网章节组织 | 查任意 API 的签名、参数、返回值 |
| `index.md` | 全部函数速查表：函数名 → 章节 + 签名 | 不确定函数是否存在 / 记不清签名 |
| `faq.md` | 平台规则与 FAQ（运行频率、复权、常见问题，来源见文件头） | 数据异常、环境差异、概念澄清 |
| `data/Stock.md` | 股票数据字典（字段类型与中文含义） | 财务/行情字段名、含义 |
| `data/Fund.md` | 基金数据字典 | 基金净值/行情字段 |
| `data/Future.md` | 期货数据字典 | 期货合约/行情字段 |
| `data/Index.md` | 指数数据字典 | 指数成分/行情字段 |
| `data/Option.md` | 期权数据字典（若存在） | 期权字段 |
| `data/Other.md` | 未分类表（若存在） | 兜底查询 |
| `tools/` | 抓取与导出工具（含 jq_knowledge.db） | 日后更新文档用 |

## AI 检索指引（给助手）

1. **定位函数**：先 grep `index.md` 确认函数存在与签名，如 `grep "get_price" index.md`。
2. **查详情**：在 `api.md` 中按函数名定位小节：`grep -n "^### get_price" api.md`，然后读取该小节。
3. **查字段**：在 `data/` 中搜表名或字段名：`grep -n "STK_AUDIT_OPINION" data/*.md`。
4. **写代码前必须核对签名**，本库签名直接来自官网，禁止凭记忆编造参数。

## 更新方法

```powershell
python tools/_src/run_scrape.py   # 重抓官网 → _src\jq_knowledge.db
Copy-Item tools/_src/jq_knowledge.db tools/jq_knowledge.db
python tools/export_markdown.py --db tools/jq_knowledge.db --out .
```

## 已知限制

- 部分函数的参数明细/示例代码在官网页面结构变化后未被完整提取（参数仅 {实际参数数} 条记录），以 `api.md` 中的**签名**为准。
- 数据字典字段以官网文档为准，字段 `meaning` 可能缺失（保留为空）。
```

- [ ] **Step 2: 验证 README 中所有路径真实存在**

```powershell
python -c "
import os
base = r'D:\jack99xu\opencodetest\810\joinquant-docs'
for line in open(os.path.join(base, 'README.md'), encoding='utf-8'):
    line = line.strip()
    if line.startswith('| `'):
        p = line.split('`')[1]
        print(('OK ' if os.path.exists(os.path.join(base, p)) else 'MISSING ') + p)
"
```

Expected: 所有文件行输出 `OK`（含 faq.md）。若某分类文件不存在（如 Option.md 无数据），在 README 表格中删除该行。

---

### Task 7: 最终验收（对照设计文档验证标准）

**Files:** 无新增（只读验证）

- [ ] **Step 1: 计数验收**

```powershell
python -c "
import sqlite3
c = sqlite3.connect(r'D:\jack99xu\opencodetest\810\joinquant-docs\tools\jq_knowledge.db')
print('api_docs:', c.execute('SELECT COUNT(*) FROM api_docs').fetchone()[0])
print('table_columns:', c.execute('SELECT COUNT(*) FROM table_columns').fetchone()[0])
"
```

Expected: api_docs ≈ 221（±10%，若 Task 2 重抓成功则以新值计，须在报告中注明）；table_columns ≈ 2479（±10%）。超出容差必须说明原因。

- [ ] **Step 2: 抽查 3 个常用函数**

```powershell
python -c "
import re
api = open(r'D:\jack99xu\opencodetest\810\joinquant-docs\api.md', encoding='utf-8').read()
for name in ['get_price', 'order', 'run_daily']:
    m = re.search(r'### ' + name + r'\uFF08.*?---', api, re.S)
    print('=====', name, '=====')
    print((m.group(0)[:600] if m else 'NOT FOUND'))
"
```

Expected: 每个函数输出含 `### 函数名`、`**签名:**`、`**章节:**`；get_price/order 若参数表存在则含 `**参数:**` 表头。缺失签名视为失败。

- [ ] **Step 3: 索引可检索性验证**

```powershell
Select-String -Path "D:\jack99xu\opencodetest\810\joinquant-docs\index.md" -Pattern "get_price|run_daily|order\(" | Select-Object -First 5
```

Expected: 输出 3 行含函数名的速查行，格式为 `| 函数名 | 章节 | 签名 |`。

- [ ] **Step 4: 数据字典非空且含中文含义**

```powershell
python -c "
import glob
total = 0
for p in glob.glob(r'D:\jack99xu\opencodetest\810\joinquant-docs\data\*.md'):
    n = len([l for l in open(p, encoding='utf-8') if l.startswith('| ') and '含义' not in l])
    total += n
print('数据字典字段总行数:', total)
"
```

Expected: ≥ 2000。

- [ ] **Step 5: 汇总验收报告**

在回复中输出：函数数、字段数、data 分类文件清单、3 函数抽查结果、README 路径校验结果。对照设计文档 4 条验证标准逐条给出「通过/不通过」。任一不通过则说明原因并给出修复方案，不得宣称完成。
