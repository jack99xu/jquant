# 聚宽数据字典

> 数据来源：聚宽官方数据文档，字段含义以 meaning 列为准。

---


## FUT_CHARGE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| clearance_charge | DECIMAL(19, 4) | 平仓手续费 | 上期所/能源中心,郑商所,中金所为交易手续费 |
| code | varchar(12) | 标的代码 |  |
| day | date | 日期 |  |
| exchange | varchar(10) | 交易所编码 | 英文编码 |
| exchange_name | varchar(30) | 交易所名称 |  |
| opening_charge | DECIMAL(19, 4) | 开仓手续费 | 上期所//能源中心,郑商所,中金所不支持 , (大商所和广期所一般等于平仓手续费) |
| short_clearance_charge | DECIMAL(19, 4) | 短平手续费 | 大商所和广期所是短平手续费,郑商所为平今,上期货//能源中心和中金所根据折扣率换算 |
| short_opening_charge | DECIMAL(19, 4) | 短开手续费 | 仅大商所(一般等于短平)和广期所支持 |
| unit | varchar(10) | 计量单位 | '元/手' 或者 '‱' |

## FUT_GLOBAL_DAILY

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| amplitude | decimal(20,6) | 振幅（%） | （当日最高点的价格－当日最低点的价格）/前收价 |
| change_pct | decimal(20,4) | 涨跌幅（%） | （当日收盘价-前收价）/前收价 |
| close | decimal(20,6) | 收盘价 |  |
| code | varchar(64) | 期货代码 | 代码列表详见下方期货代码名称对照表 |
| day | date | 日期 |  |
| high | decimal(20,6) | 最高价 |  |
| low | decimal(20,6) | 最低价 |  |
| name | varchar(64) | 期货名称 |  |
| open | decimal(20,6) | 开盘价 |  |
| pre_close | decimal(20,6) | 前收价 |  |
| volume | decimal(20,6) | 成交量 |  |

## FUT_MARGIN

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 标的代码 |  |
| day | date | 日期 |  |
| exchange | varchar(10) | 交易所编码 | 英文编码 |
| exchange_name | varchar(30) | 交易所名称 |  |
| hedg_buy_margin_rate | DECIMAL(19, 4) | 套保买保证金率 | 上期所/能源中心,大商所,广期所为交易保证金(套保) |
| hedg_sell_margin_rate | DECIMAL(19, 4) | 套保卖保证金率 | 上期所/能源中心,大商所,广期所为交易保证金(套保) |
| specul_buy_margin_rate | DECIMAL(19, 4) | 投机买保证金率 | 上期所,大商所,广期所为交易保证金(投机),中金所为多头保证金, 郑商所为交易保证金 |
| specul_sell_margin_rate | DECIMAL(19, 4) | 投机卖保证金率 | 上期所/能源中心,大商所,广期所为交易保证金(投机),中金所为空头保证金, 郑商所为交易保证金 |

## FUT_MEMBER_POSITION_RANK

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 合约编码 | 同一商品根据交割日的不同对应不同的期货合约，比如：'CU1807.XSGE' |
| day | date | 交易日 |  |
| exchange | varchar(10) | 交易所编码 | 英文编码：XSGE：上海期货交易所， XDCE：大连商品交易所，XZCE：郑州商品交易所， CCFX：中国金融期货交易所 |
| exchange_name | varchar(30) | 交易所名称 |  |
| indicator | int | 统计指标 | 统计指标根据排名类别确定，分别代表：成交量，持买单量，持卖单量。单位：手 |
| indicator_increase | int | 统计指标比上交易日增减 | 单位：手 |
| member_name | varchar(50) | 会员简称 |  |
| rank | int | 排名 |  |
| rank_type | varchar(50) | 排名类别 | 包含:成交量排名，持买单量排名，持卖单量排名 |
| rank_type_ID | int | 排名类别编码 | 501001-成交量排名, 501002-持买单量排名， 501003-持卖单量排名 |
| underlying_code | varchar(10) | 标的编码 |  |
| underlying_name | varchar(50) | 标的名称 |  |

## FUT_WAREHOUSE_RECEIPT

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| day | date | 日期 |  |
| exchange | varchar(10) | 交易所编码 | 英文编码 |
| exchange_name | varchar(30) | 交易所名称 | 上海期货交易所大连商品交易所郑州商商品交易所中国金融期货交易所 |
| product_name | varchar(20) | 品种名称 |  |
| underlying_code | varchar(10) | 品种编码 |  |
| unit | varchar(10) | 单位 |  |
| warehouse_name | varchar(20) | 仓库名称 | 上期所：将地区和仓库数据合并成一条，仓库名称=“地区”+“仓库”。大商所：仓库名称存在多个不同的名字的，取第一个字体加粗的仓库名称。郑商所：不区分品牌，对每个仓库取仓库小计值 |
| warehouse_receipt_number | int | 今日期货仓单 |  |
| warehouse_receipt_number_increase | int | 比昨日增减 |  |
