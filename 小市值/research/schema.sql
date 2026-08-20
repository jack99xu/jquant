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