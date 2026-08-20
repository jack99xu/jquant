"""归档 Markdown 模板（纯字符串渲染，db 数据 → md，单向生成）。

spec §5 模板；所有函数只接收普通 dict，不做任何 db 访问。
"""
import json


def strategy_md(info: dict) -> str:
    """strategies/Sxxxx.md。"""
    parent = info["parent_strategy_id"] or "（无，根版本）"
    experiments = info["experiments"] or ["（无，快速检查点）"]
    runs = info["runs"] or ["（无）"]
    return f"""# {info['strategy_id']}

## 基本信息
- Parent: {parent}
- Git Commit: {info['git_commit_hash']}
- File Blob Hash: {info['file_blob_hash']}
- Created: {info['created_at']}

## 变化
{info['change_summary'] or '（无摘要）'}

## 关联实验
{chr(10).join(f'- {e}' for e in experiments)}

## 关联回测
{chr(10).join(f'- {r}' for r in runs)}
"""


def experiment_md(info: dict) -> str:
    """experiments/Exxxxx.md。"""
    cand = info["candidate_strategy_id"] or "（未回填）"
    if info.get("expected_effect"):
        expected = "\n".join(f"- {line}" for line in info["expected_effect"].splitlines())
    else:
        expected = "- （未填写）"
    studies = info["studies"] or ["（无）"]
    return f"""# {info['experiment_id']}

## 核心假设
{info['title']}
{info['description'] or '（无描述）'}

## Baseline / Candidate
- Baseline: {info['baseline_strategy_id']}
- Candidate: {cand}

## Change Scope / Validation Tier
- Change Scope: {info['change_scope']}
- Validation Tier: {info['validation_tier']}
- 试验次数: {info['n_trials']}

## 预期
{expected}

## 验证计划
{info['description'] or '（无）'}

## 关联 Study
{chr(10).join(f'- {s}' for s in studies)}

## 当前状态
{info['status']}
"""


def run_md(info: dict) -> str:
    """runs/Rxxxx.md。"""
    exp = info["experiment_id"] or "（无，快速检查点）"
    cap = info["initial_capital"]
    cap_line = f"- Initial Capital: {cap:,.0f}" if cap is not None else "- Initial Capital: —"
    freq = info["frequency"] or "—"
    n_trades = info["n_trades"] if info["n_trades"] is not None else "—"
    if info["benchmark"]:
        bench = f"- 基准: {info['benchmark']}"
        if info["benchmark_return"] is not None:
            bench += f"（基准收益 {info['benchmark_return']}）"
    else:
        bench = "- 基准: —"
    regime = info["regime"] or "—"
    params = info["parameters_json"]
    params_block = f"```yaml\n{params}\n```" if params else "（无）"
    status_lines = [f"## Status\n{info['status']}"]
    if info["error_type"]:
        status_lines.append(f"- Error Type: {info['error_type']}")
    if info["error_message"]:
        status_lines.append(f"- Error Message: {info['error_message']}")
    table = "\n".join(
        f"| {m['metric_name']} | {m['metric_value']} | {m['metric_source']} |"
        for m in info["metrics"]
    ) or "（无指标）"
    src = info["source_log_path"] or "见 `聚宽回测结果及运行日志.md` 对应条目（按日期或锚点定位，不在此重复粘贴）"
    notes = info["notes"] or "（无）"
    return f"""# {info['run_id']}

## Strategy / Experiment
- Strategy: {info['strategy_id']}
- Experiment: {exp}

## Backtest 设置
- Start: {info['start_date']}
- End: {info['end_date']}
{cap_line}
- Frequency: {freq}
- 调仓次数: {n_trades}
{bench}
- 市场状态: {regime}

## Parameters
{params_block}

{chr(10).join(status_lines)}

## Metrics

| 指标 | 数值 | 来源 |
|---|---|---|
{table}

## 原始数据位置
{src}

## Notes
{notes}
"""


def study_md(info: dict) -> str:
    """studies/STxxxx.md；"## 结论"由关联 Analysis 填充（reports 层负责）。"""
    try:
        design_pretty = json.dumps(json.loads(info["design_json"]), ensure_ascii=False, indent=2)
    except Exception:
        design_pretty = info["design_json"]
    run_rows = "\n".join(
        f"| {r['run_id']} | {r['group_name'] or '—'} | {r['role'] or '—'} | {r['partition'] or '—'} | "
        f"{_fmt(r['metrics'].get('total_return'))} | {_fmt(r['metrics'].get('max_drawdown'))} | "
        f"{_fmt(r['metrics'].get('sharpe'))} |"
        for r in info["runs"]
    ) or "（无 Run）"
    conclusion = info.get("conclusion") or "（留空，由 Analysis 填写）"
    return f"""# {info['study_id']}

## Experiment / 类型
- Experiment: {info['experiment_id']}
- 类型: {info['study_type']}

## 设计（预登记，禁止事后修改）
```yaml
{design_pretty}
```

## Runs
| Run | 分组 | 角色 | 分区 | 收益 | 最大回撤 | Sharpe |
|---|---|---|---|---|---|---|
{run_rows}

## 结论
{conclusion}
"""


def analysis_md(info: dict) -> str:
    """analyses/Axxxx.md；过拟合诊断行来自 analyze_study（reports 层注入）。"""
    signals = "\n".join(info["diagnostics"]) or "（无）"
    conf = f"{info['confidence']}" if info["confidence"] is not None else "—"
    return f"""# {info['analysis_id']}

## Study
{info['study_id']}

## 结论
{info['conclusion'] or '（未填写）'}

## 决策
- Decision: {info['decision']}
- Evidence Level: {info['evidence_level']}
- Confidence: {conf}

## 过拟合诊断
Overfitting Signals:
{signals}
"""


def _fmt(value) -> str:
    """数值格式化：None → —，其余原样输出。"""
    return "—" if value is None else str(value)