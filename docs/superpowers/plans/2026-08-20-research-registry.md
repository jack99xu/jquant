# Research Registry v1 实施计划（可追溯回测记录系统）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落地"小市值策略研究登记系统 v1"——用 SQLite + Python 标准库 + Markdown 记录每次策略代码改动与对应聚宽回测结果，支撑改动有效性分析与过拟合防护。

**Architecture:** 8 表 SQLite（`小市值/research/registry.db`）为数据源头，Markdown 为阅读界面（单向生成）；CLI（`python -m research`）全部非交互（flag/JSON payload），主要操作者为 AI 助手；Strategy 谱系直接用 git commit 回答。包通过 `小市值/pyproject.toml` + `pip install -e 小市值` 安装，命令统一从仓库根 `D:\量化\聚宽` 执行。

**Tech Stack:** Python 3.12 标准库（sqlite3 / subprocess / argparse / json / statistics / pathlib / datetime / csv），pytest 测试，git（rev-parse / hash-object / status / diff / log），Windows PowerShell 5.1。

## Global Constraints

（以下约束对所有任务隐含生效，逐条来自 spec `docs/superpowers/specs/2026-08-20-research-registry-design.md`）

- 只允许 Python 标准库，禁止第三方依赖（对应 joinquant-docs/tools 惯例）
- 所有命令从仓库根 `D:\量化\聚宽` 执行；测试命令统一 `python -m pytest 小市值/research/tests/test_xxx.py -v`
- 代码注释用中文；变量/函数命名语义化英文，禁拼音
- 所有 Python 文件显式 `encoding="utf-8"` 读写；PowerShell GBK 控制台不影响 Python 输出（但 git 输出解析用 `-c core.quotepath=false` 防中文转义）
- `db.py` 每次连接必须 `PRAGMA foreign_keys = ON`
- ID 格式：前缀+4 位数字（S0001/H0001/E0001/R0001/ST0001/A0001），`next_id` 按 MAX+1 生成，单进程本地无需并发
- `strategy create` 前必须校验 `小市值/小市值策略代码.md` 工作区干净（`git diff --quiet HEAD -- <file>` 或 porcelain 解析），否则报错
- `metrics.metric_source` 仅允许：joinquant_pasted / derived_local / manual_estimate / secondhand_mention
- `runs.status` 仅允许：SUCCESS / FAILED / PARTIAL / INCOMPLETE；FAILED 必须带 error_type
- `studies.design_json` 非空；`experiments.baseline_strategy_id` 非空
- metric_value 一律存小数（0.213 而非 21.3%）；非数值信息（如最大回撤区间）写入 runs.notes
- 禁止删除 Run（含 FAILED/INCOMPLETE）；禁止历史数据迁移（决策 D2）
- 提交粒度：每个任务结束一个 commit，message 用中文描述变更

---

### Task 1: 包脚手架 + schema.sql

**Files:**
- Create: `小市值/pyproject.toml`
- Create: `小市值/research/__init__.py`
- Create: `小市值/research/__main__.py`
- Create: `小市值/research/schema.sql`
- Create: `小市值/research/tests/__init__.py`
- Test: `小市值/research/tests/test_db.py`

**Interfaces:**
- Produces: schema.sql（8 表 + D4 指标注释，`IF NOT EXISTS` 幂等）；`python -m research` 入口（Task 10 接线前先打印占位帮助）

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "research-registry"
version = "0.1.0"
description = "小市值策略研究登记系统（Research Registry v1）"
requires-python = ">=3.10"

[tool.setuptools]
packages = ["research"]
```

- [ ] **Step 2: 创建包骨架**

`小市值/research/__init__.py`:
```python
"""小市值策略研究登记系统（Research Registry v1）。"""
```

`小市值/research/__main__.py`（占位，Task 10 接线）:
```python
"""python -m research 入口。"""
import sys


def main() -> int:
    print("Research Registry v1 — CLI 尚未接线（Task 10）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`小市值/research/tests/__init__.py`:
```python
"""research 包测试目录（pytest 收集用）。"""
```

- [ ] **Step 3: 创建 schema.sql（8 表完整版，含 D1/D4 决策字段与注释）**

```sql
-- ============================================================
-- schema.sql — Research Registry v1（落地实现版，spec D4 扩展后）
-- Python 3.12 + SQLite 标准库
-- db.py 每次建立连接后必须执行 PRAGMA foreign_keys = ON;
-- 原因：ID 是人工可读字符串（S0024 这类）不是自增整数，打错一位数字
-- 在未开约束时会静默产生指向错误策略的记录，开了约束至少 insert 时报错拦截
-- 本文件全部使用 IF NOT EXISTS，init 幂等可重复执行
-- ============================================================

CREATE TABLE IF NOT EXISTS strategies (
    strategy_id         TEXT PRIMARY KEY,   -- S0001, S0002, ...
    parent_strategy_id  TEXT,               -- NULL 表示根版本

    name                TEXT NOT NULL,
    source_path         TEXT NOT NULL,      -- 固定为 "小市值/小市值策略代码.md"

    git_commit_hash     TEXT NOT NULL,      -- `git rev-parse HEAD`
    file_blob_hash      TEXT NOT NULL,      -- `git hash-object <file>`，内容指纹，
                                            -- 与 commit 解耦，识别"内容未变但重复登记"

    change_summary      TEXT,               -- 默认取 git commit message，CLI 可覆盖

    created_at          TEXT NOT NULL,

    FOREIGN KEY (parent_strategy_id) REFERENCES strategies(strategy_id)
);

CREATE TABLE IF NOT EXISTS hypotheses (
    hypothesis_id   TEXT PRIMARY KEY,       -- H0001, ...
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    expected_effect TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS experiments (
    experiment_id        TEXT PRIMARY KEY,  -- E0001, ...

    hypothesis_id        TEXT,
    baseline_strategy_id TEXT NOT NULL,     -- 每个实验必须有基线锚点
    candidate_strategy_id TEXT,             -- 允许为空：先建 Experiment 后回填

    title                TEXT NOT NULL,
    description          TEXT,

    change_scope         TEXT NOT NULL,     -- MICRO / SMALL / MEDIUM / LARGE / ARCHITECTURAL
    validation_tier      TEXT NOT NULL,     -- V1 / V2 / V3 / V4 / V5

    n_trials             INTEGER NOT NULL DEFAULT 1,  -- 试验次数（DSR/PBO 输入，决策 D1）

    status               TEXT NOT NULL DEFAULT 'PLANNED',  -- PLANNED / RUNNING / COMPLETED / ABANDONED

    created_at           TEXT NOT NULL,

    FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(hypothesis_id),
    FOREIGN KEY (baseline_strategy_id) REFERENCES strategies(strategy_id),
    FOREIGN KEY (candidate_strategy_id) REFERENCES strategies(strategy_id)
);

CREATE TABLE IF NOT EXISTS runs (
    run_id          TEXT PRIMARY KEY,       -- R0001, ...

    strategy_id     TEXT NOT NULL,
    experiment_id   TEXT,                   -- 允许为空：快速检查点无正式 Experiment

    start_date      TEXT NOT NULL,
    end_date        TEXT NOT NULL,
    initial_capital REAL,
    frequency       TEXT,

    parameters_json TEXT,

    status          TEXT NOT NULL,          -- SUCCESS / FAILED / PARTIAL / INCOMPLETE

    error_type      TEXT,                   -- 仅 status=FAILED 时填，如 SecurityNotExist / TimeoutError
    error_message   TEXT,

    n_trades        INTEGER,                -- 调仓次数（决策 D1）
    benchmark       TEXT,                   -- 基准指数代码，如 000905.XSHG（决策 D1）
    benchmark_return REAL,                  -- 基准收益（决策 D1）
    regime          TEXT,                   -- bull / bear / sideways / unknown（决策 D1）

    source_log_path TEXT,                   -- 指向聚宽回测结果及运行日志.md 具体位置/锚点
    notes           TEXT,

    created_at      TEXT NOT NULL,

    FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id),
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

CREATE TABLE IF NOT EXISTS metrics (
    run_id       TEXT NOT NULL,
    metric_name  TEXT NOT NULL,
    metric_value REAL,
    metric_source TEXT NOT NULL,  -- joinquant_pasted / derived_local / manual_estimate / secondhand_mention
                                  -- secondhand_mention：数值来自优化方向.md 等二手转述，不可作为 Analysis 证据引用

    PRIMARY KEY (run_id, metric_name),
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

-- 约定指标名（写入 metric_name，无 schema 变更）——完整清单（spec 决策 D4）：
-- 收益类：total_return(策略总收益) / annual_return(策略年化收益) / benchmark_excess_return(超额收益)
-- 风险类：max_drawdown(最大回撤) / volatility(策略波动率) / drawdown_recovery(回撤恢复天数)
-- 比率类：sharpe / sortino / calmar / information_ratio(信息比率) / profit_loss_ratio(盈亏比)
-- 胜率类：win_rate(胜率) / daily_win_rate(日胜率)
-- 交易类：win_trades(盈利次数) / loss_trades(亏损次数)——逐笔成交订单口径，与 runs.n_trades(调仓次数) 不同
-- 归因类：alpha(阿尔法) / beta(贝塔)
-- 超额风险：daily_excess_return(日均超额收益) / excess_max_drawdown(超额收益最大回撤) / excess_sharpe(超额收益夏普)
-- 基准类：benchmark_volatility(基准波动率)——基准收益存 runs.benchmark_return 字段
-- 换手类：turnover_ratio(换手率)
-- 单位约定：metric_value 一律存小数（0.213 而非 21.3%；百分比先除 100 再存），README 写明
-- 非数值信息（如最大回撤区间 "2026/03/03,2026/06/30"）不存 metrics 表，写入 runs.notes

CREATE TABLE IF NOT EXISTS studies (
    study_id     TEXT PRIMARY KEY,  -- ST0001, ...
    experiment_id TEXT NOT NULL,

    study_type   TEXT NOT NULL,     -- SINGLE / ROLLING / FACTOR_LAYER / PARAMETER_SWEEP / ABLATION

    name         TEXT NOT NULL,
    description  TEXT,

    design_json  TEXT NOT NULL,     -- 必须在看到 Run 结果前登记，v1 强制 NOT NULL（防过拟合核心）

    created_at   TEXT NOT NULL,

    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

CREATE TABLE IF NOT EXISTS study_runs (
    study_id    TEXT NOT NULL,
    run_id      TEXT NOT NULL,

    group_name  TEXT,               -- 分层/窗口分组名，如 "2020-2021"、"1-15"、"16-30"
    role        TEXT,               -- baseline / candidate
    partition   TEXT,               -- is / oos / NULL（决策 D1；SINGLE/参数扫描无 IS-OOS 概念时留空）

    PRIMARY KEY (study_id, run_id),
    FOREIGN KEY (study_id) REFERENCES studies(study_id),
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

CREATE TABLE IF NOT EXISTS analyses (
    analysis_id   TEXT PRIMARY KEY,  -- A0001, ...
    study_id      TEXT NOT NULL,

    conclusion    TEXT,
    decision      TEXT,   -- ACCEPT / REJECT / INCONCLUSIVE / DEFER
    evidence_level TEXT,  -- E0 ~ E6
    confidence    REAL,

    report_path   TEXT,
    created_at    TEXT NOT NULL,

    FOREIGN KEY (study_id) REFERENCES studies(study_id)
);
```

- [ ] **Step 4: 写 schema 测试（test_db.py，本任务先测 schema 本身）**

`小市值/research/tests/test_db.py`:
```python
"""schema.sql 建表与约束测试（Task 1 阶段仅验证 schema 文件本身）。"""
import sqlite3
from pathlib import Path

import pytest

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
            "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status) "
            "VALUES ('R0001', 'S9999', '2020-01-01', '2021-01-01', 'SUCCESS')"
        )


def test_metrics_compound_pk(tmp_path):
    conn = _connect(tmp_path / "t.db")
    _init(conn)
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status) "
        "VALUES ('R0001', 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS')"
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
```

- [ ] **Step 5: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_db.py -v`
Expected: 4 passed（schema 是纯 SQL，无需实现代码）

- [ ] **Step 6: 提交**

```bash
git add 小市值/pyproject.toml 小市值/research/__init__.py 小市值/research/__main__.py 小市值/research/schema.sql 小市值/research/tests/
git commit -m "feat(research): 包脚手架与 schema.sql（8 表 + 约定指标名清单）"
```

---
### Task 2: db.py + ids.py

**Files:**
- Create: `小市值/research/db.py`
- Create: `小市值/research/ids.py`
- Modify: `小市值/research/tests/test_db.py`（追加 db 函数测试）
- Create: `小市值/research/tests/test_ids.py`

**Interfaces:**
- Consumes: Task 1 的 `schema.sql`
- Produces:
  - `db.PACKAGE_DIR`（`小市值/research/`）、`db.SCHEMA_PATH`
  - `db.repo_root() -> Path`（向上遍历找 `.git`）
  - `db.connect(db_path: Path | str | None = None) -> sqlite3.Connection`（row_factory=Row，外键 ON；None 时用 `小市值/research/registry.db`）
  - `db.init_db(conn) -> None`（执行 schema.sql，幂等）
  - `ids.next_id(conn, prefix: str) -> str`（S/H/E/R/ST/A → 表名列名映射，MAX+1 补零 4 位）

- [ ] **Step 1: 写失败测试（test_db.py 追加 + test_ids.py）**

`小市值/research/tests/test_db.py` 追加：
```python
from research import db  # 顶部 import 区追加


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
```

`小市值/research/tests/test_ids.py`:
```python
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
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest 小市值/research/tests/test_db.py 小市值/research/tests/test_ids.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'research'`（包尚未安装）

- [ ] **Step 3: 安装包（一次性，后续任务都需要）**

Run: `pip install -e 小市值`
Expected: Successfully installed research-registry

- [ ] **Step 4: 写实现**

`小市值/research/db.py`:
```python
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
```

`小市值/research/ids.py`:
```python
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
```

- [ ] **Step 5: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_db.py 小市值/research/tests/test_ids.py -v`
Expected: 11 passed（test_db 7 个 + test_ids 4 个）

- [ ] **Step 6: 提交**

```bash
git add 小市值/research/db.py 小市值/research/ids.py 小市值/research/tests/
git commit -m "feat(research): db.py 连接与 schema 初始化、ids.py ID 生成器"
```

---
### Task 3: git_meta.py

**Files:**
- Create: `小市值/research/git_meta.py`
- Create: `小市值/research/tests/test_git_meta.py`

**Interfaces:**
- Consumes: 无（纯 git subprocess 封装）
- Produces:
  - `git_meta.git_commit_hash(root: Path) -> str`
  - `git_meta.git_blob_hash(root: Path, relpath: str) -> str`
  - `git_meta.worktree_clean(root: Path, relpath: str) -> bool`（无未提交改动，含未跟踪；用 `-c core.quotepath=false` porcelain 解析）
  - `git_meta.commit_message(root: Path) -> str`
  - `git_meta.diff_between(root: Path, h1: str, h2: str, relpath: str) -> str`
  - 私有 `_git(root, *args) -> str`：subprocess 调用，非零退出码抛 RuntimeError

- [ ] **Step 1: 写失败测试**

`小市值/research/tests/test_git_meta.py`:
```python
"""git 封装测试：在 tmp_path 构造临时 git 仓库验证（hermetic，不触碰真实仓库）。"""
import subprocess
from pathlib import Path

import pytest

from research import git_meta

HELLO_BLOB = "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0"  # git hash-object "hello"


def _make_repo(tmp_path: Path, content: str = "hello", message: str = "init") -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    f = root / "strategy.md"
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=root, check=True)
    return root


def test_commit_hash_length(tmp_path):
    root = _make_repo(tmp_path)
    assert len(git_meta.git_commit_hash(root)) == 40


def test_blob_hash_matches_known_value(tmp_path):
    root = _make_repo(tmp_path)
    assert git_meta.git_blob_hash(root, "strategy.md") == HELLO_BLOB


def test_worktree_clean_true_when_committed(tmp_path):
    root = _make_repo(tmp_path)
    assert git_meta.worktree_clean(root, "strategy.md") is True


def test_worktree_clean_false_after_edit(tmp_path):
    root = _make_repo(tmp_path)
    (root / "strategy.md").write_text("changed", encoding="utf-8")
    assert git_meta.worktree_clean(root, "strategy.md") is False


def test_commit_message(tmp_path):
    root = _make_repo(tmp_path, message="add strategy")
    assert git_meta.commit_message(root) == "add strategy"


def test_diff_between_shows_change(tmp_path):
    root = _make_repo(tmp_path)
    h1 = git_meta.git_commit_hash(root)
    (root / "strategy.md").write_text("hello world", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "second"], cwd=root, check=True)
    h2 = git_meta.git_commit_hash(root)
    diff = git_meta.diff_between(root, h1, h2, "strategy.md")
    assert "+hello world" in diff


def test_git_error_raises(tmp_path):
    with pytest.raises(RuntimeError):
        git_meta.git_commit_hash(tmp_path)  # 非 git 仓库
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest 小市值/research/tests/test_git_meta.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: 写实现**

`小市值/research/git_meta.py`:
```python
"""封装 git 命令调用（subprocess），替代自建 hash 方案。

所有命令以仓库根为 cwd；git 输出可能含中文路径，
统一用 -c core.quotepath=false 防止非 ASCII 路径被转义（Windows GBK 控制台场景）。
"""
import subprocess
from pathlib import Path


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=str(root), capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败: {result.stderr.strip()}")
    return result.stdout.strip()


def git_commit_hash(root: Path) -> str:
    """当前 HEAD 完整 hash。"""
    return _git(root, "rev-parse", "HEAD")


def git_blob_hash(root: Path, relpath: str) -> str:
    """文件内容指纹（git hash-object），与 commit 解耦。"""
    return _git(root, "hash-object", relpath)


def worktree_clean(root: Path, relpath: str) -> bool:
    """relpath 无未提交改动（含未跟踪文件），返回 True。

    用 porcelain 输出判断：输出为空即干净。
    -c core.quotepath=false 保证中文文件名不被 \345\260\217 形式转义。
    """
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "status", "--porcelain", "--", relpath],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8",
    )
    return result.stdout.strip() == ""


