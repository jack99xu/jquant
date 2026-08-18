# 聚宽策略 API 文档

> 数据来源：聚宽官方 API 文档（joinquant.com/help/api/help），由 jq-docs-mcp 抓取入库后导出。
> 参数信息来自官方页面提取，部分函数可能缺失参数明细，以**签名**为准。

---

## 策略API > 策略API介绍

### api（融资融券专用API）

**签名:** ``
**章节:** 策略API > 策略API介绍
**说明:** 注意：get_marginsec_stocks和get_margincash_stocks无法获取当前未完结交易日的数据，因为交易所的数据尚未生成。

---

### attribute_history（回测环境/模拟专用API）

**签名:** `attribute_history(security, count, unit='1d',             fields=['open','close','high','low','volume','money'],             skip_paused=True, df=True, fq='pre')`
**章节:** 策略API > 策略API介绍
**说明:** 回测环境/模拟专用API

---

### batch_cancel_orders（批量撤单）

**签名:** `batch_cancel_orders(orders)`
**章节:** 策略API > 策略API介绍
**说明:** 批量撤单

---

### batch_submit_orders（对一系列标的进行批量委托）

**签名:** `batch_submit_orders(orders)`
**章节:** 策略API > 策略API介绍
**说明:** 对一系列标的进行批量委托，委托时会对每一个委托进行验资验券，若其中任一个委托校验失败，则整个委托将会失败

---

### cancel_order（取消订单）

**签名:** `cancel_order(order)`
**章节:** 策略API > 策略API介绍
**说明:** 取消订单

---

### classMarketOrderStyle（具体订单处理方法请查看订单处理>>>下单方式）

**签名:** `classMarketOrderStyle(OrderStyle):def__init__(self, limit_price=None):self.limit_price = limit_price`
**章节:** 策略API > 策略API介绍
**说明:** 具体订单处理方法请查看订单处理>>>下单方式, 有如下子类

---

### classOrderStatus（订单状态）

