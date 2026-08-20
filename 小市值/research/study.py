"""Study（预登记设计）组织：为回答一个问题组织一组 Run。"""
import json
import sqlite3

from research import ids, run as run_mod

VALID_TYPES = {"SINGLE", "ROLLING", "FACTOR_LAYER", "PARAMETER_SWEEP", "ABLATION"}
VALID_ROLES = {"baseline", "candidate"}
VALID_PARTITIONS = {"is", "oos"}


def create_study(conn, *, experiment_id: str, study_type: str, name: str,
                 design_json: dict | list | str, description: str | None = None) -> str:
    """创建 Study。design_json 必须在看到 Run 结果前登记（防过拟合核心），强制非空。"""
    if study_type not in VALID_TYPES:
        raise RuntimeError(f"study_type 必须是 {sorted(VALID_TYPES)} 之一")
    if conn.execute("SELECT 1 FROM experiments WHERE experiment_id=?", (experiment_id,)).fetchone() is None:
        raise RuntimeError(f"Experiment {experiment_id} 不存在")
    if not design_json:
        raise RuntimeError("design_json 不能为空（必须在看到 Run 结果之前登记设计）")
    if isinstance(design_json, (dict, list)):
        design_json = json.dumps(design_json, ensure_ascii=False)
    stid = ids.next_id(conn, "ST")
    conn.execute(
        "INSERT INTO studies (study_id, experiment_id, study_type, name, description, "
        "design_json, created_at) "
        "VALUES (?,?,?,?,?,?, date('now'))",
        (stid, experiment_id, study_type, name, description, design_json),
    )
    conn.commit()
    return stid


def add_run(conn: sqlite3.Connection, study_id: str, run_id: str,
            group_name: str | None = None, role: str | None = None,
            partition: str | None = None) -> None:
    """把 Run 挂到 Study（INSERT OR REPLACE 幂等）；role/partition 枚举校验。"""
    if role is not None and role not in VALID_ROLES:
        raise RuntimeError(f"role 必须是 {sorted(VALID_ROLES)} 之一")
    if partition is not None and partition not in VALID_PARTITIONS:
        raise RuntimeError(f"partition 必须是 {sorted(VALID_PARTITIONS)} 之一")
    if conn.execute("SELECT 1 FROM studies WHERE study_id=?", (study_id,)).fetchone() is None:
        raise RuntimeError(f"Study {study_id} 不存在")
    if conn.execute("SELECT 1 FROM runs WHERE run_id=?", (run_id,)).fetchone() is None:
        raise RuntimeError(f"Run {run_id} 不存在")
    conn.execute(
        "INSERT OR REPLACE INTO study_runs (study_id, run_id, group_name, role, partition) "
        "VALUES (?,?,?,?,?)",
        (study_id, run_id, group_name, role, partition),
    )
    conn.commit()


def batch_add_runs(conn: sqlite3.Connection, study_id: str, runs: list[dict]) -> list[str]:
    """批量创建 Run 并挂入 Study（spec §8 rolling_runs.json 形态），返回新 run_id 列表。

    每项除 create_run_from_json 的键外，还可带 group/role/partition 挂入 Study 分组。
    先统一预校验 role/partition，任何一项非法即整体失败，避免先创建出孤儿 Run。
    """
    for item in runs:
        role = item.get("role")
        if role is not None and role not in VALID_ROLES:
            raise RuntimeError(f"role 必须是 {sorted(VALID_ROLES)} 之一")
        partition = item.get("partition")
        if partition is not None and partition not in VALID_PARTITIONS:
            raise RuntimeError(f"partition 必须是 {sorted(VALID_PARTITIONS)} 之一")
    created = []
    for item in runs:
        rid = run_mod.create_run_from_json(conn, item)
        add_run(conn, study_id, rid,
                group_name=item.get("group"), role=item.get("role"),
                partition=item.get("partition"))
        created.append(rid)
    return created


def show_study(conn: sqlite3.Connection, study_id: str) -> dict:
    """返回 Study 详情 + runs 明细（含策略/区间/状态）。"""
    row = conn.execute("SELECT * FROM studies WHERE study_id=?", (study_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"Study {study_id} 不存在")
    info = dict(row)
    info["runs"] = [
        dict(r) for r in conn.execute(
            "SELECT sr.run_id, sr.group_name, sr.role, sr.partition, "
            "runs.strategy_id, runs.start_date, runs.end_date, runs.status "
            "FROM study_runs sr JOIN runs ON runs.run_id = sr.run_id "
            "WHERE sr.study_id=? ORDER BY sr.run_id", (study_id,)
        )
    ]
    return info