def commit_message(root: Path) -> str:
    """最近一次 commit 的 message（change_summary 默认值来源）。"""
    return _git(root, "log", "-1", "--format=%s")


def diff_between(root: Path, h1: str, h2: str, relpath: str) -> str:
    """两个 commit 间指定文件的 diff。"""
    return _git(root, "diff", h1, h2, "--", relpath)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_git_meta.py -v`
Expected: 7 passed

- [ ] **Step 5: 提交**

```bash
git add 小市值/research/git_meta.py 小市值/research/tests/test_git_meta.py
git commit -m "feat(research): git_meta.py 封装 rev-parse/hash-object/status/log/diff"
```

---
### Task 4: strategy.py

**Files:**
- Create: `小市值/research/strategy.py`
- Create: `小市值/research/tests/test_strategy.py`

**Interfaces:**
- Consumes: `db.repo_root/connect/init_db`、`ids.next_id`、`git_meta.*`（Task 2/3）
- Produces:
  - `strategy.SOURCE_PATH = "小市值/小市值策略代码.md"`（常量）
  - `strategy.create_strategy(conn, *, parent_id=None, name=None, change_summary=None, experiment_id=None, source_path=SOURCE_PATH, quick=False, root=None) -> dict`
    - root 默认 `db.repo_root()`（测试注入临时仓库）
    - 校验 worktree_clean，否则 RuntimeError
    - change_summary 默认 commit_message；name 默认 summary 前 40 字
    - blob 与最新 Strategy 相同 → warning（不拒绝）
    - `experiment_id` 给出时：校验存在、candidate 为空，创建后回填 candidate_strategy_id
    - `quick=True` 时禁止 experiment_id
    - 返回 `{"strategy_id": str, "warning": str | None}`
  - `strategy.show_strategy(conn, strategy_id) -> dict`（含 experiments/runs 关联列表；不存在抛 RuntimeError）
  - `strategy.strategy_tree(conn, root_id: str) -> list[tuple[str, int]]`（(strategy_id, depth) 深度优先）

- [ ] **Step 1: 写失败测试**

`小市值/research/tests/test_strategy.py`:
```python
"""Strategy 登记测试。"""
import subprocess
from pathlib import Path

import pytest

from research import db, strategy


def _make_repo(tmp_path: Path, content: str = "code v1") -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    f = root / "strategy.md"
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init code"], cwd=root, check=True)
    return root


def _conn(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    db.init_db(conn)
    return conn


def test_create_root_strategy(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    res = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                   change_summary="初始策略")
    assert res["strategy_id"] == "S0001"
    row = conn.execute("SELECT * FROM strategies WHERE strategy_id='S0001'").fetchone()
    assert row["parent_strategy_id"] is None
    assert row["change_summary"] == "初始策略"
    assert len(row["git_commit_hash"]) == 40


def test_create_child_strategy(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    s1 = strategy.create_strategy(conn, root=root, source_path="strategy.md")["strategy_id"]
    (root / "strategy.md").write_text("code v2", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "v2"], cwd=root, check=True)
    res = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                   parent_id=s1, change_summary="v2 改动")
    assert res["strategy_id"] == "S0002"
    row = conn.execute("SELECT * FROM strategies WHERE strategy_id='S0002'").fetchone()
    assert row["parent_strategy_id"] == "S0001"


def test_dirty_worktree_rejected(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    (root / "strategy.md").write_text("uncommitted change", encoding="utf-8")
    with pytest.raises(RuntimeError, match="未提交改动"):
        strategy.create_strategy(conn, root=root, source_path="strategy.md")


def test_duplicate_blob_warns(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    strategy.create_strategy(conn, root=root, source_path="strategy.md")
    res = strategy.create_strategy(conn, root=root, source_path="strategy.md")
    assert res["warning"] is not None
    assert "相同" in res["warning"]


def test_name_defaults_to_summary_head(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    summary = "这是一个用于测试的较长变更摘要" * 3  # 超 40 字
    res = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                   change_summary=summary)
    row = conn.execute("SELECT name FROM strategies WHERE strategy_id=?", (res["strategy_id"],)).fetchone()
    assert len(row["name"]) == 40
    assert row["name"] == summary[:40]


def test_quick_mode_forbids_experiment(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="快速检查点"):
        strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                 quick=True, experiment_id="E0001")


def test_backfill_experiment_candidate(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    s1 = strategy.create_strategy(conn, root=root, source_path="strategy.md")["strategy_id"]
    conn.execute(
        "INSERT INTO experiments (experiment_id, baseline_strategy_id, title, change_scope, validation_tier, created_at) "
        "VALUES ('E0001', ?, 't', 'MICRO', 'V1', '2026-01-01')", (s1,))
    conn.commit()
    s2 = strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                  experiment_id="E0001")["strategy_id"]
    row = conn.execute("SELECT candidate_strategy_id FROM experiments WHERE experiment_id='E0001'").fetchone()
    assert row["candidate_strategy_id"] == s2


def test_backfill_missing_experiment_raises(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    with pytest.raises(RuntimeError, match="不存在"):
        strategy.create_strategy(conn, root=root, source_path="strategy.md",
                                 experiment_id="E9999")


def test_show_strategy_includes_links(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    s1 = strategy.create_strategy(conn, root=root, source_path="strategy.md")["strategy_id"]
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status) "
        "VALUES ('R0001', ?, '2020-01-01', '2021-01-01', 'SUCCESS')", (s1,))
    conn.commit()
    info = strategy.show_strategy(conn, s1)
    assert info["strategy_id"] == s1
    assert info["runs"] == ["R0001"]
    with pytest.raises(RuntimeError, match="不存在"):
        strategy.show_strategy(conn, "S9999")


def test_strategy_tree_depth(tmp_path):
    root = _make_repo(tmp_path)
    conn = _conn(tmp_path)
    s1 = strategy.create_strategy(conn, root=root, source_path="strategy.md")["strategy_id"]
    (root / "strategy.md").write_text("v2", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "v2"], cwd=root, check=True)
    s2 = strategy.create_strategy(conn, root=root, source_path="strategy.md", parent_id=s1)["strategy_id"]
    (root / "strategy.md").write_text("v3", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "v3"], cwd=root, check=True)
    strategy.create_strategy(conn, root=root, source_path="strategy.md", parent_id=s2)
    tree = strategy.strategy_tree(conn, s1)
    assert tree == [(s1, 0), (s2, 1), ("S0003", 2)]
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest 小市值/research/tests/test_strategy.py -v`
Expected: FAIL — ModuleNotFoundError: No module named 'research.strategy'

- [ ] **Step 3: 写实现**

`小市值/research/strategy.py`:
```python
"""Strategy（代码状态）登记与查询。"""
import sqlite3
from pathlib import Path

from research import db, git_meta, ids

SOURCE_PATH = "小市值/小市值策略代码.md"


def _latest_blob(conn: sqlite3.Connection) -> str | None:
    row = conn.execute(
        "SELECT file_blob_hash FROM strategies ORDER BY created_at DESC, rowid DESC LIMIT 1"
    ).fetchone()
    return row["file_blob_hash"] if row else None


