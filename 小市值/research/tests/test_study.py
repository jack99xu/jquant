"""Study（预登记设计）组织测试。"""
import json

import pytest

from research import db, study


def _conn(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_db(conn)
    conn.execute(
        "INSERT INTO strategies (strategy_id, name, source_path, git_commit_hash, file_blob_hash, created_at) "
        "VALUES ('S0001', 's', 'p', 'h', 'b', '2026-01-01')")
    conn.execute(
        "INSERT INTO experiments (experiment_id, baseline_strategy_id, title, change_scope, validation_tier, created_at) "
        "VALUES ('E0001', 'S0001', 't', 'MICRO', 'V2', '2026-01-01')")
    conn.commit()
    return conn


def test_create_study_with_dict_design(tmp_path):
    conn = _conn(tmp_path)
    design = {"type": "ROLLING",
              "windows": [{"start": "2020-01-01", "end": "2021-01-01", "partition": "is"}]}
    stid = study.create_study(conn, experiment_id="E0001", study_type="ROLLING",
                              name="5窗口滚动验证", design_json=design)
    assert stid == "ST0001"
    row = conn.execute("SELECT design_json FROM studies WHERE study_id=?", (stid,)).fetchone()
    assert json.loads(row["design_json"]) == design


def test_create_study_invalid_type(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="study_type"):
        study.create_study(conn, experiment_id="E0001", study_type="WALK_FORWARD",
                           name="s", design_json={})


def test_create_study_missing_experiment(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="不存在"):
        study.create_study(conn, experiment_id="E9999", study_type="SINGLE",
                           name="s", design_json={})


def test_create_study_empty_design_rejected(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="design_json"):
        study.create_study(conn, experiment_id="E0001", study_type="SINGLE",
                           name="s", design_json=None)


def test_add_run_with_role_partition(tmp_path):
    conn = _conn(tmp_path)
    stid = study.create_study(conn, experiment_id="E0001", study_type="ROLLING",
                              name="s", design_json={"note": "占位设计"})
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status, created_at) "
        "VALUES ('R0001', 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS', '2026-01-01')")
    conn.commit()
    study.add_run(conn, stid, "R0001", group_name="2020-2021", role="candidate", partition="is")
    info = study.show_study(conn, stid)
    assert info["runs"][0]["role"] == "candidate"
    assert info["runs"][0]["partition"] == "is"
    assert info["runs"][0]["group_name"] == "2020-2021"


def test_add_run_invalid_role(tmp_path):
    conn = _conn(tmp_path)
    stid = study.create_study(conn, experiment_id="E0001", study_type="SINGLE",
                              name="s", design_json={"note": "占位设计"})
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status, created_at) "
        "VALUES ('R0001', 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS', '2026-01-01')")
    conn.commit()
    with pytest.raises(RuntimeError, match="role"):
        study.add_run(conn, stid, "R0001", role="weird")


def test_add_run_invalid_partition(tmp_path):
    conn = _conn(tmp_path)
    stid = study.create_study(conn, experiment_id="E0001", study_type="SINGLE",
                              name="s", design_json={"note": "占位设计"})
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status, created_at) "
        "VALUES ('R0001', 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS', '2026-01-01')")
    conn.commit()
    with pytest.raises(RuntimeError, match="partition"):
        study.add_run(conn, stid, "R0001", partition="val")


def test_batch_add_runs_creates_and_links(tmp_path):
    conn = _conn(tmp_path)
    stid = study.create_study(conn, experiment_id="E0001", study_type="ROLLING",
                              name="滚动", design_json={"windows": []})
    payload = [
        {"strategy": "S0001", "start": "2020-01-01", "end": "2021-01-01",
         "capital": 1000000, "status": "SUCCESS",
         "group": "2020-2021", "role": "candidate", "partition": "is",
         "metrics": {"annual_return": 0.18, "sharpe": 1.3}},
        {"strategy": "S0001", "start": "2020-01-01", "end": "2021-01-01",
         "capital": 1000000, "status": "SUCCESS",
         "group": "2020-2021", "role": "baseline", "partition": "is",
         "metrics": {"annual_return": 0.14, "sharpe": 1.1}},
    ]
    created = study.batch_add_runs(conn, stid, payload)
    assert created == ["R0001", "R0002"]
    info = study.show_study(conn, stid)
    assert len(info["runs"]) == 2
    assert {r["role"] for r in info["runs"]} == {"candidate", "baseline"}
    # metrics 一并写入
    row = conn.execute("SELECT metric_value FROM metrics WHERE run_id='R0001' AND metric_name='sharpe'").fetchone()
    assert row["metric_value"] == 1.3


def test_show_study_missing(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="不存在"):
        study.show_study(conn, "ST9999")