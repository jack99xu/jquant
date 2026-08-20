"""ID 生成器测试。"""
import pytest

from research import db, ids


def _conn(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_db(conn)
    return conn


def test_next_id_starts_at_0001(tmp_path):
    conn = _conn(tmp_path)
    assert ids.next_id(conn, "S") == "S0001"
    assert ids.next_id(conn, "H") == "H0001"
    assert ids.next_id(conn, "E") == "E0001"
    assert ids.next_id(conn, "R") == "R0001"
    assert ids.next_id(conn, "ST") == "ST0001"
    assert ids.next_id(conn, "A") == "A0001"


def test_next_id_increments_per_table(tmp_path):
    conn = _conn(tmp_path)
    assert ids.next_id(conn, "S") == "S0001"
    conn.execute(
        "INSERT INTO strategies (strategy_id, name, source_path, git_commit_hash, file_blob_hash, created_at) "
        "VALUES ('S0001', 'n', 'p', 'h', 'b', '2026-01-01')"
    )
    conn.commit()
    assert ids.next_id(conn, "S") == "S0002"
    assert ids.next_id(conn, "E") == "E0001"  # 各表独立计数


def test_next_id_sees_existing_rows(tmp_path):
    conn = _conn(tmp_path)
    conn.execute(
        "INSERT INTO strategies (strategy_id, name, source_path, git_commit_hash, file_blob_hash, created_at) "
        "VALUES ('S0005', 'n', 'p', 'h', 'b', '2026-01-01')"
    )
    conn.commit()
    assert ids.next_id(conn, "S") == "S0006"


def test_next_id_unknown_prefix_raises(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(KeyError):
        ids.next_id(conn, "X")
