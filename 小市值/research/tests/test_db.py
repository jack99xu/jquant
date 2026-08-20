"""schema.sql 建表与约束测试（Task 1 阶段仅验证 schema 文件本身）。"""
import sqlite3
from pathlib import Path

import pytest

from research import db

SCHEMA = Path(__file__).resolve().parent.parent / "schema.sql"

TABLE_NAMES = {
    "strategies", "hypotheses", "experiments", "runs",
    "metrics", "studies", "study_runs", "analyses",
}


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _init(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.commit()


def test_schema_creates_all_tables(tmp_path):
    conn = _connect(tmp_path / "t.db")
    _init(conn)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    assert TABLE_NAMES <= {r["name"] for r in rows}


def test_schema_is_idempotent(tmp_path):
    conn = _connect(tmp_path / "t.db")
    _init(conn)
    _init(conn)  # 重复执行不报错
    rows = conn.execute("SELECT count(*) AS n FROM sqlite_master WHERE type='table'").fetchone()
    assert rows["n"] == len(TABLE_NAMES)  # 没有重复建表


def test_foreign_key_enforced(tmp_path):
    conn = _connect(tmp_path / "t.db")
    _init(conn)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status, created_at) "
            "VALUES ('R0001', 'S9999', '2020-01-01', '2021-01-01', 'SUCCESS', '2026-08-20')"
        )


def test_metrics_compound_pk(tmp_path):
    conn = _connect(tmp_path / "t.db")
    _init(conn)
    conn.execute(
        "INSERT INTO strategies (strategy_id, name, source_path, git_commit_hash, file_blob_hash, created_at) "
        "VALUES ('S0001', '哑铃组合 v1', '小市值/小市值策略代码.md', 'abc', 'def', '2026-08-20')"
    )
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status, created_at) "
        "VALUES ('R0001', 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS', '2026-08-20')"
    )
    conn.execute(
        "INSERT INTO metrics (run_id, metric_name, metric_value, metric_source) "
        "VALUES ('R0001', 'sharpe', 1.5, 'joinquant_pasted')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO metrics (run_id, metric_name, metric_value, metric_source) "
            "VALUES ('R0001', 'sharpe', 2.0, 'joinquant_pasted')"
        )


def test_connect_sets_row_factory_and_fk(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    assert conn.row_factory is sqlite3.Row
    # PRAGMA foreign_keys 是连接级设置，读回验证
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_init_db_via_db_module(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_db(conn)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    assert TABLE_NAMES <= {r["name"] for r in rows}


def test_repo_root_finds_git_dir():
    root = db.repo_root()
    assert (root / ".git").exists()