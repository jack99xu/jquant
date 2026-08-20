"""Strategy（代码状态）登记与查询。"""
import sqlite3
from pathlib import Path

from research import db, git_meta, ids

SOURCE_PATH = "小市值/小市值策略代码.md"


def _latest_blob(conn: sqlite3.Connection) -> str | None:
    row = conn.execute(
        "SELECT file_blob_hash FROM strategies ORDER BY created_at DESC, rowid DESC LIMIT 1"
    ).fetchone()
    return row["file_blob_hash"] if row else None


def create_strategy(conn, *, parent_id=None, name=None, change_summary=None,
                    experiment_id=None, source_path=SOURCE_PATH, quick=False,
                    root: Path | None = None) -> dict:
    """创建策略版本，返回 {"strategy_id", "warning"}。

    - 创建前校验 source_path 工作区干净（git_commit_hash 必须对应硬盘实际内容）
    - blob 与最新版本相同时给 warning 而非拒绝（可能是有意回退重登记）
    - experiment_id 给出时校验存在且 candidate 为空，创建后回填
    - quick=True（快速检查点）禁止关联 Experiment
    """
    if quick and experiment_id is not None:
        raise RuntimeError("快速检查点不能关联 Experiment（quick 模式不建实验）")
    root = root or db.repo_root()
    if not git_meta.worktree_clean(root, source_path):
        raise RuntimeError(f"{source_path} 有未提交改动，请先 git commit 再登记 Strategy")
    commit_hash = git_meta.git_commit_hash(root)
    blob = git_meta.git_blob_hash(root, source_path)
    if change_summary is None:
        change_summary = git_meta.commit_message(root)
    if name is None:
        name = (change_summary or "unnamed")[:40]

    warning = None
    latest = _latest_blob(conn)
    if latest is not None and latest == blob:
        warning = "警告: file_blob_hash 与最新 Strategy 相同（内容未变），确认是否为有意重新登记"

    if experiment_id is not None:
        exp = conn.execute(
            "SELECT candidate_strategy_id FROM experiments WHERE experiment_id=?", (experiment_id,)
        ).fetchone()
        if exp is None:
            raise RuntimeError(f"Experiment {experiment_id} 不存在")
        if exp["candidate_strategy_id"] is not None:
            raise RuntimeError(
                f"Experiment {experiment_id} 已有 candidate {exp['candidate_strategy_id']}，"
                "如需更换先显式清空原值"
            )

    sid = ids.next_id(conn, "S")
    conn.execute(
        "INSERT INTO strategies (strategy_id, parent_strategy_id, name, source_path, "
        "git_commit_hash, file_blob_hash, change_summary, created_at) "
        "VALUES (?,?,?,?,?,?,?, date('now'))",
        (sid, parent_id, name, source_path, commit_hash, blob, change_summary),
    )
    if experiment_id is not None:
        conn.execute(
            "UPDATE experiments SET candidate_strategy_id=? WHERE experiment_id=?",
            (sid, experiment_id),
        )
    conn.commit()
    return {"strategy_id": sid, "warning": warning}


def show_strategy(conn: sqlite3.Connection, strategy_id: str) -> dict:
    """返回策略详情 + 关联实验/回测列表。"""
    row = conn.execute("SELECT * FROM strategies WHERE strategy_id=?", (strategy_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"Strategy {strategy_id} 不存在")
    info = dict(row)
    info["experiments"] = [
        r["experiment_id"] for r in conn.execute(
            "SELECT experiment_id FROM experiments WHERE baseline_strategy_id=? OR candidate_strategy_id=?",
            (strategy_id, strategy_id),
        )
    ]
    info["runs"] = [
        r["run_id"] for r in conn.execute(
            "SELECT run_id FROM runs WHERE strategy_id=?", (strategy_id,)
        )
    ]
    return info


def strategy_tree(conn: sqlite3.Connection, root_id: str) -> list[tuple[str, int]]:
    """从 root_id 出发深度优先输出 [(strategy_id, depth)]。"""
    rows = conn.execute("SELECT strategy_id, parent_strategy_id FROM strategies").fetchall()
    children: dict[str | None, list[str]] = {}
    for r in rows:
        children.setdefault(r["parent_strategy_id"], []).append(r["strategy_id"])
    result: list[tuple[str, int]] = []

    def walk(sid: str, depth: int) -> None:
        result.append((sid, depth))
        for child in sorted(children.get(sid, [])):
            walk(child, depth + 1)

    if root_id not in {r["strategy_id"] for r in rows}:
        raise RuntimeError(f"Strategy {root_id} 不存在")
    walk(root_id, 0)
    return result