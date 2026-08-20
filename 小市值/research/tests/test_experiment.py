"""Hypothesis / Experiment / promote 测试。"""
import subprocess
from pathlib import Path

import pytest

from research import db, experiment, strategy


def _conn(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_db(conn)
    return conn


def _make_strategy(tmp_path, conn, summary="init") -> str:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    (root / "strategy.md").write_text("code", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", summary], cwd=root, check=True)
    return strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                    change_summary=summary)["strategy_id"]


def test_create_hypothesis(tmp_path):
    conn = _conn(tmp_path)
    hid = experiment.create_hypothesis(conn, title="调仓周期假设",
                                       description="延长调仓周期降低换手与冲击成本",
                                       expected_effect="Max Drawdown 下降")
    assert hid == "H0001"
    row = conn.execute("SELECT * FROM hypotheses WHERE hypothesis_id=?", (hid,)).fetchone()
    assert row["title"] == "调仓周期假设"


def test_create_experiment_basic(tmp_path):
    conn = _conn(tmp_path)
    s1 = _make_strategy(tmp_path, conn)
    eid = experiment.create_experiment(conn, baseline_id=s1, title="调仓周期延长",
                                       change_scope="MICRO", validation_tier="V2")
    assert eid == "E0001"
    row = conn.execute("SELECT * FROM experiments WHERE experiment_id=?", (eid,)).fetchone()
    assert row["baseline_strategy_id"] == s1
    assert row["n_trials"] == 1
    assert row["status"] == "PLANNED"


def test_create_experiment_invalid_scope(tmp_path):
    conn = _conn(tmp_path)
    s1 = _make_strategy(tmp_path, conn)
    with pytest.raises(RuntimeError, match="change_scope"):
        experiment.create_experiment(conn, baseline_id=s1, title="t",
                                     change_scope="BIG", validation_tier="V1")


def test_create_experiment_missing_baseline(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="baseline"):
        experiment.create_experiment(conn, baseline_id="S9999", title="t",
                                     change_scope="MICRO", validation_tier="V1")


def test_create_experiment_with_trials(tmp_path):
    conn = _conn(tmp_path)
    s1 = _make_strategy(tmp_path, conn)
    eid = experiment.create_experiment(conn, baseline_id=s1, title="t",
                                       change_scope="SMALL", validation_tier="V3",
                                       n_trials=5)
    row = conn.execute("SELECT n_trials FROM experiments WHERE experiment_id=?", (eid,)).fetchone()
    assert row["n_trials"] == 5


def test_create_experiment_float_trials_rejected(tmp_path):
    conn = _conn(tmp_path)
    s1 = _make_strategy(tmp_path, conn)
    with pytest.raises(RuntimeError, match="正整数"):
        experiment.create_experiment(conn, baseline_id=s1, title="t",
                                     change_scope="MICRO", validation_tier="V1",
                                     n_trials=2.5)


def test_promote_creates_experiment_with_candidate(tmp_path):
    conn = _conn(tmp_path)
    base = _make_strategy(tmp_path, conn, summary="base")
    # 第二个策略：改代码 → 新 commit
    root = tmp_path / "repo"
    (root / "strategy.md").write_text("code v2", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "candidate"], cwd=root, check=True)
    cand = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                    parent_id=base, quick=True, change_summary="候选")["strategy_id"]
    eid = experiment.promote(conn, strategy_id=cand, baseline_id=base,
                             title="升级正式实验", change_scope="SMALL", validation_tier="V2")
    row = conn.execute("SELECT candidate_strategy_id FROM experiments WHERE experiment_id=?", (eid,)).fetchone()
    assert row["candidate_strategy_id"] == cand


def test_promote_twice_rejected(tmp_path):
    conn = _conn(tmp_path)
    base = _make_strategy(tmp_path, conn, summary="base")
    root = tmp_path / "repo"
    (root / "strategy.md").write_text("code v2", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "candidate"], cwd=root, check=True)
    cand = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                    quick=True, change_summary="候选")["strategy_id"]
    experiment.promote(conn, strategy_id=cand, baseline_id=base, title="t1",
                       change_scope="SMALL", validation_tier="V2")
    with pytest.raises(RuntimeError, match="已关联"):
        experiment.promote(conn, strategy_id=cand, baseline_id=base, title="t2",
                           change_scope="SMALL", validation_tier="V2")


def test_show_experiment_includes_studies(tmp_path):
    conn = _conn(tmp_path)
    s1 = _make_strategy(tmp_path, conn)
    eid = experiment.create_experiment(conn, baseline_id=s1, title="t",
                                       change_scope="MICRO", validation_tier="V1")
    conn.execute(
        "INSERT INTO studies (study_id, experiment_id, study_type, name, design_json, created_at) "
        "VALUES ('ST0001', ?, 'SINGLE', 's', '{}', '2026-01-01')", (eid,))
    conn.commit()
    info = experiment.show_experiment(conn, eid)
    assert info["studies"] == ["ST0001"]


def test_list_experiments_filter(tmp_path):
    conn = _conn(tmp_path)
    s1 = _make_strategy(tmp_path, conn)
    experiment.create_experiment(conn, baseline_id=s1, title="t1",
                                 change_scope="MICRO", validation_tier="V1")
    e2 = experiment.create_experiment(conn, baseline_id=s1, title="t2",
                                      change_scope="SMALL", validation_tier="V2")
    conn.execute("UPDATE experiments SET status='RUNNING' WHERE experiment_id=?", (e2,))
    conn.commit()
    running = experiment.list_experiments(conn, status="RUNNING")
    assert [r["experiment_id"] for r in running] == [e2]