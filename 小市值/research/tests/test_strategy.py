"""Strategy 登记测试。"""
import subprocess
from pathlib import Path

import pytest

from research import db, strategy


def _make_repo(tmp_path: Path, content: str = "code v1") -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    f = root / "strategy.md"
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init code"], cwd=root, check=True)
    return root


def _conn(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_db(conn)
    return conn


def test_create_root_strategy(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    res = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                   change_summary="初始策略")
    assert res["strategy_id"] == "S0001"
    row = conn.execute("SELECT * FROM strategies WHERE strategy_id='S0001'").fetchone()
    assert row["parent_strategy_id"] is None
    assert row["change_summary"] == "初始策略"
    assert len(row["git_commit_hash"]) == 40


def test_create_child_strategy(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    s1 = strategy.create_strategy(conn, root=root, source_path="strategy.md")["strategy_id"]
    (root / "strategy.md").write_text("code v2", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "v2"], cwd=root, check=True)
    res = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                   parent_id=s1, change_summary="v2 改动")
    assert res["strategy_id"] == "S0002"
    row = conn.execute("SELECT * FROM strategies WHERE strategy_id='S0002'").fetchone()
    assert row["parent_strategy_id"] == "S0001"


def test_dirty_worktree_rejected(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    (root / "strategy.md").write_text("uncommitted change", encoding="utf-8")
    with pytest.raises(RuntimeError, match="未提交改动"):
        strategy.create_strategy(conn, root=root, source_path="strategy.md")


def test_duplicate_blob_warns(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    strategy.create_strategy(conn, root=root, source_path="strategy.md")
    res = strategy.create_strategy(conn, root=root, source_path="strategy.md")
    assert res["warning"] is not None
    assert "相同" in res["warning"]


def test_name_defaults_to_summary_head(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    summary = "这是一个用于测试的较长变更摘要" * 3  # 超 40 字
    res = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                   change_summary=summary)
    row = conn.execute("SELECT name FROM strategies WHERE strategy_id=?", (res["strategy_id"],)).fetchone()
    assert len(row["name"]) == 40
    assert row["name"] == summary[:40]


def test_quick_mode_forbids_experiment(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="快速检查点"):
        strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                 quick=True, experiment_id="E0001")


def test_backfill_experiment_candidate(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    s1 = strategy.create_strategy(conn, root=root, source_path="strategy.md")["strategy_id"]
    conn.execute(
        "INSERT INTO experiments (experiment_id, baseline_strategy_id, title, change_scope, validation_tier, created_at) "
        "VALUES ('E0001', ?, 't', 'MICRO', 'V1', '2026-01-01')", (s1,))
    conn.commit()
    s2 = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                  experiment_id="E0001")["strategy_id"]
    row = conn.execute("SELECT candidate_strategy_id FROM experiments WHERE experiment_id='E0001'").fetchone()
    assert row["candidate_strategy_id"] == s2


def test_backfill_missing_experiment_raises(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="不存在"):
        strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                 experiment_id="E9999")


def test_show_strategy_includes_links(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    s1 = strategy.create_strategy(conn, root=root, source_path="strategy.md")["strategy_id"]
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status, created_at) "
        "VALUES ('R0001', ?, '2020-01-01', '2021-01-01', 'SUCCESS', '2026-01-01')", (s1,))
    conn.commit()
    info = strategy.show_strategy(conn, s1)
    assert info["strategy_id"] == s1
    assert info["runs"] == ["R0001"]
    with pytest.raises(RuntimeError, match="不存在"):
        strategy.show_strategy(conn, "S9999")


def test_strategy_tree_depth(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    s1 = strategy.create_strategy(conn, root=root, source_path="strategy.md")["strategy_id"]
    (root / "strategy.md").write_text("v2", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "v2"], cwd=root, check=True)
    s2 = strategy.create_strategy(conn, root=root, source_path="strategy.md", parent_id=s1)["strategy_id"]
    (root / "strategy.md").write_text("v3", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "v3"], cwd=root, check=True)
    strategy.create_strategy(conn, root=root, source_path="strategy.md", parent_id=s2)
    tree = strategy.strategy_tree(conn, s1)
    assert tree == [(s1, 0), (s2, 1), ("S0003", 2)]