# Research Registry v1（可追溯回测记录系统）

小市值策略研究登记系统：用 SQLite（`research/registry.db`）+ 归档 Markdown 记录每次策略代码改动与对应聚宽回测结果，支撑改动有效性分析与过拟合防护。

## 安装（一次性）

```powershell
pip install -e 小市值
```

安装后从仓库根 `D:\量化\聚宽` 执行 `python -m research ...`。

## 十条宪法

1. `小市值策略代码.md` 是唯一工作源码；每次登记 Strategy 前必须先 `git commit` 该文件，确保 `git_commit_hash` 对应硬盘实际内容。
2. Strategy Version 表示代码状态，不表示成功与否；快速检查点与正式实验版本都是合法 Strategy，用是否挂载 Experiment 区分。
3. Experiment 表示一个研究假设；`change_scope` 描述代码改动范围，`validation_tier` 描述需要多严格的验证，两者不必然相关。
4. 一个 Experiment 可以包含多个代码修改，但必须共同服务于同一个核心假设；独立假设必须拆成不同 Experiment。
5. Run 表示一次实际聚宽回测，必须允许 FAILED 和 INCOMPLETE，不得删除，包括不成功和数据不全的记录。
6. Metric 与 Run 结构分离存储；每条 Metric 必须标注来源，二手转述的数字不得标记为 `joinquant_pasted`。
7. Study 的 `design_json` 必须在看到 Run 结果之前登记，不允许事后调整分组/窗口配合已看到的结果。
8. Study 与 Run 是多对多关系；Strategy、Experiment、Run、Study、Analysis 全部可互相追溯，Strategy 谱系以 git commit 为准，不重复发明 diff 机制。
9. Analysis 的 decision 必须区分"结果事实"和"研究判断"：单次漂亮回测不能直接宣布策略有效，`ARCHITECTURAL` 级别改动在 Ablation/Rolling 类 Study 完成前不得给出 ACCEPT。
10. 一切 CLI 命令必须支持非交互（flag 或 JSON payload）调用，因为主要操作者是 AI 助手。

## 单位约定

- `metrics.metric_value` 一律存小数（0.213 而非 21.3%）；百分比先除 100 再存
- 非数值信息（如最大回撤区间 "2026/03/03,2026/06/30"）写入 `runs.notes` 或对应归档 md
- 约定指标名完整清单见 `schema.sql` 注释（spec 决策 D4）