def create_strategy(conn, *, parent_id=None, name=None, change_summary=None,
                    experiment_id=None, source_path=SOURCE_PATH, quick=False,
                    root: Path | None = None) -> dict:
    """创建策略版本，返回 {"strategy_id", "warning"}。

    - 创建前校验 source_path 工作区干净（git_commit_hash 必须对应硬盘实际内容）
    - blob 与最新版本相同时给 warning 而非拒绝（可能是有意回退重登记）
    - experiment_id 给出时校验存在且 candidate 为空，创建后回填
    - quick=True（快速检查点）禁止关联 Experiment
    """
    if quick and experiment_id is not None:
        raise RuntimeError("快速检查点不能关联 Experiment（quick 模式不建实验）")
    root = root or db.repo_root()
    if not git_meta.worktree_clean(root, source_path):
        raise RuntimeError(f"{source_path} 有未提交改动，请先 git commit 再登记 Strategy")
    commit_hash = git_meta.git_commit_hash(root)
    blob = git_meta.git_blob_hash(root, source_path)
    if change_summary is None:
        change_summary = git_meta.commit_message(root)
    if name is None:
        name = (change_summary or "unnamed")[:40]

    warning = None
    latest = _latest_blob(conn)
    if latest is not None and latest == blob:
        warning = "警告: file_blob_hash 与最新 Strategy 相同（内容未变），确认是否为有意重新登记"

    if experiment_id is not None:
        exp = conn.execute(
            "SELECT candidate_strategy_id FROM experiments WHERE experiment_id=?", (experiment_id,)
        ).fetchone()
        if exp is None:
            raise RuntimeError(f"Experiment {experiment_id} 不存在")
        if exp["candidate_strategy_id"] is not None:
            raise RuntimeError(
                f"Experiment {experiment_id} 已有 candidate {exp['candidate_strategy_id']}，"
                "如需更换先显式清空原值"
            )

    sid = ids.next_id(conn, "S")
    conn.execute(
        "INSERT INTO strategies (strategy_id, parent_strategy_id, name, source_path, "
        "git_commit_hash, file_blob_hash, change_summary, created_at) "
        "VALUES (?,?,?,?,?,?,?, date('now'))",
        (sid, parent_id, name, source_path, commit_hash, blob, change_summary),
    )
    if experiment_id is not None:
        conn.execute(
            "UPDATE experiments SET candidate_strategy_id=? WHERE experiment_id=?",
            (sid, experiment_id),
        )
    conn.commit()
    return {"strategy_id": sid, "warning": warning}


def show_strategy(conn: sqlite3.Connection, strategy_id: str) -> dict:
    """返回策略详情 + 关联实验/回测列表。"""
    row = conn.execute("SELECT * FROM strategies WHERE strategy_id=?", (strategy_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"Strategy {strategy_id} 不存在")
    info = dict(row)
    info["experiments"] = [
        r["experiment_id"] for r in conn.execute(
            "SELECT experiment_id FROM experiments WHERE baseline_strategy_id=? OR candidate_strategy_id=?",
            (strategy_id, strategy_id),
        )
    ]
    info["runs"] = [
        r["run_id"] for r in conn.execute(
            "SELECT run_id FROM runs WHERE strategy_id=?", (strategy_id,)
        )
    ]
    return info


def strategy_tree(conn: sqlite3.Connection, root_id: str) -> list[tuple[str, int]]:
    """从 root_id 出发深度优先输出 [(strategy_id, depth)]。"""
    rows = conn.execute("SELECT strategy_id, parent_strategy_id FROM strategies").fetchall()
    children: dict[str | None, list[str]] = {}
    for r in rows:
        children.setdefault(r["parent_strategy_id"], []).append(r["strategy_id"])
    result: list[tuple[str, int]] = []

    def walk(sid: str, depth: int) -> None:
        result.append((sid, depth))
        for child in sorted(children.get(sid, [])):
            walk(child, depth + 1)

    if root_id not in {r["strategy_id"] for r in rows}:
        raise RuntimeError(f"Strategy {root_id} 不存在")
    walk(root_id, 0)
    return result
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_strategy.py -v`
Expected: 10 passed

- [ ] **Step 5: 提交**

```bash
git add 小市值/research/strategy.py 小市值/research/tests/test_strategy.py
git commit -m "feat(research): strategy.py 创建/查看/谱系树（git 干净校验 + blob 警告 + 实验回填）"
```

---
### Task 5: hypothesis + experiment + promote

**Files:**
- Create: `小市值/research/experiment.py`
- Create: `小市值/research/tests/test_experiment.py`

**Interfaces:**
- Consumes: `ids.next_id`；`strategy.create_strategy`（测试中造数据）
- Produces:
  - `experiment.VALID_SCOPES` / `experiment.VALID_TIERS`（常量集合）
  - `experiment.create_hypothesis(conn, *, title, description, expected_effect=None) -> str`
  - `experiment.create_experiment(conn, *, baseline_id, title, change_scope, validation_tier, hypothesis_id=None, candidate_id=None, description=None, n_trials=1) -> str`
    - scope/tier 枚举校验；baseline 存在校验；n_trials 校验 ≥1
  - `experiment.promote(conn, *, strategy_id, baseline_id, title, change_scope, validation_tier, hypothesis_id=None, description=None, n_trials=1) -> str`
    - 校验 strategy 存在且未关联任何 Experiment 的 candidate；内部调 create_experiment(candidate_id=strategy_id)
  - `experiment.show_experiment(conn, experiment_id) -> dict`（含 studies 关联）
  - `experiment.list_experiments(conn, status=None) -> list[dict]`

- [ ] **Step 1: 写失败测试**

`小市值/research/tests/test_experiment.py`:
```python
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
                                       change_scope="PARAMETER_SWEEP", validation_tier="V3",
                                       n_trials=5)
    row = conn.execute("SELECT n_trials FROM experiments WHERE experiment_id=?", (eid,)).fetchone()
    assert row["n_trials"] == 5


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
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest 小市值/research/tests/test_experiment.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: 写实现**

`小市值/research/experiment.py`:
```python
"""Hypothesis 与 Experiment 登记（含快速检查点升级 promote）。"""
import sqlite3

from research import ids

VALID_SCOPES = {"MICRO", "SMALL", "MEDIUM", "LARGE", "ARCHITECTURAL"}
VALID_TIERS = {"V1", "V2", "V3", "V4", "V5"}


def create_hypothesis(conn, *, title: str, description: str,
                      expected_effect: str | None = None) -> str:
    """创建研究假设，返回 H 开头的 hypothesis_id。"""
    hid = ids.next_id(conn, "H")
    conn.execute(
        "INSERT INTO hypotheses (hypothesis_id, title, description, expected_effect, created_at) "
        "VALUES (?,?,?,?, date('now'))",
        (hid, title, description, expected_effect),
    )
    conn.commit()
    return hid


def _validate_experiment_args(conn, baseline_id, change_scope, validation_tier, n_trials) -> None:
    if change_scope not in VALID_SCOPES:
        raise RuntimeError(f"change_scope 必须是 {sorted(VALID_SCOPES)} 之一")
    if validation_tier not in VALID_TIERS:
        raise RuntimeError(f"validation_tier 必须是 {sorted(VALID_TIERS)} 之一")
    if n_trials < 1:
        raise RuntimeError("n_trials 必须 ≥ 1")
    if conn.execute("SELECT 1 FROM strategies WHERE strategy_id=?", (baseline_id,)).fetchone() is None:
        raise RuntimeError(f"baseline Strategy {baseline_id} 不存在")


def create_experiment(conn, *, baseline_id: str, title: str, change_scope: str,
                      validation_tier: str, hypothesis_id: str | None = None,
                      candidate_id: str | None = None, description: str | None = None,
                      n_trials: int = 1) -> str:
    """创建正式实验，返回 E 开头的 experiment_id。candidate 可留空稍后回填。"""
    _validate_experiment_args(conn, baseline_id, change_scope, validation_tier, n_trials)
    eid = ids.next_id(conn, "E")
    conn.execute(
        "INSERT INTO experiments (experiment_id, hypothesis_id, baseline_strategy_id, "
        "candidate_strategy_id, title, description, change_scope, validation_tier, "
        "n_trials, status, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,'PLANNED', date('now'))",
        (eid, hypothesis_id, baseline_id, candidate_id, title, description,
         change_scope, validation_tier, n_trials),
    )
    conn.commit()
    return eid


def promote(conn, *, strategy_id: str, baseline_id: str, title: str,
            change_scope: str, validation_tier: str, hypothesis_id: str | None = None,
            description: str | None = None, n_trials: int = 1) -> str:
    """快速检查点 Strategy → 正式实验（创建新 Experiment，candidate=该 Strategy）。

    与 experiment create 区别：promote 由已有 Strategy 出发创建实验；
    strategy create --experiment 由已有 Experiment 出发回填 candidate。
    """
    if conn.execute("SELECT 1 FROM strategies WHERE strategy_id=?", (strategy_id,)).fetchone() is None:
        raise RuntimeError(f"Strategy {strategy_id} 不存在")
    existing = conn.execute(
        "SELECT experiment_id FROM experiments WHERE candidate_strategy_id=?", (strategy_id,)
    ).fetchone()
    if existing is not None:
        raise RuntimeError(f"Strategy {strategy_id} 已关联 Experiment {existing['experiment_id']}，不能重复 promote")
    return create_experiment(conn, baseline_id=baseline_id, title=title,
                             change_scope=change_scope, validation_tier=validation_tier,
                             hypothesis_id=hypothesis_id, candidate_id=strategy_id,
                             description=description, n_trials=n_trials)


def show_experiment(conn: sqlite3.Connection, experiment_id: str) -> dict:
    """返回实验详情 + 关联 Study 列表。"""
    row = conn.execute("SELECT * FROM experiments WHERE experiment_id=?", (experiment_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"Experiment {experiment_id} 不存在")
    info = dict(row)
    info["studies"] = [
        r["study_id"] for r in conn.execute(
            "SELECT study_id FROM studies WHERE experiment_id=?", (experiment_id,)
        )
    ]
    return info


def list_experiments(conn: sqlite3.Connection, status: str | None = None) -> list[dict]:
    """实验列表，可选按 status 过滤。"""
    if status:
        rows = conn.execute(
            "SELECT * FROM experiments WHERE status=? ORDER BY experiment_id", (status,)
        )
    else:
        rows = conn.execute("SELECT * FROM experiments ORDER BY experiment_id")
    return [dict(r) for r in rows]
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_experiment.py -v`
Expected: 9 passed

- [ ] **Step 5: 提交**

```bash
git add 小市值/research/experiment.py 小市值/research/tests/test_experiment.py
git commit -m "feat(research): hypothesis/experiment/promote（枚举校验 + baseline 锚定 + 升级路径）"
```

---
### Task 6: run.py

**Files:**
- Create: `小市值/research/run.py`
- Create: `小市值/research/tests/test_run.py`

**Interfaces:**
- Consumes: `ids.next_id`
- Produces:
  - `run.VALID_STATUS` / `run.VALID_SOURCES` / `run.VALID_REGIMES`（常量集合）
  - `run.create_run(conn, *, strategy_id, start_date, end_date, status, experiment_id=None, initial_capital=None, frequency=None, parameters=None, error_type=None, error_message=None, n_trades=None, benchmark=None, benchmark_return=None, regime=None, source_log_path=None, notes=None, metrics=None) -> str`
    - metrics: list[tuple[name, value, source]]；status 校验；FAILED 必须 error_type；regime 枚举；strategy 存在校验；parameters 自动 json.dumps
  - `run.add_metric(conn, run_id, name, value, source, commit=True) -> None`（(run_id, metric_name) 冲突时 UPSERT 更新）
  - `run.create_run_from_json(conn, data: dict) -> str`（spec JSON 形态：strategy/start/end/capital/status/group/role/partition 之外的键映射；metrics 为 {name: value} 字典，来源默认 joinquant_pasted）
  - `run.show_run(conn, run_id) -> dict`（含 metrics 列表）

- [ ] **Step 1: 写失败测试**

`小市值/research/tests/test_run.py`:
```python
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
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest 小市值/research/tests/test_run.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: 写实现**

`小市值/research/run.py`:
```python
"""Run（一次真实聚宽回测）登记与查询。"""
import json
import sqlite3

from research import ids

VALID_STATUS = {"SUCCESS", "FAILED", "PARTIAL", "INCOMPLETE"}
VALID_SOURCES = {"joinquant_pasted", "derived_local", "manual_estimate", "secondhand_mention"}
VALID_REGIMES = {"bull", "bear", "sideways", "unknown"}


def _check_strategy(conn: sqlite3.Connection, strategy_id: str) -> None:
    if conn.execute("SELECT 1 FROM strategies WHERE strategy_id=?", (strategy_id,)).fetchone() is None:
        raise RuntimeError(f"Strategy {strategy_id} 不存在")


def create_run(conn, *, strategy_id: str, start_date: str, end_date: str, status: str,
               experiment_id: str | None = None, initial_capital: float | None = None,
               frequency: str | None = None, parameters: dict | None = None,
               error_type: str | None = None, error_message: str | None = None,
               n_trades: int | None = None, benchmark: str | None = None,
               benchmark_return: float | None = None, regime: str | None = None,
               source_log_path: str | None = None, notes: str | None = None,
               metrics: list[tuple[str, float, str]] | None = None) -> str:
    """登记一次回测。metrics 为 [(metric_name, value, source), ...]。"""
    if status not in VALID_STATUS:
        raise RuntimeError(f"status 必须是 {sorted(VALID_STATUS)} 之一")
    if status == "FAILED" and not error_type:
        raise RuntimeError("status=FAILED 时必须提供 error_type（如 SecurityNotExist）")
    if regime is not None and regime not in VALID_REGIMES:
        raise RuntimeError(f"regime 必须是 {sorted(VALID_REGIMES)} 之一")
    _check_strategy(conn, strategy_id)

    parameters_json = json.dumps(parameters, ensure_ascii=False) if parameters else None
    rid = ids.next_id(conn, "R")
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, experiment_id, start_date, end_date, "
        "initial_capital, frequency, parameters_json, status, error_type, error_message, "
        "n_trades, benchmark, benchmark_return, regime, source_log_path, notes, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, date('now'))",
        (rid, strategy_id, experiment_id, start_date, end_date, initial_capital, frequency,
         parameters_json, status, error_type, error_message, n_trades, benchmark,
         benchmark_return, regime, source_log_path, notes),
    )
    for name, value, source in (metrics or []):
        add_metric(conn, rid, name, value, source, commit=False)
    conn.commit()
    return rid


