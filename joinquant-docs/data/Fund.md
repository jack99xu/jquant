# 聚宽数据字典

> 数据来源：聚宽官方数据文档，字段含义以 meaning 列为准。

---


## FUND_DIVIDEND

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 基金代码 |  |
| distribution_date | date | 分配收益日 |  |
| dividend_cancel_date | date | 取消分红公告日 |  |
| dividend_implement_date | dated | 分红实施公告日 |  |
| event | varchar(100) | 事项名称 |  |
| event_id | int | 事项类别 |  |
| ex_date | date | 除息日 |  |
| fund_paid_date | date | 基金红利派发日 |  |
| name | varchar(80) | 基金名称 |  |
| new_share_code | varchar(10) | 新增份额基金代码 |  |
| new_share_name | varchar(100) | 新增份额基金名称 |  |
| otc_ex_date | date | 场外除息日 |  |
| pay_date | date | 红利派发日 |  |
| process | varchar(100) | 方案进度 |  |
| process_id | int | 方案进度编码 |  |
| proportion | decimal(20,8) | 派现比例 |  |
| pub_date | date | 公布日期 |  |
| record_date | date | 权益登记日 |  |
| redeem_date | date | 再投资赎回起始日 |  |
| split_ratio | decimal(20,8) | 分拆（合并、赠送）比例 |  |

## FUND_FIN_INDICATOR

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| acc_nav_growth |  | 累计净值增长率 |  |
| adjust_nav |  | 期末还原后基金份额累计净值 |  |
| adjust_nav_growth |  | 扣除配售新股基金净值增长率 |  |
| adjust_profit |  | 本期利润扣减本期公允价值变动损益后的净额 |  |
| avg_profit |  | 加权平均份额本期利润 |  |
| avg_roe |  | 加权平均净值利润率 |  |
| code | varchar(12) | 基金代码 |  |
| name | varchar(80) | 基金名称 |  |
| nav |  | 期末基金份额净值 |  |
| nav_growth |  | 本期净值增长率 |  |
| period_end | date | 结束日期 |  |
| period_start | date | 开始日期 |  |
| profit |  | 本期利润 |  |
| profit_avaialbe_per_share |  | 期末可供分配份额利润 |  |
| profit_available |  | 期末可供分配利润 |  |
| pub_date | date | 公告日期 |  |
| report_type | varchar(32) | 报告类型 |  |
| report_type_id | int | 报告类型编码 |  |
| total_tna |  | 期末基金资产净值 |  |

## FUND_MAIN_INFO

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| advisor | varchar(100) | 基金管理人 |  |
| end_date | date | 结束日期 |  |
| invest_style | varchar(32) | 投资风格 |  |
| invest_style_id | int | 投资风格编码 |  |
| main_code | varchar(12) | 基金主体代码 |  |
| name | varchar(100) | 基金名称 |  |
| operate_mode | varchar(32) | 基金运作方式 |  |
| operate_mode_id | int | 基金运作方式编码 |  |
| pub_date | date | 发行日期 |  |
| start_date | date | 成立日期 |  |
| statistics_main_code | varchar(32) | 基金统计主代码（仅多份额基金存在此字段） |  |
| trustee | varchar(100) | 基金托管人 |  |
| underlying_asset_type | varchar(32) | 投资标的类型 |  |
| underlying_asset_type_id | int | 投资标的类型编码 |  |
| 基金运作方式编码 |  |  |  |

## FUND_MF_DAILY_PROFIT

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 基金代码 |  |
| daily_profit | decimal(10,4) | 每万份基金单位当日收益(元) |  |
| end_date | date | 收益日期 |  |
| name | varchar(80) | 基金名称 |  |
| weekly_yield | decimal(10,4) | 7日年化收益率(%) |  |

