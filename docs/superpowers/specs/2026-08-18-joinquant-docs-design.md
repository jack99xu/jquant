# 聚宽平台文档本地化整理 — 设计文档

日期：2026-08-18
状态：已获用户确认

## 背景与目标

用户正在聚宽（JoinQuant）平台编写量化策略。聚宽的代码规范、API 调用规则等官方文档分散在官网多个页面（API 文档、FAQ、数据字典），查阅不便。目标是将这些内容整理到本地，形成一份**供 AI 助手查阅**的结构化 Markdown 知识库，AI 写策略时可先检索文档再写代码，避免编造函数签名。

## 需求确认

| 维度 | 结论 |
|------|------|
| 用途 | 给 AI 助手查阅（read/grep 检索） |
| 范围 | 策略 API 文档（核心）、数据字典、平台规则与 FAQ |
| 范围外 | JQData SDK 文档（本期不做） |
| 存放位置 | 当前工作目录 `D:\jack99xu\opencodetest\810` |
| 形式 | 结构化 Markdown + 索引文件（零依赖，任何 AI 工具可用） |

## 方案选择

采用**方案 B：复用 jq-docs-mcp 抓取管线 + 自写导出脚本**。

- 数据源：聚宽官网 9 个帮助页面（公开可访问，无需登录）
- 复用 `jiaweizhang1995/jq-docs-mcp` 的抓取逻辑（`run_scrape.py`），产出 SQLite 数据库（约 221 个 API 函数、2479 个数据表字段）
- 新写 `export_markdown.py` 将 SQLite 转换为结构化 Markdown
- Fallback：若官网改版/反爬导致抓取失败，改用 `lzwme/finance-quant-skills` 的现成离线文件

环境：Python 3.12.3 ✅、git ✅（uv 未安装，用 pip 安装依赖）。

## 目录结构

```
D:\jack99xu\opencodetest\810\
└── joinquant-docs\              # 整理后的聚宽知识库（核心产出）
    ├── README.md                # 总索引：内容清单、目录导航、AI 检索指引
    ├── api.md                   # 策略 API 全文：约 221 个函数，按官网章节组织
    │                            #   （架构/设置/数据获取/交易/对象/示例）
    ├── faq.md                   # 平台规则与 FAQ（运行频率、复权、常见问题）
    ├── index.md                 # 函数速查表：函数名 → 所属章节 + 一行签名摘要
    ├── data\                    # 数据字典（2479 个字段按品类拆分）
    │   ├── Stock.md             #   股票
    │   ├── Fund.md              #   基金
    │   ├── Future.md            #   期货
    │   ├── Index.md             #   指数
    │   └── ...（按官网实际页面数）
    └── tools\                   # 工具（保留以便日后更新）
        ├── scrape_jq.py         #   抓取器（取自 jq-docs-mcp）
        ├── jq_knowledge.db      #   抓取产出的 SQLite 数据库（中间产物）
        └── export_markdown.py   #   导出器（新写：SQLite → Markdown）
```

## 数据流

```
聚宽官网 9 个帮助页面（公开可访问）
   ↓  scrape_jq.py（复用 jq-docs-mcp 抓取逻辑）
jq_knowledge.db（SQLite：functions 表 + tables/fields 表）
   ↓  export_markdown.py（新写导出器）
joinquant-docs/ 下的 Markdown 文件 + README/index
```

### 导出器输出规则

- **api.md**：按官网章节顺序排列函数，每个函数固定模板：
  `### 函数名` + 签名、参数表（名称/类型/说明）、返回值、示例代码
- **data/***：按数据表分组字段，字段行含名称/类型/中文含义
- **index.md**：全量函数名字母序速查表，每行 `函数名 | 章节 | 一句话签名`
- 文件编码统一 UTF-8，方便 AI 直接 read/grep

## 错误处理

- 抓取阶段：官网请求失败自动重试 3 次；若官网改版导致解析失败，报错并提示改用回退方案（lzwme/finance-quant-skills 的现成离线文件，需先检查其格式与覆盖范围，再决定转换方式）
- 导出阶段：空字段跳过不报错，保证文件完整性；导出器编写前先实际检查 jq-docs-mcp 的 SQLite schema，避免按假设开发
- 运行全程打印进度日志，可排查

## 验证标准（完成即验收）

1. 函数数量 ≈ 221、字段数量 ≈ 2479（与 jq-docs-mcp 声称一致；容差 ±10%，超出需说明原因）
2. 抽查 3 个常用函数（`get_price`、`order`、`run_daily`）：签名、参数、返回值齐全
3. `README.md` 中的每个文件路径真实存在；grep 抽查索引中的函数名能在对应文件中找到
4. 数据字典文件非空，包含字段的中文含义