def add_metric(conn: sqlite3.Connection, run_id: str, name: str, value: float,
               source: str, commit: bool = True) -> None:
    """写入/更新单个指标（同键 upsert，用于回填修正）。"""
    if source not in VALID_SOURCES:
        raise RuntimeError(f"metric_source 必须是 {sorted(VALID_SOURCES)} 之一")
    conn.execute(
        "INSERT INTO metrics (run_id, metric_name, metric_value, metric_source) "
        "VALUES (?,?,?,?) "
        "ON CONFLICT(run_id, metric_name) DO UPDATE SET "
        "metric_value=excluded.metric_value, metric_source=excluded.metric_source",
        (run_id, name, value, source),
    )
    if commit:
        conn.commit()


def create_run_from_json(conn: sqlite3.Connection, data: dict) -> str:
    """JSON payload 建 Run（spec §8 形态：strategy/start/end/capital + metrics 字典）。"""
    metrics = [(name, value, "joinquant_pasted")
               for name, value in (data.get("metrics") or {}).items()]
    return create_run(
        conn,
        strategy_id=data["strategy"],
        start_date=data["start"],
        end_date=data["end"],
        status=data.get("status", "SUCCESS"),
        experiment_id=data.get("experiment_id"),
        initial_capital=data.get("capital"),
        frequency=data.get("frequency"),
        parameters=data.get("parameters"),
        error_type=data.get("error_type"),
        error_message=data.get("error_message"),
        n_trades=data.get("n_trades"),
        benchmark=data.get("benchmark"),
        benchmark_return=data.get("benchmark_return"),
        regime=data.get("regime"),
        source_log_path=data.get("source_log_path"),
        notes=data.get("notes"),
        metrics=metrics,
    )


def show_run(conn: sqlite3.Connection, run_id: str) -> dict:
    """返回 Run 详情 + metrics 列表。"""
    row = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
    if row is None:
        raise RuntimeError(f"Run {run_id} 不存在")
    info = dict(row)
    info["metrics"] = [
        dict(m) for m in conn.execute(
            "SELECT metric_name, metric_value, metric_source FROM metrics WHERE run_id=? "
            "ORDER BY metric_name", (run_id,)
        )
    ]
    return info
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_run.py -v`
Expected: 11 passed

- [ ] **Step 5: 提交**

```bash
git add 小市值/research/run.py 小市值/research/tests/test_run.py
git commit -m "feat(research): run.py 回测登记（FAILED 校验/metrics upsert/JSON 批量形态）"
```

---
### Task 7: study.py

**Files:**
- Create: `小市值/research/study.py`
- Create: `小市值/research/tests/test_study.py`

**Interfaces:**
- Consumes: `run.create_run_from_json`、`ids.next_id`
- Produces:
  - `study.VALID_TYPES = {"SINGLE","ROLLING","FACTOR_LAYER","PARAMETER_SWEEP","ABLATION"}`
  - `study.VALID_ROLES = {"baseline","candidate"}`、`study.VALID_PARTITIONS = {"is","oos"}`
  - `study.create_study(conn, *, experiment_id, study_type, name, design_json, description=None) -> str`
    - design_json 可为 dict/list（自动 json.dumps）或 str；type/experiment 存在校验；design_json 强制非空（防过拟合核心：必须在看到 Run 结果前登记）
  - `study.add_run(conn, study_id, run_id, group_name=None, role=None, partition=None) -> None`（INSERT OR REPLACE 幂等；role/partition 枚举校验；study/run 存在校验）
  - `study.batch_add_runs(conn, study_id, runs: list[dict]) -> list[str]`（spec rolling_runs.json 形态，逐项 create_run_from_json + add_run(group/role/partition)，返回新建 run_id 列表）
  - `study.show_study(conn, study_id) -> dict`（含 runs 明细：run_id/group_name/role/partition/strategy_id/start_date/end_date/status）

- [ ] **Step 1: 写失败测试**

`小市值/research/tests/test_study.py`:
```python
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
                              name="s", design_json={})
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status) "
        "VALUES ('R0001', 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS')")
    conn.commit()
    study.add_run(conn, stid, "R0001", group_name="2020-2021", role="candidate", partition="is")
    info = study.show_study(conn, stid)
    assert info["runs"][0]["role"] == "candidate"
    assert info["runs"][0]["partition"] == "is"
    assert info["runs"][0]["group_name"] == "2020-2021"


def test_add_run_invalid_role(tmp_path):
    conn = _conn(tmp_path)
    stid = study.create_study(conn, experiment_id="E0001", study_type="SINGLE",
                              name="s", design_json={})
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status) "
        "VALUES ('R0001', 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS')")
    conn.commit()
    with pytest.raises(RuntimeError, match="role"):
        study.add_run(conn, stid, "R0001", role="weird")


def test_add_run_invalid_partition(tmp_path):
    conn = _conn(tmp_path)
    stid = study.create_study(conn, experiment_id="E0001", study_type="SINGLE",
                              name="s", design_json={})
    conn.execute(
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status) "
        "VALUES ('R0001', 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS')")
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
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest 小市值/research/tests/test_study.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: 写实现**

`小市值/research/study.py`:
```python
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
    """
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_study.py -v`
Expected: 9 passed

- [ ] **Step 5: 提交**

```bash
git add 小市值/research/study.py 小市值/research/tests/test_study.py
git commit -m "feat(research): study.py 预登记设计组织（design_json 强制 + is/oos 分区 + 批量建 Run）"
```

---
### Task 8: analysis.py

**Files:**
- Create: `小市值/research/analysis.py`
- Create: `小市值/research/tests/test_analysis.py`

**Interfaces:**
- Consumes: `ids.next_id`；`study_runs/runs/metrics` 表（Task 1 schema）
- Produces:
  - `analysis.VALID_DECISIONS = {"ACCEPT","REJECT","INCONCLUSIVE","DEFER"}`、`analysis.VALID_EVIDENCE = {"E0".."E6"}`
  - `analysis.analyze_study(conn, study_id) -> dict`
    - 返回 `{"study_id", "statistics", "diagnostics", "primary_metric"}`
    - statistics：每指标一行 `{metric, n, mean, median, std, min, max, positive_ratio, baseline_delta}`；std 用 population std（pstdev，n≥2 才可算，否则 None）；baseline_delta = mean(candidate) − mean(baseline)，缺任一角色则 None
    - diagnostics：5 项过拟合诊断的 `[OK] / [WARN] / [N/A]` 行（Window Stability / Parameter Stability / Factor Monotonicity / IS-OOS Gap / Best-vs-Median Gap）；**数据不足一律输出 `[N/A] 数据不足` 或 `[N/A] 未标注样本外区间`，绝不抛错**
    - primary_metric：候选 Run 中按 total_return → annual_return → benchmark_excess_return → sharpe → 任一指标 选主指标，供诊断使用
    - Study 不存在或未关联任何 Run 时抛 RuntimeError
  - `analysis.create_analysis(conn, *, study_id, decision, evidence_level, conclusion=None, confidence=None) -> str`
    - decision 枚举校验；evidence_level ∈ E0~E6 校验；confidence ∈ [0,1] 校验；study 存在校验；返回 A 开头的 analysis_id

- [ ] **Step 1: 写失败测试**

`小市值/research/tests/test_analysis.py`:
```python
"""Study 统计分析与过拟合诊断、Analysis 结论登记测试。"""
import pytest

from research import analysis, db


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
        "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status) "
        "VALUES (?, 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS')", (rid,))
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
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest 小市值/research/tests/test_analysis.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: 写实现**

`小市值/research/analysis.py`:
```python
"""Study 统计分析 + 5 项过拟合诊断 + Analysis 结论登记（spec §6/§9/§10 Phase 6）。

约定：诊断只输出 [OK]/[WARN]/[N/A] 行，不下"过拟合"结论；
最终判断留给 analysis create 的人工/AI 决策。
数据不足（SINGLE、缺分组、缺 oos 分区等）一律输出 [N/A] 而非抛错。
"""
import sqlite3
import statistics

from research import ids

VALID_DECISIONS = {"ACCEPT", "REJECT", "INCONCLUSIVE", "DEFER"}
VALID_EVIDENCE = {f"E{i}" for i in range(7)}  # E0（尚未验证）~ E6（跨多市场环境验证）

# ---- 诊断阈值（v1 简化口径，可调常量；仅供 WARNING 提示，不作最终结论）----
OOS_GAP_RATIO = 0.7     # oos 均值 < is 均值 × 0.7 → WARN（is 均值为正时）
OOS_GAP_ABS = 0.2       # is 均值为负/零时的绝对差距阈值
BEST_MEDIAN_GAP = 0.5   # (best − median) / |median| ≥ 0.5 → WARN（"显著优于"口径）
PARAM_CV_WARN = 0.5     # 参数组均值 CV > 0.5 → WARN（对参数敏感）

# 主指标候选顺序（按优先级取第一个候选 Run 中存在的）
_PRIMARY_METRICS = ("total_return", "annual_return", "benchmark_excess_return", "sharpe")


def _study_run_rows(conn: sqlite3.Connection, study_id: str) -> list[dict]:
    """study_runs 关联 runs + metrics，每 run 一个 dict（非空数值指标）。"""
    rows = conn.execute(
        "SELECT sr.group_name, sr.role, sr.partition, r.run_id "
        "FROM study_runs sr JOIN runs r ON r.run_id = sr.run_id "
        "WHERE sr.study_id=? ORDER BY sr.run_id", (study_id,)
    ).fetchall()
    result = []
    for r in rows:
        metrics = {}
        for m in conn.execute(
            "SELECT metric_name, metric_value FROM metrics WHERE run_id=?", (r["run_id"],)
        ):
            if m["metric_value"] is not None:
                metrics[m["metric_name"]] = m["metric_value"]
        result.append({"run_id": r["run_id"], "group_name": r["group_name"],
                       "role": r["role"], "partition": r["partition"], "metrics": metrics})
    return result


def _group_means(rows: list[dict], metric: str, role: str | None = None) -> dict[str, float]:
    """按分组（group_name，缺省用 run_id 兜底）聚合各 run 指标均值。"""
    groups: dict[str, list[float]] = {}
    for r in rows:
        if role is not None and r["role"] != role:
            continue
        val = r["metrics"].get(metric)
        if val is None:
            continue
        key = r["group_name"] or r["run_id"]
        groups.setdefault(key, []).append(val)
    return {k: statistics.mean(v) for k, v in groups.items()}


def _diag_window_stability(rows: list[dict], metric: str) -> str:
    """多窗口方向一致性（至少 2 个分组才可计算）。"""
    means = list(_group_means(rows, metric, role="candidate").values())
    if len(means) < 2:
        return "[N/A] 数据不足（窗口稳定性需要 ≥2 个分组）"
    if all(m >= 0 for m in means) or all(m <= 0 for m in means):
        return "[OK]   多窗口方向一致"
    return "[WARN] 多窗口方向不一致（分组间收益方向冲突）"


def _diag_parameter_stability(rows: list[dict], metric: str) -> str:
    """参数稳定性：参数组均值离散度（CV），至少 3 个参数组才可计算。"""
    means = list(_group_means(rows, metric, role="candidate").values())
    if len(means) < 3:
        return "[N/A] 数据不足（参数稳定性需要 ≥3 个参数组）"
    avg = statistics.mean(means)
    cv = statistics.pstdev(means) / abs(avg) if avg else float("inf")
    if cv > PARAM_CV_WARN:
        return f"[WARN] 参数间均值离散度过高（CV={cv:.2f}），结果对参数敏感"
    return "[OK]   参数间表现稳定"


def _diag_factor_monotonicity(rows: list[dict], metric: str) -> str:
    """因子单调性：按分组名排序后均值逐级同向，至少 3 个层级才可计算。"""
    means = _group_means(rows, metric, role="candidate")
    if len(means) < 3:
        return "[N/A] 数据不足（因子单调性需要 ≥3 个层级）"
    vals = [means[k] for k in sorted(means)]
    diffs = [b - a for a, b in zip(vals, vals[1:])]
    if all(d >= 0 for d in diffs) or all(d <= 0 for d in diffs):
        return "[OK]   因子层级近似单调"
    return "[WARN] 因子层级不单调（分层收益未按层级顺序排列）"


def _diag_is_oos_gap(rows: list[dict], metric: str) -> str:
    """IS-OOS Gap：仅当存在 partition='oos' 的 run 时才计算，否则 [N/A] 未标注样本外区间。"""
    is_vals = [r["metrics"][metric] for r in rows
               if r["partition"] == "is" and r["metrics"].get(metric) is not None]
    oos_vals = [r["metrics"][metric] for r in rows
                if r["partition"] == "oos" and r["metrics"].get(metric) is not None]
    if not oos_vals:
        return "[N/A] 未标注样本外区间"
    if not is_vals:
        return "[N/A] 数据不足（无 is 分区样本）"
    is_mean, oos_mean = statistics.mean(is_vals), statistics.mean(oos_vals)
    gap = (oos_mean < is_mean * OOS_GAP_RATIO) if is_mean > 0 else (oos_mean < is_mean - OOS_GAP_ABS)
    if gap:
        return f"[WARN] OOS 表现明显低于 IS（IS={is_mean:.3f} OOS={oos_mean:.3f}）"
    return f"[OK]   IS-OOS 差距在可接受范围（IS={is_mean:.3f} OOS={oos_mean:.3f}）"


