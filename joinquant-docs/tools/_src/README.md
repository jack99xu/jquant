<p align="center">
  <h1 align="center">jq-docs-mcp</h1>
  <p align="center">
    <strong>让 AI 写出正确的聚宽代码</strong>
  </p>
  <p align="center">
    <a href="https://python.org"><img src="https://img.shields.io/badge/python-3.12+-blue" alt="Python"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-brightgreen" alt="MCP"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  </p>
</p>

---

> **问题：** AI 写聚宽策略时总是瞎编函数签名、搞错参数名、返回值类型全靠猜。
>
> **方案：** 把聚宽官方文档塞进 AI 的工具箱，查了再写，一次写对。

**jq-docs-mcp** 是一个 [MCP](https://modelcontextprotocol.io) 服务器，内置 **221 个 API 函数** 和 **2,479 个数据表字段** 的完整文档。一行命令安装，AI 直接查表写代码。

## 30 秒安装

**Claude Code：**

```bash
claude mcp add jq-docs -- uvx --from git+https://github.com/jiaweizhang1995/jq-docs-mcp jq-docs-mcp
```

没了。重启 Claude，开始用。

<details>
<summary><b>Claude Desktop</b></summary>

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "jq-docs": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/jiaweizhang1995/jq-docs-mcp",
        "jq-docs-mcp"
      ]
    }
  }
}
```

</details>

## 效果演示

装好之后，直接对 Claude 说人话：

```
👤  get_price 怎么用？有哪些参数？
🤖  [调用 lookup_function] → 返回完整签名、8个参数说明、返回值类型、示例代码

👤  搜索融资融券相关的 API
🤖  [调用 search_docs] → 找到 get_mtss、get_margincash_stocks 等 4 个 API

👤  balance_sheet 表有哪些字段？
🤖  [调用 lookup_table_columns] → 返回 123 个字段的名称、类型、中文含义

👤  帮我写一个获取茅台近一年日线数据的策略
🤖  [先查 get_price 文档，确认参数] → 写出正确代码，不靠猜
```

**没有这个工具：** AI 靠记忆编代码 → 参数名拼错 → 运行报错 → 来回改

**有了这个工具：** AI 先查文档再写 → 一次正确 → 直接跑

## 6 个查询工具

| 工具 | 用途 | 示例 |
|------|------|------|
| `lookup_function` | 精确查询函数文档 | "get_price 的参数是什么" |
| `search_docs` | 中英文关键词搜索 | "搜索融资融券" |
| `list_by_section` | 按分类浏览 | "获取股票数据分类下有哪些函数" |
| `search_in_section` | 分类内搜索 | "在财务数据里搜索 balance" |
| `list_functions` | 列出全部 221 个函数 | "都有哪些可用的 API" |
| `lookup_table_columns` | 查询数据表字段 | "income_statement 有哪些列" |

## 数据覆盖

从聚宽官方 9 个帮助页面完整抓取：

```
📊 221 个 API 函数    — 签名、参数、返回值、示例代码
📋 2,479 个表字段    — 字段名、类型、中文含义
🔍 支持中英文搜索    — "融资融券" 和 "get_mtss" 都能找到
❌ 找不到时给建议    — 输错函数名会推荐相似函数
```

## 高级用法

### 自定义数据库

默认使用内置数据库。如果你自己抓取了更新的数据：

```bash
JQ_DB_PATH=/path/to/your/jq_knowledge.db jq-docs-mcp
```

### 重新抓取

```bash
git clone https://github.com/jiaweizhang1995/jq-docs-mcp.git
cd jq-docs-mcp
uv sync
uv run python run_scrape.py
```

> API 文档页面公开可访问，无需登录。策略页面需要手机号登录。

## 技术栈

- **运行时依赖：** 仅 [FastMCP](https://github.com/jlowin/fastmcp) — 轻量、零配置
- **数据库：** SQLite 只读模式，757KB，随包分发
- **传输协议：** stdio（本地运行，无需网络）

## License

MIT

---

<p align="center">
  <sub>Built with <a href="https://github.com/anthropics/claude-code">Claude Code</a></sub>
</p>
