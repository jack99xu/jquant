# 聚宽 API 函数速查表

| 函数名 | 章节 | 签名 |
|--------|------|------|
| api | 策略API > 策略API介绍 | `` |
| attribute_history | 策略API > 策略API介绍 | `attribute_history(security, count, unit='1d',             fields=['open','close','high','low','volume','money'],             skip_paused=True, df=True, fq='pre')` |
| batch_cancel_orders | 策略API > 策略API介绍 | `batch_cancel_orders(orders)` |
| batch_submit_orders | 策略API > 策略API介绍 | `batch_submit_orders(orders)` |
| cancel_order | 策略API > 策略API介绍 | `cancel_order(order)` |
| classMarketOrderStyle | 策略API > 策略API介绍 | `classMarketOrderStyle(OrderStyle):def__init__(self, limit_price=None):self.limit_price = limit_price` |
| classOrderStatus | 策略API > 策略API介绍 | `classOrderStatus(Enum):# 订单新创建未委托，用于盘前/隔夜单，订单在开盘时变为 open 状态开始撮合new =8# 订单未完成, 无任何成交open =0# 订单未完成, 部分成交filled =1# 订单完成, 已撤销, 可能有成交, 需要看 Order.filled 字段canceled =2# 订单完成, 交易所已拒绝, 可能有成交, 需要看 Order.filled 字段rejected =3# 订单完成, 全部成交, Order.filled 等于 Order.amountheld =4` |
| create_backtest | 策略API > 策略API介绍 | `create_backtest(algorithm_id, start_date, end_date, frequency="day", initial_cash=10000, initial_positions=None, extras=None, name=None, code="", benchmark=None, python_version=2, use_credit=False)` |
| defhandle_data | 策略API > 策略API介绍 | `defhandle_data(context, data):# 执行下面的语句之后, context.portfolio 的整数 1context.portfolio =1log.info(context.portfolio)# 要恢复系统的变量, 只需要使用下面的语句即可delcontext.portfolio# 此时, context.portfolio 将变成账户信息.log.info(context.portfolio.total_value)` |
| disable_cache | 策略API > 策略API介绍 | `disable_cache()` |
| enable_profile | 策略API > 策略API介绍 | `enable_profile()` |
| error | 策略API > 策略API介绍 | `log.error(content) log.warn(content) log.info(content) log.debug(content) print(content1, content2, ...)` |
| get_all_factors | 策略API > 策略API介绍 | `get_all_factors()` |
| get_all_securities | 策略API > 策略API介绍 | `get_all_securities(types=[],date=None)` |
| get_all_trade_days | 策略API > 策略API介绍 | `fromjqdataimport* get_all_trade_days()` |
| get_bars | 策略API > 策略API介绍 | `get_bars(security, count, unit='1d',fields=['date','open','high','low','close'],          include_now=False, end_dt=None, fq_ref_date=None, df=False)` |
| get_billboard_list | 策略API > 策略API介绍 | `get_billboard_list(stock_list, start_date, end_date, count)` |
| get_call_auction | 策略API > 策略API介绍 | `fromjqdataimport* get_call_auction(security, start_date=None, end_date=None, fields=None)` |
| get_concept | 策略API > 策略API介绍 | `get_concept(security, date=None)` |
| get_concept_stocks | 策略API > 策略API介绍 | `get_concept_stocks(concept_code, date=None)` |
| get_concepts | 策略API > 策略API介绍 | `fromjqdataimport* get_concepts()` |
| get_current_data | 策略API > 策略API介绍 | `get_current_data()` |
| get_current_tick | 策略API > 策略API介绍 | `get_current_tick(security, dt=None, df=False)` |
| get_dominant_future | 策略API > 策略API介绍 | `get_dominant_future(underlying_symbol, date=None)` |
| get_extras | 策略API > 策略API介绍 | `get_extras(info, security_list, start_date='2015-01-01', end_date='2015-12-31', df=True, count=None)` |
| get_fundamentals | 策略API > 策略API介绍 | `get_fundamentals(query_object, date=None, statDate=None)` |
| get_fundamentals_continuously | 策略API > 策略API介绍 | `get_fundamentals_continuously(query_object, end_date=None,count=None, panel=True)` |
| get_future_contracts | 策略API > 策略API介绍 | `get_future_contracts(security, date=None)` |
| get_history_fundamentals | 策略API > 策略API介绍 | `get_history_fundamentals(security, fields, watch_date=None, stat_date=None, count=1, interval='1q', stat_by_year=False)` |
| get_index_stocks | 策略API > 策略API介绍 | `get_index_stocks(index_symbol, date=None)` |
| get_index_weights | 策略API > 策略API介绍 | `get_index_weights(index_id, date=None)` |
| get_industries | 策略API > 策略API介绍 | `fromjqdataimport* get_industries(name, date=None)` |
| get_industry | 策略API > 策略API介绍 | `get_industry(security, date=None)` |
| get_industry_stocks | 策略API > 策略API介绍 | `get_industry_stocks(industry_code, date=None)` |
| get_margincash_stocks | 策略API > 策略API介绍 | `get_margincash_stocks()` |
| get_marginsec_stocks | 策略API > 策略API介绍 | `get_marginsec_stocks(date=None)` |
| get_money_flow | 策略API > 策略API介绍 | `fromjqdataimport* get_money_flow(security_list, start_date=None, end_date=None, fields=None, count=None)` |
| get_mtss | 策略API > 策略API介绍 | `fromjqdataimport* get_mtss(security_list, start_date=None, end_date=None, fields=None, count=None)` |
| get_open_orders | 策略API > 策略API介绍 | `get_open_orders()` |
| get_orders | 策略API > 策略API介绍 | `get_orders(order_id=None, security=None, status=None)` |
| get_price | 策略API > 策略API介绍 | `get_price(security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='pre', count=None, panel=True, fill_paused=True)` |
| get_security_info | 策略API > 策略API介绍 | `get_security_info(code, date=None)` |
| get_ticks | 策略API > 策略API介绍 | `get_ticks(security, end_dt, start_dt=None, count=None, fields=['time','current','high','low','volume','money'], skip=True, df=False)` |
| get_trade_day | 策略API > 策略API介绍 | `get_trade_day(security, query_dt)` |
| get_trade_days | 策略API > 策略API介绍 | `fromjqdataimport* get_trade_days(start_date=None, end_date=None, count=None)` |
| get_trades | 策略API > 策略API介绍 | `get_trades()` |
| get_valuation | 策略API > 策略API介绍 | `fromjqdataimport* get_valuation(security, start_date=None, end_date=None, fields=None, count=None)` |
| handle_tick | 策略API > 策略API介绍 | `handle_tick(context, tick)` |
| history | 策略API > 策略API介绍 | `history(count, unit='1d', field='avg', security_list=None, df=True, skip_paused=False, fq='pre')` |
| inout_cash | 策略API > 策略API介绍 | `inout_cash(cash, pindex=0)` |
| is_dangerous | 策略API > 策略API介绍 | `context.subportfolios[i].is_dangerous(margin_rate)` |
| jqlib | 策略API > 策略API介绍 | `` |
| margincash_close | 策略API > 策略API介绍 | `margincash_close(security, amount, style=None, pindex=0)` |
| margincash_direct_refund | 策略API > 策略API介绍 | `margincash_direct_refund(value, pindex=0)` |
| margincash_open | 策略API > 策略API介绍 | `margincash_open(security, amount, style=None, pindex=0)` |
| marginsec_close | 策略API > 策略API介绍 | `marginsec_close(security, amount, style=None, pindex=0)` |
| marginsec_direct_refund | 策略API > 策略API介绍 | `marginsec_direct_refund(security, amount, pindex=0)` |
| marginsec_open | 策略API > 策略API介绍 | `marginsec_open(security, amount, style=None, pindex=0)` |
| normalize_code | 策略API > 策略API介绍 | `normalize_code()` |
| order | 策略API > 策略API介绍 | `order(security, amount, style=None, side='long', pindex=0, close_today=False)` |
| order_target | 策略API > 策略API介绍 | `order_target(security, amount, style=None, side='long', pindex=0, close_today=False)` |
| order_target_value | 策略API > 策略API介绍 | `order_target_value(security, value, style=None, side='long', pindex=0, close_today=False)` |
| order_value | 策略API > 策略API介绍 | `order_value(security, value, style=None, side='long', pindex=0, close_today=False)` |
| portfolio_optimizer | 策略API > 策略API介绍 | `portfolio_optimizer(date, securities, target, constraints, bounds=[Bound(0.0,1.0)], default_port_weight_range=[0.0,1.0], ftol=1e-9, return_none_if_fail=True)` |
| read_file | 策略API > 策略API介绍 | `read_file(path)` |
| record | 策略API > 策略API介绍 | `record(**kwargs)` |
| run_query | 策略API > 策略API介绍 | `fromjqdataimport* finance.run_query(query_object)` |
| send_message | 策略API > 策略API介绍 | `send_message(message,channel='weixin')` |
| set_benchmark | 策略API > 策略API介绍 | `set_benchmark(security)` |
| set_commission | 策略API > 策略API介绍 | `set_commission(object)` |
| set_option | 策略API > 策略API介绍 | `set_option('use_real_price', value)` |
| set_order_cost | 策略API > 策略API介绍 | `set_order_cost(cost, type, ref=None)` |
| set_slippage | 策略API > 策略API介绍 | `set_slippage(object,type=None, ref=None)` |
| set_subportfolios | 策略API > 策略API介绍 | `set_subportfolios([SubPortfolioConfig(cash,type), ... ])` |
| set_universe | 策略API > 策略API介绍 | `set_universe(security_list)` |
| subscribe | 策略API > 策略API介绍 | `subscribe(security, frequency)` |
| transfer_cash | 策略API > 策略API介绍 | `transfer_cash(from_pindex, to_pindex, cash)` |
| unsubscribe | 策略API > 策略API介绍 | `unsubscribe(security, frequency)` |
| unsubscribe_all | 策略API > 策略API介绍 | `unsubscribe_all()` |
| write_file | 策略API > 策略API介绍 | `write_file(path, content, append=False)` |
| 获取行业、概念成份股 | 股票数据 > 获取股票数据 | `# 获取行业板块成分股get_industry_stocks(industry_code, date=None)# 获取概念板块成分股get_concept_stocks(concept_code, date=None)` |
| STK_AH_PRICE_COMP | JQData使用说明 > 股票 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_AH_PRICE_COMP).filter(finance.STK_AH_PRICE_COMP.a_code==a_code).order_by(finance.STK_AH_PRICE_COMP.day).limit(n)` |
| STK_EL_CONST_CHANGE | JQData使用说明 > 股票 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EL_CONST_CHANGE).filter(finance.STK_EL_CONST_CHANGE.code==code).limit(n))` |
| STK_EL_TOP_ACTIVATE | JQData使用说明 > 股票 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EL_TOP_ACTIVATE).filter(finance.STK_EL_TOP_ACTIVATE.code==code).limit(n))` |
| STK_EXCHANGE_LINK_CALENDAR | JQData使用说明 > 股票 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EXCHANGE_LINK_CALENDAR).filter(finance.STK_EXCHANGE_LINK_CALENDAR.day==day).limit(n))` |
| STK_EXCHANGE_LINK_RATE | JQData使用说明 > 股票 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EXCHANGE_LINK_RATE).filter(finance.STK_EXCHANGE_LINK_RATE.day==day).limit(n))` |
| STK_EXCHANGE_TRADE_INFO | JQData使用说明 > 股票 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EXCHANGE_TRADE_INFO).filter(finance.STK_EXCHANGE_TRADE_INFO.exchange_code==exchange_code).limit(n)` |
| STK_HK_HOLD_INFO | JQData使用说明 > 股票 | `from jqdatasdk import finance df=finance.run_query(query(finance.STK_HK_HOLD_INFO).filter(finance.STK_HK_HOLD_INFO.link_id==310001)) print(df)` |
| STK_ML_QUOTA | JQData使用说明 > 股票 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_ML_QUOTA).filter(finance.STK_ML_QUOTA.day==day).limit(n))` |
| STK_MT_TOTAL | JQData使用说明 > 股票 | `fromjqdatasdkimport* finance.run_query(query(finance.STK_MT_TOTAL).filter(finance.STK_MT_TOTAL.date=='2019-05-23').limit(n))` |
| SW1_DAILY_PRICE | JQData使用说明 > 股票 | `df=finance.run_query(query(finance.SW1_DAILY_PRICE).filter(finance.SW1_DAILY_PRICE.code=='801010').limit(n)) print(df)` |
| get_locked_shares | JQData使用说明 > 股票 | `get_locked_shares(stock_list, start_date, end_date, forward_count)` |
| STK_CAPITAL_CHANGE | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_CAPITAL_CHANGE).filter(finance.STK_CAPITAL_CHANGE.code==code).limit(n))` |
| STK_COMPANY_INFO | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_COMPANY_INFO).filter(finance.STK_COMPANY_INFO.code==code).limit(n))` |
| STK_EMPLOYEE_INFO | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EMPLOYEE_INFO).filter(finance.STK_EMPLOYEE_INFO.code==code).limit(n))` |
| STK_HOLDER_NUM | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_HOLDER_NUM).filter(finance.STK_HOLDER_NUM.code==code).limit(n))` |
| STK_LIMITED_SHARES_LIST | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_LIMITED_SHARES_LIST).filter(finance.STK_LIMITED_SHARES_LIST.code==code).limit(n))` |
| STK_LIMITED_SHARES_UNLIMIT | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_LIMITED_SHARES_UNLIMIT).filter(finance.STK_LIMITED_SHARES_UNLIMIT.code==code).limit(n))` |
| STK_LIST | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_LIST).filter(finance.STK_LIST.code==code).limit(n))` |
| STK_MANAGEMENT_INFO | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_MANAGEMENT_INFO).filter(finance.STK_MANAGEMENT_INFO.code==code).order_by(finance.STK_MANAGEMENT_INFO.pub_date).limit(n)` |
| STK_NAME_HISTORY | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_NAME_HISTORY).filter(finance.STK_NAME_HISTORY.code==code).limit(n))` |
| STK_SHAREHOLDERS_SHARE_CHANGE | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHAREHOLDERS_SHARE_CHANGE).filter(finance.STK_SHAREHOLDERS_SHARE_CHANGE.code==code).limit(n))` |
| STK_SHAREHOLDER_FLOATING_TOP10 | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHAREHOLDER_FLOATING_TOP10).filter(finance.STK_SHAREHOLDER_FLOATING_TOP10.code==code).limit(n))` |
| STK_SHAREHOLDER_TOP10 | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHAREHOLDER_TOP10).filter(finance.STK_SHAREHOLDER_TOP10.code==code).limit(n))` |
| STK_SHARES_FROZEN | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHARES_FROZEN).filter(finance.STK_SHARES_FROZEN.code==code).limit(n))` |
| STK_SHARES_PLEDGE | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHARES_PLEDGE).filter(finance.STK_SHARES_PLEDGE.code==code).limit(n))` |
| STK_STATUS_CHANGE | JQData使用说明 > 上市公司基础信息 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_STATUS_CHANGE).filter(finance.STK_STATUS_CHANGE.code==code).limit(n))` |
| FINANCE_BALANCE_SHEET_PARENT | 股票数据 > 获取报告期财务数据 | `from jqdata import finance finance.run_query(query(finance.FINANCE_BALANCE_SHEET_PARENT).filter(finance.FINANCE_BALANCE_SHEET_PARENT.code==code).limit(n))` |
| FINANCE_CASHFLOW_STATEMENT_PARENT | 股票数据 > 获取报告期财务数据 | `from jqdata import finance finance.run_query(query(finance.FINANCE_CASHFLOW_STATEMENT_PARENT).filter(finance.FINANCE_CASHFLOW_STATEMENT_PARENT.code==code).limit(n))` |
| FINANCE_INCOME_STATEMENT_PARENT | 股票数据 > 获取报告期财务数据 | `from jqdata import finance finance.run_query(query(finance.FINANCE_INCOME_STATEMENT_PARENT).filter(finance.FINANCE_INCOME_STATEMENT_PARENT.code==code).limit(n))` |
| STK_AUDIT_OPINION | 股票数据 > 获取报告期财务数据 | `fromjqdataimportfinance finance.run_query(query(finance.STK_AUDIT_OPINION).filter(finance.STK_AUDIT_OPINION.code==code).limit(n))` |
| STK_BALANCE_SHEET_PARENT | 股票数据 > 获取报告期财务数据 | `from jqdata import finance finance.run_query(query(finance.STK_BALANCE_SHEET_PARENT).filter(finance.STK_BALANCE_SHEET_PARENT.code==code).limit(n))` |
| STK_INCOME_STATEMENT_PARENT | 股票数据 > 获取报告期财务数据 | `from jqdata import finance finance.run_query(query(finance.STK_INCOME_STATEMENT_PARENT).filter(finance.STK_INCOME_STATEMENT_PARENT.code==code).limit(n))` |
| STK_PERFORMANCE_LETTERS | 股票数据 > 获取报告期财务数据 | `fromjqdataimportfinance finance.run_query(query(finance.STK_PERFORMANCE_LETTERS).filter(finance.STK_PERFORMANCE_LETTERS.code==code).limit(n))` |
| STK_REPORT_DISCLOSURE | 股票数据 > 获取报告期财务数据 | `fromjqdataimportfinance finance.run_query(query(finance.STK_REPORT_DISCLOSURE).filter(finance.STK_REPORT_DISCLOSURE.code==code).limit(n))` |
| FINANCE_BALANCE_SHEET | JQData使用说明 > 财务数据 | `from jqdatasdk import finance finance.run_query(query(finance.FINANCE_BALANCE_SHEET).filter(finance.FINANCE_BALANCE_SHEET.code==code).limit(n))` |
| FINANCE_CASHFLOW_STATEMENT | JQData使用说明 > 财务数据 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FINANCE_CASHFLOW_STATEMENT).filter(finance.FINANCE_CASHFLOW_STATEMENT.code==code).limit(n))` |
| FINANCE_INCOME_STATEMENT | JQData使用说明 > 财务数据 | `from jqdatasdk import finance finance.run_query(query(finance.FINANCE_INCOME_STATEMENT).filter(finance.FINANCE_INCOME_STATEMENT.code==code).limit(n))` |
| STK_BALANCE_SHEET | JQData使用说明 > 财务数据 | `from jqdatasdk import finance finance.run_query(query(finance.STK_BALANCE_SHEET).filter(finance.STK_BALANCE_SHEET.code==code).limit(n))` |
| STK_CASHFLOW_STATEMENT | JQData使用说明 > 财务数据 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_CASHFLOW_STATEMENT).filter(finance.STK_CASHFLOW_STATEMENT.code==code).limit(n))` |
| STK_FIN_FORCAST | JQData使用说明 > 财务数据 | `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_FIN_FORCAST).filter(finance.STK_FIN_FORCAST.code==code).limit(n))` |
| STK_INCOME_STATEMENT | JQData使用说明 > 财务数据 | `from jqdatasdk import finance finance.run_query(query(finance.STK_INCOME_STATEMENT).filter(finance.STK_INCOME_STATEMENT.code==code).limit(n))` |
| STK_CASHFLOW_STATEMENT_PARENT | JQData使用说明 > 合并现金流量表 | `from jqdatasdk import finance finance.run_query(query(finance.STK_CASHFLOW_STATEMENT_PARENT).filter(finance.STK_CASHFLOW_STATEMENT_PARENT.code==code).limit(n))` |
| FUND_DIVIDEND | JQData使用说明 > 基金 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_DIVIDEND).filter(finance.FUND_DIVIDEND.code==code).limit(n))` |
| FUND_FIN_INDICATOR | JQData使用说明 > 基金 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_FIN_INDICATOR).filter(finance.FUND_FIN_INDICATOR.code==code).limit(n))` |
| FUND_MAIN_INFO | JQData使用说明 > 基金 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_MAIN_INFO).filter(finance.FUND_MAIN_INFO.main_code==main_code).limit(n))` |
| FUND_MF_DAILY_PROFIT | JQData使用说明 > 基金 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_MF_DAILY_PROFIT).filter(finance.FUND_MF_DAILY_PROFIT.code==code).limit(n))` |
| FUND_NET_VALUE | JQData使用说明 > 基金 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_NET_VALUE).filter(finance.FUND_NET_VALUE.code==code).limit(n))` |
| FUND_PORTFOLIO | JQData使用说明 > 基金 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_PORTFOLIO).filter(finance.FUND_PORTFOLIO.code==code).limit(n))` |
| FUND_PORTFOLIO_BOND | JQData使用说明 > 基金 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_PORTFOLIO_BOND).filter(finance.FUND_PORTFOLIO_BOND.code==code).limit(n))` |
| FUND_PORTFOLIO_STOCK | JQData使用说明 > 基金 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_PORTFOLIO_STOCK).filter(finance.FUND_PORTFOLIO_STOCK.code==code).limit(n))` |
| FUND_SHARE_DAILY | JQData使用说明 > 基金 | `fromjqdatasdkimport* finance.run_query(query(finance.FUND_SHARE_DAILY).filter(finance.FUND_SHARE_DAILY.date=='2019-05-23').limit(n))` |
| FUND_INVEST_TARGET | 场内基金数据 > 获取基金数据 | `from jqdata import*finance.run_query(query(finance.FUND_INVEST_TARGET).filter(finance.FUND_INVEST_TARGET.code== '510190.XSHG'))` |
| 基金列表 | 场内基金数据 > 获取基金数据 | `df = get_all_securities("fund")#获取所有场内基金df[df['type'] =='reits']# 获取所有reits基金df[df.display_name.str.contains("指\|增")]#获取名称中含"指"或"增" 的场内基金df[df.display_name.str.contains("指")&df.display_name.str.contains("增")]#获取名称中含"指"和"增" 的场内基金` |
| FUT_GLOBAL_DAILY | JQData使用说明 > 期货 | `fromjqdatasdkimportfinance df=finance.run_query(query(finance.FUT_GLOBAL_DAILY).filter(finance.FUT_GLOBAL_DAILY.day==date).limit(n))` |
| FUT_MEMBER_POSITION_RANK | JQData使用说明 > 期货 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUT_MEMBER_POSITION_RANK).filter(finance.FUT_MEMBER_POSITION_RANK.code==code).limit(n))` |
| FUT_WAREHOUSE_RECEIPT | JQData使用说明 > 期货 | `fromjqdatasdkimportfinance finance.run_query(query(finance.FUT_WAREHOUSE_RECEIPT).filter(finance.FUT_WAREHOUSE_RECEIPT.underlying_code==underlying_code).limit(n))` |
| get_futures_info | JQData使用说明 > 期货 | `get_futures_info(securities=None, fields=('contract_multiplier','tick_size','trade_time'))` |
| FUT_CHARGE | 期货数据 > 获取期货数据 | `fromjqdataimportfinance finance.run_query(query(finance.FUT_CHARGE).filter(finance.FUT_CHARGE.day==date).limit(n))` |
| FUT_MARGIN | 期货数据 > 获取期货数据 | `fromjqdataimportfinance finance.run_query(query(finance.FUT_MARGIN).filter(finance.FUT_MARGIN.day==date).limit(n))` |
| auth | JQData使用说明 > JQData-本地量化数据说明书 | `fromjqdatasdkimport* auth('ID','Password')#ID是申请时所填写的手机号；Password为聚宽官网登录密码` |
| get_query_count | JQData使用说明 > JQData-本地量化数据说明书 | `get_query_count()` |
| uctrlfu | JQData使用说明 > JQData-本地量化数据说明书 | `` |
| print | 策略API > 非交易时段下单的特别说明 | `# 导入函数库importpandasaspdfromjqdataimport*fromjqfactorimportFactorfromjqlib.optimizerimport*# 初始化函数，设定基准等等definitialize(context):# 设定沪深300作为基准set_benchmark('000300.XSHG')# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 过滤掉order系列API产生的比error级别低的log# log.set_level('order', 'error')### 股票相关设定 #### 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003,                             min_commission=5), type='stock')# 优化器设置g.optimizer =2#设定使用的优化模型optimize_model = {1:"模型1：等权重配置",2:"模型2：组合风险平价；股票的总权重限制为0到90%，ETF的总权重限制为0到10%；每只标的权重不超过10%",3:"模型3：组合风险最小化（最小化组合方差）；组合总权重限制为90%到100%；组合年化收益率目标下限为10%",4:"模型4：'人气指标5日均值'最大化；组合年化收益率目标下限为10%；每只标的权重不超过20%",5:"模型5：组合夏普比率最大化；每只标的权重不超过10%"}     print("优化%s"%(optimize_model[g.optimizer]))## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）# 开盘前运行run_monthly(before_market_open, monthday=1, time='9:00', reference_security='000300.XSHG')# 开盘运行run_monthly(market_open, monthday=1, time='9:30', reference_security='000300.XSHG')## 开盘前运行函数defbefore_market_open(context):print('调仓日期：%s'%context.current_dt.date())# 选出上证50成分股的一部分与选定的ETF基金进行组合,构成股票池。etf = ['159902.XSHE','159903.XSHE','510050.XSHG','510880.XSHG','510440.XSHG',         ]     g.buy_list = list(get_index_stocks('000016.XSHG')[-15:]) + etf## 开盘时运行函数defmarket_open(context):# 将不在股票池中的股票卖出sell_list = set(context.portfolio.positions.keys()) - set(g.buy_list)forstockinsell_list:         order_target_value(stock,0)# 组合优化模型ifg.optimizer ==1:# 模型1：等权重配置optimized_weight = pd.Series(data=[1.0/len(g.buy_list)]*len(g.buy_list),                                     index=g.buy_list)elifg.optimizer ==2:# 模型2：组合风险平价；股票的总权重限制为0到90%，ETF的总权重限制为0到10%；每只标的权重不超过10%optimized_weight = portfolio_optimizer(date=context.previous_date,                                     securities = g.buy_list,                                     target = RiskParity(count=250, risk_budget=None),# risk_budget 为 None默认为每只股票贡献相等constraints = [MarketConstraint('stock', low=0.0, high=0.9),                                                   MarketConstraint('etf', low=0.0, high=0.1)],                                     bounds=[Bound(0,0.1)],                                     default_port_weight_range=[0.,1.0],                                     ftol=1e-09,                                     return_none_if_fail=True)elifg.optimizer ==3:# 模型3：组合风险最小化（最小化组合方差）；组合总权重限制为90%到100%；组合年化收益率目标下限为10%optimized_weight = portfolio_optimizer(date=context.previous_date,                                     securities = g.buy_list,                                     target = MinVariance(count=250),                                     constraints = [WeightConstraint(low=0.9, high=1.0),                                                    AnnualProfitConstraint(limit=0.1, count=250)],                                     bounds=[],                                     default_port_weight_range=[0.,1.0],                                     ftol=1e-09,                                     return_none_if_fail=True)elifg.optimizer ==4:# 模型4：组合标的因子值最大化# 定义因子：人气指标5日均值classAR(Factor):name ='ar'# 每天获取过去五日的数据max_window =5# 获取的数据是人气指标dependencies = ['AR']defcalc(self, data):returndata['AR'].mean()# 模型4：'人气指标5日均值'最大化；组合年化收益率目标下限为10%；每只标的权重不超过20%optimized_weight = portfolio_optimizer(date=context.previous_date,                                     securities = g.buy_list,                                     target = MaxFactorValue(factor=AR, count=1),                                     constraints = [AnnualProfitConstraint(limit=0.2, count=250)],                                     bounds=[Bound(0,0.2)],                                     default_port_weight_range=[0.,1.0],                                     ftol=1e-09,                                     return_none_if_fail=True)elifg.optimizer ==5:# 模型5：组合夏普比率最大化；每只标的权重不超过10%optimized_weight = portfolio_optimizer(date=context.previous_date,                                     securities = g.buy_list,                                     target = MaxSharpeRatio(rf=0.0,weight_sum_equal=0.5, count=250),#无风险利率为0，最大化夏普比率需要约束组合权重的和为0.5constraints = [],                                     bounds=[Bound(0,0.1)],                                     default_port_weight_range=[0.,1.0],                                     ftol=1e-09,                                     return_none_if_fail=True)# 查看优化结果print(optimized_weight)# 优化失败，给予警告iftype(optimized_weight) == type(None):         print('警告：组合优化失败')# 按优化结果，执行调仓操作else:         total_value = context.portfolio.total_value# 获取总资产forstockinoptimized_weight.keys():             value = total_value * optimized_weight[stock]# 确定每个标的的权重order_target_value(stock, value)# 调整标的至目标权重` |
| filter | JQData使用说明 > JQData常见报错及数据处理规则 | `from jqdata import*q = query(finance.STK_INCOME_STATEMENT.company_name,  finance.STK_INCOME_STATEMENT.code,  finance.STK_INCOME_STATEMENT.pub_date,  finance.STK_INCOME_STATEMENT.start_date,  finance.STK_INCOME_STATEMENT.end_date,  finance.STK_INCOME_STATEMENT.total_operating_revenue,            finance.STK_INCOME_STATEMENT.report_type,           finance.STK_INCOME_STATEMENT.report_date, finance.STK_INCOME_STATEMENT.np_parent_company_owners).filter(      finance.STK_INCOME_STATEMENT.code=='300080.XSHE',      finance.STK_INCOME_STATEMENT.end_date=='2019-03-31',  #     finance.STK_INCOME_STATEMENT.report_type==1).limit(200)  df = finance.run_query(q)df.sort_values(by=['pub_date'],ascending=False)` |
| STK_XR_XD | JQData使用说明 > 通用接口 | `fromjqdatasdkimport* auth(username, pwd) q = query(finance.STK_XR_XD)# 注意需要先登陆,否则会报错表不存在finance.run_query(q)` |
| CCTV_NEWS | JQData使用说明 > 新闻联播文本 | `fromjqdatasdkimport* finance.run_query(query(finance.CCTV_NEWS).filter(finance.CCTV_NEWS.day=='2019-02-19').limit(n))` |
| get_factor_effect | JQData使用说明 > 因子数据（含新接口） | `get_factor_effect(security, start_date, end_date, period, factor, group_num=5)` |
| definitialize | 策略API > 开始写策略 | `definitialize(context):# 定义一个全局变量, 保存要操作的股票g.security ='000001.XSHE'# 运行函数run_daily(market_open, time='every_bar')defmarket_open(context):ifg.securitynotincontext.portfolio.positions:         order(g.security,1000)else:         order(g.security,-800)` |
| 实用的策略 | 策略API > 开始写策略 | `# 导入聚宽函数库importjqdata# 初始化函数，设定要操作的股票、基准等等definitialize(context):# 定义一个全局变量, 保存要操作的股票# 000001(股票:平安银行)g.security ='000001.XSHE'# 设定沪深300作为基准set_benchmark('000300.XSHG')# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 运行函数run_daily(market_open, time='every_bar')# 每个单位时间(如果按天回测,则每天调用一次,如果按分钟,则每分钟调用一次)调用一次defmarket_open(context):security = g.security# 获取股票的收盘价close_data = attribute_history(security,5,'1d', ['close'])# 取得过去五天的平均价格MA5 = close_data['close'].mean()# 取得上一时间点价格current_price = close_data['close'][-1]# 取得当前的现金cash = context.portfolio.available_cash# 如果上一时间点价格高出五天平均价1%, 则全仓买入ifcurrent_price >1.01*MA5:# 用所有 cash 买入股票order_value(security, cash)# 记录这次买入log.info("Buying %s"% (security))# 如果上一时间点价格低于五天平均价, 则空仓卖出elifcurrent_price < MA5andcontext.portfolio.positions[security].closeable_amount >0:# 卖出所有股票,使这只股票的最终持有量为0order_target(security,0)# 记录这次卖出log.info("Selling %s"% (security))# 画出上一时间点价格record(stock_price=current_price)` |
| bar | 策略API > 撮合流程 | `` |
| tick | 策略API > 撮合流程 | `` |
| after_code_changed | 策略API > 策略程序架构♠ | `after_code_changed(context)` |
| after_trading_end | 策略API > 策略程序架构♠ | `after_trading_end(context)` |
| before_trading_start | 策略API > 策略程序架构♠ | `before_trading_start(context)` |
| defon_strategy_end | 策略API > 策略程序架构♠ | `defon_strategy_end(context)` |
| handle_data | 策略API > 策略程序架构♠ | `handle_data(context, data)` |
| initialize | 策略API > 策略程序架构♠ | `initialize(context)` |
| on_event | 策略API > 策略程序架构♠ | `on_event(context, event)` |
| process_initialize | 策略API > 策略程序架构♠ | `process_initialize(context)` |
| neutralize | 因子分析 > 因子数据处理函数 | `neutralize(series, how=None, date=None, axis=1)` |
| standardlize | 因子分析 > 因子数据处理函数 | `standardlize(series, inf2nan=True, axis=1)` |
| winsorize | 因子分析 > 因子数据处理函数 | `winsorize(series, scale=None, range=None, qrange=None, inclusive=True, inf2nan=True, axis=1)` |
| winsorize_med | 因子分析 > 因子数据处理函数 | `winsorize_med(series, scale=1, inclusive=True, inf2nan=True, axis=1)` |
| 均线策略 | 策略API > 策略示例 | `# 导入聚宽函数库importjqdata# 初始化函数，设定要操作的股票、基准等等definitialize(context):# 定义一个全局变量, 保存要操作的股票# 000001(股票:平安银行)g.security ='000001.XSHE'# 设定沪深300作为基准set_benchmark('000300.XSHG')# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 每个单位时间(如果按天回测,则每天调用一次,如果按分钟,则每分钟调用一次)调用一次defhandle_data(context, data):security = g.security# 获取股票的收盘价close_data = attribute_history(security,5,'1d', ['close'])# 取得过去五天的平均价格MA5 = close_data['close'].mean()# 取得上一时间点价格current_price = close_data['close'][-1]# 取得当前的现金cash = context.portfolio.available_cash# 如果上一时间点价格高出五天平均价5%, 则全仓买入if(current_price >1.05*MA5)and(cash>0):# 用所有 cash 买入股票order_value(security, cash)# 记录这次买入log.info("Buying %s"% (security))# 如果上一时间点价格低于五天平均价, 则空仓卖出elifcurrent_price <0.95*MA5andcontext.portfolio.positions[security].closeable_amount >0:# 卖出所有股票,使这只股票的最终持有量为0order_target(security,0)# 记录这次卖出log.info("Selling %s"% (security))# 画出上一时间点价格record(stock_price=current_price)` |
| 多股票持仓示例 | 策略API > 策略示例 | `# 导入聚宽函数库importjqdatadefinitialize(context):# 初始化此策略# 设置我们要操作的股票池g.stocks = ['000001.XSHE','000002.XSHE','000004.XSHE','000005.XSHE']# 设定沪深300作为基准set_benchmark('000300.XSHG')# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 每个单位时间(如果按天回测,则每天调用一次,如果按分钟,则每分钟调用一次)调用一次defhandle_data(context, data):# 循环每只股票forsecuritying.stocks:# 得到股票之前3天的平均价vwap = data[security].vwap(3)# 得到上一时间点股票收盘价price = data[security].close# 得到当前资金余额cash = context.portfolio.available_cash# 如果上一时间点价格小于三天平均价*0.995，并且持有该股票，卖出ifprice < vwap *0.995andcontext.portfolio.positions[security].closeable_amount >0:# 下入卖出单order(security,-100)# 记录这次卖出log.info("Selling %s"% (security))# 如果上一时间点价格大于三天平均价*1.005，并且有现金余额，买入elifprice > vwap *1.005andcash >0:# 下入买入单order(security,100)# 记录这次买入log.info("Buying %s"% (security))` |
| 多股票追涨策略 | 策略API > 策略示例 | `# 导入聚宽函数库importjqdata# 初始化程序, 整个回测只运行一次definitialize(context):# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 每天买入股票数量g.daily_buy_count  =5# 设置我们要操作的股票池, 这里我们操作多只股票，下列股票选自计算机信息技术相关板块g.stocks = get_industry_stocks('I64') + get_industry_stocks('I65')# 防止板块之间重复包含某只股票, 排除掉重复的, g.stocks 现在是一个集合(set)g.stocks = set(g.stocks)# 让每天早上开盘时执行 morning_sell_allrun_daily(morning_sell_all,'09:30')defmorning_sell_all(context):# 将目前所有的股票卖出forsecurityincontext.portfolio.positions:# 全部卖出order_target(security,0)# 记录这次卖出log.info("Selling %s"% (security))defbefore_trading_start(context):# 今天已经买入的股票g.today_bought_stocks = set()# 得到所有股票昨日收盘价, 每天只需要取一次, 所以放在 before_trading_start 中g.last_df = history(1,'1d','close',g.stocks)# 在每分钟的第一秒运行, data 是上一分钟的切片数据defhandle_data(context, data):# 判断是否在当日最后的2小时，我们只追涨最后2小时满足追涨条件的股票ifcontext.current_dt.hour <13:return# 每天只买这么多个iflen(g.today_bought_stocks) >= g.daily_buy_count:return# 只遍历今天还没有买入的股票forsecurityin(g.stocks - g.today_bought_stocks):# 得到当前价格price = data[security].close# 获取这只股票昨天收盘价last_close = g.last_df[security][0]# 如果上一时间点价格已经涨了9.5%~9.9%# 今天的涨停价格区间大于1元，今天没有买入该支股票ifprice/last_close >1.095\andprice/last_close <1.099\anddata[security].high_limit - last_close >=1.0:# 得到当前资金余额cash = context.portfolio.available_cash# 计算今天还需要买入的股票数量need_count = g.daily_buy_count - len(g.today_bought_stocks)# 把现金分成几份,buy_cash = context.portfolio.available_cash / need_count# 买入这么多现金的股票order_value(security, buy_cash)# 放入今日已买股票的集合g.today_bought_stocks.add(security)# 记录这次买入log.info("Buying %s"% (security))# 买够5个之后就不买了iflen(g.today_bought_stocks) >= g.daily_buy_count:break` |
| _get_extra_data | 因子分析 > 因子定义和计算 | `self._get_extra_data(securities=[],fields=[])` |
| calc_factors | 因子分析 > 因子定义和计算 | `calc_factors(securities, factors, start_date, end_date, use_real_price, skip_paused)` |
| classMA5 | 因子分析 > 因子定义和计算 | `classMA5(Factor):name ='ma5'# 每天获取过去五日的数据max_window =5# 获取的数据是收盘价dependencies = ['close']defcalc(self, data):# print("现在处理{}的数据"format( self._current_date)) #打印逻辑日期returndata['close'][-5:].mean()` |
| 因子定义 dependencies 中的财务因子 | 因子分析 > 因子定义和计算 | `# 计算营业收入TTMfromjqfactorimportFactorclassOR_TTM(Factor):# 设置因子名称name ='operating_revenue_ttm'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据，即前四季度的营业收入dependencies = ['operating_revenue','operating_revenue_1','operating_revenue_2','operating_revenue_3']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 计算 ttm ， 为前四季度相加ttm = data['operating_revenue'] + data['operating_revenue_1'] + data['operating_revenue_2'] + data['operating_revenue_3']# 将 ttm 转换成 seriesreturnttm.mean()` |
| 示例-计算TTM数据 | 因子分析 > 因子定义和计算 | `# 计算营业收入TTMfromjqfactorimportFactorclassOR_TTM(Factor):# 设置因子名称name ='operating_revenue_ttm'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据，即前四季度的营业收入dependencies = ['operating_revenue','operating_revenue_1','operating_revenue_2','operating_revenue_3']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 计算 ttm ， 为前四季度相加ttm = data['operating_revenue'] + data['operating_revenue_1'] + data['operating_revenue_2'] + data['operating_revenue_3']# 将 ttm 转换成 seriesreturnttm.mean()` |
| calc_autocorrelation | 因子分析 > 因子分析 | `far.calc_autocorrelation(rank=True)` |
| calc_autocorrelation_n_days_lag | 因子分析 > 因子分析 | `far.calc_autocorrelation_n_days_lag(n=9,rank=True)` |
| calc_average_cumulative_return_by_quantile | 因子分析 > 因子分析 | `far.calc_average_cumulative_return_by_quantile(periods_before=5,periods_after=15,demeaned=False,group_adjust=False)` |
| calc_cumulative_return_by_quantile | 因子分析 > 因子分析 | `far.calc_cumulative_return_by_quantile(period=5)` |
| calc_cumulative_returns | 因子分析 > 因子分析 | `far.calc_cumulative_returns(period=5,demeaned=False,group_adjust=False)` |
| calc_factor_alpha_beta | 因子分析 > 因子分析 | `far.calc_factor_alpha_beta(demeaned=True,group_adjust=False)` |
| calc_factor_information_coefficient | 因子分析 > 因子分析 | `far.calc_factor_information_coefficient(group_adjust=False, by_group=False,method='rank')` |
| calc_factor_returns | 因子分析 > 因子分析 | `far.calc_factor_returns(demeaned=True,group_adjust=False)` |
| calc_ic_mean_n_days_lag | 因子分析 > 因子分析 | `far.calc_ic_mean_n_days_lag(n=10,group_adjust=False,by_group=False,method=None)` |
| calc_mean_information_coefficient | 因子分析 > 因子分析 | `far.calc_mean_information_coefficient(group_adjust=False, by_group=False, by_time=None,method='rank')` |
| calc_mean_return_by_quantile | 因子分析 > 因子分析 | `mean,std = far.calc_mean_return_by_quantile(by_date=False,by_group=False,demeaned=False,group_adjust=False)` |
| calc_quantile_turnover_mean_n_days_lag | 因子分析 > 因子分析 | `far.calc_quantile_turnover_mean_n_days_lag(n=10)` |
| calc_top_down_cumulative_returns | 因子分析 > 因子分析 | `far.calc_top_down_cumulative_returns(period=5,demeaned=False,group_adjust=False)` |
| compute_mean_returns_spread | 因子分析 > 因子分析 | `mean, std = far.compute_mean_returns_spread (upper_quant=None,lower_quant=None,by_date=True,by_group=False,demeaned=False,group_adjust=False)` |
| create_event_returns_tear_sheet | 因子分析 > 因子分析 | `far.create_event_returns_tear_sheet(avgretplot=(5, 15),demeaned=False,group_adjust=False,std_bar=False)` |
| create_full_tear_sheet | 因子分析 > 因子分析 | `far.create_full_tear_sheet(demeaned=False,group_adjust=False,by_group=False,turnover_periods=None, avgretplot=(5, 15),std_bar=False)` |
| create_information_tear_sheet | 因子分析 > 因子分析 | `far.create_information_tear_sheet(group_adjust=False,by_group=False)` |
| create_returns_tear_sheet | 因子分析 > 因子分析 | `far.create_returns_tear_sheet(demeaned=False,group_adjust=False,by_group=False)` |
| create_summary_tear_sheet | 因子分析 > 因子分析 | `far.create_summary_tear_sheet(demeaned=False,group_adjust=False)` |
| create_turnover_tear_sheet | 因子分析 > 因子分析 | `far.create_turnover_tear_sheet(turnover_periods=None)` |
| naninfforward_return | 因子分析 > 因子分析 | `` |
| plot_cumulative_returns | 因子分析 > 因子分析 | `far.plot_cumulative_returns(period=1,demeaned=False,group_adjust=False)` |
| plot_cumulative_returns_by_quantile | 因子分析 > 因子分析 | `far.plot_cumulative_returns_by_quantile(period=(1, 3, 9),demeaned=False,group_adjust=False)` |
| plot_disable_chinese_label | 因子分析 > 因子分析 | `far.plot_disable_chinese_label()` |
| plot_events_distribution | 因子分析 > 因子分析 | `far.plot_events_distribution(num_days=1)` |
| plot_factor_auto_correlation | 因子分析 > 因子分析 | `far.plot_factor_auto_correlation(periods=None,rank=True)` |
| plot_ic_by_group | 因子分析 > 因子分析 | `far.plot_ic_by_group(group_adjust=False,method='rank')` |
| plot_ic_hist | 因子分析 > 因子分析 | `far.plot_ic_hist(group_adjust=False,method='rank')` |
| plot_ic_qq | 因子分析 > 因子分析 | `far.plot_ic_qq(group_adjust=False,method='rank',theoretical_dist='norm')` |
| plot_ic_ts | 因子分析 > 因子分析 | `far.plot_ic_ts(group_adjust=False,method='rank')` |
| plot_information_table | 因子分析 > 因子分析 | `far.plot_information_table(group_adjust=False,method='rank')` |
| plot_mean_quantile_returns_spread_time_series | 因子分析 > 因子分析 | `far.plot_mean_quantile_returns_spread_time_series(demeaned=False,group_adjust=False,bandwidth=1)` |
| plot_monthly_ic_heatmap | 因子分析 > 因子分析 | `far.plot_monthly_ic_heatmap(group_adjust=False)` |
| plot_quantile_average_cumulative_return | 因子分析 > 因子分析 | `far.plot_quantile_average_cumulative_return(periods_before=5,periods_after=10,by_quantile=False,std_bar=False,demeaned=False,group_adjust=False)` |
| plot_quantile_returns_bar | 因子分析 > 因子分析 | `far.plot_quantile_returns_bar(by_group=False,demeaned=False,group_adjust=False)` |
| plot_quantile_statistics_table | 因子分析 > 因子分析 | `far.plot_quantile_statistics_table()` |
| plot_returns_table | 因子分析 > 因子分析 | `far.plot_returns_table(demeaned=False,group_adjust=False)` |
| plot_top_bottom_quantile_turnover | 因子分析 > 因子分析 | `far.plot_top_bottom_quantile_turnover(periods=(1,3,9))` |
| plot_turnover_table | 因子分析 > 因子分析 | `far.plot_turnover_table()` |
| 因子分析API | 因子分析 > 因子分析 | `#载入函数库fromjqfactorimportanalyze_factor#对因子进行分析far = analyze_factor(factor, start_date, end_date, industry, universe, quantiles, periods, weight_method, use_real_price, skip_paused, max_loss, factor_dep_definitions)` |
| classROATTM | 因子分析 > 示例 | `classROATTM(Factor):name ='roa_ttm'max_window =1# 定义依赖的数据： 过去四个季度的净利润， 以及最新一个季度的总资产dependencies = ['net_profit','net_profit_1','net_profit_2','net_profit_3','total_assets']defcalc(self, data):# 计算净利润的 ttm 值net_profit_ttm = data['net_profit'] + data['net_profit_1'] + data['net_profit_2'] + data['net_profit_3']# 计算 ROAresult = net_profit_ttm / data['total_assets']# 把结果转成一个 seriesreturnresult.mean()` |
| filterwarnings | 因子分析 > 示例 | `# 载入函数库fromjqfactorimportanalyze_factorfromjqdataimport*fromjqlibimportalpha191importpandasaspdimportwarnings warnings.filterwarnings("ignore")# 测试开始时间start_date ='2019-10-01'# 测试结束时间end_date ='2019-11-11'# 测试时间区间的交易日date_list = get_trade_days(start_date=start_date, end_date=end_date)# 转换交易日时间的数据类型# date_list = [date.strftime('%Y-%m-%d') for date in date_list]# 获取一段时间股票池191因子数据factor_data = {}# 循环获取每天数据fordateindate_list:# 获取每天的股票池universe = get_index_stocks('000300.XSHG', date=date)# 获取每天股票池的因子数据_factor_data = alpha191.alpha_002(code=universe, end_date=date, fq='post')# 添加每天的因子数据factor_data[date] = _factor_data# 将字典类型数据转换为DataFramefactor_data = pd.DataFrame(factor_data).T# 将 index 转换为 DatetimeIndexfactor_data.index = pd.to_datetime(factor_data.index)# 对因子进行分析，参数使用默认值far = analyze_factor(factor=factor_data, )# 展示全部分析far.create_full_tear_sheet(demeaned=False, group_adjust=False, by_group=False, turnover_periods=None,                             avgretplot=(5,15), std_bar=False)` |
| fromjqfactorimportFactorclassGROSSPROFITABILITY | 因子分析 > 示例 | `fromjqfactorimportFactorclassGROSSPROFITABILITY(Factor):# 设置因子名称name ='gross_profitability'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据# 在策略中需要使用 get_fundamentals 获取的 income.total_operating_revenue, 在这里可以直接写做total_operating_revenue。 其他数据同理。dependencies = ['total_operating_revenue','total_operating_cost','total_assets']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 获取单季度的营业总收入数据 , index 是日期，column 是股票代码， value 是营业总收入total_operating_revenue = data['total_operating_revenue']# 获取单季度的营业总成本数据total_operating_cost = data['total_operating_cost']# 获取总资产total_assets = data['total_assets']# 计算 gross_profitabilitygross_profitability = (total_operating_revenue - total_operating_cost)/total_assets# 由于 gross_profitability 是一个一行 n 列的 dataframe，可以直接求 mean 转成 seriesreturngross_profitability.mean()` |
| fromjqfactorimportFactorclassHs300Alpha | 因子分析 > 示例 | `fromjqfactorimportFactorclassHs300Alpha(Factor):# 设置因子名称name ='hs300_alpha'# 设置获取数据的时间窗口长度max_window =10# 设置依赖的数据dependencies = ['close']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 获取个股的收盘价数据close = data['close']# 计算个股近10日收益stock_return = close.iloc[-1,:]/close.iloc[0,:]-1# 获取指数（沪深300）的收盘价数据index_close = self._get_extra_data(securities=['000300.XSHG'], fields=['close'])['close']# 计算指数的近10日收益index_return = index_close.iat[-1,0]/index_close.iat[0,0] -1# 计算 alphaalpha = stock_return - index_returnreturnalpha` |
| fromjqfactorimportFactorclassNetProfitGrowth | 因子分析 > 示例 | `fromjqfactorimportFactorclassNetProfitGrowth(Factor):# 设置因子名称name ='net_profit_growth_rate'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据dependencies = ['net_profit_y','net_profit_y1']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 个股最新一年度的净利润数据net_profit_y = data['net_profit_y']# 个股最新一年度的上一年的净利润数据net_profit_y1 = data['net_profit_y1']# 计算增长率growth = net_profit_y/net_profit_y1 -1# 返回一个 seriesreturngrowth.mean()` |
| fromjqfactorimportFactorimportnumpyasnpclassALPHA013 | 因子分析 > 示例 | `fromjqfactorimportFactorimportnumpyasnpclassALPHA013(Factor):# 设置因子名称name ='alpha013'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据dependencies = ['high','low','volume','money']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 最高价的 dataframe ， index 是日期， column 是股票代码high = data['high']# 最低价的 dataframe ， index 是日期， column 是股票代码low = data['low']#计算 vwapvwap = data['money']/data['volume']# 返回因子值， 这里求平均值是为了把只有一行的 dataframe 转成 seriesreturn(np.power(high*low,0.5) - vwap).mean()` |
| fromjqfactorimportFactorimportnumpyasnpimportpandasaspdclassDebtEquityRatio | 因子分析 > 示例 | `fromjqfactorimportFactorimportnumpyasnpimportpandasaspdclassDebtEquityRatio(Factor):name ='debt_to_equity_ratio'max_window =1dependencies = ['total_liability','equities_parent_company_owners',# 以下为中性化需要使用的数据'market_cap','HY001','HY002','HY003','HY004','HY005','HY006','HY007','HY008','HY009','HY010','HY011']defcalc(self, data):tl = data['total_liability']         epco = data['equities_parent_company_owners']         result = tl / epcoreturnneutralization(data, result.mean())# 行业市值中性化defneutralization(data, factor):fromstatsmodels.apiimportOLS     industry_exposure = pd.DataFrame(index=data['HY001'].columns)     industry_list = ['HY001','HY002','HY003','HY004','HY005','HY006','HY007','HY008','HY009','HY010','HY011']forkey, valueindata.items():ifkeyinindustry_list:             industry_exposure[key]=value.iloc[-1]     market_cap_exposure = data['market_cap'].iloc[-1]     total_exposure = pd.concat([market_cap_exposure,industry_exposure],axis=1)     result = OLS(factor, total_exposure, missing='drop').fit().residreturnresult` |
| dataframe | 因子分析 > 附录 | `` |
| valueerrornoobjectstoconcatenate | 因子分析 > 附录 | `` |