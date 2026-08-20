"""db → Markdown 报告生成（单向：db 为唯一真相，禁止手工编辑生成文件）。

spec §10 Phase 7：数据库 → 5 类 Markdown 自动生成；
analyses/*.md 由 analysis create 时一并生成/重写；
studies/*.md 的"结论"章节由关联 Analysis 填充。
"""
import sqlite3
from pathlib import Path

from research import analysis, db, experiment, run, strategy, templates

REPORT_DIRS = {
    "strategy": "strategies", "experiment": "experiments", "run": "runs",
    "study": "studies", "analysis": "analyses",
}


def _root(root: Path | None) -> Path:
    """报告输出根目录：默认 小市值/research/（spec §2 目录约定）。"""
    return root or db.PACKAGE_DIR


def _write(kind: str, entity_id: str, content: str, root: Path | None) -> Path:
    out_dir = _root(root) / REPORT_DIRS[kind]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{entity_id}.md"
    path.write_text(content, encoding="utf-8")
    return path


def write_strategy_report(conn: sqlite3.Connection, strategy_id: str,
                          root: Path | None = None) -> Path:
    info = strategy.show_strategy(conn, strategy_id)
    return _write("strategy", strategy_id, templates.strategy_md(info), root)


def _experiment_info(conn: sqlite3.Connection, experiment_id: str) -> dict:
    """Experiment 详情 + hypotheses.expected_effect（供模板渲染）。"""
    info = experiment.show_experiment(conn, experiment_id)
    if info.get("hypothesis_id"):
        h = conn.execute(
            "SELECT expected_effect FROM hypotheses WHERE hypothesis_id=?", (info["hypothesis_id"],)
        ).fetchone()
        if h is not None and h["expected_effect"] is not None:
            info["expected_effect"] = h["expected_effect"]
    return info


def write_experiment_report(conn: sqlite3.Connection, experiment_id: str,
                            root: Path | None = None) -> Path:
    info = _experiment_info(conn, experiment_id)
    return _write("experiment", experiment_id, templates.experiment_md(info), root)


def write_run_report(conn: sqlite3.Connection, run_id: str,
                     root: Path | None = None) -> Path:
    info = run.show_run(conn, run_id)
    return _write("run", run_id, templates.run_md(info), root)


def _study_info(conn: sqlite3.Connection, study_id: str) -> dict:
    """Study 详情 + runs 指标 + 最新 Analysis 结论（供模板渲染）。"""
    row = conn.execute("SELECT * FROM studies WHERE study_id=?", (study_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"Study {study_id} 不存在")
    info = dict(row)
    info["runs"] = []
    for sr in conn.execute(
        "SELECT sr.run_id, sr.group_name, sr.role, sr.partition "
        "FROM study_runs sr WHERE sr.study_id=? ORDER BY sr.run_id", (study_id,)
    ):
        run_info = dict(sr)
        run_info["metrics"] = {
            m["metric_name"]: m["metric_value"]
            for m in conn.execute(
                "SELECT metric_name, metric_value FROM metrics WHERE run_id=? "
                "AND metric_value IS NOT NULL", (sr["run_id"],)
            )
        }
        info["runs"].append(run_info)
    conclusion_row = conn.execute(
        "SELECT conclusion FROM analyses WHERE study_id=? "
        "ORDER BY created_at DESC, analysis_id DESC LIMIT 1", (study_id,)
    ).fetchone()
    info["conclusion"] = conclusion_row["conclusion"] if conclusion_row else None
    return info


def write_study_report(conn: sqlite3.Connection, study_id: str,
                       root: Path | None = None) -> Path:
    info = _study_info(conn, study_id)
    return _write("study", study_id, templates.study_md(info), root)


def write_analysis_report(conn: sqlite3.Connection, analysis_id: str,
                          root: Path | None = None) -> Path:
    row = conn.execute("SELECT * FROM analyses WHERE analysis_id=?", (analysis_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"Analysis {analysis_id} 不存在")
    info = dict(row)
    info["diagnostics"] = analysis.analyze_study(conn, info["study_id"])["diagnostics"]
    path = _write("analysis", analysis_id, templates.analysis_md(info), root)
    conn.execute("UPDATE analyses SET report_path=? WHERE analysis_id=?", (str(path), analysis_id))
    conn.commit()
    return path


def write_all_reports(conn: sqlite3.Connection, root: Path | None = None) -> list[Path]:
    """全量重生成 5 类报告（db 为唯一真相）。"""
    paths = []
    for (sid,) in conn.execute("SELECT strategy_id FROM strategies"):
        paths.append(write_strategy_report(conn, sid, root))
    for (eid,) in conn.execute("SELECT experiment_id FROM experiments"):
        paths.append(write_experiment_report(conn, eid, root))
    for (rid,) in conn.execute("SELECT run_id FROM runs"):
        paths.append(write_run_report(conn, rid, root))
    for (stid,) in conn.execute("SELECT study_id FROM studies"):
        paths.append(write_study_report(conn, stid, root))
    for (aid,) in conn.execute("SELECT analysis_id FROM analyses"):
        paths.append(write_analysis_report(conn, aid, root))
    return paths