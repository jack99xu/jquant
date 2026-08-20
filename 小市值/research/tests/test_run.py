"""Run（聚宽回测）登记测试。"""
import pytest

from research import db, run


def _conn(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_db(conn)
    conn.execute(
        "INSERT INTO strategies (strategy_id, name, source_path, git_commit_hash, file_blob_hash, created_at) "
        "VALUES ('S0001', 's', 'p', 'h', 'b', '2026-01-01')")
    conn.commit()
    return conn


def test_create_run_success(tmp_path):
    conn = _conn(tmp_path)
    rid = run.create_run(conn, strategy_id="S0001", start_date="2020-01-01",
                         end_date="2021-01-01", status="SUCCESS",
                         metrics=[("annual_return", 0.213, "joinquant_pasted"),
                                  ("sharpe", 1.52, "joinquant_pasted")])
    assert rid == "R0001"
    info = run.show_run(conn, rid)
    assert info["strategy_id"] == "S0001"
    assert len(info["metrics"]) == 2


def test_create_run_with_d1_fields(tmp_path):
    conn = _conn(tmp_path)
    rid = run.create_run(conn, strategy_id="S0001", start_date="2020-01-01",
                         end_date="2021-01-01", status="SUCCESS",
                         n_trades=12, benchmark="000905.XSHG", benchmark_return=0.102,
                         regime="sideways", source_log_path="聚宽回测结果及运行日志.md#2021-01-04",
                         notes="最大回撤区间: 2026/03/03, 2026/06/30")
    row = conn.execute("SELECT * FROM runs WHERE run_id=?", (rid,)).fetchone()
    assert row["n_trades"] == 12
    assert row["benchmark"] == "000905.XSHG"
    assert row["regime"] == "sideways"


def test_create_run_failed_requires_error_type(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="error_type"):
        run.create_run(conn, strategy_id="S0001", start_date="2020-01-01",
                       end_date="2021-01-01", status="FAILED")


def test_create_run_failed_with_error(tmp_path):
    conn = _conn(tmp_path)
    rid = run.create_run(conn, strategy_id="S0001", start_date="2020-01-01",
                         end_date="2021-01-01", status="FAILED",
                         error_type="SecurityNotExist", error_message="代码或后缀错误")
    row = conn.execute("SELECT error_type FROM runs WHERE run_id=?", (rid,)).fetchone()
    assert row["error_type"] == "SecurityNotExist"


def test_create_run_invalid_status(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="status"):
        run.create_run(conn, strategy_id="S0001", start_date="2020-01-01",
                       end_date="2021-01-01", status="DONE")


def test_create_run_invalid_regime(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="regime"):
        run.create_run(conn, strategy_id="S0001", start_date="2020-01-01",
                       end_date="2021-01-01", status="SUCCESS", regime="crazy")


def test_create_run_missing_strategy(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="不存在"):
        run.create_run(conn, strategy_id="S9999", start_date="2020-01-01",
                       end_date="2021-01-01", status="SUCCESS")


def test_add_metric_upsert(tmp_path):
    conn = _conn(tmp_path)
    rid = run.create_run(conn, strategy_id="S0001", start_date="2020-01-01",
                         end_date="2021-01-01", status="SUCCESS")
    run.add_metric(conn, rid, "sharpe", 1.5, "joinquant_pasted")
    run.add_metric(conn, rid, "sharpe", 1.6, "derived_local")  # 同键更新
    info = run.show_run(conn, rid)
    sharpe = [m for m in info["metrics"] if m["metric_name"] == "sharpe"]
    assert len(sharpe) == 1
    assert sharpe[0]["metric_value"] == 1.6


def test_add_metric_invalid_source(tmp_path):
    conn = _conn(tmp_path)
    rid = run.create_run(conn, strategy_id="S0001", start_date="2020-01-01",
                         end_date="2021-01-01", status="SUCCESS")
    with pytest.raises(RuntimeError, match="metric_source"):
        run.add_metric(conn, rid, "sharpe", 1.5, "fabricated")


def test_create_run_from_json(tmp_path):
    conn = _conn(tmp_path)
    data = {
        "strategy": "S0001", "start": "2020-01-01", "end": "2021-01-01",
        "capital": 1000000, "status": "SUCCESS",
        "n_trades": 12, "benchmark": "000905.XSHG", "regime": "sideways",
        "metrics": {"annual_return": 0.18, "sharpe": 1.3, "max_drawdown": 0.15},
    }
    rid = run.create_run_from_json(conn, data)
    info = run.show_run(conn, rid)
    assert info["initial_capital"] == 1000000
    assert len(info["metrics"]) == 3
    assert all(m["metric_source"] == "joinquant_pasted" for m in info["metrics"])


def test_parameters_json_roundtrip(tmp_path):
    conn = _conn(tmp_path)
    rid = run.create_run(conn, strategy_id="S0001", start_date="2020-01-01",
                         end_date="2021-01-01", status="SUCCESS",
                         parameters={"rebalance_days": 5, "stocknum": 30})
    row = conn.execute("SELECT parameters_json FROM runs WHERE run_id=?", (rid,)).fetchone()
    import json
    assert json.loads(row["parameters_json"]) == {"rebalance_days": 5, "stocknum": 30}