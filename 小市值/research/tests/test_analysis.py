"""Study 统计分析与过拟合诊断、Analysis 结论登记测试。"""
import pytest

from research import analysis, db, reports  # reports 为 Task 9 追加（顶部 import 区）


def _conn(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_db(conn)
    conn.execute(
        "INSERT INTO strategies (strategy_id, name, source_path, git_commit_hash, file_blob_hash, created_at) "
        "VALUES ('S0001', 's', 'p', 'h', 'b', '2026-01-01')")
    conn.execute(
        "INSERT INTO experiments (experiment_id, baseline_strategy_id, title, change_scope, validation_tier, created_at) "
        "VALUES ('E0001', 'S0001', 't', 'MICRO', 'V2', '2026-01-01')")
    conn.execute(
        "INSERT INTO studies (study_id, experiment_id, study_type, name, design_json, created_at) "
        "VALUES ('ST0001', 'E0001', 'ROLLING', '滚动', '{\"windows\": []}', '2026-01-01')")
    conn.commit()
    return conn


def _add_run(conn, rid, role, partition, metrics, group="g1"):
    """造一个 Run + metrics + 挂入 ST0001。"""
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status, created_at) "
        "VALUES (?, 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS', '2026-01-01')", (rid,))
    for name, value in metrics.items():
        conn.execute(
            "INSERT INTO metrics (run_id, metric_name, metric_value, metric_source) "
            "VALUES (?, ?, ?, 'joinquant_pasted')", (rid, name, value))
    conn.execute(
        "INSERT INTO study_runs (study_id, run_id, group_name, role, partition) "
        "VALUES ('ST0001', ?, ?, ?, ?)", (rid, group, role, partition))
    conn.commit()


def test_analyze_single_run_na(tmp_path):
    """SINGLE 场景（1 个 run）：统计可算，诊断全部 [N/A]，不抛错。"""
    conn = _conn(tmp_path)
    _add_run(conn, "R0001", "candidate", "is", {"total_return": 0.1}, group="g1")
    result = analysis.analyze_study(conn, "ST0001")
    stats = {s["metric"]: s for s in result["statistics"]}
    assert stats["total_return"]["n"] == 1
    assert stats["total_return"]["std"] is None
    assert all(line.startswith("[N/A]") for line in result["diagnostics"])


def test_analyze_statistics(tmp_path):
    conn = _conn(tmp_path)
    _add_run(conn, "R0001", "candidate", "is", {"total_return": 0.1}, group="g1")
    _add_run(conn, "R0002", "candidate", "is", {"total_return": 0.2}, group="g2")
    _add_run(conn, "R0003", "candidate", "is", {"total_return": 0.3}, group="g3")
    result = analysis.analyze_study(conn, "ST0001")
    s = {x["metric"]: x for x in result["statistics"]}["total_return"]
    assert s["mean"] == pytest.approx(0.2)
    assert s["median"] == pytest.approx(0.2)
    assert s["min"] == pytest.approx(0.1)
    assert s["max"] == pytest.approx(0.3)
    assert s["positive_ratio"] == 1.0


def test_analyze_baseline_delta(tmp_path):
    conn = _conn(tmp_path)
    _add_run(conn, "R0001", "candidate", "is", {"total_return": 0.2}, group="g1")
    _add_run(conn, "R0002", "baseline", "is", {"total_return": 0.1}, group="g1")
    result = analysis.analyze_study(conn, "ST0001")
    s = {x["metric"]: x for x in result["statistics"]}["total_return"]
    assert s["baseline_delta"] == pytest.approx(0.1)


def test_analyze_oos_gap_warns(tmp_path):
    conn = _conn(tmp_path)
    _add_run(conn, "R0001", "candidate", "is", {"total_return": 0.3}, group="g1")
    _add_run(conn, "R0002", "candidate", "oos", {"total_return": 0.05}, group="g2")
    result = analysis.analyze_study(conn, "ST0001")
    warn_lines = [line for line in result["diagnostics"] if line.startswith("[WARN]")]
    assert any("OOS" in line for line in warn_lines)


def test_analyze_oos_missing_na(tmp_path):
    conn = _conn(tmp_path)
    _add_run(conn, "R0001", "candidate", "is", {"total_return": 0.3}, group="g1")
    result = analysis.analyze_study(conn, "ST0001")
    assert any(line == "[N/A] 未标注样本外区间" for line in result["diagnostics"])


def test_analyze_missing_study_raises(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="不存在"):
        analysis.analyze_study(conn, "ST9999")


def test_create_analysis_basic(tmp_path):
    conn = _conn(tmp_path)
    aid = analysis.create_analysis(conn, study_id="ST0001", decision="ACCEPT",
                                   evidence_level="E2", conclusion="方向一致",
                                   confidence=0.8)
    assert aid == "A0001"
    row = conn.execute("SELECT * FROM analyses WHERE analysis_id=?", (aid,)).fetchone()
    assert row["decision"] == "ACCEPT"
    assert row["evidence_level"] == "E2"
    assert row["confidence"] == 0.8


def test_create_analysis_invalid_decision(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="decision"):
        analysis.create_analysis(conn, study_id="ST0001", decision="REJECTED",
                                 evidence_level="E2")


