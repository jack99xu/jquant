"""Study 统计分析 + 5 项过拟合诊断 + Analysis 结论登记（spec §6/§9/§10 Phase 6）。

约定：诊断只输出 [OK]/[WARN]/[N/A] 行，不下"过拟合"结论；
最终判断留给 analysis create 的人工/AI 决策。
数据不足（SINGLE、缺分组、缺 oos 分区等）一律输出 [N/A] 而非抛错。
"""
import sqlite3
import statistics

from research import ids

VALID_DECISIONS = {"ACCEPT", "REJECT", "INCONCLUSIVE", "DEFER"}
VALID_EVIDENCE = {f"E{i}" for i in range(7)}  # E0（尚未验证）~ E6（跨多市场环境验证）

# ---- 诊断阈值（v1 简化口径，可调常量；仅供 WARNING 提示，不作最终结论）----
OOS_GAP_RATIO = 0.7     # oos 均值 < is 均值 × 0.7 → WARN（is 均值为正时）
OOS_GAP_ABS = 0.2       # is 均值为负/零时的绝对差距阈值
BEST_MEDIAN_GAP = 0.5   # (best − median) / |median| ≥ 0.5 → WARN（"显著优于"口径）
PARAM_CV_WARN = 0.5     # 参数组均值 CV > 0.5 → WARN（对参数敏感）

# 主指标候选顺序（按优先级取第一个候选 Run 中存在的）
_PRIMARY_METRICS = ("total_return", "annual_return", "benchmark_excess_return", "sharpe")


def _study_run_rows(conn: sqlite3.Connection, study_id: str) -> list[dict]:
    """study_runs 关联 runs + metrics，每 run 一个 dict（非空数值指标）。"""
    rows = conn.execute(
        "SELECT sr.group_name, sr.role, sr.partition, r.run_id "
        "FROM study_runs sr JOIN runs r ON r.run_id = sr.run_id "
        "WHERE sr.study_id=? ORDER BY sr.run_id", (study_id,)
    ).fetchall()
    result = []
    for r in rows:
        metrics = {}
        for m in conn.execute(
            "SELECT metric_name, metric_value FROM metrics WHERE run_id=?", (r["run_id"],)
        ):
            if m["metric_value"] is not None:
                metrics[m["metric_name"]] = m["metric_value"]
        result.append({"run_id": r["run_id"], "group_name": r["group_name"],
                       "role": r["role"], "partition": r["partition"], "metrics": metrics})
    return result


def _group_means(rows: list[dict], metric: str, role: str | None = None) -> dict[str, float]:
    """按分组（group_name，缺省用 run_id 兜底）聚合各 run 指标均值。"""
    groups: dict[str, list[float]] = {}
    for r in rows:
        if role is not None and r["role"] != role:
            continue
        val = r["metrics"].get(metric)
        if val is None:
            continue
        key = r["group_name"] or r["run_id"]
        groups.setdefault(key, []).append(val)
    return {k: statistics.mean(v) for k, v in groups.items()}


def _diag_window_stability(rows: list[dict], metric: str) -> str:
    """多窗口方向一致性（至少 2 个分组才可计算）。"""
    means = list(_group_means(rows, metric, role="candidate").values())
    if len(means) < 2:
        return "[N/A] 数据不足（窗口稳定性需要 ≥2 个分组）"
    if all(m >= 0 for m in means) or all(m <= 0 for m in means):
        return "[OK]   多窗口方向一致"
    return "[WARN] 多窗口方向不一致（分组间收益方向冲突）"


def _diag_parameter_stability(rows: list[dict], metric: str) -> str:
    """参数稳定性：参数组均值离散度（CV），至少 3 个参数组才可计算。"""
    means = list(_group_means(rows, metric, role="candidate").values())
    if len(means) < 3:
        return "[N/A] 数据不足（参数稳定性需要 ≥3 个参数组）"
    avg = statistics.mean(means)
    cv = statistics.pstdev(means) / abs(avg) if avg else float("inf")
    if cv > PARAM_CV_WARN:
        return f"[WARN] 参数间均值离散度过高（CV={cv:.2f}），结果对参数敏感"
    return "[OK]   参数间表现稳定"


def _diag_factor_monotonicity(rows: list[dict], metric: str) -> str:
    """因子单调性：按分组名排序后均值逐级同向，至少 3 个层级才可计算。"""
    means = _group_means(rows, metric, role="candidate")
    if len(means) < 3:
        return "[N/A] 数据不足（因子单调性需要 ≥3 个层级）"
    vals = [means[k] for k in sorted(means)]
    diffs = [b - a for a, b in zip(vals, vals[1:])]
    if all(d >= 0 for d in diffs) or all(d <= 0 for d in diffs):
        return "[OK]   因子层级近似单调"
    return "[WARN] 因子层级不单调（分层收益未按层级顺序排列）"