## FUND_NET_VALUE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| acc_factor | decimal(20,6) | 累计复权因子 | 基金从上市至今累计分红拆分送股的复权因子 |
| code | varchar(12) | 基金代码 |  |
| day | date | 交易日 |  |
| factor | decimal(20,6) | 复权因子 | 交易日最近一次分红拆分送股的复权因子 |
| net_value | decimal(20,6) | 单位净值 | 基金单位净值=（基金资产总值－基金负债）÷ 基金总份额 |
| refactor_net_value | decimal(20,6) | 累计复权净值 | 复权单位净值＝单计净值＋成立以来每份累计分红派息的金额（1+涨跌幅） |
| sum_value | decimal(20,6) | 累计净值 | 累计单位净值＝单位净值＋成立以来每份累计分红派息的金额 |

## FUND_PORTFOLIO

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| buying_back_rate | decimal(10,4) | 买入返售金融资产占比 |  |
| buying_back_value | decimal(20,4) | 买入返售金融资产金额 |  |
| code | varchar(12) | 基金代码 |  |
| deposit_rate | decimal(10,4) | 银行存款和结算备付金合计占比 |  |
| deposit_value | decimal(20,4) | 银行存款和结算备付金合计 |  |
| derivative_rate | decimal(10,4) | 金融衍生品投资占比 |  |
| derivative_value | decimal(20,4) | 金融衍生品投资金额 |  |
| equity_rate | decimal(10,4) | 权益类投资占比 |  |
| equity_value | decimal(20,4) | 权益类投资金额 |  |
| fixed_income_rate | decimal(10,4) | 固定收益投资占比 |  |
| fixed_income_value | decimal(20,4) | 固定收益投资金额 |  |
| name | varchar(80) | 基金名称 |  |
| others_rate | decimal(10,4) | 其他资产占比 |  |
| others_value | decimal(20,4) | 其他资产 |  |
| period_end | date | 报告期 |  |
| period_start | date | 开始日期 |  |
| precious_metal_rate | decimal(10,4) | 贵金属投资占比 |  |
| precious_metal_value | decimal(20,4) | 贵金属投资金额 |  |
| pub_date | date | 公告日期 |  |
| report_type | varchar(32) | 报告类型 |  |
| report_type_id | int | 报告类型编码 |  |
| stock_rate | decimal(10,4) | 股票投资占比 |  |
| stock_value | decimal(20,4) | 股票投资金额 |  |
| total_asset | decimal(20,4) | 总资产合计 |  |

## FUND_PORTFOLIO_BOND

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 基金代码 |  |
| market_cap | decimal(20,4) | 持有债券的市值 |  |
| name | varchar(100) | 债券名称 |  |
| period_end | date | 报告期 |  |
| period_start | date | 开始日期 |  |
| proportion | decimal(10,4) | 占净值比例 |  |
| pub_date | date | 公告日期 |  |
| rank | int | 持仓排名 |  |
| report_type | varchar(32) | 报告类型 |  |
| report_type_id | int | 报告类型编码 |  |
| shares | decimal(20,4) | 持有债券数量 |  |
| symbol | varchar(32) | 债券代码 |  |

## FUND_PORTFOLIO_STOCK

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 基金代码 |  |
| market_cap | decimal(20,4) | 持有股票的市值 |  |
| name | varchar(100) | 股票名称 |  |
| period_end | date | 报告期 |  |
| period_start | date | 开始日期 |  |
| proportion | decimal(10,4) | 占净值比例 |  |
| pub_date | date | 公告日期 |  |
| rank | int | 持仓排名 |  |
| report_type | varchar(32) | 报告类型 |  |
| report_type_id | int | 报告类型编码 |  |
| shares | decimal(20,4) | 持有股票 |  |
| symbol | varchar(32) | 股票代码 |  |

## FUND_SHARE_DAILY

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a1_p~a5_p | float | 五档卖价 |  |
| a1_v~a5_v | float | 五档卖量 |  |
| b1_p~b5_p | float | 五档买价 |  |
| b1_v~b5_v | float | 五档买量 |  |
| current | float | 当前价 |  |
| high | float | 当日最高价 |  |
| low | float | 当日最低价 |  |
| money | float | 累计成交额 |  |
| time | datetime | 时间 |  |
| volume | float | 累计成交量（股） |  |
