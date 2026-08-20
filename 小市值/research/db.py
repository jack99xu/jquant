"""数据库连接与初始化（Research Registry v1）。"""
import sqlite3
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent   # 小市值/research/
SCHEMA_PATH = PACKAGE_DIR / "schema.sql"


def repo_root() -> Path:
    """向上遍历查找仓库根（含 .git 的目录），所有命令从仓库根执行。"""
    cur = PACKAGE_DIR.parent  # 小市值/
    while cur != cur.parent:
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    raise RuntimeError(f"无法定位仓库根（从 {PACKAGE_DIR} 向上未找到 .git）")


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """建立连接并开启外键约束；db_path 默认 小市值/research/registry.db（spec 目录约定）。"""
    if db_path is None:
        db_path = PACKAGE_DIR / "registry.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """执行 schema.sql 建表（IF NOT EXISTS，幂等）。"""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()