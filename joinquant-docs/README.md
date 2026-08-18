# 聚宽（JoinQuant）平台知识库

> 供 AI 助手与本人查阅的本地化文档。数据来自聚宽官方帮助页面，由 jq-docs-mcp 抓取入库后导出为 Markdown。
> 生成日期：2026-08-18；函数 221 个，数据字段 2476 个。

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

- 部分函数的参数明细/示例代码在官网页面结构变化后未被完整提取（参数仅 83 条记录），以 `api.md` 中的**签名**为准。
- 数据字典字段以官网文档为准，字段 `meaning` 可能缺失（保留为空）。
