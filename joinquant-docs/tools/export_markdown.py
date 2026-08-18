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
    """读取 api_docs 全部函数，按章节首次出现顺序 + 函数名排序

    中文章节按 UTF-8 字节排序会打乱官网目录顺序（如 '交易' 在 '数据' 前），
    因此以每章首条记录的 rowid 作为章节序号，保持抓取时的官网顺序。
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT function_name, section, call_signature, description,
               return_type, example_code, chinese_name
        FROM api_docs AS d
        ORDER BY (SELECT MIN(rowid) FROM api_docs AS d2
                  WHERE d2.section = d.section), d.function_name
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
    lines.append(f"**签名:** `{escape_cell(doc['signature'])}`")
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
            lines.append(
                f"| {escape_cell(p['name'])} | {escape_cell(p['type'])} "
                f"| {req} | {escape_cell(p['desc'])} |"
            )
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


def escape_cell(value):
    """转义 Markdown 表格单元格中的竖线与换行，避免截断表格列/行

    仅用于表格单元格与行内代码（签名）等单行上下文；
    不得用于代码围栏内的 example_code（换行必须保留）。
    """
    return (value.replace('|', '\\|')
                 .replace('\r\n', ' ')
                 .replace('\r', ' ')
                 .replace('\n', ' '))


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
                lines.append(
                    f"| {escape_cell(c['name'])} | {escape_cell(c['type'])} "
                    f"| {escape_cell(c['meaning'])} | {escape_cell(c['desc'])} |"
                )
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
        lines.append(
            f"| {escape_cell(d['name'])} | {escape_cell(d['section'])} "
            f"| `{escape_cell(d['signature'])}` |"
        )
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
