"""Run（一次真实聚宽回测）登记与查询。"""
import json
import sqlite3

from research import ids

VALID_STATUS = {"SUCCESS", "FAILED", "PARTIAL", "INCOMPLETE"}
VALID_SOURCES = {"joinquant_pasted", "derived_local", "manual_estimate", "secondhand_mention"}
VALID_REGIMES = {"bull", "bear", "sideways", "unknown"}


def _check_strategy(conn: sqlite3.Connection, strategy_id: str) -> None:
    if conn.execute("SELECT 1 FROM strategies WHERE strategy_id=?", (strategy_id,)).fetchone() is None:
        raise RuntimeError(f"Strategy {strategy_id} 不存在")


def create_run(conn, *, strategy_id: str, start_date: str, end_date: str, status: str,
               experiment_id: str | None = None, initial_capital: float | None = None,
               frequency: str | None = None, parameters: dict | None = None,
               error_type: str | None = None, error_message: str | None = None,
               n_trades: int | None = None, benchmark: str | None = None,
               benchmark_return: float | None = None, regime: str | None = None,
               source_log_path: str | None = None, notes: str | None = None,
               metrics: list[tuple[str, float, str]] | None = None) -> str:
    """登记一次回测。metrics 为 [(metric_name, value, source), ...]。"""
    if status not in VALID_STATUS:
        raise RuntimeError(f"status 必须是 {sorted(VALID_STATUS)} 之一")
    if status == "FAILED" and not error_type:
        raise RuntimeError("status=FAILED 时必须提供 error_type（如 SecurityNotExist）")
    if regime is not None and regime not in VALID_REGIMES:
        raise RuntimeError(f"regime 必须是 {sorted(VALID_REGIMES)} 之一")
    _check_strategy(conn, strategy_id)

    parameters_json = json.dumps(parameters, ensure_ascii=False) if parameters is not None else None
    rid = ids.next_id(conn, "R")
    try:
        conn.execute(
            "INSERT INTO runs (run_id, strategy_id, experiment_id, start_date, end_date, "
            "initial_capital, frequency, parameters_json, status, error_type, error_message, "
            "n_trades, benchmark, benchmark_return, regime, source_log_path, notes, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, date('now'))",
            (rid, strategy_id, experiment_id, start_date, end_date, initial_capital, frequency,
             parameters_json, status, error_type, error_message, n_trades, benchmark,
             benchmark_return, regime, source_log_path, notes),
        )
        for name, value, source in (metrics or []):
            add_metric(conn, rid, name, value, source, commit=False)
        conn.commit()
    except BaseException:
        # 中途任何失败（如非法 metric_source）都回滚，不留孤儿 runs 行
        conn.rollback()
        raise
    return rid


def add_metric(conn: sqlite3.Connection, run_id: str, name: str, value: float,
               source: str, commit: bool = True) -> None:
    """写入/更新单个指标（同键 upsert，用于回填修正）。"""
    if source not in VALID_SOURCES:
        raise RuntimeError(f"metric_source 必须是 {sorted(VALID_SOURCES)} 之一")
    conn.execute(
        "INSERT INTO metrics (run_id, metric_name, metric_value, metric_source) "
        "VALUES (?,?,?,?) "
        "ON CONFLICT(run_id, metric_name) DO UPDATE SET "
        "metric_value=excluded.metric_value, metric_source=excluded.metric_source",
        (run_id, name, value, source),
    )
    if commit:
        conn.commit()


def create_run_from_json(conn: sqlite3.Connection, data: dict) -> str:
    """JSON payload 建 Run（spec §8 形态：strategy/start/end/capital + metrics 字典）。"""
    missing = [k for k in ("strategy", "start", "end") if k not in data]
    if missing:
        raise RuntimeError(f"JSON 缺少必要字段: {missing}")
    metrics = [(name, value, "joinquant_pasted")
               for name, value in (data.get("metrics") or {}).items()]
    return create_run(
        conn,
        strategy_id=data["strategy"],
        start_date=data["start"],
        end_date=data["end"],
        status=data.get("status", "SUCCESS"),
        experiment_id=data.get("experiment_id"),
        initial_capital=data.get("capital"),
        frequency=data.get("frequency"),
        parameters=data.get("parameters"),
        error_type=data.get("error_type"),
        error_message=data.get("error_message"),
        n_trades=data.get("n_trades"),
        benchmark=data.get("benchmark"),
        benchmark_return=data.get("benchmark_return"),
        regime=data.get("regime"),
        source_log_path=data.get("source_log_path"),
        notes=data.get("notes"),
        metrics=metrics,
    )


def show_run(conn: sqlite3.Connection, run_id: str) -> dict:
    """返回 Run 详情 + metrics 列表。"""
    row = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"Run {run_id} 不存在")
    info = dict(row)
    info["metrics"] = [
        dict(m) for m in conn.execute(
            "SELECT metric_name, metric_value, metric_source FROM metrics WHERE run_id=? "
            "ORDER BY metric_name", (run_id,)
        )
    ]
    return info