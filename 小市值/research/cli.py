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