def _diag_best_vs_median(rows: list[dict], metric: str) -> str:
    """Best-vs-Median Gap：最优参数组 vs 中位数，至少 3 个参数点才可计算。"""
    means = list(_group_means(rows, metric, role="candidate").values())
    if len(means) < 3:
        return "[N/A] 数据不足（Best-vs-Median 需要 ≥3 个参数点）"
    best, med = max(means), statistics.median(means)
    rel = (best - med) / (abs(med) + 1e-9)
    if rel >= BEST_MEDIAN_GAP:
        return f"[WARN] 最优参数显著优于中位数（best={best:.3f} median={med:.3f}，过拟合信号）"
    return f"[OK]   最优参数与中位数差距不大（best={best:.3f} median={med:.3f}）"


def analyze_study(conn: sqlite3.Connection, study_id: str) -> dict:
    """统计 + 5 项过拟合诊断。数据不足输出 [N/A] 而非报错（spec §6/§9）。"""
    if conn.execute("SELECT 1 FROM studies WHERE study_id=?", (study_id,)).fetchone() is None:
        raise RuntimeError(f"Study {study_id} 不存在")
    rows = _study_run_rows(conn, study_id)
    if not rows:
        raise RuntimeError(f"Study {study_id} 未关联任何 Run，无法分析")

    statistics_rows = []
    for name in sorted({m for r in rows for m in r["metrics"]}):
        vals = [r["metrics"][name] for r in rows if r["metrics"].get(name) is not None]
        cand = [r["metrics"][name] for r in rows
                if r["role"] == "candidate" and r["metrics"].get(name) is not None]
        base = [r["metrics"][name] for r in rows
                if r["role"] == "baseline" and r["metrics"].get(name) is not None]
        delta = (statistics.mean(cand) - statistics.mean(base)) if cand and base else None
        statistics_rows.append({
            "metric": name, "n": len(vals),
            "mean": statistics.mean(vals) if vals else None,
            "median": statistics.median(vals) if vals else None,
            "std": statistics.pstdev(vals) if len(vals) >= 2 else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "positive_ratio": statistics.mean([v > 0 for v in vals]) if vals else None,
            "baseline_delta": delta,
        })

    cand_metrics = {m for r in rows if r["role"] == "candidate" for m in r["metrics"]}
    primary = next((m for m in _PRIMARY_METRICS if m in cand_metrics), None)
    if primary is None and cand_metrics:
        primary = sorted(cand_metrics)[0]
    if primary is None:
        diagnostics = ["[N/A] 数据不足（候选 Run 无可用指标）"] * 5
    else:
        diagnostics = [
            _diag_window_stability(rows, primary),
            _diag_parameter_stability(rows, primary),
            _diag_factor_monotonicity(rows, primary),
            _diag_is_oos_gap(rows, primary),
            _diag_best_vs_median(rows, primary),
        ]
    return {"study_id": study_id, "statistics": statistics_rows,
            "diagnostics": diagnostics, "primary_metric": primary}


def create_analysis(conn: sqlite3.Connection, *, study_id: str, decision: str,
                    evidence_level: str, conclusion: str | None = None,
                    confidence: float | None = None) -> str:
    """登记一条 Analysis 结论，返回 A 开头的 analysis_id（spec §10 Phase 6）。"""
    if conn.execute("SELECT 1 FROM studies WHERE study_id=?", (study_id,)).fetchone() is None:
        raise RuntimeError(f"Study {study_id} 不存在")
    if decision not in VALID_DECISIONS:
        raise RuntimeError(f"decision 必须是 {sorted(VALID_DECISIONS)} 之一")
    if evidence_level not in VALID_EVIDENCE:
        raise RuntimeError("evidence_level 必须是 E0~E6 之一")
    if confidence is not None and not (0 <= confidence <= 1):
        raise RuntimeError("confidence 必须在 [0, 1] 区间")
    aid = ids.next_id(conn, "A")
    conn.execute(
        "INSERT INTO analyses (analysis_id, study_id, conclusion, decision, evidence_level, "
        "confidence, created_at) VALUES (?,?,?,?,?,?, date('now'))",
        (aid, study_id, conclusion, decision, evidence_level, confidence),
    )
    conn.commit()
    return aid
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_analysis.py -v`
Expected: 10 passed

- [ ] **Step 5: 提交**

```bash
git add 小市值/research/analysis.py 小市值/research/tests/test_analysis.py
git commit -m "feat(research): analysis.py 统计与 5 项过拟合诊断（数据不足输出 N/A）+ Analysis 登记"
```

---
### Task 9: templates.py + reports.py

**Files:**
- Create: `小市值/research/templates.py`
- Create: `小市值/research/reports.py`
- Modify: `小市值/research/tests/test_analysis.py`（追加"报告生成测试"小节——spec §2/§13 约定 8 个测试文件，不新建 test_templates.py/test_reports.py）

**Interfaces:**
- Consumes: `db.PACKAGE_DIR`、`strategy.show_strategy`、`experiment.show_experiment`、`run.show_run`、`analysis.analyze_study`（Task 4/5/6/8）
- Produces:
  - `templates.strategy_md(info: dict) -> str` / `templates.experiment_md(info: dict) -> str` / `templates.run_md(info: dict) -> str` / `templates.study_md(info: dict) -> str` / `templates.analysis_md(info: dict) -> str`（纯字符串渲染，spec §5 模板）
  - `reports.write_strategy_report(conn, strategy_id, root=None) -> Path` / `write_experiment_report` / `write_run_report` / `write_study_report` / `write_analysis_report` / `write_all_reports(conn, root=None) -> list[Path]`
    - 输出目录：`小市值/research/{strategies,experiments,runs,studies,analyses}/`（root 参数供测试注入临时目录）
    - 单向生成 db→md；`write_analysis_report` 同时回写 `analyses.report_path`；`write_study_report` 的"## 结论"章节取该 Study 最新一条 Analysis 的 conclusion（spec §5/§10 Phase 7）

- [ ] **Step 1: 写失败测试（追加到 test_analysis.py 末尾）**

`小市值/research/tests/test_analysis.py` 追加：
```python
# ==================== 报告生成测试（Task 9，spec §10 Phase 7） ====================
from research import reports  # 顶部 import 区追加


def _seed_report_data(conn):
    """造一份完整数据：strategy + experiment + run + study + analysis。"""
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
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest 小市值/research/tests/test_analysis.py -v`
Expected: FAIL — ModuleNotFoundError: No module named 'research.reports'

- [ ] **Step 3: 写实现**

`小市值/research/templates.py`:
```python
"""归档 Markdown 模板（纯字符串渲染，db 数据 → md，单向生成）。

spec §5 模板；所有函数只接收普通 dict，不做任何 db 访问。
"""
import json


def strategy_md(info: dict) -> str:
    """strategies/Sxxxx.md。"""
    parent = info["parent_strategy_id"] or "（无，根版本）"
    experiments = info["experiments"] or ["（无，快速检查点）"]
    runs = info["runs"] or ["（无）"]
    return f"""# {info['strategy_id']}

## 基本信息
- Parent: {parent}
- Git Commit: {info['git_commit_hash']}
- File Blob Hash: {info['file_blob_hash']}
- Created: {info['created_at']}

## 变化
{info['change_summary'] or '（无摘要）'}

## 关联实验
{chr(10).join(f'- {e}' for e in experiments)}

## 关联回测
{chr(10).join(f'- {r}' for r in runs)}
"""


def experiment_md(info: dict) -> str:
    """experiments/Exxxxx.md。"""
    cand = info["candidate_strategy_id"] or "（未回填）"
    if info.get("expected_effect"):
        expected = "\n".join(f"- {line}" for line in info["expected_effect"].splitlines())
    else:
        expected = "- （未填写）"
    studies = info["studies"] or ["（无）"]
    return f"""# {info['experiment_id']}

## 核心假设
{info['title']}
{info['description'] or '（无描述）'}

## Baseline / Candidate
- Baseline: {info['baseline_strategy_id']}
- Candidate: {cand}

## Change Scope / Validation Tier
- Change Scope: {info['change_scope']}
- Validation Tier: {info['validation_tier']}
- 试验次数: {info['n_trials']}

## 预期
{expected}

## 验证计划
{info['description'] or '（无）'}

## 关联 Study
{chr(10).join(f'- {s}' for s in studies)}

## 当前状态
{info['status']}
"""


def run_md(info: dict) -> str:
    """runs/Rxxxx.md。"""
    exp = info["experiment_id"] or "（无，快速检查点）"
    cap = info["initial_capital"]
    cap_line = f"- Initial Capital: {cap:,.0f}" if cap is not None else "- Initial Capital: —"
    freq = info["frequency"] or "—"
    n_trades = info["n_trades"] if info["n_trades"] is not None else "—"
    if info["benchmark"]:
        bench = f"- 基准: {info['benchmark']}"
        if info["benchmark_return"] is not None:
            bench += f"（基准收益 {info['benchmark_return']}）"
    else:
        bench = "- 基准: —"
    regime = info["regime"] or "—"
    params = info["parameters_json"]
    params_block = f"```yaml\n{params}\n```" if params else "（无）"
    status_lines = [f"## Status\n{info['status']}"]
    if info["error_type"]:
        status_lines.append(f"- Error Type: {info['error_type']}")
    if info["error_message"]:
        status_lines.append(f"- Error Message: {info['error_message']}")
    table = "\n".join(
        f"| {m['metric_name']} | {m['metric_value']} | {m['metric_source']} |"
        for m in info["metrics"]
    ) or "（无指标）"
    src = info["source_log_path"] or "见 `聚宽回测结果及运行日志.md` 对应条目（按日期或锚点定位，不在此重复粘贴）"
    notes = info["notes"] or "（无）"
    return f"""# {info['run_id']}

## Strategy / Experiment
- Strategy: {info['strategy_id']}
- Experiment: {exp}

## Backtest 设置
- Start: {info['start_date']}
- End: {info['end_date']}
{cap_line}
- Frequency: {freq}
- 调仓次数: {n_trades}
{bench}
- 市场状态: {regime}

## Parameters
{params_block}

{chr(10).join(status_lines)}

## Metrics

| 指标 | 数值 | 来源 |
|---|---|---|
{table}

## 原始数据位置
{src}

## Notes
{notes}
"""


def study_md(info: dict) -> str:
    """studies/STxxxx.md；"## 结论"由关联 Analysis 填充（reports 层负责）。"""
    try:
        design_pretty = json.dumps(json.loads(info["design_json"]), ensure_ascii=False, indent=2)
    except Exception:
        design_pretty = info["design_json"]
    run_rows = "\n".join(
        f"| {r['run_id']} | {r['group_name'] or '—'} | {r['role'] or '—'} | {r['partition'] or '—'} | "
        f"{_fmt(r['metrics'].get('total_return'))} | {_fmt(r['metrics'].get('max_drawdown'))} | "
        f"{_fmt(r['metrics'].get('sharpe'))} |"
        for r in info["runs"]
    ) or "（无 Run）"
    conclusion = info.get("conclusion") or "（留空，由 Analysis 填写）"
    return f"""# {info['study_id']}

## Experiment / 类型
- Experiment: {info['experiment_id']}
- 类型: {info['study_type']}

## 设计（预登记，禁止事后修改）
```yaml
{design_pretty}
```

## Runs
| Run | 分组 | 角色 | 分区 | 收益 | 最大回撤 | Sharpe |
|---|---|---|---|---|---|---|
{run_rows}

## 结论
{conclusion}
"""


def analysis_md(info: dict) -> str:
    """analyses/Axxxx.md；过拟合诊断行来自 analyze_study（reports 层注入）。"""
    signals = "\n".join(info["diagnostics"]) or "（无）"
    conf = f"{info['confidence']}" if info["confidence"] is not None else "—"
    return f"""# {info['analysis_id']}

## Study
{info['study_id']}

## 结论
{info['conclusion'] or '（未填写）'}

## 决策
- Decision: {info['decision']}
- Evidence Level: {info['evidence_level']}
- Confidence: {conf}

## 过拟合诊断
Overfitting Signals:
{signals}
"""


def _fmt(value) -> str:
    """数值格式化：None → —，其余原样输出。"""
    return "—" if value is None else str(value)
```

`小市值/research/reports.py`:
```python
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


