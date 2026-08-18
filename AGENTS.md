# AGENTS.md

## 项目定位

项目分两部分：

- **聚宽知识库**（`joinquant-docs/`）：把聚宽官方 API 文档、数据字典、FAQ 整理成本地 Markdown，供 AI 写策略时 grep/read 检索，防止编造 API 签名。已生成（2026-08-18，plan 执行完毕）；维护任务是重跑抓取/导出（命令见下）
- **小市值策略研究**（`小市值/`）：小市值因子策略的迭代工作区，当前主要工作方向。工作流：改代码 → 用户复制到聚宽平台跑回测 → 回测结果与日志粘贴回本地 → 验证效果（详见"小市值策略"一节）

## 目录结构

- `joinquant-docs/` — 知识库根：
  - `api.md`（221 函数，按官网章节组织）、`index.md`（函数速查表 221 行）、`faq.md`（平台规则/FAQ）、`README.md`（总索引，含 AI 检索指引）
  - `data/` — 数据字典 5 个文件：Stock/Fund/Future/Index/Other（**无 Option.md**——db 中无 `OPT*` 表）
- `joinquant-docs/tools/` — 工具与数据源：
  - `export_markdown.py`（导出器，零第三方依赖）、`test_export.py`（15 个 pytest 测试）
  - `jq_knowledge.db`（数据源 SQLite）、`_src/`（上游 jq-docs-mcp 克隆，含 `run_scrape.py` 抓取脚本）
- `小市值/` — 小市值因子策略工作区（3 个 md，职责与约定见"小市值策略"一节）
- `docs/superpowers/` — 设计文档 `specs/2026-08-18-joinquant-docs-design.md` 与实施计划 `plans/2026-08-18-joinquant-docs.md`（已完成，改动流程时参照）

## 小市值策略（当前主战场）

三个文件的职责（勿混淆）：

- `小市值/小市值策略代码.md` — 唯一策略源码。**每次改动后的完整代码写回此文件**，由用户复制到聚宽平台运行。AI 无法在本地跑回测；回测区间/初始资金等配置在平台侧设置，代码中没有
- `小市值/聚宽回测结果及运行日志.md` — 用户把平台回测结果与运行日志粘贴至此。评价策略效果、排查报错**只准引用此文件内容**，不得编造收益/回撤/胜率数据
- `小市值/优化方向.md` — 用户记录的待优化项，**只读参考，禁止直接执行**。用户要求：每次实验必须明确变更范围、核心假设和验证等级；一个实验允许包含多个代码修改，但必须能明确说明这些修改共同验证的研究假设。若多个修改彼此独立、可单独验证，应拆分为多个实验；若多个修改是实现同一策略机制所必需的，可作为同一实验

策略要点（改动前先读该文件核对，以下为概览）：

- 逻辑：PE(TTM)<20 股票池中市值最大/最小各取一半 → 30 只等权"哑铃组合"，每 5 交易日（周一 09:30）调仓、开盘市价买入；唯一下单函数 `order_target_value`
- 过滤链顺序：688 科创板 → ST/退 → 停牌 → 涨停（`last_price < high_limit`）→ 次新（<180 天）→ 换手率 >1%（**自算**：昨日成交量/流通股本×10000×100；刻意不用 `valuation.turnover_ratio`，该字段不可靠）
- `get_fundamentals` 显式锚定 `context.previous_date`；`get_price` 取前一交易日数据，无未来函数

已知时间线矛盾（引用文件时注意）：

- 优化方向.md 称"当前策略不设流动性约束"，但当前代码已实现换手率过滤与 688 过滤——**文档条目不能直接当未完成事项**，须先对照代码核状态
- 回测日志文件停留在 2021-01~02 的旧回测（7 次调仓）；2024-01/2026-05/2026-07 等最新回测（最大回撤 17.42%、2026-07-22 后反弹 +21.6%）的摘要**未粘贴**，仅 优化方向.md 文字提及
- 日志解读参照：科创板"市价单需要指定保护限价"报错来自旧回测（当时无 688 过滤）；"因为资金有限，下单数量调整为 X"+"已经跌停，市价卖单取消"= 卖出未成交导致现金不足；"开仓/平仓数量必须是100的整数倍，调整为 X"为正常校验提示（INFO），非错误

## 聚宽平台要点（写/改策略代码时防编造）