**签名:** `classOrderStatus(Enum):# 订单新创建未委托，用于盘前/隔夜单，订单在开盘时变为 open 状态开始撮合new =8# 订单未完成, 无任何成交open =0# 订单未完成, 部分成交filled =1# 订单完成, 已撤销, 可能有成交, 需要看 Order.filled 字段canceled =2# 订单完成, 交易所已拒绝, 可能有成交, 需要看 Order.filled 字段rejected =3# 订单完成, 全部成交, Order.filled 等于 Order.amountheld =4`
**章节:** 策略API > 策略API介绍
**说明:** 订单状态, Enum特性使用的第三方库(https://pypi.python.org/pypi/enum34)获取订单状态的方法请参考上面Order对象

---

### create_backtest（通过一个策略ID从研究中创建回测）

**签名:** `create_backtest(algorithm_id, start_date, end_date, frequency="day", initial_cash=10000, initial_positions=None, extras=None, name=None, code="", benchmark=None, python_version=2, use_credit=False)`
**章节:** 策略API > 策略API介绍
**说明:** 通过一个策略ID从研究中创建回测，只能在研究中使用，目前不支持在回测及模拟交易中使用；

---

### defhandle_data（示例）

**签名:** `defhandle_data(context, data):# 执行下面的语句之后, context.portfolio 的整数 1context.portfolio =1log.info(context.portfolio)# 要恢复系统的变量, 只需要使用下面的语句即可delcontext.portfolio# 此时, context.portfolio 将变成账户信息.log.info(context.portfolio.total_value)`
**章节:** 策略API > 策略API介绍
**说明:** 示例

---

### disable_cache（在默认情况下系统启用了缓存以加快运行速度）

**签名:** `disable_cache()`
**章节:** 策略API > 策略API介绍
**说明:** 在默认情况下系统启用了缓存以加快运行速度，但在策略内存占用较大时容易超过设置的内存上限而触发系统杀死进程。若用户反复出现策略因内存占用超限而被终止的情况，可以考虑在initialize函数中调用disable_cache来关闭缓存机制。

---

### enable_profile（回测环境专用API）

**签名:** `enable_profile()`
**章节:** 策略API > 策略API介绍
**说明:** 回测环境专用API

---

### error（分级别打log）

**签名:** `log.error(content) log.warn(content) log.info(content) log.debug(content) print(content1, content2, ...)`
**章节:** 策略API > 策略API介绍
**说明:** 分级别打log,跟python的logging模块一致
print输出的结果等同于log.info, 但是print后面的每一个元素会占用一行

---

### get_all_factors（参数）

**签名:** `get_all_factors()`
**章节:** 策略API > 策略API介绍
**说明:** 参数

---

### get_all_securities（获取平台支持的所有股票、基金、指数、期货、期权信息）

**签名:** `get_all_securities(types=[],date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取平台支持的所有股票、基金、指数、期货、期权信息

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| types：默认为stock，这里请在使用时注意防止未来函数。 |  | 是 |  |
| date |  | 是 | 日期, 一个字符串或者 [datetime.datetime]/[datetime.date] 对象, 用于获取某日期还在上市的股票信息. 默认值为 None, 表示获取所有日期的股票信息 |

---

### get_all_trade_days（获取所有交易日）

**签名:** `fromjqdataimport* get_all_trade_days()`
**章节:** 策略API > 策略API介绍
**说明:** 获取所有交易日, 不需要传入参数, 返回一个包含所有交易日的 numpy.ndarray, 每个元素为一个datetime.date类型.

---

### get_bars（获取各种时间周期的 bar 数据）

**签名:** `get_bars(security, count, unit='1d',fields=['date','open','high','low','close'],          include_now=False, end_dt=None, fq_ref_date=None, df=False)`
**章节:** 策略API > 策略API介绍
**说明:** 获取各种时间周期的 bar 数据， bar 的分割方式与主流股票软件相同， 而且支持返回当前时刻所在 bar 的数据；get_bars 开盘时取的bar高开低收都是当天的开盘价，成交量成交额为0；get_bars 没有跳过停牌选项，所获取的数据都是不包含停牌的数据，如果bar个数少于count个，则返回实际个数，并不会填充。更详细的get_bars解释，【API解析】get_bars 定义和逻辑

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| security |  | 是 | 期权合约代码；如security='10001979.XSHG' #50ETF期权，上海证券交易所；security='CU2001C42000.XSGE'#铜期权，上海期货交易所； security='SR003C5600.XZCE' #白糖期权，郑州商品交易所； security='M2005-P-2400.XDCE' #豆粕期权，大连商品交易所； |
| count |  | 是 | 大于0的整数，表示获取bar的个数。如果行情数据的bar不足count个，返回的长度则小于count个数。 |
| unit |  | 是 | bar的时间单位, 支持如下周期：'1m', '5m', '15m', '30m', '60m', '120m', '1d', '1w', '1M'。其中m表示分钟，d表示天，w表示周，M表示月。 |
| fields |  | 是 | 获取数据的字段， 支持如下值：'date', 'open', 'close', 'high', 'low', 'volume', 'money'。 |
| include_now |  | 是 | 取值True 或者False。 表示是否包含当前bar, 比如策略时间是9:33，unit参数为5m， 如果 include_now=True,则返回9:30-9:33这个分钟 bar。 |
| end_dt：查询的截止时间，支持的类型为datetime.datetime或None，默认为datetime.now()。 |  | 是 |  |

---

### get_billboard_list（获取指定日期区间内的龙虎榜数据）

**签名:** `get_billboard_list(stock_list, start_date, end_date, count)`
**章节:** 策略API > 策略API介绍
**说明:** 获取指定日期区间内的龙虎榜数据

---

### get_call_auction（获取指定时间区间内交易日09:25的集合竞价数据）

**签名:** `fromjqdataimport* get_call_auction(security, start_date=None, end_date=None, fields=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取指定时间区间内交易日09:25的集合竞价数据，支持股票（2010年至今）、场内基金（2019年至今）、指数（2017年至今）和上交所ETF期权（2017年至今）的集合竞价数据，当日的集合竞价数据最晚于9:28分返回。

---

### get_concept（数据调用方法）

**签名:** `get_concept(security, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 数据调用方法

---

### get_concept_stocks（获取在给定日期一个概念板块的所有股票）

**签名:** `get_concept_stocks(concept_code, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取在给定日期一个概念板块的所有股票，概念板块分类列表见数据页面-行业概念数据。

---

### get_concepts（获取所有的概念板块列表）

**签名:** `fromjqdataimport* get_concepts()`
**章节:** 策略API > 策略API介绍
**说明:** 获取所有的概念板块列表，行业分类列表见数据页面-行业概念数据。

---

### get_current_data（回测环境/模拟专用API）

**签名:** `get_current_data()`
**章节:** 策略API > 策略API介绍
**说明:** 回测环境/模拟专用API

---

### get_current_tick（获取当前tick数据）

**签名:** `get_current_tick(security, dt=None, df=False)`
**章节:** 策略API > 策略API介绍

---

### get_dominant_future（参数）

**签名:** `get_dominant_future(underlying_symbol, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 参数

---

### get_extras（得到多只标的在一段时间的如下额外的数据:）

**签名:** `get_extras(info, security_list, start_date='2015-01-01', end_date='2015-12-31', df=True, count=None)`
**章节:** 策略API > 策略API介绍
**说明:** 得到多只标的在一段时间的如下额外的数据:

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| info |  | 是 | [‘futures_sett_price’，‘futures_positions’] 中的一个 |
| security_list |  | 是 | 标的列表 |
| start_date/end_date |  | 是 | 开始结束日期, 同[get_price] |
| df |  | 是 | 返回[pandas.DataFrame]对象还是一个dict, 同[history] |

---

### get_fundamentals（查询财务数据）

**签名:** `get_fundamentals(query_object, date=None, statDate=None)`
**章节:** 策略API > 策略API介绍
**说明:** 查询财务数据，详细的财务数据表及字段描述请点击财务数据文档查看，Query 对象的使用方法请参考Query的简单教程

---

### get_fundamentals_continuously（查询多日财务数据）

**签名:** `get_fundamentals_continuously(query_object, end_date=None,count=None, panel=True)`
**章节:** 策略API > 策略API介绍
**说明:** 查询多日财务数据，详细的财务数据表及字段描述请点击财务数据文档查看，Query 对象的使用方法请参考Query的简单教程

---

### get_future_contracts（获取某期货品种在策略当前日期的可交易合约标的列表）

**签名:** `get_future_contracts(security, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取某期货品种在策略当前日期的可交易合约标的列表

---

### get_history_fundamentals（获取多个季度/年度的三大财务报表和财务指标数据）

**签名:** `get_history_fundamentals(security, fields, watch_date=None, stat_date=None, count=1, interval='1q', stat_by_year=False)`
**章节:** 策略API > 策略API介绍
**说明:** 获取多个季度/年度的三大财务报表和财务指标数据. 可指定单季度数据, 也可以指定年度数据。可以指定观察日期, 也可以指定最后一个报告期的结束日期

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| security：股票代码或者股票代码列表。 |  | 是 |  |
| fields：要查询的财务数据的列表, 季度数据和年度数据可选择的列不同。示例：[balance.cash_equivalents, cash_flow.net_deposit_increase, income.total_operating_revenue] |  | 是 |  |
| watch_date：观察日期, 如果指定, 将返回 watch_date 日期前(包含该日期)发布的报表数据 |  | 是 |  |
| stat_date：统计日期, 可以是 '2019'/'2019q1'/'2018q4' 格式, 如果指定, 将返回 stat_date 对应报告期及之前的历史报告期的报表数据watch_date 和 stat_date 只能指定一个, 而且必须指定一个如果没有 stat_date 指定报告期的数据, 则该数据会缺失一行. |  | 是 |  |
| watch_date 和 stat_date 只能指定一个, 而且必须指定一个 |  | 是 |  |
| 如果没有 stat_date 指定报告期的数据, 则该数据会缺失一行. |  | 是 |  |
| count：查询历史的多个报告期时, 指定的报告期数量. 如果股票历史报告期的数量小于 count, 则该股票返回的数据行数将小于 count |  | 是 |  |
| interval：查询多个报告期数据时, 指定报告期间隔, 可选值 | '1q'/'1y', 表示间隔一季度或者一年, 举例说明:stat_date='2019q1', interval='1q', count=4, 将返回 2018q2,2018q3,2018q4,2019q1 的数据stat_date='2019q1', interval='1y', count=4, 将返回 2016q1,2017q1,2018q1,2019q1 的数据stat_by_year=True, stat_date='2018', interval='1y', count=4 将返回 2015/2016/2017/2018 年度的年报数据 | 是 |  |
| stat_date='2019q1', interval='1q', count=4, 将返回 2018q2,2018q3,2018q4,2019q1 的数据 |  | 是 |  |
| stat_date='2019q1', interval='1y', count=4, 将返回 2016q1,2017q1,2018q1,2019q1 的数据 |  | 是 |  |
| stat_by_year=True, stat_date='2018', interval='1y', count=4 将返回 2015/2016/2017/2018 年度的年报数据 |  | 是 |  |
| stat_by_year：bool, 是否返回年度数据. 默认返回的按季度统计的数据(比如income表中只有单个季度的利润).如果是True：interval必须是 '1y'如果指定了 stat_date 的话, stat_date 必须是一个代表年份整数、字符串, 表明统计的年份，比如2019, "2019"。但不能是"20191q"这种格式。fields 可以选择 balance/income/cash_flow/indicator/bank_indicator/security_indicator/insurance_indicator 表中的列如果是False：fields只能选择balance/income/cash_flow/indicator 表中的列 |  | 是 |  |
| 如果是True：interval必须是 '1y'如果指定了 stat_date 的话, stat_date 必须是一个代表年份整数、字符串, 表明统计的年份，比如2019, "2019"。但不能是"20191q"这种格式。fields 可以选择 balance/income/cash_flow/indicator/bank_indicator/security_indicator/insurance_indicator 表中的列 |  | 是 |  |
| interval必须是 '1y' |  | 是 |  |
| 如果指定了 stat_date 的话, stat_date 必须是一个代表年份整数、字符串, 表明统计的年份，比如2019, "2019"。但不能是"20191q"这种格式。 |  | 是 |  |
| fields 可以选择 balance/income/cash_flow/indicator/bank_indicator/security_indicator/insurance_indicator 表中的列 |  | 是 |  |
| 如果是False：fields只能选择balance/income/cash_flow/indicator 表中的列 |  | 是 |  |

**返回值:** pandas.DataFrame, 数据库查询结果. 数据格式同 get_fundamentals. 每个股票每个报告期(一季度或者一年)的数据占用一行.

---

### get_index_stocks（获取一个指数给定日期在平台可交易的成分股列表）

**签名:** `get_index_stocks(index_symbol, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取一个指数给定日期在平台可交易的成分股列表，请点击指数列表查看指数信息

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| index_symbol, 指数代码 |  | 是 |  |
| date |  | 是 | 查询日期, 一个字符串(格式类似’2015-10-15’)或者[datetime.date]/[datetime.datetime]对象, 可以是None, 使用默认日期. 这个默认日期在回测和研究模块上有点差别: |

---

### get_index_weights（获取指数成分股权重）

**签名:** `get_index_weights(index_id, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取指数成分股权重，每月更新一次，一般在月底或者月初参数

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| index_id |  | 是 | 代表指数的标准形式代码， 形式：指数代码.交易所代码，例如"000001.XSHG"。 |
| date |  | 是 | 查询权重信息的日期，形式："%Y-%m-%d"，例如"2018-05-03"；date可以是None，当date=None时，返回最近一次更新的指数成份股权重。 |

---

### get_industries（按照行业分类获取行业列表）

**签名:** `fromjqdataimport* get_industries(name, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 按照行业分类获取行业列表。

---

### get_industry（参数）

**签名:** `get_industry(security, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 参数

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| security：标的代码，类型为字符串，形式如"000001.XSHE"；或为包含标的代码字符串的列表，形如["000001.XSHE", "000002.XSHE"] |  | 是 |  |
| date：查询的日期。类型为字符串，形如"2018-06-01"或"2018-06-01 09:00:00"；或为datetime.datetime对象和datetime.date。注意传入对象的时分秒将被忽略。 |  | 是 |  |

---

### get_industry_stocks（获取在给定日期一个行业的所有股票）

**签名:** `get_industry_stocks(industry_code, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取在给定日期一个行业的所有股票，行业分类列表见数据页面-行业概念数据。

---

### get_margincash_stocks（参数date: 查询日期）

**签名:** `get_margincash_stocks()`
**章节:** 策略API > 策略API介绍
**说明:** 参数date: 查询日期，回测模块中若不填，日期默认为回测的日期；研究模块中若不填，默认为最新日期；也可指定日期。

---

### get_marginsec_stocks（参数date: 查询日期）

**签名:** `get_marginsec_stocks(date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 参数date: 查询日期，回测模块中若不填，日期默认为回测的日期；研究模块中若不填，默认为最新日期；也可指定日期。

---

### get_money_flow（获取一只或者多只股票在一个时间段内的资金流向数据）

**签名:** `fromjqdataimport* get_money_flow(security_list, start_date=None, end_date=None, fields=None, count=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取一只或者多只股票在一个时间段内的资金流向数据，仅包含股票数据，不可用于获取期货数据;提供2010年至今的数据，数据频率为天;净额 : 为正是资金流入, 为负为资金流出;

---

### get_mtss（获取一只或者多只股票在一个时间段内的融资融券信息）

**签名:** `fromjqdataimport* get_mtss(security_list, start_date=None, end_date=None, fields=None, count=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取一只或者多只股票在一个时间段内的融资融券信息

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| security_list |  | 是 | 一只股票代码或者一个股票代码的 list |
| start_date |  | 是 | 开始日期, 一个字符串或者datetime.datetime/datetime.date对象 |
| end_date |  | 是 | 结束日期, 一个字符串或者datetime.date/datetime.datetime对象 |
| fields |  | 是 | 字段名或者 list, 可选. 默认为 None, 表示取全部字段, 各字段含义如下： |

---

### get_open_orders（获得当天的所有未完成的订单）

**签名:** `get_open_orders()`
**章节:** 策略API > 策略API介绍
**说明:** 获得当天的所有未完成的订单

---

### get_orders（获取当天的所有订单）

**签名:** `get_orders(order_id=None, security=None, status=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取当天的所有订单

---

### get_price（获取一支或者多只股票的行情数据）

**签名:** `get_price(security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='pre', count=None, panel=True, fill_paused=True)`
**章节:** 策略API > 策略API介绍
**说明:** 获取一支或者多只股票的行情数据, 按天或者按分钟，这里在使用时注意 end_date 的设置， 传入的值不要大于context.current_dt，否则会引入未来函数。

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| 当取分钟数据时, 时间可以精确到分钟, 比如 |  | 是 | 传入datetime.datetime(2015, 1, 1, 10, 0, 0)或者'2015-01-01 10:00:00'. |
| 当取分钟数据时, 如果只传入日期, 则日内时间是当日的 00:00:00. |  | 是 |  |
| 当取天数据时, 传入的日内时间会被忽略 |  | 是 |  |

---

### get_security_info（获取股票/基金/指数/期货的信息）

**签名:** `get_security_info(code, date=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取股票/基金/指数/期货的信息.

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code |  | 是 | 指数代码 |

---

### get_ticks（股票部分）

**签名:** `get_ticks(security, end_dt, start_dt=None, count=None, fields=['time','current','high','low','volume','money'], skip=True, df=False)`
**章节:** 策略API > 策略API介绍

---

### get_trade_day（获取指定时刻标的对应的交易日）

**签名:** `get_trade_day(security, query_dt)`
**章节:** 策略API > 策略API介绍
**说明:** 获取指定时刻标的对应的交易日。返回一个dict，key为标的代码，value为标的在此时刻对应的交易日。

---

### get_trade_days（获取指定日期范围内的所有交易日）

**签名:** `fromjqdataimport* get_trade_days(start_date=None, end_date=None, count=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取指定日期范围内的所有交易日, 返回一个包含datetime.date object的列表, 包含指定的 start_date 和 end_date, 默认返回至 datetime.date.today() 的所有交易日

---

### get_trades（获取当天的所有成交记录）

**签名:** `get_trades()`
**章节:** 策略API > 策略API介绍
**说明:** 获取当天的所有成交记录, 一个订单可能分多次成交

---

### get_valuation（获取多个标的在指定交易日范围内的市值表数据）

**签名:** `fromjqdataimport* get_valuation(security, start_date=None, end_date=None, fields=None, count=None)`
**章节:** 策略API > 策略API介绍
**说明:** 获取多个标的在指定交易日范围内的市值表数据

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| security |  | 是 | 标的code字符串列表或者单个标的字符串 |
| end_date |  | 是 | 查询结束时间 |
| start_date |  | 是 | 查询开始时间，不能与count共用 |
| count |  | 是 | 表示往前查询每一个标的count个交易日的数据，如果期间标的停牌，则该标的返回的市值数据数量小于count |
| fields |  | 是 | 财务数据中市值表的字段，返回结果中总会包含code、day字段，可用字段如下： |

**返回值:** 返回一个dataframe，索引默认是pandas的整数索引，返回的结果中总会包含code、day字段。

---

### handle_tick（该函数在策略订阅的标的产生 tick 事件时被调用一次）

**签名:** `handle_tick(context, tick)`
**章节:** 策略API > 策略API介绍
**说明:** 该函数在策略订阅的标的产生 tick 事件时被调用一次。如果没有 tick 事件， 则不会被调用。

---

### history（回测环境/模拟专用API）

**签名:** `history(count, unit='1d', field='avg', security_list=None, df=True, skip_paused=False, fq='pre')`
**章节:** 策略API > 策略API介绍
**说明:** 回测环境/模拟专用API，可以在投资研究中获取

---

### inout_cash（账户转入或转出资金）

**签名:** `inout_cash(cash, pindex=0)`
**章节:** 策略API > 策略API介绍
**说明:** 账户转入或转出资金，当日的出入金从当日开始记入成本，用于计算收益，即当日结束计算收益时的本金是包含当日出入金金额的；

---

### is_dangerous（判断指定仓位）

**签名:** `context.subportfolios[i].is_dangerous(margin_rate)`
**章节:** 策略API > 策略API介绍
**说明:** 判断指定仓位，是否低于指定的保证金比率，高于该比例返回False，低于该比例返回True.

---

### jqlib（聚宽工具库）

**签名:** ``
**章节:** 策略API > 策略API介绍

---

### margincash_close（卖券还款）

**签名:** `margincash_close(security, amount, style=None, pindex=0)`
**章节:** 策略API > 策略API介绍
**说明:** 卖券还款

---

### margincash_direct_refund（直接还款）

**签名:** `margincash_direct_refund(value, pindex=0)`
**章节:** 策略API > 策略API介绍
**说明:** 直接还款

---

### margincash_open（融资买入）

**签名:** `margincash_open(security, amount, style=None, pindex=0)`
**章节:** 策略API > 策略API介绍
**说明:** 融资买入

---

### marginsec_close（买券还券）

**签名:** `marginsec_close(security, amount, style=None, pindex=0)`
**章节:** 策略API > 策略API介绍
**说明:** 买券还券

---

### marginsec_direct_refund（直接还券）

**签名:** `marginsec_direct_refund(security, amount, pindex=0)`
**章节:** 策略API > 策略API介绍
**说明:** 直接还券

---

### marginsec_open（融券卖出）

**签名:** `marginsec_open(security, amount, style=None, pindex=0)`
**章节:** 策略API > 策略API介绍
**说明:** 融券卖出

---

### normalize_code（将其他形式的股票代码转换为聚宽可用的股票代码形式）

**签名:** `normalize_code()`
**章节:** 策略API > 策略API介绍
**说明:** 将其他形式的股票代码转换为聚宽可用的股票代码形式。

---

### order（买卖标的）

**签名:** `order(security, amount, style=None, side='long', pindex=0, close_today=False)`
**章节:** 策略API > 策略API介绍
**说明:** 买卖标的。调用成功后, 您将可以调用[get_open_orders]取得所有未完成的交易, 也可以调用[cancel_order]取消交易

---

### order_target（买卖标的）

**签名:** `order_target(security, amount, style=None, side='long', pindex=0, close_today=False)`
**章节:** 策略API > 策略API介绍
**说明:** 买卖标的, 使最终标的的数量达到指定的amount，注意使用此接口下单时若指定的标的有未完成的订单，则先前未完成的订单将会被取消

---

### order_target_value（调整标的仓位到value价值）

**签名:** `order_target_value(security, value, style=None, side='long', pindex=0, close_today=False)`
**章节:** 策略API > 策略API介绍
**说明:** 调整标的仓位到value价值，注意使用此接口下单时若指定的标的有未完成的订单，则先前未完成的订单将会被取消

---

### order_value（买卖价值为value的标的）

**签名:** `order_value(security, value, style=None, side='long', pindex=0, close_today=False)`
**章节:** 策略API > 策略API介绍
**说明:** 买卖价值为value的标的。

---

### portfolio_optimizer（组合优化函数）

**签名:** `portfolio_optimizer(date, securities, target, constraints, bounds=[Bound(0.0,1.0)], default_port_weight_range=[0.0,1.0], ftol=1e-9, return_none_if_fail=True)`
**章节:** 策略API > 策略API介绍
**说明:** 优化函数, 用于计算在某些约束条件下的最优组合权重

---

### read_file（读取私有文件）

**签名:** `read_file(path)`
**章节:** 策略API > 策略API介绍
**说明:** 在回测及模拟交易中读取你的私有文件(您的私有文件可以在研究模块中看到)在回测及模拟交易中读取/写入研究中不同格式的文件

---

### record（回测环境/模拟专用API）

**签名:** `record(**kwargs)`
**章节:** 策略API > 策略API介绍
**说明:** 回测环境/模拟专用API

---

### run_query（查询深沪港通、股东信息、公司概况等数据）

**签名:** `fromjqdataimport* finance.run_query(query_object)`
**章节:** 策略API > 策略API介绍
**说明:** 查询深沪港通、股东信息、公司概况等数据，详细的数据字段描述请点击市场通（沪港通深港通和港股通）查看

---

### send_message（聚宽官网实时运行模拟交易专用API）

**签名:** `send_message(message,channel='weixin')`
**章节:** 策略API > 策略API介绍
**说明:** 聚宽官网实时运行模拟交易专用API

---

### set_benchmark（默认我们选定了沪深300指数的每日价格作为判断您策略好坏和一系列风险值计算的基准）

**签名:** `set_benchmark(security)`
**章节:** 策略API > 策略API介绍
**说明:** 默认我们选定了沪深300指数的每日价格作为判断您策略好坏和一系列风险值计算的基准. 您也可以使用set_benchmark指定其他股票/指数/ETF/自定义组合的价格作为基准。

---

### set_commission（已废弃）

**签名:** `set_commission(object)`
**章节:** 策略API > 策略API介绍
**说明:** 已废弃。请使用set_order_cost替代

---

### set_option（该设定必须在initialize中调用）

**签名:** `set_option('use_real_price', value)`
**章节:** 策略API > 策略API介绍
**说明:** 该设定必须在initialize中调用，建议开启设置是否开启动态复权（真实价格）模式，默认是False(主要是为了让旧的策略不会出错)。
是否开启动态复权模式对模拟交易是有影响的，原理参考拆分合并与分红，【API解析】| 动态复权与技术指标。

---

### set_order_cost（指定每笔交易要收取的手续费）

**签名:** `set_order_cost(cost, type, ref=None)`
**章节:** 策略API > 策略API介绍
**说明:** 指定每笔交易要收取的手续费, 系统会根据用户指定的费率计算每笔交易的手续费

---

### set_slippage（设定滑点）

**签名:** `set_slippage(object,type=None, ref=None)`
**章节:** 策略API > 策略API介绍
**说明:** 设定滑点，回测/模拟时有效.

---

### set_subportfolios（初始化或者修改 subportfolios 的配置）

**签名:** `set_subportfolios([SubPortfolioConfig(cash,type), ... ])`
**章节:** 策略API > 策略API介绍
**说明:** 初始化或者修改 subportfolios 的配置，只能在 initialize 中调用, 每个 SubPortfolioConfig 中 cash 的和应该等于总的初始资金

---

### set_universe（设置或者更新此策略要操作的股票池 context）

**签名:** `set_universe(security_list)`
**章节:** 策略API > 策略API介绍
**说明:** 设置或者更新此策略要操作的股票池 context.universe. 请注意:

---

### subscribe（订阅标的的 tick 事件）

**签名:** `subscribe(security, frequency)`
**章节:** 策略API > 策略API介绍
**说明:** 订阅标的的 tick 事件， 必须在频率为 tick 的回测、模拟中使用。

---

### transfer_cash（资金划转）

**签名:** `transfer_cash(from_pindex, to_pindex, cash)`
**章节:** 策略API > 策略API介绍
**说明:** 从序号为 from_pindex 的 subportfolio 转移 cash 到序号为 to_pindex 的 subportfolio
资金转移及时到账

---

### unsubscribe（取消订阅标的的 tick 事件）

**签名:** `unsubscribe(security, frequency)`
**章节:** 策略API > 策略API介绍
**说明:** 取消订阅标的的 tick 事件

---

### unsubscribe_all（取消订阅所有 tick 事件）

**签名:** `unsubscribe_all()`
**章节:** 策略API > 策略API介绍
**说明:** 取消订阅所有 tick 事件

---

### write_file（将回测或者模拟交易的数据写入投资研究path文件）

**签名:** `write_file(path, content, append=False)`
**章节:** 策略API > 策略API介绍
**说明:** 将回测或者模拟交易的数据写入投资研究path文件, 写入后, 您可以立即在研究模块中看到这个文件,默认在投资研究的根目录在回测及模拟交易中读取/写入研究中不同格式的文件

---

## 股票数据 > 获取股票数据

### 获取行业、概念成份股（获取行业、概念成份股）

**签名:** `# 获取行业板块成分股get_industry_stocks(industry_code, date=None)# 获取概念板块成分股get_concept_stocks(concept_code, date=None)`
**章节:** 股票数据 > 获取股票数据
**说明:** 获取在给定日期一个行业或概念板块的所有股票，行业分类、概念分类列表见数据页面-行业概念数据。

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| industry_code |  | 是 | 行业编码 |
| date |  | 是 | 查询日期, 一个字符串(格式类似’2015-10-15’)或者[datetime.date]/[datetime.datetime]对象, 可以是None, 使用默认日期. 这个默认日期在回测和研究模块上有点差别: |

**返回值:** 返回股票代码的list

**示例代码:**

```python
# 获取计算机/互联网行业的成分股stocks = get_industry_stocks('I64')# 获取风力发电概念板块的成分股stocks = get_concept_stocks('GN036')
```

---

## JQData使用说明 > 股票

### STK_AH_PRICE_COMP（记录同时在A股和H股上市的股票的价格比对）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_AH_PRICE_COMP).filter(finance.STK_AH_PRICE_COMP.a_code==a_code).order_by(finance.STK_AH_PRICE_COMP.day).limit(n)`
**章节:** JQData使用说明 > 股票
**说明:** 记录同时在A股和H股上市的股票的价格比对。

---

### STK_EL_CONST_CHANGE（记录沪港通、深港通和港股通的成分股的变动情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EL_CONST_CHANGE).filter(finance.STK_EL_CONST_CHANGE.code==code).limit(n))`
**章节:** JQData使用说明 > 股票
**说明:** 记录沪港通、深港通和港股通的成分股的变动情况。

---

### STK_EL_TOP_ACTIVATE（统计沪港通、深港通和港股通前十大交易活跃股的交易状况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EL_TOP_ACTIVATE).filter(finance.STK_EL_TOP_ACTIVATE.code==code).limit(n))`
**章节:** JQData使用说明 > 股票
**说明:** 统计沪港通、深港通和港股通前十大交易活跃股的交易状况。

---

### STK_EXCHANGE_LINK_CALENDAR（记录沪港通、深港通和港股通每天是否开市）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EXCHANGE_LINK_CALENDAR).filter(finance.STK_EXCHANGE_LINK_CALENDAR.day==day).limit(n))`
**章节:** JQData使用说明 > 股票
**说明:** 记录沪港通、深港通和港股通每天是否开市。

---

### STK_EXCHANGE_LINK_RATE（包含2014年11月起人民币和港币之间的参考汇率/结算汇兑比率信息）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EXCHANGE_LINK_RATE).filter(finance.STK_EXCHANGE_LINK_RATE.day==day).limit(n))`
**章节:** JQData使用说明 > 股票
**说明:** 包含2014年11月起人民币和港币之间的参考汇率/结算汇兑比率信息。

---

### STK_EXCHANGE_TRADE_INFO（记录沪深两市股票交易的成交情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EXCHANGE_TRADE_INFO).filter(finance.STK_EXCHANGE_TRADE_INFO.exchange_code==exchange_code).limit(n)`
**章节:** JQData使用说明 > 股票
**说明:** 记录沪深两市股票交易的成交情况，包括市值、成交量，市盈率等情况。

---

### STK_HK_HOLD_INFO（记录了北向资金（沪股通、深股通）和南向资金港股通的持股数量和持股比例）

**签名:** `from jqdatasdk import finance df=finance.run_query(query(finance.STK_HK_HOLD_INFO).filter(finance.STK_HK_HOLD_INFO.link_id==310001)) print(df)`
**章节:** JQData使用说明 > 股票
**说明:** 记录了北向资金（沪股通、深股通）和南向资金港股通的持股数量和持股比例

---

### STK_ML_QUOTA（记录沪股通、深股通和港股通每个交易日的成交与额度的控制情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_ML_QUOTA).filter(finance.STK_ML_QUOTA.day==day).limit(n))`
**章节:** JQData使用说明 > 股票
**说明:** 记录沪股通、深股通和港股通每个交易日的成交与额度的控制情况。

---

### STK_MT_TOTAL（描述：记录上海交易所和深圳交易所的融资融券汇总数据）

**签名:** `fromjqdatasdkimport* finance.run_query(query(finance.STK_MT_TOTAL).filter(finance.STK_MT_TOTAL.date=='2019-05-23').limit(n))`
**章节:** JQData使用说明 > 股票
**说明:** 描述：记录上海交易所和深圳交易所的融资融券汇总数据

---

### SW1_DAILY_PRICE（记录了申万一级行业指数的历史日行情数据）

**签名:** `df=finance.run_query(query(finance.SW1_DAILY_PRICE).filter(finance.SW1_DAILY_PRICE.code=='801010').limit(n)) print(df)`
**章节:** JQData使用说明 > 股票
**说明:** 记录了申万一级行业指数的历史日行情数据，每日18:00更新。

---

### get_locked_shares（获取指定日期区间内的限售解禁数据）

**签名:** `get_locked_shares(stock_list, start_date, end_date, forward_count)`
**章节:** JQData使用说明 > 股票
**说明:** 获取指定日期区间内的限售解禁数据

---

## JQData使用说明 > 上市公司基础信息

### STK_CAPITAL_CHANGE（获取上市公司的股本变动情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_CAPITAL_CHANGE).filter(finance.STK_CAPITAL_CHANGE.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司的股本变动情况

---

### STK_COMPANY_INFO（获取上市公司最新公布的基本信息）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_COMPANY_INFO).filter(finance.STK_COMPANY_INFO.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司最新公布的基本信息，包含注册资本，主营业务，行业分类等。

---

### STK_EMPLOYEE_INFO（获取上市公司在公告中公布的员工情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_EMPLOYEE_INFO).filter(finance.STK_EMPLOYEE_INFO.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司在公告中公布的员工情况，包括员工人数、学历等信息

---

### STK_HOLDER_NUM（获取上市公司全部股东户数）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_HOLDER_NUM).filter(finance.STK_HOLDER_NUM.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司全部股东户数，A股股东、B股股东、H股股东的持股户数

---

### STK_LIMITED_SHARES_LIST（获取上市公司受限股份上市公告日期和预计解禁日期）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_LIMITED_SHARES_LIST).filter(finance.STK_LIMITED_SHARES_LIST.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司受限股份上市公告日期和预计解禁日期。

---

### STK_LIMITED_SHARES_UNLIMIT（获取公司已上市的受限股份实际解禁的日期）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_LIMITED_SHARES_UNLIMIT).filter(finance.STK_LIMITED_SHARES_UNLIMIT.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取公司已上市的受限股份实际解禁的日期。

---

### STK_LIST（获取沪深A股的上市信息）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_LIST).filter(finance.STK_LIST.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取沪深A股的上市信息，包含上市日期、交易所、发行价格、初始上市数量等

---

### STK_MANAGEMENT_INFO（记录上市公司管理人员的任职情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_MANAGEMENT_INFO).filter(finance.STK_MANAGEMENT_INFO.code==code).order_by(finance.STK_MANAGEMENT_INFO.pub_date).limit(n)`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 记录上市公司管理人员的任职情况。

---

### STK_NAME_HISTORY（获取在A股市场和B股市场上市的股票简称的变更情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_NAME_HISTORY).filter(finance.STK_NAME_HISTORY.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取在A股市场和B股市场上市的股票简称的变更情况

---

### STK_SHAREHOLDERS_SHARE_CHANGE（获取上市公司大股东的增减持情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHAREHOLDERS_SHARE_CHANGE).filter(finance.STK_SHAREHOLDERS_SHARE_CHANGE.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司大股东的增减持情况。

---

### STK_SHAREHOLDER_FLOATING_TOP10（获取上市公司前十大流通股东的持股情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHAREHOLDER_FLOATING_TOP10).filter(finance.STK_SHAREHOLDER_FLOATING_TOP10.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司前十大流通股东的持股情况，包括持股数量，所持股份性质，变动原因等。

---

### STK_SHAREHOLDER_TOP10（获取上市公司前十大股东的持股情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHAREHOLDER_TOP10).filter(finance.STK_SHAREHOLDER_TOP10.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司前十大股东的持股情况，包括持股数量，所持股份性质，变动原因等。

---

### STK_SHARES_FROZEN（获取上市公司股东股份的冻结情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHARES_FROZEN).filter(finance.STK_SHARES_FROZEN.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司股东股份的冻结情况

---

### STK_SHARES_PLEDGE（获取上市公司股东股份的质押情况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_SHARES_PLEDGE).filter(finance.STK_SHARES_PLEDGE.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司股东股份的质押情况。

---

### STK_STATUS_CHANGE（上市公司状态变动）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_STATUS_CHANGE).filter(finance.STK_STATUS_CHANGE.code==code).limit(n))`
**章节:** JQData使用说明 > 上市公司基础信息
**说明:** 获取上市公司已发行未上市、正常上市、实行ST、*ST、暂停上市、终止上市的变动情况等

---

## 股票数据 > 获取报告期财务数据

### FINANCE_BALANCE_SHEET_PARENT（金融类母公司资产负债表）

**签名:** `from jqdata import finance finance.run_query(query(finance.FINANCE_BALANCE_SHEET_PARENT).filter(finance.FINANCE_BALANCE_SHEET_PARENT.code==code).limit(n))`
**章节:** 股票数据 > 获取报告期财务数据
**说明:** 获取金融类上市公司的母公司资产负债表信息

---

### FINANCE_CASHFLOW_STATEMENT_PARENT（金融类母公司现金流量表）

**签名:** `from jqdata import finance finance.run_query(query(finance.FINANCE_CASHFLOW_STATEMENT_PARENT).filter(finance.FINANCE_CASHFLOW_STATEMENT_PARENT.code==code).limit(n))`
**章节:** 股票数据 > 获取报告期财务数据
**说明:** 获取金融类上市公司的母公司现金流量表信息

---

### FINANCE_INCOME_STATEMENT_PARENT（金融类母公司利润表）

**签名:** `from jqdata import finance finance.run_query(query(finance.FINANCE_INCOME_STATEMENT_PARENT).filter(finance.FINANCE_INCOME_STATEMENT_PARENT.code==code).limit(n))`
**章节:** 股票数据 > 获取报告期财务数据
**说明:** 获取金融类上市公司的母公司利润表信息

---

### STK_AUDIT_OPINION（审计意见(新上线数据)）

**签名:** `fromjqdataimportfinance finance.run_query(query(finance.STK_AUDIT_OPINION).filter(finance.STK_AUDIT_OPINION.code==code).limit(n))`
**章节:** 股票数据 > 获取报告期财务数据
**说明:** 获取上市公司定期报告及审计报告中出具的审计意见

---

### STK_BALANCE_SHEET_PARENT（母公司资产负债表）

**签名:** `from jqdata import finance finance.run_query(query(finance.STK_BALANCE_SHEET_PARENT).filter(finance.STK_BALANCE_SHEET_PARENT.code==code).limit(n))`
**章节:** 股票数据 > 获取报告期财务数据
**说明:** 获取上市公司定期公告中公布的母公司资产负债表（2007版）

---

### STK_INCOME_STATEMENT_PARENT（母公司利润表）

**签名:** `from jqdata import finance finance.run_query(query(finance.STK_INCOME_STATEMENT_PARENT).filter(finance.STK_INCOME_STATEMENT_PARENT.code==code).limit(n))`
**章节:** 股票数据 > 获取报告期财务数据
**说明:** 获取上市公司母公司利润的信息（2007版）

---

### STK_PERFORMANCE_LETTERS（业绩快报(新上线数据)）

**签名:** `fromjqdataimportfinance finance.run_query(query(finance.STK_PERFORMANCE_LETTERS).filter(finance.STK_PERFORMANCE_LETTERS.code==code).limit(n))`
**章节:** 股票数据 > 获取报告期财务数据
**说明:** 获取上市公司业绩快报信息

---

### STK_REPORT_DISCLOSURE（定期报告预约披露时间表(新上线数据)）

**签名:** `fromjqdataimportfinance finance.run_query(query(finance.STK_REPORT_DISCLOSURE).filter(finance.STK_REPORT_DISCLOSURE.code==code).limit(n))`
**章节:** 股票数据 > 获取报告期财务数据
**说明:** 获取上市公司定期报告预约披露及实际披露日期

---

## JQData使用说明 > 财务数据

### FINANCE_BALANCE_SHEET（获取金融类上市公司的合并资产负债表信息）

**签名:** `from jqdatasdk import finance finance.run_query(query(finance.FINANCE_BALANCE_SHEET).filter(finance.FINANCE_BALANCE_SHEET.code==code).limit(n))`
**章节:** JQData使用说明 > 财务数据
**说明:** 获取金融类上市公司的合并资产负债表信息

---

### FINANCE_CASHFLOW_STATEMENT（获取金融类上市公司的合并现金流量表信息）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FINANCE_CASHFLOW_STATEMENT).filter(finance.FINANCE_CASHFLOW_STATEMENT.code==code).limit(n))`
**章节:** JQData使用说明 > 财务数据
**说明:** 获取金融类上市公司的合并现金流量表信息

---

### FINANCE_INCOME_STATEMENT（获取金融类上市公司的合并利润表信息）

**签名:** `from jqdatasdk import finance finance.run_query(query(finance.FINANCE_INCOME_STATEMENT).filter(finance.FINANCE_INCOME_STATEMENT.code==code).limit(n))`
**章节:** JQData使用说明 > 财务数据
**说明:** 获取金融类上市公司的合并利润表信息

---

### STK_BALANCE_SHEET（获取上市公司定期公告中公布的合并资产负债表（2007版））

**签名:** `from jqdatasdk import finance finance.run_query(query(finance.STK_BALANCE_SHEET).filter(finance.STK_BALANCE_SHEET.code==code).limit(n))`
**章节:** JQData使用说明 > 财务数据
**说明:** 获取上市公司定期公告中公布的合并资产负债表（2007版）

---

### STK_CASHFLOW_STATEMENT（获取上市公司定期公告中公布的合并现金流量表数据（2007版））

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_CASHFLOW_STATEMENT).filter(finance.STK_CASHFLOW_STATEMENT.code==code).limit(n))`
**章节:** JQData使用说明 > 财务数据
**说明:** 获取上市公司定期公告中公布的合并现金流量表数据（2007版）

---

### STK_FIN_FORCAST（获取上市公司业绩预告等信息）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.STK_FIN_FORCAST).filter(finance.STK_FIN_FORCAST.code==code).limit(n))`
**章节:** JQData使用说明 > 财务数据
**说明:** 获取上市公司业绩预告等信息

---

### STK_INCOME_STATEMENT（获取上市公司定期公告中公布的合并利润表数据（2007版））

**签名:** `from jqdatasdk import finance finance.run_query(query(finance.STK_INCOME_STATEMENT).filter(finance.STK_INCOME_STATEMENT.code==code).limit(n))`
**章节:** JQData使用说明 > 财务数据
**说明:** 获取上市公司定期公告中公布的合并利润表数据（2007版）

---

## JQData使用说明 > 合并现金流量表

### STK_CASHFLOW_STATEMENT_PARENT（母公司现金流量表）

**签名:** `from jqdatasdk import finance finance.run_query(query(finance.STK_CASHFLOW_STATEMENT_PARENT).filter(finance.STK_CASHFLOW_STATEMENT_PARENT.code==code).limit(n))`
**章节:** JQData使用说明 > 合并现金流量表
**说明:** 获取上市公司定期公告中公布的母公司现金流量表（2007版）

---

## JQData使用说明 > 基金

### FUND_DIVIDEND（描述：记录基金分红、拆分和合并的方案）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_DIVIDEND).filter(finance.FUND_DIVIDEND.code==code).limit(n))`
**章节:** JQData使用说明 > 基金
**说明:** 描述：记录基金分红、拆分和合并的方案

---

### FUND_FIN_INDICATOR（描述：基金财务指标表）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_FIN_INDICATOR).filter(finance.FUND_FIN_INDICATOR.code==code).limit(n))`
**章节:** JQData使用说明 > 基金
**说明:** 描述：基金财务指标表

---

### FUND_MAIN_INFO（描述：记录不同基金的主体信息）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_MAIN_INFO).filter(finance.FUND_MAIN_INFO.main_code==main_code).limit(n))`
**章节:** JQData使用说明 > 基金
**说明:** 描述：记录不同基金的主体信息

---

### FUND_MF_DAILY_PROFIT（描述：货币基金收益日报）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_MF_DAILY_PROFIT).filter(finance.FUND_MF_DAILY_PROFIT.code==code).limit(n))`
**章节:** JQData使用说明 > 基金
**说明:** 描述：货币基金收益日报

---

### FUND_NET_VALUE（描述：记录公募基金的净值数据）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_NET_VALUE).filter(finance.FUND_NET_VALUE.code==code).limit(n))`
**章节:** JQData使用说明 > 基金
**说明:** 描述：记录公募基金的净值数据

---

### FUND_PORTFOLIO（描述：基金资产组合概况）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_PORTFOLIO).filter(finance.FUND_PORTFOLIO.code==code).limit(n))`
**章节:** JQData使用说明 > 基金
**说明:** 描述：基金资产组合概况

---

### FUND_PORTFOLIO_BOND（描述：记录公募基金按季度公布的债券组合）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_PORTFOLIO_BOND).filter(finance.FUND_PORTFOLIO_BOND.code==code).limit(n))`
**章节:** JQData使用说明 > 基金
**说明:** 描述：记录公募基金按季度公布的债券组合，为债券投资者提供一些参照

---

### FUND_PORTFOLIO_STOCK（描述：统计基金季度报表、半年度报表和年度报表披露的股票持仓数据）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUND_PORTFOLIO_STOCK).filter(finance.FUND_PORTFOLIO_STOCK.code==code).limit(n))`
**章节:** JQData使用说明 > 基金
**说明:** 描述：统计基金季度报表、半年度报表和年度报表披露的股票持仓数据

---

### FUND_SHARE_DAILY（描述：记录每日场内基金份额数据）

**签名:** `fromjqdatasdkimport* finance.run_query(query(finance.FUND_SHARE_DAILY).filter(finance.FUND_SHARE_DAILY.date=='2019-05-23').limit(n))`
**章节:** JQData使用说明 > 基金
**说明:** 描述：记录每日场内基金份额数据

---

## 场内基金数据 > 获取基金数据

### FUND_INVEST_TARGET（获取etf跟踪指数信息）

**签名:** `from jqdata import*finance.run_query(query(finance.FUND_INVEST_TARGET).filter(finance.FUND_INVEST_TARGET.code== '510190.XSHG'))`
**章节:** 场内基金数据 > 获取基金数据
**说明:** 字段设计：

---

### 基金列表（基金列表）

**签名:** `df = get_all_securities("fund")#获取所有场内基金df[df['type'] =='reits']# 获取所有reits基金df[df.display_name.str.contains("指\|增")]#获取名称中含"指"或"增" 的场内基金df[df.display_name.str.contains("指")&df.display_name.str.contains("增")]#获取名称中含"指"和"增" 的场内基金`
**章节:** 场内基金数据 > 获取基金数据
**说明:** 我们目前提供了所有上市交易的场内基金数据(含已退市)，包含ETF、LOF、分级AB(已全部退市)、货币基金及reits基金

---

## JQData使用说明 > 期货

### FUT_GLOBAL_DAILY（描述：记录主要外盘商品期货的日行情数据）

**签名:** `fromjqdatasdkimportfinance df=finance.run_query(query(finance.FUT_GLOBAL_DAILY).filter(finance.FUT_GLOBAL_DAILY.day==date).limit(n))`
**章节:** JQData使用说明 > 期货
**说明:** 描述：记录主要外盘商品期货的日行情数据，包含开盘价、收盘价、最高价、最低价、成交量等

---

### FUT_MEMBER_POSITION_RANK（描述：记录各个期货交易所对不同商品下的期货合约）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUT_MEMBER_POSITION_RANK).filter(finance.FUT_MEMBER_POSITION_RANK.code==code).limit(n))`
**章节:** JQData使用说明 > 期货
**说明:** 描述：记录各个期货交易所对不同商品下的期货合约，记录该交易所会员持仓排名前20的信息。（每天更新）

---

### FUT_WAREHOUSE_RECEIPT（描述：期货仓单是指由期货交易所指定交割仓库）

**签名:** `fromjqdatasdkimportfinance finance.run_query(query(finance.FUT_WAREHOUSE_RECEIPT).filter(finance.FUT_WAREHOUSE_RECEIPT.underlying_code==underlying_code).limit(n))`
**章节:** JQData使用说明 > 期货
**说明:** 描述：期货仓单是指由期货交易所指定交割仓库，按照期货交易所指定的程序，签发的符合合约规定质量的实物提货凭证。记录了交易所所有期货实物的库存情况以及变更情况。

---

### get_futures_info（参数）

**签名:** `get_futures_info(securities=None, fields=('contract_multiplier','tick_size','trade_time'))`
**章节:** JQData使用说明 > 期货
**说明:** 参数

---

## 期货数据 > 获取期货数据

### FUT_CHARGE（期货手续费及保证金）

**签名:** `fromjqdataimportfinance finance.run_query(query(finance.FUT_CHARGE).filter(finance.FUT_CHARGE.day==date).limit(n))`
**章节:** 期货数据 > 获取期货数据
**说明:** 描述：获取期货手续费。注意这是结算参数，正常是盘后更新，但是盘前也可以根据公告推导,因此盘前(含夜盘)是推算得到的，准确的结算参数需要在盘后 17:00 之后获取

---

### FUT_MARGIN（获取期货保证金）

**签名:** `fromjqdataimportfinance finance.run_query(query(finance.FUT_MARGIN).filter(finance.FUT_MARGIN.day==date).limit(n))`
**章节:** 期货数据 > 获取期货数据
**说明:** 描述：获取期货保证金(结算参数)。

---

## JQData使用说明 > JQData-本地量化数据说明书

### auth（认证登录）

**签名:** `fromjqdatasdkimport* auth('ID','Password')#ID是申请时所填写的手机号；Password为聚宽官网登录密码`
**章节:** JQData使用说明 > JQData-本地量化数据说明书
**说明:** 打开代码编辑器（第三方编辑器请指定运行环境为已安装JQData的Python环境），输入如下代码认证用户身份。认证完毕后显示“auth success”即可开始调用数据，认证步骤如下：

---

### get_query_count（描述：查看当日剩余可调用条数）

**签名:** `get_query_count()`
**章节:** JQData使用说明 > JQData-本地量化数据说明书
**说明:** 描述：查看当日剩余可调用条数，试用账号默认是每日50万条；正式账号是每日2亿条。说明：一行表示一条，如下图；如果不确定的话，可以在调用前后分别查询下可调用条数

---

### uctrlfu（由于内容较多，可使用Ctrl+F搜索您需要的数据。）

**签名:** ``
**章节:** JQData使用说明 > JQData-本地量化数据说明书

---

## 策略API > 非交易时段下单的特别说明

### print（投资组合优化器）

**签名:** `# 导入函数库importpandasaspdfromjqdataimport*fromjqfactorimportFactorfromjqlib.optimizerimport*# 初始化函数，设定基准等等definitialize(context):# 设定沪深300作为基准set_benchmark('000300.XSHG')# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 过滤掉order系列API产生的比error级别低的log# log.set_level('order', 'error')### 股票相关设定 #### 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003,                             min_commission=5), type='stock')# 优化器设置g.optimizer =2#设定使用的优化模型optimize_model = {1:"模型1：等权重配置",2:"模型2：组合风险平价；股票的总权重限制为0到90%，ETF的总权重限制为0到10%；每只标的权重不超过10%",3:"模型3：组合风险最小化（最小化组合方差）；组合总权重限制为90%到100%；组合年化收益率目标下限为10%",4:"模型4：'人气指标5日均值'最大化；组合年化收益率目标下限为10%；每只标的权重不超过20%",5:"模型5：组合夏普比率最大化；每只标的权重不超过10%"}     print("优化%s"%(optimize_model[g.optimizer]))## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）# 开盘前运行run_monthly(before_market_open, monthday=1, time='9:00', reference_security='000300.XSHG')# 开盘运行run_monthly(market_open, monthday=1, time='9:30', reference_security='000300.XSHG')## 开盘前运行函数defbefore_market_open(context):print('调仓日期：%s'%context.current_dt.date())# 选出上证50成分股的一部分与选定的ETF基金进行组合,构成股票池。etf = ['159902.XSHE','159903.XSHE','510050.XSHG','510880.XSHG','510440.XSHG',         ]     g.buy_list = list(get_index_stocks('000016.XSHG')[-15:]) + etf## 开盘时运行函数defmarket_open(context):# 将不在股票池中的股票卖出sell_list = set(context.portfolio.positions.keys()) - set(g.buy_list)forstockinsell_list:         order_target_value(stock,0)# 组合优化模型ifg.optimizer ==1:# 模型1：等权重配置optimized_weight = pd.Series(data=[1.0/len(g.buy_list)]*len(g.buy_list),                                     index=g.buy_list)elifg.optimizer ==2:# 模型2：组合风险平价；股票的总权重限制为0到90%，ETF的总权重限制为0到10%；每只标的权重不超过10%optimized_weight = portfolio_optimizer(date=context.previous_date,                                     securities = g.buy_list,                                     target = RiskParity(count=250, risk_budget=None),# risk_budget 为 None默认为每只股票贡献相等constraints = [MarketConstraint('stock', low=0.0, high=0.9),                                                   MarketConstraint('etf', low=0.0, high=0.1)],                                     bounds=[Bound(0,0.1)],                                     default_port_weight_range=[0.,1.0],                                     ftol=1e-09,                                     return_none_if_fail=True)elifg.optimizer ==3:# 模型3：组合风险最小化（最小化组合方差）；组合总权重限制为90%到100%；组合年化收益率目标下限为10%optimized_weight = portfolio_optimizer(date=context.previous_date,                                     securities = g.buy_list,                                     target = MinVariance(count=250),                                     constraints = [WeightConstraint(low=0.9, high=1.0),                                                    AnnualProfitConstraint(limit=0.1, count=250)],                                     bounds=[],                                     default_port_weight_range=[0.,1.0],                                     ftol=1e-09,                                     return_none_if_fail=True)elifg.optimizer ==4:# 模型4：组合标的因子值最大化# 定义因子：人气指标5日均值classAR(Factor):name ='ar'# 每天获取过去五日的数据max_window =5# 获取的数据是人气指标dependencies = ['AR']defcalc(self, data):returndata['AR'].mean()# 模型4：'人气指标5日均值'最大化；组合年化收益率目标下限为10%；每只标的权重不超过20%optimized_weight = portfolio_optimizer(date=context.previous_date,                                     securities = g.buy_list,                                     target = MaxFactorValue(factor=AR, count=1),                                     constraints = [AnnualProfitConstraint(limit=0.2, count=250)],                                     bounds=[Bound(0,0.2)],                                     default_port_weight_range=[0.,1.0],                                     ftol=1e-09,                                     return_none_if_fail=True)elifg.optimizer ==5:# 模型5：组合夏普比率最大化；每只标的权重不超过10%optimized_weight = portfolio_optimizer(date=context.previous_date,                                     securities = g.buy_list,                                     target = MaxSharpeRatio(rf=0.0,weight_sum_equal=0.5, count=250),#无风险利率为0，最大化夏普比率需要约束组合权重的和为0.5constraints = [],                                     bounds=[Bound(0,0.1)],                                     default_port_weight_range=[0.,1.0],                                     ftol=1e-09,                                     return_none_if_fail=True)# 查看优化结果print(optimized_weight)# 优化失败，给予警告iftype(optimized_weight) == type(None):         print('警告：组合优化失败')# 按优化结果，执行调仓操作else:         total_value = context.portfolio.total_value# 获取总资产forstockinoptimized_weight.keys():             value = total_value * optimized_weight[stock]# 确定每个标的的权重order_target_value(stock, value)# 调整标的至目标权重`
**章节:** 策略API > 非交易时段下单的特别说明
**说明:** 投资组合优化是指应用概率论与数理统计、最优化方法以及线性代数等相关数学理论方法，根据既定目标收益和风险容许程度（例如最大化收益，最小化风险，风险平价等），将投资重新组合，分散风险的过程，它体现了投资者的意愿和投资者所受到的约束，即在一定风险水平下收益最大化或一定收益水平下的风险最小化。

---

## JQData使用说明 > JQData常见报错及数据处理规则

### filter（数据处理规则）

**签名:** `from jqdata import*q = query(finance.STK_INCOME_STATEMENT.company_name,  finance.STK_INCOME_STATEMENT.code,  finance.STK_INCOME_STATEMENT.pub_date,  finance.STK_INCOME_STATEMENT.start_date,  finance.STK_INCOME_STATEMENT.end_date,  finance.STK_INCOME_STATEMENT.total_operating_revenue,            finance.STK_INCOME_STATEMENT.report_type,           finance.STK_INCOME_STATEMENT.report_date, finance.STK_INCOME_STATEMENT.np_parent_company_owners).filter(      finance.STK_INCOME_STATEMENT.code=='300080.XSHE',      finance.STK_INCOME_STATEMENT.end_date=='2019-03-31',  #     finance.STK_INCOME_STATEMENT.report_type==1).limit(200)  df = finance.run_query(q)df.sort_values(by=['pub_date'],ascending=False)`
**章节:** JQData使用说明 > JQData常见报错及数据处理规则
**说明:** 1. 为什么我在别的网站上查的财务指标和聚宽提供的财务指标数据不一致？

---

## JQData使用说明 > 通用接口

### STK_XR_XD（除权除息数据）

**签名:** `fromjqdatasdkimport* auth(username, pwd) q = query(finance.STK_XR_XD)# 注意需要先登陆,否则会报错表不存在finance.run_query(q)`
**章节:** JQData使用说明 > 通用接口
**说明:** 目前可通过 run_query 方法进行查询的数据都为储存于mysql的数据(单季度数据通过get_fundamentals/get_fundamentals_continuously查询)。根据数据的品种我们大致分为四类 :

---

## JQData使用说明 > 新闻联播文本

### CCTV_NEWS（获取新闻联播每日播报的新闻文本数据）

**签名:** `fromjqdatasdkimport* finance.run_query(query(finance.CCTV_NEWS).filter(finance.CCTV_NEWS.day=='2019-02-19').limit(n))`
**章节:** JQData使用说明 > 新闻联播文本
**说明:** 获取新闻联播每日播报的新闻文本数据，数据来源：央视新闻联播频道，时间范围：2009-06-26至今。

---

## JQData使用说明 > 因子数据（含新接口）

### get_factor_effect（单因子分层回测函数是为了检测单个因子的选股收益效果而设计）

**签名:** `get_factor_effect(security, start_date, end_date, period, factor, group_num=5)`
**章节:** JQData使用说明 > 因子数据（含新接口）
**说明:** 单因子分层回测函数是为了检测单个因子的选股收益效果而设计。指定股票池，根据因子值从小到大将股票池等分成几组，按照一定的调仓周期进行交易，从而得到各个股票组合从开始交易至各个调仓周期结束日期的累计收益，最后从各组股票的收益情况来判断因子的选股效果。

---

## 策略API > 开始写策略

### definitialize（简单但是完整的策略）

**签名:** `definitialize(context):# 定义一个全局变量, 保存要操作的股票g.security ='000001.XSHE'# 运行函数run_daily(market_open, time='every_bar')defmarket_open(context):ifg.securitynotincontext.portfolio.positions:         order(g.security,1000)else:         order(g.security,-800)`
**章节:** 策略API > 开始写策略
**说明:** 先来看一个简单但是完整的策略:

---

### 实用的策略（实用的策略）

**签名:** `# 导入聚宽函数库importjqdata# 初始化函数，设定要操作的股票、基准等等definitialize(context):# 定义一个全局变量, 保存要操作的股票# 000001(股票:平安银行)g.security ='000001.XSHE'# 设定沪深300作为基准set_benchmark('000300.XSHG')# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 运行函数run_daily(market_open, time='every_bar')# 每个单位时间(如果按天回测,则每天调用一次,如果按分钟,则每分钟调用一次)调用一次defmarket_open(context):security = g.security# 获取股票的收盘价close_data = attribute_history(security,5,'1d', ['close'])# 取得过去五天的平均价格MA5 = close_data['close'].mean()# 取得上一时间点价格current_price = close_data['close'][-1]# 取得当前的现金cash = context.portfolio.available_cash# 如果上一时间点价格高出五天平均价1%, 则全仓买入ifcurrent_price >1.01*MA5:# 用所有 cash 买入股票order_value(security, cash)# 记录这次买入log.info("Buying %s"% (security))# 如果上一时间点价格低于五天平均价, 则空仓卖出elifcurrent_price < MA5andcontext.portfolio.positions[security].closeable_amount >0:# 卖出所有股票,使这只股票的最终持有量为0order_target(security,0)# 记录这次卖出log.info("Selling %s"% (security))# 画出上一时间点价格record(stock_price=current_price)`
**章节:** 策略API > 开始写策略
**说明:** 在这个策略里, 我们会根据历史价格做出判断:

---

## 策略API > 撮合流程

### bar（按分钟Bar撮合）

**签名:** ``
**章节:** 策略API > 撮合流程

---

### tick（按tick撮合）

**签名:** ``
**章节:** 策略API > 撮合流程

---

## 策略API > 策略程序架构♠

### after_code_changed（模拟盘在每天的交易时间结束后会休眠）

**签名:** `after_code_changed(context)`
**章节:** 策略API > 策略程序架构♠
**说明:** 模拟盘在每天的交易时间结束后会休眠，第二天开盘时会恢复，如果在恢复时发现代码已经发生了修改，则会在恢复时执行这个函数。
具体的使用场景：可以利用这个函数修改一些模拟盘的数据。

---

### after_trading_end（该函数会在每天结束交易后被调用一次）

**签名:** `after_trading_end(context)`
**章节:** 策略API > 策略程序架构♠
**说明:** 该函数会在每天结束交易后被调用一次, 您可以在这里添加一些每天收盘后要执行的内容. 这个时候所有未完成的订单已经取消.

---

### before_trading_start（该函数会在每天开始交易前被调用一次）

**签名:** `before_trading_start(context)`
**章节:** 策略API > 策略程序架构♠
**说明:** 该函数会在每天开始交易前被调用一次, 您可以在这里添加一些每天都要初始化的东西.

---

### defon_strategy_end（在回测、模拟交易正常结束时被调用）

**签名:** `defon_strategy_end(context)`
**章节:** 策略API > 策略程序架构♠
**说明:** 在回测、模拟交易正常结束时被调用， 失败时不会被调用。

---

### handle_data（该函数每个单位时间会调用一次）

**签名:** `handle_data(context, data)`
**章节:** 策略API > 策略程序架构♠
**说明:** 该函数每个单位时间会调用一次, 如果按天回测,则每天调用一次,如果按分钟,则每分钟调用一次  ,tick频率不支持这个函数。

---

### initialize（初始化方法）

**签名:** `initialize(context)`
**章节:** 策略API > 策略程序架构♠
**说明:** 初始化方法，在整个回测、模拟中最开始执行一次，用于初始一些全局变量

---

### on_event（用户在策略中定义on_event）

**签名:** `on_event(context, event)`
**章节:** 策略API > 策略程序架构♠
**说明:** 用户在策略中定义on_event，在账户中持仓的标的发生对应的事件时on_event会被调用。建议用户使用isinstance对事件类型进行判断。
目前已支持的事件有：

---

### process_initialize（该函数会在每次模拟盘/回测进程重启时执行）

**签名:** `process_initialize(context)`
**章节:** 策略API > 策略程序架构♠
**说明:** 该函数会在每次模拟盘/回测进程重启时执行, 一般用来初始化一些不能持久化保存的内容. 在initialize后执行.

---

## 因子分析 > 因子数据处理函数

### neutralize（中性化）

**签名:** `neutralize(series, how=None, date=None, axis=1)`
**章节:** 因子分析 > 因子数据处理函数
**说明:** 中性化后的因子数据

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| data | pd.Series/pd.DataFrame , 待中性化的序列，序列的 index 为股票的 code | 是 |  |
| how |  | 是 | str list 。 中性化使用的因子名称列表。默认为 ['jq_l1', 'market_cap'] 支持的内容包括：'jq_l1'： 聚宽一级行业'jq_l2'： 聚宽二级行业'sw_l1'： 申万一级行业'sw_l2'： 申万二级行业'sw_l3'： 申万三级行业风险因子：可以使用的风险因子包括： ['size', 'beta', 'momentum', 'residual_volatility', 'non_linear_size', 'book_to_price_ratio', 'liquidity', 'earnings_yield', 'growth', 'leverage'] |
| 'jq_l1'： 聚宽一级行业 |  | 是 |  |
| 'jq_l2'： 聚宽二级行业 |  | 是 |  |
| 'sw_l1'： 申万一级行业 |  | 是 |  |
| 'sw_l2'： 申万二级行业 |  | 是 |  |
| 'sw_l3'： 申万三级行业 |  | 是 |  |
| 风险因子：可以使用的风险因子包括： ['size', 'beta', 'momentum', 'residual_volatility', 'non_linear_size', 'book_to_price_ratio', 'liquidity', 'earnings_yield', 'growth', 'leverage'] |  | 是 |  |
| date |  | 是 | 日期格式 str  将用 date 这天的相关变量数据对 series 进行中性化 |
| axis |  | 是 | 默认为 1。仅在 data 为 pd.DataFrame 时生效。 表示沿哪个方向做标准化，0 为对每列做中性化，1 为对每行做中性化 |

**返回值:** 中性化后的因子数据

**示例代码:**

```python
# 导入需要的函数库importpandasaspdimportnumpyasnpfromjqfactorimportneutralize# 生成数据data = pd.DataFrame(np.random.rand(3,300), columns=get_index_stocks('000300.XSHG', date='2018-05-02'),index=['a','b','c'])# 数据中性化neutralize(data, how=['jq_l1','market_cap'], date='2018-05-02', axis=1)
```

---

### standardlize（标准化）

**签名:** `standardlize(series, inf2nan=True, axis=1)`
**章节:** 因子分析 > 因子数据处理函数
**说明:** 标准化后的因子数据

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| data | pd.Series/pd.DataFrame/np.array, 待标准化的序列 | 是 |  |
| inf2nan |  | 是 | 是否将 np.inf 和 -np.inf 替换成 np.nan。默认为 True |
| axis=1 |  | 是 | 在 data 为 pd.DataFrame 时使用，如果 series 为 pd.DataFrame，沿哪个方向做标准化。0 为对每列做标准化，1 为对每行做标准化 |

**返回值:** 标准化后的因子数据

**示例代码:**

```python
# 导入需要的函数库importpandasaspdimportnumpyasnpfromjqfactorimportstandardlize# 生成数据data = pd.DataFrame(np.random.rand(3,300), columns=get_index_stocks('000300.XSHG', date='2018-05-02'),index=['a','b','c'])# 数据标准化standardlize(data, inf2nan=True, axis=0)
```

---

### winsorize（去极值）

**签名:** `winsorize(series, scale=None, range=None, qrange=None, inclusive=True, inf2nan=True, axis=1)`
**章节:** 因子分析 > 因子数据处理函数
**说明:** 去极值处理之后的因子数据

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| data | pd.Series/pd.DataFrame/np.array, 待缩尾的序列 | 是 |  |
| scale | 标准差倍数，与 range，qrange 三选一，不可同时使用。会将位于 [mu | 是 | scale * sigma, mu + scale * sigma] 边界之外的值替换为边界值 |
| range |  | 是 | 列表， 缩尾的上下边界。与 scale，qrange 三选一，不可同时使用。 |
| qrange |  | 是 | 列表，缩尾的上下分位数边界，值应在 0 到 1 之间，如 [0.05, 0.95]。与 scale，range 三选一，不可同时使用。 |
| inclusive |  | 是 | 是否将位于边界之外的值替换为边界值，默认为 True。如果为 True，则将边界之外的值替换为边界值，否则则替换为 np.nan |
| inf2nan |  | 是 | 是否将 np.inf 和 -np.inf 替换成 np.nan，默认为 True如果为 True，在缩尾之前会先将 np.inf 和 -np.inf 替换成 np.nan，缩尾的时候不会考虑 np.nan，否则 inf 被认为是在上界之上，-inf 被认为在下界之下 |
| axis |  | 是 | 在 data 为 pd.DataFrame 时使用，沿哪个方向做标准化，默认为 1。 0 为对每列做缩尾，1 为对每行做缩尾。 |

**返回值:** 去极值处理之后的因子数据

**示例代码:**

```python
# 导入需要的函数库importpandasaspdimportnumpyasnpfromjqfactorimportwinsorize# 生成数据data = pd.DataFrame(np.random.rand(3,300), columns=get_index_stocks('000300.XSHG', date='2018-05-02'),index=['a','b','c'])# 数据去极值winsorize(data, qrange=[0.05,0.93], inclusive=True, inf2nan=True, axis=1)
```

---

### winsorize_med（中位数去极值）

**签名:** `winsorize_med(series, scale=1, inclusive=True, inf2nan=True, axis=1)`
**章节:** 因子分析 > 因子数据处理函数
**说明:** 中位数去极值之后的因子数据

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| data | pd.Series/pd.DataFrame/np.array, 待缩尾的序列 | 是 |  |
| scale | 倍数，默认为 1.0。会将位于 [med | 是 | scale * distance, med + scale * distance] 边界之外的值替换为边界值/np.nan |
| inclusive bool  是否将位于边界之外的值替换为边界值，默认为 True。 如果为 True，则将边界之外的值替换为边界值，否则则替换为 np.nan |  | 是 |  |
| inf2nan |  | 是 | 是否将 np.inf 和 -np.inf 替换成 np.nan，默认为 True。如果为 True，在缩尾之前会先将 np.inf 和 -np.inf 替换成 np.nan，缩尾的时候不会考虑 np.nan，否则 inf 被认为是在上界之上，-inf 被认为在下界之下 |
| axis |  | 是 | 在 data 为 pd.DataFrame 时使用，沿哪个方向做标准化，默认为 1。0 为对每列做缩尾，1 为对每行做缩尾 |

**返回值:** 中位数去极值之后的因子数据

**示例代码:**

```python
# 导入需要的函数库importpandasaspdimportnumpyasnpfromjqfactorimportwinsorize_med# 生成数据data = pd.DataFrame(np.random.rand(3,300), columns=get_index_stocks('000300.XSHG', date='2018-05-02'),index=['a','b','c'])# 数据中位数去极值winsorize_med(data, scale=1, inclusive=True, inf2nan=True, axis=0)
```

---

## 策略API > 策略示例

### 均线策略（均线策略）

**签名:** `# 导入聚宽函数库importjqdata# 初始化函数，设定要操作的股票、基准等等definitialize(context):# 定义一个全局变量, 保存要操作的股票# 000001(股票:平安银行)g.security ='000001.XSHE'# 设定沪深300作为基准set_benchmark('000300.XSHG')# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 每个单位时间(如果按天回测,则每天调用一次,如果按分钟,则每分钟调用一次)调用一次defhandle_data(context, data):security = g.security# 获取股票的收盘价close_data = attribute_history(security,5,'1d', ['close'])# 取得过去五天的平均价格MA5 = close_data['close'].mean()# 取得上一时间点价格current_price = close_data['close'][-1]# 取得当前的现金cash = context.portfolio.available_cash# 如果上一时间点价格高出五天平均价5%, 则全仓买入if(current_price >1.05*MA5)and(cash>0):# 用所有 cash 买入股票order_value(security, cash)# 记录这次买入log.info("Buying %s"% (security))# 如果上一时间点价格低于五天平均价, 则空仓卖出elifcurrent_price <0.95*MA5andcontext.portfolio.positions[security].closeable_amount >0:# 卖出所有股票,使这只股票的最终持有量为0order_target(security,0)# 记录这次卖出log.info("Selling %s"% (security))# 画出上一时间点价格record(stock_price=current_price)`
**章节:** 策略API > 策略示例
**说明:** 当价格高于5日均线平均价格1.05时买入，当价格低于5日平均价格0.95时卖出。

---

### 多股票持仓示例（多股票持仓示例）

**签名:** `# 导入聚宽函数库importjqdatadefinitialize(context):# 初始化此策略# 设置我们要操作的股票池g.stocks = ['000001.XSHE','000002.XSHE','000004.XSHE','000005.XSHE']# 设定沪深300作为基准set_benchmark('000300.XSHG')# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 每个单位时间(如果按天回测,则每天调用一次,如果按分钟,则每分钟调用一次)调用一次defhandle_data(context, data):# 循环每只股票forsecuritying.stocks:# 得到股票之前3天的平均价vwap = data[security].vwap(3)# 得到上一时间点股票收盘价price = data[security].close# 得到当前资金余额cash = context.portfolio.available_cash# 如果上一时间点价格小于三天平均价*0.995，并且持有该股票，卖出ifprice < vwap *0.995andcontext.portfolio.positions[security].closeable_amount >0:# 下入卖出单order(security,-100)# 记录这次卖出log.info("Selling %s"% (security))# 如果上一时间点价格大于三天平均价*1.005，并且有现金余额，买入elifprice > vwap *1.005andcash >0:# 下入买入单order(security,100)# 记录这次买入log.info("Buying %s"% (security))`
**章节:** 策略API > 策略示例
**说明:** 这是一个较简单的多股票操作示例，当价格高于三天平均价1.005则买入100股，当价格小于三天平均价0.995则卖出。

---

### 多股票追涨策略（多股票追涨策略）

**签名:** `# 导入聚宽函数库importjqdata# 初始化程序, 整个回测只运行一次definitialize(context):# 开启动态复权模式(真实价格)set_option('use_real_price',True)# 每天买入股票数量g.daily_buy_count  =5# 设置我们要操作的股票池, 这里我们操作多只股票，下列股票选自计算机信息技术相关板块g.stocks = get_industry_stocks('I64') + get_industry_stocks('I65')# 防止板块之间重复包含某只股票, 排除掉重复的, g.stocks 现在是一个集合(set)g.stocks = set(g.stocks)# 让每天早上开盘时执行 morning_sell_allrun_daily(morning_sell_all,'09:30')defmorning_sell_all(context):# 将目前所有的股票卖出forsecurityincontext.portfolio.positions:# 全部卖出order_target(security,0)# 记录这次卖出log.info("Selling %s"% (security))defbefore_trading_start(context):# 今天已经买入的股票g.today_bought_stocks = set()# 得到所有股票昨日收盘价, 每天只需要取一次, 所以放在 before_trading_start 中g.last_df = history(1,'1d','close',g.stocks)# 在每分钟的第一秒运行, data 是上一分钟的切片数据defhandle_data(context, data):# 判断是否在当日最后的2小时，我们只追涨最后2小时满足追涨条件的股票ifcontext.current_dt.hour <13:return# 每天只买这么多个iflen(g.today_bought_stocks) >= g.daily_buy_count:return# 只遍历今天还没有买入的股票forsecurityin(g.stocks - g.today_bought_stocks):# 得到当前价格price = data[security].close# 获取这只股票昨天收盘价last_close = g.last_df[security][0]# 如果上一时间点价格已经涨了9.5%~9.9%# 今天的涨停价格区间大于1元，今天没有买入该支股票ifprice/last_close >1.095\andprice/last_close <1.099\anddata[security].high_limit - last_close >=1.0:# 得到当前资金余额cash = context.portfolio.available_cash# 计算今天还需要买入的股票数量need_count = g.daily_buy_count - len(g.today_bought_stocks)# 把现金分成几份,buy_cash = context.portfolio.available_cash / need_count# 买入这么多现金的股票order_value(security, buy_cash)# 放入今日已买股票的集合g.today_bought_stocks.add(security)# 记录这次买入log.info("Buying %s"% (security))# 买够5个之后就不买了iflen(g.today_bought_stocks) >= g.daily_buy_count:break`
**章节:** 策略API > 策略示例
**说明:** 当股票在当日收盘30分钟内涨幅到达9.5%~9.9%时间段的时候，我们进行买入，在第二天开盘卖出。注意：请按照分钟进行回测该策略。

---

## 因子分析 > 因子定义和计算

### _get_extra_data（在因子定义中获取额外数据）

**签名:** `self._get_extra_data(securities=[],fields=[])`
**章节:** 因子分析 > 因子定义和计算
**说明:** 在 calc 方法中获取额外数据的方法。可以用来获取指数收盘价等数据。只能在 calc 内部使用

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| securities:股票代码的列表，可以使用个股和指数 |  | 是 |  |
| fields:基础因子名称列表。表示需要获取那些基础因子。支持的因子与 dependencies 中相同。 |  | 是 |  |

**返回值:** dict, 结构与 data 类似。
dict 的 key 是 fields 中定义的基础因子名称。 value 是一个 dataframe。
dataframe 的 index 是日期索引， column 是 securities 中定义的股票代码， values 是因子值。
其中， index 的时间跨度与 data 中一致， 都是由 max_window 定义的。

---

### calc_factors（因子计算）

**签名:** `calc_factors(securities, factors, start_date, end_date, use_real_price, skip_paused)`
**章节:** 因子分析 > 因子定义和计算
**说明:** 在回测以及研究中， 可以通过调用jqfactor中的 calc_factors 函数来计算单因子分析中定义的因子值。

**参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| securities |  | 是 | 股票代码列表。 |
| factors |  | 是 | 因子(object)列表 |
| start_date |  | 是 | 开始日期 |
| end_date |  | 是 | 在回测中使用时，注意应该保证截止日期小于 context.current_dt |
| use_real_price |  | 是 | 是否使用真实价格。默认为 False，表示使用后复权价格。 |
| skip_paused:是否跳过停牌。 默认为 False。 注意：当 dependencies 使用的因子为价量信息，且 skip_paused = True 时，返回的 DataFrame 的索引由 datetime 变为 int， 值越大，表示离『当前』日期越近。其他情况下，返回的 DataFrame 的索引为 datetime。 |  | 是 |  |

**示例代码:**

```python
# 导入函数库fromjqfactorimportFactor, calc_factors# 定义因子classALPHA013(Factor):name ='alpha013_name'max_window =1dependencies = ['high','low','volume','money']defcalc(self, data):high = data['high']
        low = data['low']
        vwap = data['money']/data['volume']return(np.power(high*low,0.5) - vwap).mean()# 定义因子classGROSSPROFITABILITY(Factor):name ='gross_profitability'max_window =1dependencies = ['total_operating_revenue','total_operating_cost','total_assets']defcalc(self, data):total_operating_revenue = data['total_operating_revenue']
        total_operating_cost = data['total_operating_cost']
        total_assets = data['total_assets']
        gross_profitability = (total_operating_revenue - total_operating_cost)/total_assetsreturngross_profitability.mean()# 定义股票池securities = ['600000.XSHG','600016.XSHG']# 计算因子值factors = calc_factors(securities, [ALPHA013(),GROSSPROFITABILITY()], start_date='2017-01-01', end_date='2017-02-01',  use_real_price=False, skip_paused=False)# 查看因子值factors['alpha013_name'].head()
>>>600000.XSHG600016.XSHG2017-01-03-0.176511-0.0701542017-01-04-0.0680260.0062682017-01-05-0.0920720.0226042017-01-06-0.0214110.2599062017-01-090.054015-0.118956
```

---

### classMA5（因子定义）

**签名:** `classMA5(Factor):name ='ma5'# 每天获取过去五日的数据max_window =5# 获取的数据是收盘价dependencies = ['close']defcalc(self, data):# print("现在处理{}的数据"format( self._current_date)) #打印逻辑日期returndata['close'][-5:].mean()`
**章节:** 因子分析 > 因子定义和计算
**说明:** 使用方法用户需要实现一个自定义因子的类， 继承 Factor 类， 并实现 calc 方法。max_window 和 dependencies 定义了在 calc 中可以获取到的数据，calc 实现因子的算法。calc 的返回值即每天的因子值。 calc 需要返回一个pandas.Series。index 是股票代码， value 是因子值。

---

### 因子定义 dependencies 中的财务因子（因子定义 dependencies 中的财务因子）

**签名:** `# 计算营业收入TTMfromjqfactorimportFactorclassOR_TTM(Factor):# 设置因子名称name ='operating_revenue_ttm'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据，即前四季度的营业收入dependencies = ['operating_revenue','operating_revenue_1','operating_revenue_2','operating_revenue_3']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 计算 ttm ， 为前四季度相加ttm = data['operating_revenue'] + data['operating_revenue_1'] + data['operating_revenue_2'] + data['operating_revenue_3']# 将 ttm 转换成 seriesreturnttm.mean()`
**章节:** 因子分析 > 因子定义和计算
**说明:** 在因子定义中，如果依赖的基础因子名称（dependencies）为财务因子，可能有些小伙伴理解起来有困难，下面通过一些场景和示例帮助理解。也可以自学一下金融方面的基础知识，多查看一些上市公司的财务报告。

---

### 示例-计算TTM数据（示例-计算TTM数据）

**签名:** `# 计算营业收入TTMfromjqfactorimportFactorclassOR_TTM(Factor):# 设置因子名称name ='operating_revenue_ttm'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据，即前四季度的营业收入dependencies = ['operating_revenue','operating_revenue_1','operating_revenue_2','operating_revenue_3']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 计算 ttm ， 为前四季度相加ttm = data['operating_revenue'] + data['operating_revenue_1'] + data['operating_revenue_2'] + data['operating_revenue_3']# 将 ttm 转换成 seriesreturnttm.mean()`
**章节:** 因子分析 > 因子定义和计算

---

## 因子分析 > 因子分析

### calc_autocorrelation（根据调仓周期确定滞后期的每天计算因子自相关性）

**签名:** `far.calc_autocorrelation(rank=True)`
**章节:** 因子分析 > 因子分析
**说明:** 当日因子值和滞后period天的因子值的自相关性

---

### calc_autocorrelation_n_days_lag（滞后1-n天因子值自相关性均值）

**签名:** `far.calc_autocorrelation_n_days_lag(n=9,rank=True)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### calc_average_cumulative_return_by_quantile（按照当天的分位数算分位数未来和过去的收益均值和标准差）

**签名:** `far.calc_average_cumulative_return_by_quantile(periods_before=5,periods_after=15,demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### calc_cumulative_return_by_quantile（计算指定调仓周期的各分位数每日累积收益）

**签名:** `far.calc_cumulative_return_by_quantile(period=5)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### calc_cumulative_returns（计算指定调仓周期的按因子值加权组合每日累积收益）

**签名:** `far.calc_cumulative_returns(period=5,demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 当 调仓周期 period > 1 时，组合的累积收益计算方法为：

---

### calc_factor_alpha_beta（计算因子的 alpha 和 beta）

**签名:** `far.calc_factor_alpha_beta(demeaned=True,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 因子值加权组合每日收益 = beta * 市场组合每日收益 + alpha

---

### calc_factor_information_coefficient（计算每日因子信息系数（IC值））

**签名:** `far.calc_factor_information_coefficient(group_adjust=False, by_group=False,method='rank')`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### calc_factor_returns（计算按因子值加权组合每日收益）

**签名:** `far.calc_factor_returns(demeaned=True,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 权重 = 每日因子值 / 每日因子值的绝对值的和

---

### calc_ic_mean_n_days_lag（滞后 0 - n 天因子收益信息系数(IC)的均值）

**签名:** `far.calc_ic_mean_n_days_lag(n=10,group_adjust=False,by_group=False,method=None)`
**章节:** 因子分析 > 因子分析
**说明:** 滞后 n 天 IC 表示使用当日因子值和滞后 n 天的因子收益计算 IC

---

### calc_mean_information_coefficient（计算因子信息系数均值（IC值均值））

**签名:** `far.calc_mean_information_coefficient(group_adjust=False, by_group=False, by_time=None,method='rank')`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### calc_mean_return_by_quantile（属性列表）

**签名:** `mean,std = far.calc_mean_return_by_quantile(by_date=False,by_group=False,demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 用于访问因子分析的结果，大部分为惰性属性，在访问才会计算结果并返回

---

### calc_quantile_turnover_mean_n_days_lag（各分位数滞后1天到n天的换手率均值）

**签名:** `far.calc_quantile_turnover_mean_n_days_lag(n=10)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### calc_top_down_cumulative_returns（计算做多最大分位，做空最小分位组合每日累积收益）

**签名:** `far.calc_top_down_cumulative_returns(period=5,demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 当 调仓周期 period > 1 时，组合的累积收益计算方法 见 calc_cumulative_returns

---

### compute_mean_returns_spread（计算两个分位数相减的因子收益和标准差）

**签名:** `mean, std = far.compute_mean_returns_spread (upper_quant=None,lower_quant=None,by_date=True,by_group=False,demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### create_event_returns_tear_sheet（因子预测能力分析）

**签名:** `far.create_event_returns_tear_sheet(avgretplot=(5, 15),demeaned=False,group_adjust=False,std_bar=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数:

---

### create_full_tear_sheet（绘制图表）

**签名:** `far.create_full_tear_sheet(demeaned=False,group_adjust=False,by_group=False,turnover_periods=None, avgretplot=(5, 15),std_bar=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数:

---

### create_information_tear_sheet（因子 IC 分析）

**签名:** `far.create_information_tear_sheet(group_adjust=False,by_group=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数:

---

### create_returns_tear_sheet（因子收益分析）

**签名:** `far.create_returns_tear_sheet(demeaned=False,group_adjust=False,by_group=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数:

---

### create_summary_tear_sheet（因子值特征分析）

**签名:** `far.create_summary_tear_sheet(demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数:

---

### create_turnover_tear_sheet（因子换手率分析）

**签名:** `far.create_turnover_tear_sheet(turnover_periods=None)`
**章节:** 因子分析 > 因子分析
**说明:** 参数:

---

### naninfforward_return（去除 nan/inf，整理后的因子值、forward_return 和分位数）

**签名:** ``
**章节:** 因子分析 > 因子分析

---

### plot_cumulative_returns（画按因子值加权多空组合每日累积收益图）

**签名:** `far.plot_cumulative_returns(period=1,demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_cumulative_returns_by_quantile（画各分位数每日累积收益图）

**签名:** `far.plot_cumulative_returns_by_quantile(period=(1, 3, 9),demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_disable_chinese_label（关闭中文图例显示）

**签名:** `far.plot_disable_chinese_label()`
**章节:** 因子分析 > 因子分析

---

### plot_events_distribution（画有效因子数量统计图）

**签名:** `far.plot_events_distribution(num_days=1)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_factor_auto_correlation（画因子自相关图）

**签名:** `far.plot_factor_auto_correlation(periods=None,rank=True)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_ic_by_group（画按行业分组信息系数(IC)图）

**签名:** `far.plot_ic_by_group(group_adjust=False,method='rank')`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_ic_hist（画信息系数分布直方图）

**签名:** `far.plot_ic_hist(group_adjust=False,method='rank')`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_ic_qq（画信息系数 qq 图）

**签名:** `far.plot_ic_qq(group_adjust=False,method='rank',theoretical_dist='norm')`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_ic_ts（画信息系数(IC)时间序列图）

**签名:** `far.plot_ic_ts(group_adjust=False,method='rank')`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_information_table（打印信息系数（IC）相关表）

**签名:** `far.plot_information_table(group_adjust=False,method='rank')`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_mean_quantile_returns_spread_time_series（画最高分位减最低分位收益图）

**签名:** `far.plot_mean_quantile_returns_spread_time_series(demeaned=False,group_adjust=False,bandwidth=1)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_monthly_ic_heatmap（画月度信息系数(IC)图）

**签名:** `far.plot_monthly_ic_heatmap(group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_quantile_average_cumulative_return（因子预测能力平均累计收益图）

**签名:** `far.plot_quantile_average_cumulative_return(periods_before=5,periods_after=10,by_quantile=False,std_bar=False,demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_quantile_returns_bar（画各分位数平均收益图）

**签名:** `far.plot_quantile_returns_bar(by_group=False,demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_quantile_statistics_table（打印各分位数统计表）

**签名:** `far.plot_quantile_statistics_table()`
**章节:** 因子分析 > 因子分析

---

### plot_returns_table（打印因子收益表）

**签名:** `far.plot_returns_table(demeaned=False,group_adjust=False)`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_top_bottom_quantile_turnover（画最高最低分位换手率图）

**签名:** `far.plot_top_bottom_quantile_turnover(periods=(1,3,9))`
**章节:** 因子分析 > 因子分析
**说明:** 参数：

---

### plot_turnover_table（打印换手率表）

**签名:** `far.plot_turnover_table()`
**章节:** 因子分析 > 因子分析

---

### 因子分析API（因子分析API）

**签名:** `#载入函数库fromjqfactorimportanalyze_factor#对因子进行分析far = analyze_factor(factor, start_date, end_date, industry, universe, quantiles, periods, weight_method, use_real_price, skip_paused, max_loss, factor_dep_definitions)`
**章节:** 因子分析 > 因子分析
**说明:** 为了让用户在研究环境中，可以便捷的分析因子，我们准备了单因子分析工具

---

## 因子分析 > 示例

### classROATTM（『多季度』 资产回报率）

**签名:** `classROATTM(Factor):name ='roa_ttm'max_window =1# 定义依赖的数据： 过去四个季度的净利润， 以及最新一个季度的总资产dependencies = ['net_profit','net_profit_1','net_profit_2','net_profit_3','total_assets']defcalc(self, data):# 计算净利润的 ttm 值net_profit_ttm = data['net_profit'] + data['net_profit_1'] + data['net_profit_2'] + data['net_profit_3']# 计算 ROAresult = net_profit_ttm / data['total_assets']# 把结果转成一个 seriesreturnresult.mean()`
**章节:** 因子分析 > 示例
**说明:** 因子公式

---

### filterwarnings（构建因子数据进行单因子分析）

**签名:** `# 载入函数库fromjqfactorimportanalyze_factorfromjqdataimport*fromjqlibimportalpha191importpandasaspdimportwarnings warnings.filterwarnings("ignore")# 测试开始时间start_date ='2019-10-01'# 测试结束时间end_date ='2019-11-11'# 测试时间区间的交易日date_list = get_trade_days(start_date=start_date, end_date=end_date)# 转换交易日时间的数据类型# date_list = [date.strftime('%Y-%m-%d') for date in date_list]# 获取一段时间股票池191因子数据factor_data = {}# 循环获取每天数据fordateindate_list:# 获取每天的股票池universe = get_index_stocks('000300.XSHG', date=date)# 获取每天股票池的因子数据_factor_data = alpha191.alpha_002(code=universe, end_date=date, fq='post')# 添加每天的因子数据factor_data[date] = _factor_data# 将字典类型数据转换为DataFramefactor_data = pd.DataFrame(factor_data).T# 将 index 转换为 DatetimeIndexfactor_data.index = pd.to_datetime(factor_data.index)# 对因子进行分析，参数使用默认值far = analyze_factor(factor=factor_data, )# 展示全部分析far.create_full_tear_sheet(demeaned=False, group_adjust=False, by_group=False, turnover_periods=None,                             avgretplot=(5,15), std_bar=False)`
**章节:** 因子分析 > 示例
**说明:** 前面的例子讲述了通过自定义类实现因子，本例讲解如何直接获取因子数据或者构建因子数据，然后对得到的数据进行单因子分析。其中的factor_data数据需要自己获取，并整理成符合因子分析要求的格式。更多关于factor_data数据格式请查看单因子分析框架jqfactor_analyzer

---

### fromjqfactorimportFactorclassGROSSPROFITABILITY（『基本面』gross profitability）

**签名:** `fromjqfactorimportFactorclassGROSSPROFITABILITY(Factor):# 设置因子名称name ='gross_profitability'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据# 在策略中需要使用 get_fundamentals 获取的 income.total_operating_revenue, 在这里可以直接写做total_operating_revenue。 其他数据同理。dependencies = ['total_operating_revenue','total_operating_cost','total_assets']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 获取单季度的营业总收入数据 , index 是日期，column 是股票代码， value 是营业总收入total_operating_revenue = data['total_operating_revenue']# 获取单季度的营业总成本数据total_operating_cost = data['total_operating_cost']# 获取总资产total_assets = data['total_assets']# 计算 gross_profitabilitygross_profitability = (total_operating_revenue - total_operating_cost)/total_assets# 由于 gross_profitability 是一个一行 n 列的 dataframe，可以直接求 mean 转成 seriesreturngross_profitability.mean()`
**章节:** 因子分析 > 示例
**说明:** 参考链接

---

### fromjqfactorimportFactorclassHs300Alpha（『指数』近10日 alpha）

**签名:** `fromjqfactorimportFactorclassHs300Alpha(Factor):# 设置因子名称name ='hs300_alpha'# 设置获取数据的时间窗口长度max_window =10# 设置依赖的数据dependencies = ['close']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 获取个股的收盘价数据close = data['close']# 计算个股近10日收益stock_return = close.iloc[-1,:]/close.iloc[0,:]-1# 获取指数（沪深300）的收盘价数据index_close = self._get_extra_data(securities=['000300.XSHG'], fields=['close'])['close']# 计算指数的近10日收益index_return = index_close.iat[-1,0]/index_close.iat[0,0] -1# 计算 alphaalpha = stock_return - index_returnreturnalpha`
**章节:** 因子分析 > 示例
**说明:** 因子公式

---

### fromjqfactorimportFactorclassNetProfitGrowth（『基本面』近两年净利润增长率）

**签名:** `fromjqfactorimportFactorclassNetProfitGrowth(Factor):# 设置因子名称name ='net_profit_growth_rate'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据dependencies = ['net_profit_y','net_profit_y1']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 个股最新一年度的净利润数据net_profit_y = data['net_profit_y']# 个股最新一年度的上一年的净利润数据net_profit_y1 = data['net_profit_y1']# 计算增长率growth = net_profit_y/net_profit_y1 -1# 返回一个 seriesreturngrowth.mean()`
**章节:** 因子分析 > 示例
**说明:** 因子公式

---

### fromjqfactorimportFactorimportnumpyasnpclassALPHA013（『价量』alpha 191 中的 013）

**签名:** `fromjqfactorimportFactorimportnumpyasnpclassALPHA013(Factor):# 设置因子名称name ='alpha013'# 设置获取数据的时间窗口长度max_window =1# 设置依赖的数据dependencies = ['high','low','volume','money']# 计算因子的函数， 需要返回一个 pandas.Series, index 是股票代码，value 是因子值defcalc(self, data):# 最高价的 dataframe ， index 是日期， column 是股票代码high = data['high']# 最低价的 dataframe ， index 是日期， column 是股票代码low = data['low']#计算 vwapvwap = data['money']/data['volume']# 返回因子值， 这里求平均值是为了把只有一行的 dataframe 转成 seriesreturn(np.power(high*low,0.5) - vwap).mean()`
**章节:** 因子分析 > 示例
**说明:** 因子链接

---

### fromjqfactorimportFactorimportnumpyasnpimportpandasaspdclassDebtEquityRatio（『中性化』产权比率）

**签名:** `fromjqfactorimportFactorimportnumpyasnpimportpandasaspdclassDebtEquityRatio(Factor):name ='debt_to_equity_ratio'max_window =1dependencies = ['total_liability','equities_parent_company_owners',# 以下为中性化需要使用的数据'market_cap','HY001','HY002','HY003','HY004','HY005','HY006','HY007','HY008','HY009','HY010','HY011']defcalc(self, data):tl = data['total_liability']         epco = data['equities_parent_company_owners']         result = tl / epcoreturnneutralization(data, result.mean())# 行业市值中性化defneutralization(data, factor):fromstatsmodels.apiimportOLS     industry_exposure = pd.DataFrame(index=data['HY001'].columns)     industry_list = ['HY001','HY002','HY003','HY004','HY005','HY006','HY007','HY008','HY009','HY010','HY011']forkey, valueindata.items():ifkeyinindustry_list:             industry_exposure[key]=value.iloc[-1]     market_cap_exposure = data['market_cap'].iloc[-1]     total_exposure = pd.concat([market_cap_exposure,industry_exposure],axis=1)     result = OLS(factor, total_exposure, missing='drop').fit().residreturnresult`
**章节:** 因子分析 > 示例
**说明:** 因子公式

---

## 因子分析 > 附录

### dataframe（将自有因子值转换成 DataFrame 格式的数据）

**签名:** ``
**章节:** 因子分析 > 附录
**说明:** 将自有因子值转换成 DataFrame 格式的数据

---

### valueerrornoobjectstoconcatenate（因子分析错误处理）

**签名:** ``
**章节:** 因子分析 > 附录
**说明:** 检查下得到的因子数据索引的数据类型是否正常，index为日期的DatetimeIndex;可以使用pandas的to_datetime方法转换；

---