def _diag_is_oos_gap(rows: list[dict], metric: str) -> str:
    """IS-OOS Gap：仅当存在 partition='oos' 的 run 时才计算，否则 [N/A] 未标注样本外区间。"""
    is_vals = [r["metrics"][metric] for r in rows
               if r["partition"] == "is" and r["metrics"].get(metric) is not None]
    oos_vals = [r["metrics"][metric] for r in rows
                if r["partition"] == "oos" and r["metrics"].get(metric) is not None]
    if not oos_vals:
        return "[N/A] 未标注样本外区间"
    if not is_vals:
        return "[N/A] 数据不足（无 is 分区样本）"
    is_mean, oos_mean = statistics.mean(is_vals), statistics.mean(oos_vals)
    gap = (oos_mean < is_mean * OOS_GAP_RATIO) if is_mean > 0 else (oos_mean < is_mean - OOS_GAP_ABS)
    if gap:
        return f"[WARN] OOS 表现明显低于 IS（IS={is_mean:.3f} OOS={oos_mean:.3f}）"
    return f"[OK]   IS-OOS 差距在可接受范围（IS={is_mean:.3f} OOS={oos_mean:.3f}）"


def _diag_best_vs_median(rows: list[dict], metric: str) -> str:
    """Best-vs-Median Gap：最优参数组 vs 中位数，至少 3 个参数点才可计算。"""
    means = list(_group_means(rows, metric, role="candidate").values())
    if len(means) < 3:
        return "[N/A] 数据不足（Best-vs-Median 需要 ≥3 个参数点）"
    best, med = max(means), statistics.median(means)
    rel = (best - med) / (abs(med) + 1e-9)
    if rel >= BEST_MEDIAN_GAP:
        return f"[WARN] 最优参数显著优于中位数（best={best:.3f} median={med:.3f}，过拟合信号）"
    return f"[OK]   最优参数与中位数差距不大（best={best:.3f} median={med:.3f}）"


def analyze_study(conn: sqlite3.Connection, study_id: str) -> dict:
    """统计 + 5 项过拟合诊断。数据不足输出 [N/A] 而非报错（spec §6/§9）。"""
    if conn.execute("SELECT 1 FROM studies WHERE study_id=?", (study_id,)).fetchone() is None:
        raise RuntimeError(f"Study {study_id} 不存在")
    rows = _study_run_rows(conn, study_id)
    if not rows:
        raise RuntimeError(f"Study {study_id} 未关联任何 Run，无法分析")

    statistics_rows = []
    for name in sorted({m for r in rows for m in r["metrics"]}):
        vals = [r["metrics"][name] for r in rows if r["metrics"].get(name) is not None]
        cand = [r["metrics"][name] for r in rows
                if r["role"] == "candidate" and r["metrics"].get(name) is not None]
        base = [r["metrics"][name] for r in rows
                if r["role"] == "baseline" and r["metrics"].get(name) is not None]
        delta = (statistics.mean(cand) - statistics.mean(base)) if cand and base else None
        statistics_rows.append({
            "metric": name, "n": len(vals),
            "mean": statistics.mean(vals) if vals else None,
            "median": statistics.median(vals) if vals else None,
            "std": statistics.pstdev(vals) if len(vals) >= 2 else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "positive_ratio": statistics.mean([v > 0 for v in vals]) if vals else None,
            "baseline_delta": delta,
        })

    cand_metrics = {m for r in rows if r["role"] == "candidate" for m in r["metrics"]}
    primary = next((m for m in _PRIMARY_METRICS if m in cand_metrics), None)
    if primary is None and cand_metrics:
        primary = sorted(cand_metrics)[0]
    if primary is None:
        diagnostics = ["[N/A] 数据不足（候选 Run 无可用指标）"] * 5
    else:
        diagnostics = [
            _diag_window_stability(rows, primary),
            _diag_parameter_stability(rows, primary),
            _diag_factor_monotonicity(rows, primary),
            _diag_is_oos_gap(rows, primary),
            _diag_best_vs_median(rows, primary),
        ]
    return {"study_id": study_id, "statistics": statistics_rows,
            "diagnostics": diagnostics, "primary_metric": primary}


def create_analysis(conn: sqlite3.Connection, *, study_id: str, decision: str,
                    evidence_level: str, conclusion: str | None = None,
                    confidence: float | None = None) -> str:
    """登记一条 Analysis 结论，返回 A 开头的 analysis_id（spec §10 Phase 6）。"""
    if conn.execute("SELECT 1 FROM studies WHERE study_id=?", (study_id,)).fetchone() is None:
        raise RuntimeError(f"Study {study_id} 不存在")
    if decision not in VALID_DECISIONS:
        raise RuntimeError(f"decision 必须是 {sorted(VALID_DECISIONS)} 之一")
    if evidence_level not in VALID_EVIDENCE:
        raise RuntimeError("evidence_level 必须是 E0~E6 之一")
    if confidence is not None and not (0 <= confidence <= 1):
        raise RuntimeError("confidence 必须在 [0, 1] 区间")
    aid = ids.next_id(conn, "A")
    conn.execute(
        "INSERT INTO analyses (analysis_id, study_id, conclusion, decision, evidence_level, "
        "confidence, created_at) VALUES (?,?,?,?,?,?, date('now'))",
        (aid, study_id, conclusion, decision, evidence_level, confidence),
    )
    conn.commit()
    return aid