def test_create_analysis_invalid_evidence(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="evidence"):
        analysis.create_analysis(conn, study_id="ST0001", decision="ACCEPT",
                                 evidence_level="E9")


def test_create_analysis_missing_study(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="不存在"):
        analysis.create_analysis(conn, study_id="ST9999", decision="ACCEPT",
                                 evidence_level="E2")


# ==================== 报告生成测试（Task 9，spec §10 Phase 7） ====================


def _seed_report_data(conn):
    """造一份完整数据：strategy + experiment + run + study + analysis。

    Task 9 落地时修正：与 _conn 共用 S0001/E0001/ST0001 主键，先按外键
    依赖顺序清空 7 表，使本函数不依赖调用前的表状态（否则 UNIQUE 冲突）。
    """
    for table in ("analyses", "study_runs", "studies", "metrics",
                  "runs", "experiments", "strategies"):
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.execute(
        "INSERT INTO strategies (strategy_id, parent_strategy_id, name, source_path, "
        "git_commit_hash, file_blob_hash, change_summary, created_at) "
        "VALUES ('S0001', NULL, '根版本', '小市值/小市值策略代码.md', "
        "'a'*40, 'b'*40, '初始策略', '2026-08-18')")
    conn.execute(
        "INSERT INTO experiments (experiment_id, baseline_strategy_id, candidate_strategy_id, "
        "title, change_scope, validation_tier, n_trials, status, created_at) "
        "VALUES ('E0001', 'S0001', 'S0001', '指数趋势风控', 'LARGE', 'V4', 3, 'RUNNING', '2026-08-18')")
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, experiment_id, start_date, end_date, "
        "initial_capital, frequency, status, n_trades, benchmark, benchmark_return, regime, created_at) "
        "VALUES ('R0001', 'S0001', 'E0001', '2020-01-01', '2021-01-01', 1000000, 'daily', "
        "'SUCCESS', 12, '000905.XSHG', 0.102, 'sideways', '2026-08-18')")
    conn.execute(
        "INSERT INTO metrics (run_id, metric_name, metric_value, metric_source) "
        "VALUES ('R0001', 'total_return', 0.213, 'joinquant_pasted'), "
        "('R0001', 'max_drawdown', 0.174, 'joinquant_pasted'), "
        "('R0001', 'sharpe', 1.52, 'joinquant_pasted')")
    conn.execute(
        "INSERT INTO studies (study_id, experiment_id, study_type, name, design_json, created_at) "
        "VALUES ('ST0001', 'E0001', 'ROLLING', '滚动验证', "
        "'{\"type\": \"ROLLING\", \"windows\": []}', '2026-08-18')")
    conn.execute(
        "INSERT INTO study_runs (study_id, run_id, group_name, role, partition) "
        "VALUES ('ST0001', 'R0001', '2020-2021', 'candidate', 'is')")
    conn.execute(
        "INSERT INTO analyses (analysis_id, study_id, conclusion, decision, evidence_level, "
        "confidence, created_at) "
        "VALUES ('A0001', 'ST0001', '候选策略方向一致', 'ACCEPT', 'E2', 0.8, '2026-08-18')")
    conn.commit()


def test_strategy_report_written(tmp_path):
    conn = _conn(tmp_path)
    _seed_report_data(conn)
    path = reports.write_strategy_report(conn, "S0001", root=tmp_path / "out")
    assert path.name == "S0001.md"
    text = path.read_text(encoding="utf-8")
    assert "# S0001" in text
    assert "Git Commit" in text
    assert "初始策略" in text


def test_experiment_report_written(tmp_path):
    conn = _conn(tmp_path)
    _seed_report_data(conn)
    path = reports.write_experiment_report(conn, "E0001", root=tmp_path / "out")
    text = path.read_text(encoding="utf-8")
    assert "Baseline: S0001" in text
    assert "Candidate: S0001" in text
    assert "试验次数: 3" in text


def test_run_report_metrics_table(tmp_path):
    conn = _conn(tmp_path)
    _seed_report_data(conn)
    path = reports.write_run_report(conn, "R0001", root=tmp_path / "out")
    text = path.read_text(encoding="utf-8")
    assert "| total_return | 0.213 | joinquant_pasted |" in text
    assert "000905.XSHG" in text
    assert "SUCCESS" in text


def test_study_report_conclusion_filled(tmp_path):
    conn = _conn(tmp_path)
    _seed_report_data(conn)
    path = reports.write_study_report(conn, "ST0001", root=tmp_path / "out")
    text = path.read_text(encoding="utf-8")
    assert "## 结论" in text
    assert "候选策略方向一致" in text  # 由关联 Analysis 填充（spec §5/§13 验收 3）


def test_analysis_report_diagnostics(tmp_path):
    conn = _conn(tmp_path)
    _seed_report_data(conn)
    path = reports.write_analysis_report(conn, "A0001", root=tmp_path / "out")
    text = path.read_text(encoding="utf-8")
    assert "Decision: ACCEPT" in text
    assert "Evidence Level: E2" in text
    assert "Overfitting Signals:" in text
    # report_path 回写
    row = conn.execute("SELECT report_path FROM analyses WHERE analysis_id='A0001'").fetchone()
    assert row["report_path"] == str(path)