def write_experiment_report(conn: sqlite3.Connection, experiment_id: str,
                            root: Path | None = None) -> Path:
    info = experiment.show_experiment(conn, experiment_id)
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_analysis.py -v`
Expected: 15 passed（Task 8 的 10 个 + 报告生成 5 个）

- [ ] **Step 5: 提交**

```bash
git add 小市值/research/templates.py 小市值/research/reports.py 小市值/research/tests/test_analysis.py
git commit -m "feat(research): templates/reports 归档 Markdown 单向生成（5 类报告 + Study 结论回填）"
```

---
### Task 10: cli.py + README（十条宪法）

**Files:**
- Create: `小市值/research/cli.py`
- Modify: `小市值/research/__main__.py`（接线 cli.main）
- Create: `小市值/research/README.md`（十条宪法，spec §12）
- Modify: `小市值/research/tests/test_analysis.py`（追加 CLI 冒烟测试——保持 8 个测试文件）

**Interfaces:**
- Consumes: `db.connect/init_db`、`strategy.*`、`experiment.*`、`run.*`、`study.*`、`analysis.*`、`reports.*`（Task 2/4/5/6/7/8/9）
- Produces:
  - `cli.main(argv: list[str] | None = None) -> int`（argparse 子命令分发；RuntimeError → stderr 打印"错误: ..."并返回 1；成功返回 0）
  - `cli._get_conn()`（模块级间接层，测试 monkeypatch 注入临时 db，避免触碰真实 registry.db）
  - `cli.REPORT_ROOT: Path | None`（报告输出根目录，测试注入用；None 时用 reports 默认 小市值/research/）
  - 子命令全集（spec §8）：`init` / `strategy create|show|tree` / `hypothesis create` / `experiment create|show|list` / `promote` / `run create|add-metric|show` / `study create|add-run|batch-add-runs|show` / `analyze` / `analysis create`
  - `小市值/research/README.md`：十条宪法（spec §12 原文）+ 安装说明 + 单位约定

- [ ] **Step 1: 写失败测试（追加到 test_analysis.py 末尾）**

`小市值/research/tests/test_analysis.py` 追加：
```python
# ==================== CLI 冒烟测试（Task 10，spec §8） ====================
from research import cli  # 顶部 import 区追加


def _cli_env(tmp_path, monkeypatch):
    """构造临时 db 并注入 cli：_get_conn 返回该连接，报告输出到 tmp 目录。"""
    conn = db.connect(tmp_path / "t.db")
    db.init_db(conn)
    conn.execute(
        "INSERT INTO strategies (strategy_id, name, source_path, git_commit_hash, file_blob_hash, created_at) "
        "VALUES ('S0001', 's', 'p', 'h', 'b', '2026-01-01')")
    conn.commit()
    monkeypatch.setattr(cli, "_get_conn", lambda: conn)
    monkeypatch.setattr(cli, "REPORT_ROOT", tmp_path / "out")
    return conn


def test_cli_init_creates_db(tmp_path, monkeypatch):
    conn = _cli_env(tmp_path, monkeypatch)
    assert cli.main(["init"]) == 0  # init 幂等，不报错
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    assert {r["name"] for r in rows} >= {"strategies", "runs", "studies", "analyses"}


def test_cli_run_create_and_show(tmp_path, monkeypatch, capsys):
    conn = _cli_env(tmp_path, monkeypatch)
    code = cli.main(["run", "create", "--strategy", "S0001",
                     "--start", "2020-01-01", "--end", "2021-01-01",
                     "--status", "SUCCESS",
                     "--metric", "sharpe=1.52", "--metric", "total_return=0.213"])
    assert code == 0
    assert "R0001" in capsys.readouterr().out
    row = conn.execute("SELECT metric_value FROM metrics WHERE metric_name='sharpe'").fetchone()
    assert row["metric_value"] == 1.52
    assert cli.main(["run", "show", "R0001"]) == 0


def test_cli_missing_entity_returns_1(tmp_path, monkeypatch, capsys):
    _cli_env(tmp_path, monkeypatch)
    assert cli.main(["run", "show", "R9999"]) == 1
    assert "不存在" in capsys.readouterr().err


