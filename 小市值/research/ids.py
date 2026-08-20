"""人工可读 ID 生成（S0001 格式，前缀+4 位数字）。"""
import sqlite3

# 前缀 → (表名, 主键列名)
_ID_MAP = {
    "S": ("strategies", "strategy_id"),
    "H": ("hypotheses", "hypothesis_id"),
    "E": ("experiments", "experiment_id"),
    "R": ("runs", "run_id"),
    "ST": ("studies", "study_id"),
    "A": ("analyses", "analysis_id"),
}


def next_id(conn: sqlite3.Connection, prefix: str) -> str:
    """返回下一个形如 S0001 的 ID（MAX+1）。单进程本地场景无需处理并发。"""
    table, column = _ID_MAP[prefix]
    row = conn.execute(f"SELECT MAX({column}) AS m FROM {table}").fetchone()
    current = int(row["m"][len(prefix):]) if row["m"] else 0
    return f"{prefix}{current + 1:04d}"