- **聚宽没有 `sell()`**。卖出 = `order(security, -amount)` 或 `order_target(security, 0)`（签名以 `joinquant-docs/api.md` 为准）
- `order_target_value`/`order_target` 会先取消该标的未完成订单；`order` 创建失败返回 `None`
- `run_daily` 不在本地库（见"数据源与已知缺口"）：`time` 为具体时刻（如 `'14:50'`）时**必须分钟级回测**才执行；被调函数只收 `context` 参数；与 `handle_data` 勿混用
- 金额下单按当时实际价折算股数并向下取整到 100 股整数倍 → 滑点可致 Cash 为负/仓位>100%，官方 FAQ 认定为正常现象，非 bug
- 撮合：涨停市价买单、跌停市价卖单会被撤销；停牌股委托无法成交，须用 `get_current_data()[s].paused` 过滤
- 常见报错对照：`SecurityNotExist`=代码/后缀错误；`下单数量为0`=资金不足最小单位；`TimeoutError ... 1800 seconds`=单函数超时被强杀；`we can't find the handler`=模拟盘换代码后未 `after_code_changed`+`unschedule_all` 重注册
- 数据限制：指数不可买卖、无行业行情与指数 PE/股息率；`valuation` 字段口径：`market_cap` 总市值(亿元)、`circulating_market_cap` 流通市值、`pe_ratio`(TTM)、`pb_ratio`、`turnover_ratio`

## 常用命令（从仓库根实测可用）

```powershell
# 运行导出器测试（15 个）
python -m pytest joinquant-docs/tools/test_export.py -v

# 重新导出知识库（db → markdown，幂等）
python joinquant-docs/tools/export_markdown.py --db joinquant-docs/tools/jq_knowledge.db --out joinquant-docs

# 更新数据（抓官网 → 复制 db → 重导出；需先 pip 装 playwright 等依赖）
python joinquant-docs/tools/_src/run_scrape.py
Copy-Item joinquant-docs/tools/_src/jq_knowledge.db joinquant-docs/tools/jq_knowledge.db
python joinquant-docs/tools/export_markdown.py --db joinquant-docs/tools/jq_knowledge.db --out joinquant-docs
```

## 环境事实（实测验证）

- Windows + PowerShell 5.1。python 3.12.3 可用；**uv 不可用**（依赖安装用 pip）
- PowerShell 控制台为 GBK：python 脚本直接 print 中文会乱码，排查输出时用 `chcp 65001` 或 `PYTHONIOENCODING=utf-8`
- 已关联 GitHub 仓库 `https://github.com/jack99xu/jquant.git`（分支 `main`），改动后可正常 commit/push（push 前先看 `git status` 确认无敏感文件）
- `tools/_src` 上游克隆的 `.git` 元数据已按用户确认删除（2026-08-18 建仓时），`_src` 现为普通目录随仓库同步；上游源 `https://github.com/jiaweizhang1995/jq-docs-mcp.git`，需更新时可重新 clone
- .gitignore 已排除 `.opencode/`、`.omo/`、`.codegraph/`、`.pytest_cache/`、`__pycache__/`——新增工具目录前检查是否需补规则
- 权限坑：read/write/Get-Content/Copy-Item 等文件操作对**工作区外路径**（如 `C:\Users\14671\AppData\Local\Temp\opencode\`）会被权限规则拦截；但 git clone、python 执行可正常访问该路径。需要探查外部数据时，用命令方式（git/python）而非文件工具
- 临时工作目录 `C:\Users\14671\AppData\Local\Temp\opencode\` 已预授权（仅命令访问）
- 根目录 `.opencode/`、`.omo/`、`.codegraph/`、`.pytest_cache/` 为工具配置/会话状态/缓存，非项目内容，勿改动

## 数据源与已知缺口（检索时防误判，最重要）

- db 计数：`api_docs` 221 函数、`api_params` 83 参数（覆盖率低属预期，以**签名**为准）、`table_columns` 2479 字段（含中文含义）
- **`run_daily` 不在 db 中**（上游 jq-docs-mcp 数据缺口；策略API 区部分函数名存成本地上位名如 `definitialize`）。grep index.md 会看到 3 处 "run_daily" 字样——那是其他函数签名里内嵌的策略示例代码，**不是真实函数行**。用户要查 run_daily 时如实说明缺口，不要编造签名
- `api_return_attrs`（5 行，内容错误）与 `strategies`（社区策略）两表**不可用，禁止导出**
- `indicator` 表（股票财务指标）会被 `IND` 前缀规则分入 `data/Index.md`——分类规则如此，属已知

## 导出器实现要点（改动 `export_markdown.py` 前必读）

- `escape_cell`：表格单元格统一转义 `|` → `\|`、`\r\n`/`\n` → 空格；**严禁**应用于 `example_code` 代码围栏（围栏换行必须保留）
- `load_api_docs` 排序为"章节首次出现顺序（MIN(rowid)）"——中文按 UTF-8 字节序排会打乱章节顺序，**勿改回 `ORDER BY section`**
- 仅用标准库（sqlite3/os/argparse）；所有生成文件 UTF-8（python 打开文件显式 `encoding='utf-8'`）
- 代码注释用中文；变量命名语义化英文（禁拼音）

## 验收基准（维护后回归用）

函数 ≈221（±10%）、字段 ≈2479（±10%）；抽查 `get_price`/`order` 签名齐全；README 路径全部存在；数据字典含中文含义行 ≥2000。注：`run_daily` 抽查项因数据源缺口不适用。
