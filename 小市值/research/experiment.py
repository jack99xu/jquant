"""Hypothesis 与 Experiment 登记（含快速检查点升级 promote）。"""
import sqlite3

from research import ids

VALID_SCOPES = {"MICRO", "SMALL", "MEDIUM", "LARGE", "ARCHITECTURAL"}
VALID_TIERS = {"V1", "V2", "V3", "V4", "V5"}


def create_hypothesis(conn, *, title: str, description: str,
                      expected_effect: str | None = None) -> str:
    """创建研究假设，返回 H 开头的 hypothesis_id。"""
    hid = ids.next_id(conn, "H")
    conn.execute(
        "INSERT INTO hypotheses (hypothesis_id, title, description, expected_effect, created_at) "
        "VALUES (?,?,?,?, date('now'))",
        (hid, title, description, expected_effect),
    )
    conn.commit()
    return hid


def _validate_experiment_args(conn, baseline_id, change_scope, validation_tier, n_trials) -> None:
    if change_scope not in VALID_SCOPES:
        raise RuntimeError(f"change_scope 必须是 {sorted(VALID_SCOPES)} 之一")
    if validation_tier not in VALID_TIERS:
        raise RuntimeError(f"validation_tier 必须是 {sorted(VALID_TIERS)} 之一")
    if n_trials < 1:
        raise RuntimeError("n_trials 必须 ≥ 1")
    if conn.execute("SELECT 1 FROM strategies WHERE strategy_id=?", (baseline_id,)).fetchone() is None:
        raise RuntimeError(f"baseline Strategy {baseline_id} 不存在")


def create_experiment(conn, *, baseline_id: str, title: str, change_scope: str,
                      validation_tier: str, hypothesis_id: str | None = None,
                      candidate_id: str | None = None, description: str | None = None,
                      n_trials: int = 1) -> str:
    """创建正式实验，返回 E 开头的 experiment_id。candidate 可留空稍后回填。"""
    _validate_experiment_args(conn, baseline_id, change_scope, validation_tier, n_trials)
    eid = ids.next_id(conn, "E")
    conn.execute(
        "INSERT INTO experiments (experiment_id, hypothesis_id, baseline_strategy_id, "
        "candidate_strategy_id, title, description, change_scope, validation_tier, "
        "n_trials, status, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,'PLANNED', date('now'))",
        (eid, hypothesis_id, baseline_id, candidate_id, title, description,
         change_scope, validation_tier, n_trials),
    )
    conn.commit()
    return eid


def promote(conn, *, strategy_id: str, baseline_id: str, title: str,
            change_scope: str, validation_tier: str, hypothesis_id: str | None = None,
            description: str | None = None, n_trials: int = 1) -> str:
    """快速检查点 Strategy → 正式实验（创建新 Experiment，candidate=该 Strategy）。

    与 experiment create 区别：promote 由已有 Strategy 出发创建实验；
    strategy create --experiment 由已有 Experiment 出发回填 candidate。
    """
    if conn.execute("SELECT 1 FROM strategies WHERE strategy_id=?", (strategy_id,)).fetchone() is None:
        raise RuntimeError(f"Strategy {strategy_id} 不存在")
    existing = conn.execute(
        "SELECT experiment_id FROM experiments WHERE candidate_strategy_id=?", (strategy_id,)
    ).fetchone()
    if existing is not None:
        raise RuntimeError(f"Strategy {strategy_id} 已关联 Experiment {existing['experiment_id']}，不能重复 promote")
    return create_experiment(conn, baseline_id=baseline_id, title=title,
                             change_scope=change_scope, validation_tier=validation_tier,
                             hypothesis_id=hypothesis_id, candidate_id=strategy_id,
                             description=description, n_trials=n_trials)


def show_experiment(conn: sqlite3.Connection, experiment_id: str) -> dict:
    """返回实验详情 + 关联 Study 列表。"""
    row = conn.execute("SELECT * FROM experiments WHERE experiment_id=?", (experiment_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"Experiment {experiment_id} 不存在")
    info = dict(row)
    info["studies"] = [
        r["study_id"] for r in conn.execute(
            "SELECT study_id FROM studies WHERE experiment_id=?", (experiment_id,)
        )
    ]
    return info


def list_experiments(conn: sqlite3.Connection, status: str | None = None) -> list[dict]:
    """实验列表，可选按 status 过滤。"""
    if status:
        rows = conn.execute(
            "SELECT * FROM experiments WHERE status=? ORDER BY experiment_id", (status,)
        )
    else:
        rows = conn.execute("SELECT * FROM experiments ORDER BY experiment_id")
    return [dict(r) for r in rows]