def test_cli_analyze_and_analysis_flow(tmp_path, monkeypatch, capsys):
    conn = _cli_env(tmp_path, monkeypatch)
    conn.execute(
        "INSERT INTO experiments (experiment_id, baseline_strategy_id, title, change_scope, validation_tier, created_at) "
        "VALUES ('E0001', 'S0001', 't', 'MICRO', 'V2', '2026-01-01')")
    conn.execute(
        "INSERT INTO studies (study_id, experiment_id, study_type, name, design_json, created_at) "
        "VALUES ('ST0001', 'E0001', 'ROLLING', '滚动', '{\"windows\": []}', '2026-01-01')")
    for rid, role, part, val in [("R0001", "candidate", "is", 0.2), ("R0002", "candidate", "oos", 0.1)]:
        conn.execute(
            "INSERT INTO runs (run_id, strategy_id, start_date, end_date, status) "
            "VALUES (?, 'S0001', '2020-01-01', '2021-01-01', 'SUCCESS')", (rid,))
        conn.execute(
            "INSERT INTO metrics (run_id, metric_name, metric_value, metric_source) "
            "VALUES (?, 'total_return', ?, 'joinquant_pasted')", (rid, val))
        conn.execute(
            "INSERT INTO study_runs (study_id, run_id, group_name, role, partition) "
            "VALUES ('ST0001', ?, 'g1', ?, ?)", (rid, role, part))
    conn.commit()
    assert cli.main(["analyze", "ST0001"]) == 0
    assert "Overfitting Signals" in capsys.readouterr().out
    code = cli.main(["analysis", "create", "--study", "ST0001", "--decision", "ACCEPT",
                     "--evidence", "E2", "--conclusion", "方向一致"])
    assert code == 0
    assert "A0001" in capsys.readouterr().out
    # analysis create 一并生成 analyses/A0001.md 与回填 studies/ST0001.md 结论（spec Phase 7）
    assert (tmp_path / "out" / "analyses" / "A0001.md").exists()
    study_md = (tmp_path / "out" / "studies" / "ST0001.md").read_text(encoding="utf-8")
    assert "方向一致" in study_md
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest 小市值/research/tests/test_analysis.py -v`
Expected: FAIL — ModuleNotFoundError: No module named 'research.cli'

- [ ] **Step 3: 写实现**

`小市值/research/cli.py`:
```python
"""python -m research 命令行入口（全部非交互：flag 或 JSON payload，spec §8）。

主要操作者是 AI 助手；所有命令从仓库根 D:\\量化\\聚宽 执行。
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

from research import analysis, db, experiment, reports, run, strategy, study

REPORT_ROOT: Path | None = None  # 报告输出根目录（测试注入用；None 走 reports 默认）


def _get_conn() -> sqlite3.Connection:
    """连接间接层：默认 registry.db，测试 monkeypatch 注入临时 db。"""
    return db.connect()


def cmd_init(_args: argparse.Namespace) -> int:
    conn = _get_conn()
    db.init_db(conn)
    print(f"已初始化数据库: {db.PACKAGE_DIR / 'registry.db'}")
    return 0


def cmd_strategy_create(args: argparse.Namespace) -> int:
    conn = _get_conn()
    result = strategy.create_strategy(
        conn, parent_id=args.parent, name=args.name,
        change_summary=args.summary, experiment_id=args.experiment,
        quick=args.quick,
    )
    if result["warning"]:
        print(result["warning"])
    print(f"已创建 Strategy {result['strategy_id']}")
    reports.write_strategy_report(conn, result["strategy_id"], REPORT_ROOT)
    return 0


def cmd_strategy_show(args: argparse.Namespace) -> int:
    conn = _get_conn()
    info = strategy.show_strategy(conn, args.strategy_id)
    print(f"{info['strategy_id']}  Parent: {info['parent_strategy_id']}")
    print(f"  名称: {info['name']}")
    print(f"  Git Commit: {info['git_commit_hash']}")
    print(f"  变更: {info['change_summary']}")
    print(f"  关联实验: {', '.join(info['experiments']) or '无'}")
    print(f"  关联回测: {', '.join(info['runs']) or '无'}")
    return 0


def cmd_strategy_tree(args: argparse.Namespace) -> int:
    conn = _get_conn()
    for sid, depth in strategy.strategy_tree(conn, args.root_id):
        print("  " * depth + sid)
    return 0


def cmd_hypothesis_create(args: argparse.Namespace) -> int:
    conn = _get_conn()
    hid = experiment.create_hypothesis(conn, title=args.title,
                                       description=args.description,
                                       expected_effect=args.expected)
    print(f"已创建 Hypothesis {hid}")
    return 0


def cmd_experiment_create(args: argparse.Namespace) -> int:
    conn = _get_conn()
    eid = experiment.create_experiment(
        conn, baseline_id=args.baseline, title=args.title,
        change_scope=args.scope, validation_tier=args.tier,
        hypothesis_id=args.hypothesis, candidate_id=args.candidate,
        description=args.description, n_trials=args.n_trials,
    )
    print(f"已创建 Experiment {eid}")
    reports.write_experiment_report(conn, eid, REPORT_ROOT)
    return 0


def cmd_experiment_show(args: argparse.Namespace) -> int:
    conn = _get_conn()
    info = experiment.show_experiment(conn, args.experiment_id)
    print(f"{info['experiment_id']}  {info['title']}")
    print(f"  Baseline: {info['baseline_strategy_id']}  Candidate: {info['candidate_strategy_id'] or '（未回填）'}")
    print(f"  Scope: {info['change_scope']}  Tier: {info['validation_tier']}  n_trials: {info['n_trials']}")
    print(f"  Status: {info['status']}")
    print(f"  关联 Study: {', '.join(info['studies']) or '无'}")
    return 0


def cmd_experiment_list(args: argparse.Namespace) -> int:
    conn = _get_conn()
    for info in experiment.list_experiments(conn, status=args.status):
        print(f"{info['experiment_id']}  {info['title']}  [{info['status']}]")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    conn = _get_conn()
    eid = experiment.promote(
        conn, strategy_id=args.strategy, baseline_id=args.baseline,
        title=args.title, change_scope=args.scope, validation_tier=args.tier,
        hypothesis_id=args.hypothesis, description=args.description,
        n_trials=args.n_trials,
    )
    print(f"已创建 Experiment {eid}（candidate={args.strategy}）")
    reports.write_experiment_report(conn, eid, REPORT_ROOT)
    return 0


def cmd_run_create(args: argparse.Namespace) -> int:
    conn = _get_conn()
    if args.from_json:
        data = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        rid = run.create_run_from_json(conn, data)
    else:
        metrics = []
        for kv in args.metric or []:
            name, _, value = kv.partition("=")
            metrics.append((name, float(value), "joinquant_pasted"))
        rid = run.create_run(
            conn, strategy_id=args.strategy, start_date=args.start,
            end_date=args.end, status=args.status,
            experiment_id=args.experiment, initial_capital=args.capital,
            frequency=args.frequency,
            parameters=json.loads(args.parameters) if args.parameters else None,
            error_type=args.error_type, error_message=args.error_message,
            n_trades=args.n_trades, benchmark=args.benchmark,
            benchmark_return=args.benchmark_return, regime=args.regime,
            source_log_path=args.source_log_path, notes=args.notes,
            metrics=metrics,
        )
    print(f"已创建 Run {rid}")
    reports.write_run_report(conn, rid, REPORT_ROOT)
    return 0


def cmd_run_add_metric(args: argparse.Namespace) -> int:
    conn = _get_conn()
    run.add_metric(conn, args.run_id, args.name, args.value, args.source)
    print(f"已写入指标 {args.run_id}.{args.name}")
    return 0


def cmd_run_show(args: argparse.Namespace) -> int:
    conn = _get_conn()
    info = run.show_run(conn, args.run_id)
    print(f"{info['run_id']}  Strategy: {info['strategy_id']}  Status: {info['status']}")
    print(f"  区间: {info['start_date']} ~ {info['end_date']}")
    for m in info["metrics"]:
        print(f"  {m['metric_name']} = {m['metric_value']} [{m['metric_source']}]")
    return 0


def cmd_study_create(args: argparse.Namespace) -> int:
    conn = _get_conn()
    design = json.loads(Path(args.design).read_text(encoding="utf-8"))
    stid = study.create_study(conn, experiment_id=args.experiment,
                              study_type=args.type, name=args.name,
                              design_json=design, description=args.description)
    print(f"已创建 Study {stid}")
    reports.write_study_report(conn, stid, REPORT_ROOT)
    return 0


def cmd_study_add_run(args: argparse.Namespace) -> int:
    conn = _get_conn()
    study.add_run(conn, args.study_id, args.run, group_name=args.group,
                  role=args.role, partition=args.partition)
    print(f"已挂入 {args.run} → {args.study_id}")
    return 0


def cmd_study_batch_add_runs(args: argparse.Namespace) -> int:
    conn = _get_conn()
    payload = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    created = study.batch_add_runs(conn, args.study_id, payload)
    print(f"已创建并挂入: {', '.join(created)}")
    reports.write_study_report(conn, args.study_id, REPORT_ROOT)
    return 0


def cmd_study_show(args: argparse.Namespace) -> int:
    conn = _get_conn()
    info = study.show_study(conn, args.study_id)
    print(f"{info['study_id']}  {info['name']}  [{info['study_type']}]")
    for r in info["runs"]:
        print(f"  {r['run_id']}  group={r['group_name'] or '—'}  role={r['role'] or '—'}  "
              f"partition={r['partition'] or '—'}  {r['strategy_id']}  {r['start_date']}~{r['end_date']}  {r['status']}")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    conn = _get_conn()
    result = analysis.analyze_study(conn, args.study_id)
    print(f"Study {args.study_id} 统计（主指标: {result['primary_metric'] or '无'}）:")
    for s in result["statistics"]:
        print(f"  {s['metric']}: n={s['n']} mean={s['mean']} median={s['median']} "
              f"std={s['std']} min={s['min']} max={s['max']} "
              f"positive_ratio={s['positive_ratio']} baseline_delta={s['baseline_delta']}")
    print("Overfitting Signals:")
    for line in result["diagnostics"]:
        print(f"  {line}")
    return 0


def cmd_analysis_create(args: argparse.Namespace) -> int:
    conn = _get_conn()
    aid = analysis.create_analysis(conn, study_id=args.study, decision=args.decision,
                                   evidence_level=args.evidence,
                                   conclusion=args.conclusion, confidence=args.confidence)
    # spec Phase 7：analysis create 时一并生成 analyses/*.md，并回填 studies/*.md 结论章节
    reports.write_analysis_report(conn, aid, REPORT_ROOT)
    reports.write_study_report(conn, args.study, REPORT_ROOT)
    print(f"已创建 Analysis {aid}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research", description="小市值策略研究登记系统 v1")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="初始化数据库（幂等）")
    p_init.set_defaults(func=cmd_init)

    p_sc = sub.add_parser("strategy", help="策略版本管理")
    sc_sub = p_sc.add_subparsers(dest="subcommand", required=True)
    p_screate = sc_sub.add_parser("create", help="登记策略版本（执行前要求工作区干净）")
    p_screate.add_argument("--parent", help="父 Strategy ID（不传即根版本）")
    p_screate.add_argument("--experiment", help="已有 Experiment ID，创建后回填 candidate")
    p_screate.add_argument("--summary", help="变更摘要（默认取 git commit message）")
    p_screate.add_argument("--name", help="策略名（默认取 summary 前 40 字）")
    p_screate.add_argument("--quick", action="store_true", help="快速检查点（禁止关联 Experiment）")
    p_screate.set_defaults(func=cmd_strategy_create)
    p_sshow = sc_sub.add_parser("show")
    p_sshow.add_argument("strategy_id")
    p_sshow.set_defaults(func=cmd_strategy_show)
    p_stree = sc_sub.add_parser("tree")
    p_stree.add_argument("root_id")
    p_stree.set_defaults(func=cmd_strategy_tree)

    p_hc = sub.add_parser("hypothesis", help="研究假设")
    hc_sub = p_hc.add_subparsers(dest="subcommand", required=True)
    p_hcreate = hc_sub.add_parser("create")
    p_hcreate.add_argument("--title", required=True)
    p_hcreate.add_argument("--description", required=True)
    p_hcreate.add_argument("--expected", help="预期效果")
    p_hcreate.set_defaults(func=cmd_hypothesis_create)

    p_ec = sub.add_parser("experiment", help="正式实验")
    ec_sub = p_ec.add_subparsers(dest="subcommand", required=True)
    p_ecreate = ec_sub.add_parser("create")
    p_ecreate.add_argument("--hypothesis", help="Hypothesis ID")
    p_ecreate.add_argument("--baseline", required=True, help="基线 Strategy ID")
    p_ecreate.add_argument("--candidate", help="候选 Strategy ID（可留空稍后回填）")
    p_ecreate.add_argument("--title", required=True)
    p_ecreate.add_argument("--description")
    p_ecreate.add_argument("--scope", required=True, choices=sorted(experiment.VALID_SCOPES))
    p_ecreate.add_argument("--tier", required=True, choices=sorted(experiment.VALID_TIERS))
    p_ecreate.add_argument("--n-trials", type=int, default=1)
    p_ecreate.set_defaults(func=cmd_experiment_create)
    p_eshow = ec_sub.add_parser("show")
    p_eshow.add_argument("experiment_id")
    p_eshow.set_defaults(func=cmd_experiment_show)
    p_elist = ec_sub.add_parser("list")
    p_elist.add_argument("--status", help="按状态过滤，如 RUNNING")
    p_elist.set_defaults(func=cmd_experiment_list)

    p_promote = sub.add_parser("promote", help="快速检查点 Strategy → 正式实验")
    p_promote.add_argument("--strategy", required=True, help="快速检查点 Strategy ID")
    p_promote.add_argument("--hypothesis", help="Hypothesis ID")
    p_promote.add_argument("--baseline", required=True, help="基线 Strategy ID")
    p_promote.add_argument("--title", required=True)
    p_promote.add_argument("--description")
    p_promote.add_argument("--scope", required=True, choices=sorted(experiment.VALID_SCOPES))
    p_promote.add_argument("--tier", required=True, choices=sorted(experiment.VALID_TIERS))
    p_promote.add_argument("--n-trials", type=int, default=1)
    p_promote.set_defaults(func=cmd_promote)

    p_rc = sub.add_parser("run", help="聚宽回测登记")
    rc_sub = p_rc.add_subparsers(dest="subcommand", required=True)
    p_rcreate = rc_sub.add_parser("create")
    p_rcreate.add_argument("--strategy", help="Strategy ID（--from-json 时忽略）")
    p_rcreate.add_argument("--experiment", help="Experiment ID（可省略）")
    p_rcreate.add_argument("--start", help="回测开始日期 YYYY-MM-DD")
    p_rcreate.add_argument("--end", help="回测结束日期 YYYY-MM-DD")
    p_rcreate.add_argument("--capital", type=float, help="初始资金")
    p_rcreate.add_argument("--status", choices=sorted(run.VALID_STATUS), default="SUCCESS")
    p_rcreate.add_argument("--frequency")
    p_rcreate.add_argument("--parameters", help="参数字典 JSON 字符串")
    p_rcreate.add_argument("--error-type")
    p_rcreate.add_argument("--error-message")
    p_rcreate.add_argument("--n-trades", type=int, help="调仓次数")
    p_rcreate.add_argument("--benchmark", help="基准指数代码，如 000905.XSHG")
    p_rcreate.add_argument("--benchmark-return", type=float)
    p_rcreate.add_argument("--regime", choices=sorted(run.VALID_REGIMES))
    p_rcreate.add_argument("--source-log-path")
    p_rcreate.add_argument("--notes")
    p_rcreate.add_argument("--metric", action="append", help="指标 k=v（可重复），来源默认 joinquant_pasted")
    p_rcreate.add_argument("--from-json", help="JSON payload 文件路径（spec §8 形态）")
    p_rcreate.set_defaults(func=cmd_run_create)
    p_radd = rc_sub.add_parser("add-metric")
    p_radd.add_argument("run_id")
    p_radd.add_argument("--name", required=True)
    p_radd.add_argument("--value", type=float, required=True)
    p_radd.add_argument("--source", choices=sorted(run.VALID_SOURCES), default="joinquant_pasted")
    p_radd.set_defaults(func=cmd_run_add_metric)
    p_rshow = rc_sub.add_parser("show")
    p_rshow.add_argument("run_id")
    p_rshow.set_defaults(func=cmd_run_show)

    p_st = sub.add_parser("study", help="Study 预登记设计")
    st_sub = p_st.add_subparsers(dest="subcommand", required=True)
    p_stcreate = st_sub.add_parser("create")
    p_stcreate.add_argument("--experiment", required=True)
    p_stcreate.add_argument("--type", required=True, choices=sorted(study.VALID_TYPES))
    p_stcreate.add_argument("--name", required=True)
    p_stcreate.add_argument("--design", required=True, help="design_json 文件路径（JSON）")
    p_stcreate.add_argument("--description")
    p_stcreate.set_defaults(func=cmd_study_create)
    p_stadd = st_sub.add_parser("add-run")
    p_stadd.add_argument("study_id")
    p_stadd.add_argument("--run", required=True)
    p_stadd.add_argument("--group")
    p_stadd.add_argument("--role", choices=sorted(study.VALID_ROLES))
    p_stadd.add_argument("--partition", choices=sorted(study.VALID_PARTITIONS))
    p_stadd.set_defaults(func=cmd_study_add_run)
    p_stbatch = st_sub.add_parser("batch-add-runs")
    p_stbatch.add_argument("study_id")
    p_stbatch.add_argument("--from-json", required=True, help="rolling_runs.json 文件路径")
    p_stbatch.set_defaults(func=cmd_study_batch_add_runs)
    p_stshow = st_sub.add_parser("show")
    p_stshow.add_argument("study_id")
    p_stshow.set_defaults(func=cmd_study_show)

    p_an = sub.add_parser("analyze", help="输出统计 + 5 项过拟合诊断")
    p_an.add_argument("study_id")
    p_an.set_defaults(func=cmd_analyze)

    p_ac = sub.add_parser("analysis", help="Analysis 结论登记")
    ac_sub = p_ac.add_subparsers(dest="subcommand", required=True)
    p_acreate = ac_sub.add_parser("create")
    p_acreate.add_argument("--study", required=True)
    p_acreate.add_argument("--decision", required=True, choices=sorted(analysis.VALID_DECISIONS))
    p_acreate.add_argument("--evidence", required=True, choices=sorted(analysis.VALID_EVIDENCE))
    p_acreate.add_argument("--conclusion")
    p_acreate.add_argument("--confidence", type=float)
    p_acreate.set_defaults(func=cmd_analysis_create)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

`小市值/research/__main__.py`（整体替换占位版）:
```python
"""python -m research 入口。"""
import sys

from research import cli


def main() -> int:
    return cli.main()


if __name__ == "__main__":
    sys.exit(main())
```

`小市值/research/README.md`（十条宪法，spec §12 原文）:
```markdown
# Research Registry v1（可追溯回测记录系统）

小市值策略研究登记系统：用 SQLite（`research/registry.db`）+ 归档 Markdown 记录每次策略代码改动与对应聚宽回测结果，支撑改动有效性分析与过拟合防护。

## 安装（一次性）

```powershell
pip install -e 小市值
```

安装后从仓库根 `D:\量化\聚宽` 执行 `python -m research ...`。

## 十条宪法

1. `小市值策略代码.md` 是唯一工作源码；每次登记 Strategy 前必须先 `git commit` 该文件，确保 `git_commit_hash` 对应硬盘实际内容。
2. Strategy Version 表示代码状态，不表示成功与否；快速检查点与正式实验版本都是合法 Strategy，用是否挂载 Experiment 区分。
3. Experiment 表示一个研究假设；`change_scope` 描述代码改动范围，`validation_tier` 描述需要多严格的验证，两者不必然相关。
4. 一个 Experiment 可以包含多个代码修改，但必须共同服务于同一个核心假设；独立假设必须拆成不同 Experiment。
5. Run 表示一次实际聚宽回测，必须允许 FAILED 和 INCOMPLETE，不得删除，包括不成功和数据不全的记录。
6. Metric 与 Run 结构分离存储；每条 Metric 必须标注来源，二手转述的数字不得标记为 `joinquant_pasted`。
7. Study 的 `design_json` 必须在看到 Run 结果之前登记，不允许事后调整分组/窗口配合已看到的结果。
8. Study 与 Run 是多对多关系；Strategy、Experiment、Run、Study、Analysis 全部可互相追溯，Strategy 谱系以 git commit 为准，不重复发明 diff 机制。
9. Analysis 的 decision 必须区分"结果事实"和"研究判断"：单次漂亮回测不能直接宣布策略有效，`ARCHITECTURAL` 级别改动在 Ablation/Rolling 类 Study 完成前不得给出 ACCEPT。
10. 一切 CLI 命令必须支持非交互（flag 或 JSON payload）调用，因为主要操作者是 AI 助手。

## 单位约定

- `metrics.metric_value` 一律存小数（0.213 而非 21.3%）；百分比先除 100 再存
- 非数值信息（如最大回撤区间 "2026/03/03,2026/06/30"）写入 `runs.notes` 或对应归档 md
- 约定指标名完整清单见 `schema.sql` 注释（spec 决策 D4）
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest 小市值/research/tests/test_analysis.py -v`
Expected: 19 passed（Task 8 的 10 个 + 报告生成 5 个 + CLI 4 个）

- [ ] **Step 5: 提交**

```bash
git add 小市值/research/cli.py 小市值/research/__main__.py 小市值/research/README.md 小市值/research/tests/test_analysis.py
git commit -m "feat(research): cli.py 全子命令接线（非交互）+ README 十条宪法"
```

---
### Task 11: AGENTS.md 联动 + 端到端验收

**Files:**
- Modify: `AGENTS.md`（仓库根，spec §11 的 5 项更新）
- 无新测试文件（验收按 spec §13 的 9 条在真实仓库执行）

**Interfaces:**
- Consumes: 全部模块（Task 1-10 产出）
- Produces: 更新后的 `AGENTS.md`；`小市值/research/registry.db` 纳入版本控制；5 类归档 Markdown 目录

- [ ] **Step 1: 更新 AGENTS.md（spec §11 的 5 项）**

在 `AGENTS.md` 中做以下 5 处修改（保留原有内容，只增改）：

1. **"目录结构"一节**：在 `小市值/` 条目下补充：
   ```markdown
   - `小市值/research/` — 研究登记系统（Research Registry v1）：`registry.db`（SQLite 数据源头，纳入 git 提交）、`cli.py`（`python -m research` 全子命令）、`schema.sql`、`strategies|experiments|runs|studies|analyses/`（归档 Markdown，单向生成，禁止手工编辑）、`README.md`（十条宪法）
   ```

2. **"小市值策略"一节**：工作流描述改为引用 README 并说明两级工作流：
   ```markdown
   - 登记纪律见 `小市值/research/README.md`（十条宪法）。两级工作流：快速检查点（`strategy create --quick`，摩擦≈commit message）与正式实验（Hypothesis → Experiment → Study → Analysis 完整链条）；快速检查点方向有戏时用 `promote` 升级为正式实验
   ```

3. **"常用命令"一节**：补充安装步骤与命令系列：
   ```markdown
   # 研究登记系统（一次性安装）
   pip install -e 小市值

   # 常用命令（全部从仓库根执行）
   python -m research init
   python -m research strategy create --parent S0023 --summary "..."        # 登记策略版本（先 commit 代码文件）
   python -m research strategy create --quick --parent S0023 --summary "..." # 快速检查点
   python -m research strategy show S0024 / strategy tree S0001
   python -m research hypothesis create --title "..." --description "..." --expected "..."
   python -m research experiment create --hypothesis H0010 --baseline S0020 --title "..." --scope MICRO --tier V2
   python -m research run create --strategy S0024 --start 2020-01-01 --end 2021-01-01 --status SUCCESS --metric sharpe=1.52
   python -m research run create --from-json run.json
   python -m research study create --experiment E0008 --type ROLLING --name "..." --design design.json
   python -m research study batch-add-runs ST0012 --from-json rolling_runs.json
   python -m research analyze ST0012
   python -m research analysis create --study ST0012 --decision ACCEPT --evidence E2 --conclusion "..."
   python -m research promote --strategy S0024 --hypothesis H0012 --baseline S0023 --title "..." --scope MICRO --tier V2
   ```

4. **"小市值策略"一节**：补操作前提：
   ```markdown
   - 登记 Strategy 前必须先 `git commit` 该代码文件（`小市值/小市值策略代码.md`），`git_commit_hash` 必须对应硬盘实际内容；工作区有未提交改动时 `strategy create` 会报错拦截
   ```

5. **"小市值策略"一节**：保留"评价策略效果只准引用聚宽回测结果及运行日志.md 内容"规则，并说明延续方式：
   ```markdown
   - "评价策略效果只准引用聚宽回测结果及运行日志.md 内容"规则在新系统延续：登记 Run 时每条指标必须标注 `metric_source`（joinquant_pasted / derived_local / manual_estimate / secondhand_mention），只有 `joinquant_pasted` 可作为 Analysis 证据引用，二手转述（如优化方向.md 提及的数值）必须标 `secondhand_mention` 且不得用于 Analysis 结论
   ```

- [ ] **Step 2: 全量测试**

Run: `python -m pytest 小市值/research/tests/ -v`
Expected: 全部通过（8 个测试文件：test_db / test_ids / test_git_meta / test_strategy / test_experiment / test_run / test_study / test_analysis，spec §13 验收 1）

- [ ] **Step 3: 端到端验收（spec §13 的 9 条，按顺序执行）**

前置：确认 `小市值/小市值策略代码.md` 已提交（`strategy create` 要求工作区干净）：
```powershell
git -c core.quotepath=false status --porcelain -- 小市值/小市值策略代码.md
# 若输出非空：先 git add 小市值/小市值策略代码.md 再 git commit -m "..."，然后继续
```

**验收 2（CLI 全命令链路，注意顺序：先根 Strategy 才能建 Experiment）**：

```powershell
# ① 初始化（验收 9：从仓库根可执行）
python -m research init
# 预期: 已初始化数据库: ...\小市值\research\registry.db

# ② 根版本 Strategy（无 --parent）
python -m research strategy create --summary "初始策略基线"
# 预期: 已创建 Strategy S0001

# ③ 快速检查点
python -m research strategy create --quick --parent S0001 --summary "试一下调仓改10天"
# 预期: 已创建 Strategy S0002

# ④ Hypothesis
python -m research hypothesis create --title "调仓周期假设" --description "延长调仓周期降低换手与冲击成本" --expected "Max Drawdown 下降"
# 预期: 已创建 Hypothesis H0001

# ⑤ Experiment（baseline 指向根 Strategy）
python -m research experiment create --hypothesis H0001 --baseline S0001 --title "调仓周期延长" --scope MICRO --tier V2
# 预期: 已创建 Experiment E0001

# ⑥ run create（flag 形式）
python -m research run create --strategy S0002 --start 2020-01-01 --end 2021-01-01 --capital 1000000 --status SUCCESS --n-trades 12 --benchmark 000905.XSHG --benchmark-return 0.102 --regime sideways --metric total_return=0.213 --metric sharpe=1.52 --metric max_drawdown=0.174
# 预期: 已创建 Run R0001

# ⑦ run create（--from-json 形式；JSON 文件放系统临时目录，不污染仓库）
@'
{"strategy": "S0002", "start": "2020-01-01", "end": "2021-01-01", "capital": 1000000, "status": "SUCCESS", "n_trades": 12, "benchmark": "000905.XSHG", "benchmark_return": 0.102, "regime": "sideways", "metrics": {"annual_return": 0.18, "sharpe": 1.3, "max_drawdown": 0.15}}
'@ | Set-Content -Path "$env:TEMP\rr_run.json" -Encoding UTF8
python -m research run create --from-json "$env:TEMP\rr_run.json"
# 预期: 已创建 Run R0002

# ⑧ study create（design_json 预登记）
@'
{"type": "ROLLING", "windows": [{"start": "2020-01-01", "end": "2021-01-01", "partition": "is"}]}
'@ | Set-Content -Path "$env:TEMP\rr_design.json" -Encoding UTF8
python -m research study create --experiment E0001 --type ROLLING --name "5窗口滚动验证" --design "$env:TEMP\rr_design.json"
# 预期: 已创建 Study ST0001

# ⑨ study batch-add-runs（一次建 2 个 Run + metrics + 挂入 Study）
@'
[
  {"strategy": "S0002", "start": "2020-01-01", "end": "2021-01-01", "capital": 1000000, "status": "SUCCESS", "group": "2020-2021", "role": "candidate", "partition": "is", "metrics": {"total_return": 0.213, "sharpe": 1.52, "max_drawdown": 0.174}},
  {"strategy": "S0001", "start": "2020-01-01", "end": "2021-01-01", "capital": 1000000, "status": "SUCCESS", "group": "2020-2021", "role": "baseline", "partition": "is", "metrics": {"total_return": 0.140, "sharpe": 1.10, "max_drawdown": 0.190}}
]
'@ | Set-Content -Path "$env:TEMP\rr_rolling.json" -Encoding UTF8
python -m research study batch-add-runs ST0001 --from-json "$env:TEMP\rr_rolling.json"
# 预期: 已创建并挂入: R0003, R0004

# ⑩ analyze（统计 + 5 项过拟合诊断）
python -m research analyze ST0001
# 预期: 输出各指标统计行 + "Overfitting Signals:" + [OK]/[WARN]/[N/A] 行

# ⑪ analysis create（同时生成 analyses/A0001.md 并回填 studies/ST0001.md 结论）
python -m research analysis create --study ST0001 --decision ACCEPT --evidence E2 --conclusion "候选策略方向一致，IS-OOS 差距可接受"
# 预期: 已创建 Analysis A0001

# ⑫ promote（快速检查点 S0002 → 正式实验）
python -m research promote --strategy S0002 --hypothesis H0001 --baseline S0001 --title "调仓周期延长（升级）" --scope MICRO --tier V2
# 预期: 已创建 Experiment E0002（candidate=S0002）
```

**验收 3（5 类 Markdown 生成且与 db 一致）**：
```powershell
Get-ChildItem 小市值\research\strategies, 小市值\research\experiments, 小市值\research\runs, 小市值\research\studies, 小市值\research\analyses -Filter *.md
# 预期: 每类目录至少 1 个文件（S0001/S0002、E0001/E0002、R0001~R0004、ST0001、A0001）
Get-Content 小市值\research\studies\ST0001.md
# 预期: "## 结论" 章节含 "候选策略方向一致，IS-OOS 差距可接受"（由 Analysis 填充）
Get-Content 小市值\research\analyses\A0001.md
# 预期: 含 "Decision: ACCEPT"、"Evidence Level: E2"、"Overfitting Signals:"
```

**验收 4（未提交改动拦截）**：
```powershell
Add-Content -Path 小市值\小市值策略代码.md -Value "# 临时改动（验收用）" -Encoding UTF8
python -m research strategy create --parent S0001 --summary "不应成功"
# 预期: 错误: 小市值/小市值策略代码.md 有未提交改动，请先 git commit 再登记 Strategy（退出码 1）
git restore 小市值/小市值策略代码.md
```

**验收 5（blob 相同警告）**：
```powershell
python -m research strategy create --parent S0001 --summary "内容未变重登记"
# 预期: 输出 "警告: file_blob_hash 与最新 Strategy 相同..." 且仍创建成功（S0003）
```

**验收 6（FAILED/INCOMPLETE Run + metric_source 枚举强制）**：
```powershell
python -m research run create --strategy S0002 --start 2020-01-01 --end 2021-01-01 --status FAILED --error-type SecurityNotExist --error-message "代码或后缀错误"
# 预期: 已创建 Run R0005（FAILED 必须带 error_type，缺失时报错）
python -m research run add-metric R0001 --name sharpe --value 1.5 --source fabricated
# 预期: 错误: metric_source 必须是 ... 之一（枚举强制校验）
python -m research run add-metric R0001 --name sharpe --value 1.6 --source derived_local
# 预期: 已写入指标 R0001.sharpe（同键 upsert 更新，不报错）
```

**验收 7（AGENTS.md 5 项更新）**：人工核对 Step 1 的 5 处修改均已落入 `AGENTS.md`。

**验收 8（registry.db 纳入版本控制，根目录 git status 干净）**：
```powershell
git add 小市值/research/registry.db 小市值/research/strategies 小市值/research/experiments 小市值/research/runs 小市值/research/studies 小市值/research/analyses
git commit -m "feat(research): 端到端验收（registry.db 纳入版本控制 + 归档报告）"
git status
# 预期: working tree clean（临时 JSON 在 $env:TEMP，不污染仓库）
```

- [ ] **Step 4: 提交 AGENTS.md**

```bash
git add AGENTS.md
git commit -m "docs: AGENTS.md 联动研究登记系统（目录/工作流/命令/前提/数据纪律）"
```

---

## Self-Review

- [ ] **Spec 覆盖检查**：逐条核对 spec 关键点已落入本计划——
  - [ ] schema 8 表 + D1 六字段（n_trades / benchmark / benchmark_return / regime / n_trials / study_runs.partition）+ D4 约定指标名注释（Task 1）
  - [ ] 运行目录约定：所有命令从仓库根执行；`pip install -e 小市值` 安装机制（Global Constraints / Task 2 Step 3）
  - [ ] strategy create 工作区干净校验 + blob 相同警告 + `--experiment` 回填 + 根版本引导（Task 4）
  - [ ] promote 语义：由 Strategy 出发创建 Experiment，无 `promote --experiment` 变体（Task 5）
  - [ ] run：FAILED 必须 error_type、metrics upsert、`--from-json`、metric_value 存小数、非数值信息进 notes（Task 6）
  - [ ] study：design_json 强制非空、is/oos 分区、batch-add-runs（Task 7）
  - [ ] analyze：mean/median/std/min/max/positive_ratio/baseline_delta + 5 项诊断 + `[N/A] 数据不足` / `[N/A] 未标注样本外区间`（Task 8）
  - [ ] analysis create：decision 四值 + evidence E0~E6（Task 8）
  - [ ] 5 类 Markdown 单向生成 + Study 结论由 Analysis 填充 + analyses 由 analysis create 一并生成（Task 9）
  - [ ] CLI 全子命令非交互 + README 十条宪法（Task 10）
  - [ ] AGENTS.md 5 项更新 + 验收 9 条（Task 11）

- [ ] **占位符扫描**：全文无 "TBD" / "TODO" / "implement later" / "Similar to Task N" / "add error handling" 等占位表述；每个 checkbox 步骤都带完整代码块或精确命令；无"留待实现"的接口。

- [ ] **类型一致性检查**：
  - [ ] Task 2 产出 `db.connect/init_db/repo_root`、`ids.next_id` 与 Task 4/5/6/7/8 的 Consumes 签名一致
  - [ ] Task 4 产出 `create_strategy(conn, *, parent_id, name, change_summary, experiment_id, source_path, quick, root)` 与 Task 10 cli 调用参数一致
  - [ ] Task 6 产出 `create_run_from_json(conn, data)` 与 Task 7 `batch_add_runs` 调用一致
  - [ ] Task 8 产出 `analyze_study(conn, study_id) -> dict`（statistics / diagnostics / primary_metric）与 Task 9 `write_analysis_report`、Task 10 `cmd_analyze` 消费一致
  - [ ] Task 9 产出 `write_*_report(conn, id, root=None) -> Path` 与 Task 10 各 create 命令调用一致
  - [ ] 测试文件数量保持 8 个（spec §2/§13）：test_db / test_ids / test_git_meta / test_strategy / test_experiment / test_run / test_study / test_analysis（Task 9/10 的测试追加进 test_analysis.py）







