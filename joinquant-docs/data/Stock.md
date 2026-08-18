# 聚宽数据字典

> 数据来源：聚宽官方数据文档，字段含义以 meaning 列为准。

---


## STK_AH_PRICE_COMP

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_code | varchar(12) | a股代码 | '000002.XSHE' |
| a_price | decimal(10,4) | a股收盘价 | 人民币 |
| a_quote_change | decimal(10,4) | a股涨跌幅 | % |
| day | date | 日期 |  |
| h_a_comp | decimal(10,4) | 比价(H/A) | A股人民币价格/(H股港币价格*港币兑人民币的汇率) |
| h_code | varchar(12) | h股代码 |  |
| h_price | decimal(10,4) | h股收盘价 | 港币 |
| h_quote_change | decimal(10,4) | h股涨跌幅 | % |
| name | varchar(32) | 股票简称 |  |

## STK_AUDIT_OPINION

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| accountant | VARCHAR(100) | 会计师 |  |
| accounting_firm | VARCHAR(100) | 会计师事务所 |  |
| end_date | DATE | 报告日期 |  |
| opinion_type | VARCHAR(20) | 审计意见类型 |  |
| opinion_type_id | INTEGER(11) | 审计意见类型id |  |
| pub_date | DATE | 公告日期 |  |
| report_type | TINYINT(4) | 审计报告类型 | 0(财务报表审计报告), 1(内部控制审计报告) |

## STK_BALANCE_SHEET

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_code | varchar(12) | A股代码 |  |
| account_receivable | decimal(20,4) | 应收账款 |  |
| accounts_payable | decimal(20,4) | 应付账款 |  |
| advance_payment | decimal(20,4) | 预付款项 |  |
| advance_peceipts | decimal(20,4) | 预收款项 |  |
| affiliated_company_payable | decimal(20,4) | 应付关联公司款 |  |
| affiliated_company_receivable | decimal(20,4) | 应收关联公司款 |  |
| b_code | varchar(12) | B股代码 |  |
| bill_and_account_payable | decimal(20,4) | 应付票据及应付账款 |  |
| bill_and_account_receivable | decimal(20,4) | 应收票据及应收账款 |  |
| bill_receivable | decimal(20,4) | 应收票据 |  |
| biological_assets | decimal(20,4) | 生产性生物资产 |  |
| bond_invest | decimal(20,4) | 债权投资 |  |
| bonds_payable | decimal(20,4) | 应付债券 |  |
| borrowing_capital | decimal(20,4) | 拆入资金 |  |
| borrowing_from_centralbank | decimal(20,4) | 向中央银行借款 |  |
| bought_sellback_assets | decimal(20,4) | 买入返售金融资产 |  |
| capital_reserve_fund | decimal(20,4) | 资本公积 |  |
| cash_equivalents | decimal(20,4) | 货币资金 |  |
| code | varchar(12) | 股票代码 |  |
| commission_payable | decimal(20,4) | 应付手续费及佣金 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| constru_in_process | decimal(20,4) | 在建工程 |  |
| construction_materials | decimal(20,4) | 工程物资 |  |
| contract_assets | decimal(20,4) | 合同资产 |  |
| contract_liability | decimal(20,4) | 合同负债 |  |
| deferred_earning | decimal(20,4) | 递延收益-非流动负债 |  |
| deferred_earning_current | decimal(20,4) | 递延收益-流动负债 |  |
| deferred_tax_assets | decimal(20,4) | 递延所得税资产 |  |
| deferred_tax_liability | decimal(20,4) | 递延所得税负债 |  |
| deposit_in_interbank | decimal(20,4) | 吸收存款及同业存放 |  |
| derivative_financial_asset | decimal(20,4) | 衍生金融资产 |  |
| derivative_financial_liability | decimal(20,4) | 衍生金融负债 |  |
| development_expenditure | decimal(20,4) | 开发支出 |  |
| dividend_payable | decimal(20,4) | 应付股利 |  |
| dividend_receivable | decimal(20,4) | 应收股利 |  |
| end_date | date | 截止日期 |  |
| equities_parent_company_owners | decimal(20,4) | 归属于母公司所有者权益 |  |
| estimate_liability | decimal(20,4) | 预计负债 |  |
| estimate_liability_current | decimal(20,4) | 预计负债-流动负债 |  |
| expendable_biological_asset | decimal(20,4) | 消耗性生物资产 | 消耗性生物资产，是指为出售而持有的、或在将来收获为农产品的生物资产，包括生长中的大田作物、蔬菜、用材林，以及存栏代售的牲畜等 |
| fixed_assets | decimal(20,4) | 固定资产 |  |
| fixed_assets_liquidation | decimal(20,4) | 固定资产清理 |  |
| foreign_currency_report_conv_diff | decimal(20,4) | 外币报表折算价差 |  |
| good_will | decimal(20,4) | 商誉 |  |
| h_code | varchar(12) | H股代码 |  |
| hold_for_sale_assets | decimal(20,4) | 可供出售金融资产 |  |
| hold_sale_asset | decimal(20,4) | 划分为持有待售的资产 |  |
| hold_sale_liability | decimal(20,4) | 划分为持有待售的负债 |  |
| hold_to_maturity_investments | decimal(20,4) | 持有至到期投资 |  |
| insurance_contract_reserves | decimal(20,4) | 保险合同准备金 |  |
| insurance_receivables | decimal(20,4) | 应收保费 |  |
| intangible_assets | decimal(20,4) | 无形资产 |  |
| interest_payable | decimal(20,4) | 应付利息 |  |
| interest_receivable | decimal(20,4) | 应收利息 |  |
| inventories | decimal(20,4) | 存货 |  |
| investment_property | decimal(20,4) | 投资性房地产 |  |
| irregular_item_adjustment | decimal(20,4) | 非正常经营项目收益调整 |  |
| lease_liability | decimal(20,4) | 租赁负债 |  |
| lend_capital | decimal(20,4) | 拆出资金 |  |
| loan_and_advance_current_assets | decimal(20,4) | 发放贷款及垫款-流动资产 |  |
| loan_and_advance_noncurrent_assets | decimal(20,4) | 发放贷款及垫款-非流动资产 |  |
| long_deferred_expense | decimal(20,4) | 长期待摊费用 |  |
| longterm_account_payable | decimal(20,4) | 长期应付款 |  |
| longterm_equity_invest | decimal(20,4) | 长期股权投资 |  |
| longterm_loan | decimal(20,4) | 长期借款 |  |
| longterm_receivable_account | decimal(20,4) | 长期应收款 |  |
| longterm_salaries_payable | decimal(20,4) | 长期应付职工薪酬 |  |
| minority_interests | decimal(20,4) | 少数股东权益 |  |
| non_current_asset_in_one_year | decimal(20,4) | 一年内到期的非流动资产 |  |
| non_current_liability_in_one_year | decimal(20,4) | 一年内到期的非流动负债 |  |
| notes_payable | decimal(20,4) | 应付票据 |  |
| oil_gas_assets | decimal(20,4) | 油气资产 |  |
| ordinary_risk_reserve_fund | decimal(20,4) | 一般风险准备 |  |
| other_bond_invest | decimal(20,4) | 其他债权投资 |  |
| other_comprehensive_income | decimal(20,4) | 其他综合收益 |  |
| other_current_assets | decimal(20,4) | 其他流动资产 |  |
| other_current_liability | decimal(20,4) | 其他流动负债 |  |
| other_equity_tools | decimal(20,4) | 其他权益工具 |  |
| other_equity_tools_invest | decimal(20,4) | 其他权益工具投资 |  |
| other_non_current_assets | decimal(20,4) | 其他非流动资产 |  |
| other_non_current_financial_assets | decimal(20,4) | 其他非流动金融资产 |  |
| other_non_current_liability | decimal(20,4) | 其他非流动负债 |  |
| other_payable | decimal(20,4) | 其他应付款 |  |
| other_receivable | decimal(20,4) | 其他应收款 |  |
| paidin_capital | decimal(20,4) | 实收资本（或股本） |  |
| pepertual_liability_equity | decimal(20,4) | 永续债-所有者权益 |  |
| pepertual_liability_noncurrent | decimal(20,4) | 永续债-非流动负债 |  |
| preferred_shares_equity | decimal(20,4) | 其中：优先股-所有者权益 |  |
| preferred_shares_noncurrent | decimal(20,4) | 优先股-非流动负债 |  |
| proxy_secu_proceeds | decimal(20,4) | 代理买卖证券款 |  |
| pub_date | date | 公告日期 |  |
| receivable_fin | decimal(20,4) | 应收款项融资 |  |
| receivings_from_vicariously_sold_securities | decimal(20,4) | 代理承销证券款 |  |
| reinsurance_contract_reserves_receivable | decimal(20,4) | 应收分保合同准备金 |  |
| reinsurance_payables | decimal(20,4) | 应付分保账款 |  |
| reinsurance_receivables | decimal(20,4) | 应收分保账款 |  |
| report_date | date | 报告期 |  |
| report_type | int | 报告期类型 | 0本期，1上期 |
| retained_profit | decimal(20,4) | 未分配利润 |  |
| salaries_payable | decimal(20,4) | 应付职工薪酬 |  |
| settlement_provi | decimal(20,4) | 结算备付金 |  |
| shortterm_loan | decimal(20,4) | 短期借款 |  |
| sold_buyback_secu_proceeds | decimal(20,4) | 卖出回购金融资产款 |  |
| source | varchar(60) | 报表来源 |  |
| source_id | int | 报表来源编码 | 如下 报表来源编码 |
| specific_account_payable | decimal(20,4) | 专项应付款 |  |
| specific_reserves | decimal(20,4) | 专项储备 |  |
| surplus_reserve_fund | decimal(20,4) | 盈余公积 |  |
| taxs_payable | decimal(20,4) | 应交税费 |  |
| total_assets | decimal(20,4) | 资产总计 |  |
| total_current_assets | decimal(20,4) | 流动资产合计 |  |
| total_current_liability | decimal(20,4) | 流动负债合计 |  |
| total_liability | decimal(20,4) | 负债合计 |  |
| total_non_current_assets | decimal(20,4) | 非流动资产合计 |  |
| total_non_current_liability | decimal(20,4) | 非流动负债合计 |  |
| total_owner_equities | decimal(20,4) | 所有者权益（或股东权益）合计 |  |
| total_sheet_owner_equities | decimal(20,4) | 负债和所有者权益（或股东权益）合计 |  |
| trading_assets | decimal(20,4) | 交易性金融资产 |  |
| trading_liability | decimal(20,4) | 交易性金融负债 |  |
| treasury_stock | decimal(20,4) | 库存股 |  |
| usufruct_assets | decimal(20,4) | 使用权资产 |  |

## STK_BALANCE_SHEET_PARENT

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_code | varchar(12) | A股代码 |  |
| account_receivable | decimal(20,4) | 应收账款 |  |
| accounts_payable | decimal(20,4) | 应付账款 |  |
| advance_payment | decimal(20,4) | 预付款项 |  |
| advance_peceipts | decimal(20,4) | 预收款项 |  |
| affiliated_company_payable | decimal(20,4) | 应付关联公司款 |  |
| affiliated_company_receivable | decimal(20,4) | 应收关联公司款 |  |
| b_code | varchar(12) | B股代码 |  |
| bill_and_account_payable | decimal(20,4) | 应付票据及应付账款 |  |
| bill_and_account_receivable | decimal(20,4) | 应收票据及应收账款 |  |
| bill_receivable | decimal(20,4) | 应收票据 |  |
| biological_assets | decimal(20,4) | 生产性生物资产 |  |
| bond_invest | decimal(20,4) | 债权投资 |  |
| bonds_payable | decimal(20,4) | 应付债券 |  |
| borrowing_capital | decimal(20,4) | 拆入资金 |  |
| borrowing_from_centralbank | decimal(20,4) | 向中央银行借款 |  |
| bought_sellback_assets | decimal(20,4) | 买入返售金融资产 |  |
| capital_reserve_fund | decimal(20,4) | 资本公积 |  |
| cash_equivalents | decimal(20,4) | 货币资金 |  |
| code | varchar(12) | 股票代码 |  |
| commission_payable | decimal(20,4) | 应付手续费及佣金 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| constru_in_process | decimal(20,4) | 在建工程 |  |
| construction_materials | decimal(20,4) | 工程物资 |  |
| contract_assets | decimal(20,4) | 合同资产 |  |
| contract_liability | decimal(20,4) | 合同负债 |  |
| deferred_earning | decimal(20,4) | 递延收益-非流动负债 |  |
| deferred_earning_current | decimal(20,4) | 递延收益-流动负债 |  |
| deferred_tax_assets | decimal(20,4) | 递延所得税资产 |  |
| deferred_tax_liability | decimal(20,4) | 递延所得税负债 |  |
| deposit_in_interbank | decimal(20,4) | 吸收存款及同业存放 |  |
| derivative_financial_asset | decimal(20,4) | 衍生金融资产 |  |
| derivative_financial_liability | decimal(20,4) | 衍生金融负债 |  |
| development_expenditure | decimal(20,4) | 开发支出 |  |
| dividend_payable | decimal(20,4) | 应付股利 |  |
| dividend_receivable | decimal(20,4) | 应收股利 |  |
| end_date | date | 截止日期 |  |
| equities_parent_company_owners | decimal(20,4) | 归属于母公司所有者权益 |  |
| estimate_liability | decimal(20,4) | 预计负债 |  |
| estimate_liability_current | decimal(20,4) | 预计负债-流动负债 |  |
| expendable_biological_asset | decimal(20,4) | 消耗性生物资产 | 消耗性生物资产，是指为出售而持有的、或在将来收获为农产品的生物资产，包括生长中的大田作物、蔬菜、用材林，以及存栏代售的牲畜等 |
| fixed_assets | decimal(20,4) | 固定资产 |  |
| fixed_assets_liquidation | decimal(20,4) | 固定资产清理 |  |
| foreign_currency_report_conv_diff | decimal(20,4) | 外币报表折算价差 |  |
| good_will | decimal(20,4) | 商誉 |  |
| h_code | varchar(12) | H股代码 |  |
| hold_for_sale_assets | decimal(20,4) | 可供出售金融资产 |  |
| hold_sale_asset | decimal(20,4) | 划分为持有待售的资产 |  |
| hold_sale_liability | decimal(20,4) | 划分为持有待售的负债 |  |
| hold_to_maturity_investments | decimal(20,4) | 持有至到期投资 |  |
| insurance_contract_reserves | decimal(20,4) | 保险合同准备金 |  |
| insurance_receivables | decimal(20,4) | 应收保费 |  |
| intangible_assets | decimal(20,4) | 无形资产 |  |
| interest_payable | decimal(20,4) | 应付利息 |  |
| interest_receivable | decimal(20,4) | 应收利息 |  |
| inventories | decimal(20,4) | 存货 |  |
| investment_property | decimal(20,4) | 投资性房地产 |  |
| irregular_item_adjustment | decimal(20,4) | 非正常经营项目收益调整 |  |
| lease_liability | decimal(20,4) | 租赁负债 |  |
| lend_capital | decimal(20,4) | 拆出资金 |  |
| loan_and_advance_current_assets | decimal(20,4) | 发放贷款及垫款-流动资产 |  |
| loan_and_advance_noncurrent_assets | decimal(20,4) | 发放贷款及垫款-非流动资产 |  |
| long_deferred_expense | decimal(20,4) | 长期待摊费用 |  |
| longterm_account_payable | decimal(20,4) | 长期应付款 |  |
| longterm_equity_invest | decimal(20,4) | 长期股权投资 |  |
| longterm_loan | decimal(20,4) | 长期借款 |  |
| longterm_receivable_account | decimal(20,4) | 长期应收款 |  |
| longterm_salaries_payable | decimal(20,4) | 长期应付职工薪酬 |  |
| minority_interests | decimal(20,4) | 少数股东权益 |  |
| non_current_asset_in_one_year | decimal(20,4) | 一年内到期的非流动资产 |  |
| non_current_liability_in_one_year | decimal(20,4) | 一年内到期的非流动负债 |  |
| notes_payable | decimal(20,4) | 应付票据 |  |
| oil_gas_assets | decimal(20,4) | 油气资产 |  |
| ordinary_risk_reserve_fund | decimal(20,4) | 一般风险准备 |  |
| other_bond_invest | decimal(20,4) | 其他债权投资 |  |
| other_comprehensive_income | decimal(20,4) | 其他综合收益 |  |
| other_current_assets | decimal(20,4) | 其他流动资产 |  |
| other_current_liability | decimal(20,4) | 其他流动负债 |  |
| other_equity_tools | decimal(20,4) | 其他权益工具 |  |
| other_equity_tools_invest | decimal(20,4) | 其他权益工具投资 |  |
| other_non_current_assets | decimal(20,4) | 其他非流动资产 |  |
| other_non_current_financial_assets | decimal(20,4) | 其他非流动金融资产 |  |
| other_non_current_liability | decimal(20,4) | 其他非流动负债 |  |
| other_payable | decimal(20,4) | 其他应付款 |  |
| other_receivable | decimal(20,4) | 其他应收款 |  |
| paidin_capital | decimal(20,4) | 实收资本（或股本） |  |
| pepertual_liability_equity | decimal(20,4) | 永续债-所有者权益 |  |
| pepertual_liability_noncurrent | decimal(20,4) | 永续债-非流动负债 |  |
| preferred_shares_equity | decimal(20,4) | 其中：优先股-所有者权益 |  |
| preferred_shares_noncurrent | decimal(20,4) | 优先股-非流动负债 |  |
| proxy_secu_proceeds | decimal(20,4) | 代理买卖证券款 |  |
| pub_date | date | 公告日期 |  |
| receivable_fin | decimal(20,4) | 应收款项融资 |  |
| receivings_from_vicariously_sold_securities | decimal(20,4) | 代理承销证券款 |  |
| reinsurance_contract_reserves_receivable | decimal(20,4) | 应收分保合同准备金 |  |
| reinsurance_payables | decimal(20,4) | 应付分保账款 |  |
| reinsurance_receivables | decimal(20,4) | 应收分保账款 |  |
| report_date | date | 报告期 |  |
| report_type | int | 报告期类型 | 0本期，1上期 |
| retained_profit | decimal(20,4) | 未分配利润 |  |
| salaries_payable | decimal(20,4) | 应付职工薪酬 |  |
| settlement_provi | decimal(20,4) | 结算备付金 |  |
| shortterm_loan | decimal(20,4) | 短期借款 |  |
| sold_buyback_secu_proceeds | decimal(20,4) | 卖出回购金融资产款 |  |
| source | varchar(60) | 报表来源 |  |
| source_id | int | 报表来源编码 | 如下 报表来源编码 |
| specific_account_payable | decimal(20,4) | 专项应付款 |  |
| specific_reserves | decimal(20,4) | 专项储备 |  |
| surplus_reserve_fund | decimal(20,4) | 盈余公积 |  |
| taxs_payable | decimal(20,4) | 应交税费 |  |
| total_assets | decimal(20,4) | 资产总计 |  |
| total_current_assets | decimal(20,4) | 流动资产合计 |  |
| total_current_liability | decimal(20,4) | 流动负债合计 |  |
| total_liability | decimal(20,4) | 负债合计 |  |
| total_non_current_assets | decimal(20,4) | 非流动资产合计 |  |
| total_non_current_liability | decimal(20,4) | 非流动负债合计 |  |
| total_owner_equities | decimal(20,4) | 所有者权益（或股东权益）合计 |  |
| total_sheet_owner_equities | decimal(20,4) | 负债和所有者权益（或股东权益）合计 |  |
| trading_assets | decimal(20,4) | 交易性金融资产 |  |
| trading_liability | decimal(20,4) | 交易性金融负债 |  |
| treasury_stock | decimal(20,4) | 库存股 |  |
| usufruct_assets | decimal(20,4) | 使用权资产 |  |

## STK_CAPITAL_CHANGE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| change_date | date | 变动日期 |  |
| change_reason | varchar(120) | 变动原因 |  |
| change_reason_id | int | 变动原因编码 |  |
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| control_shareholder_limited | decimal(20,4) | 控股股东、实际控制人(受限) | 单位:万股 |
| core_employee_limited | decimal(20,4) | 核心员工(受限) | 单位:万股 |
| individual_fund_limited | decimal(20,4) | 个人或基金(受限) | 单位:万股 |
| legal of other_instate_limited | decimal(20,4) | 其他内资持股（受限）中的境内法人持股 | 单位:万股 |
| legal of outstate_limited | decimal(20,4) | 外资持股（受限）中的境外法人持股 | 单位:万股 |
| natural of other_instate_limited | decimal(20,4) | 其他内资持股（受限）中的境内自然人持股 | 单位:万股 |
| natural of outstate_limited | decimal(20,4) | 外资持股（受限）境外自然人持股 | 单位:万股 |
| other_instate_limited | decimal(20,4) | 其他内资持股（受限） | 单位:万股 |
| other_legal_limited | decimal(20,4) | 其他法人(受限) | 单位:万股 |
| other_limited | decimal(20,4) | 其他(受限) | 单位:万股 |
| outstate_limited | decimal(20,4) | 外资持股（受限） | 单位:万股 |
| pub_date | date | 公告日期 |  |
| share_b | decimal(20,4) | 境内上市外资股（B股） | 单位:万股 |
| share_b_limited | decimal（20,4） | 限售B股 | 单位:万股 |
| share_convert | decimal(20,4) | 转配股 | 单位:万股 |
| share_fund | decimal(20,4) | 证券投资基金持股 | 单位:万股 |
| share_h | decimal(20,4) | 境外上市外资股（H股） | 单位:万股 |
| share_h_limited | decimal(20,4) | 限售H股 | 单位:万股 |
| share_inside | decimal(20,4) | 内部职工股 | 单位:万股 |
| share_instate_legal | decimal(20,4) | 境内法人持股 | 单位:万股 |
| share_legal_issue | decimal(20,4) | 配售法人股 | 战略投资配售股份+证券投资基金配售股份+一般法人配售股份 |
| share_limited | decimal(20,4) | 流通受限股份 | 单位:万股 |
| share_management | decimal(20,4) | 高管股 | 单位:万股 |
| share_management_limited | decimal(20,4) | 限售高管股 | 单位:万股 |
| share_nation | decimal(20,4) | 国家持股 | 单位:万股 |
| share_nation_legal | decimal(20,4) | 国有法人持股 | 单位:万股 |
| share_nation_legal_limited | decimal(20,4) | 国有法人持股（受限） | 单位:万股 |
| share_nation_limited | decimal(20,4) | 国家持股（受限） | 单位:万股 |
| share_natural | decimal(20,4) | 自然人持股 | 单位:万股 |
| share_non_trade | decimal(20,4) | 未流通股份 | 发起人股份 + 募集法人股份 + 内部职工股 + 优先股 +转配股+其他未流通股+配售法人股+已发行未上市股份 |
| share_normal_legal | decimal(20,4) | 一般法人持股 | 单位:万股 |
| share_other_limited | decimal(20,4) | 其他流通受限股份 | 单位:万股 |
| share_other_nontrade | decimal(20,4) | 其他未流通股 | 单位:万股 |
| share_other_trade | decimal(20,4) | 其他流通股 | 单位:万股 |
| share_outstate_legal | decimal(20,4) | 境外法人持股 | 单位:万股 |
| share_perferred | decimal(20,4) | 优先股 | 单位:万股 |
| share_raised | decimal(20,4) | 募集法人股 | 单位:万股 |
| share_rmb | decimal(20,4) | 人民币普通股 | 单位:万股 |
| share_start | decimal(20,4) | 发起人股份 | 国家持股 +国有法人持股+境内法人持股 + 境外法人持股 + 自然人持股 |
| share_strategic_investor | decimal(20,4) | 战略投资者持股 | 单位:万股 |
| share_total | decimal(20,4) | 总股本 | 未流通股份+已流通股份，单位：万股 |
| share_trade_total | decimal(20,4) | 已流通股份（自由流通股） | 人民币普通股+ 境内上市外资股(B股)+ 境外上市外资股(H股)+高管股+ 其他流通股 |

## STK_CASHFLOW_STATEMENT

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_code | varchar(12) | A股代码 |  |
| assets_depreciation_reserves | decimal(20,4) | 资产减值准备 |  |
| b_code | varchar(12) | B股代码 |  |
| borrowing_repayment | decimal(20,4) | 偿还债务支付的现金 |  |
| cash_and_equivalents_at_end | decimal(20,4) | 期末现金及现金等价物余额 |  |
| cash_at_beginning | decimal(20,4) | 现金的期初余额 |  |
| cash_at_end | decimal(20,4) | 现金的期末余额 |  |
| cash_equivalent_increase | decimal(20,4) | 现金及现金等价物净增加额 |  |
| cash_equivalent_increase_indirect | decimal(20,4) | 现金及现金等价物净增加额_间接法 |  |
| cash_equivalents_at_beginning | decimal(20,4) | 期初现金及现金等价物余额 |  |
| cash_from_bonds_issue | decimal(20,4) | 发行债券收到的现金 |  |
| cash_from_borrowing | decimal(20,4) | 取得借款收到的现金 |  |
| cash_from_invest | decimal(20,4) | 吸收投资收到的现金 |  |
| cash_from_mino_s_invest_sub | decimal(20,4) | 子公司吸收少数股东投资收到的现金 |  |
| cbs_expiring_in_one_year | decimal(20,4) | 一年内到期的可转换公司债券 |  |
| code | varchar(12) | 股票主证券代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| credit_impairment_loss | decimal(20,4) | 信用减值损失(现金流量表补充科目) |  |
| debt_to_capital | decimal(20,4) | 债务转为资本 |  |
| deffered_tax_asset_decrease | decimal(20,4) | 递延所得税资产减少 |  |
| deffered_tax_liability_increase | decimal(20,4) | 递延所得税负债增加 |  |
| defferred_expense_amortization | decimal(20,4) | 长期待摊费用摊销 |  |
| dividend_interest_payment | decimal(20,4) | 分配股利、利润或偿付利息支付的现金 |  |
| end_date | date | 截止日期 |  |
| equivalents_at_beginning | decimal(20,4) | 现金等价物的期初余额 |  |
| equivalents_at_end | decimal(20,4) | 现金等价物的期末余额 |  |
| exchange_rate_change_effect | decimal(20,4) | 汇率变动对现金的影响 |  |
| fair_value_change_loss | decimal(20,4) | 公允价值变动损失 |  |
| financial_cost | decimal(20,4) | 财务费用 |  |
| financial_lease_fixed_assets | decimal(20,4) | 融资租入固定资产 |  |
| fix_intan_other_asset_acqui_cash | decimal(20,4) | 购建固定资产、无形资产和其他长期资产支付的现金 |  |
| fix_intan_other_asset_dispo_cash | decimal(20,4) | 处置固定资产、无形资产和其他长期资产收回的现金净额 |  |
| fix_intan_other_asset_dispo_loss | decimal(20,4) | 处置固定资产、无形资产和其他长期资产的损失 |  |
| fixed_asset_scrap_loss | decimal(20,4) | 固定资产报废损失 |  |
| fixed_assets_depreciation | decimal(20,4) | 固定资产折旧、油气资产折耗、生产性生物资产折旧 |  |
| goods_and_services_cash_paid | decimal(20,4) | 购买商品、接受劳务支付的现金 |  |
| goods_sale_and_service_render_cash | decimal(20,4) | 销售商品、提供劳务收到的现金 |  |
| h_code | varchar(12) | H股代码 |  |
| handling_charges_and_commission | decimal(20,4) | 支付利息、手续费及佣金的现金 |  |
| impawned_loan_net_increase | decimal(20,4) | 质押贷款净增加额 |  |
| intangible_assets_amortization | decimal(20,4) | 无形资产摊销 |  |
| interest_and_commission_cashin | decimal(20,4) | 收取利息、手续费及佣金的现金 |  |
| inventory_decrease | decimal(20,4) | 存货的减少 |  |
| invest_cash_paid | decimal(20,4) | 投资支付的现金 |  |
| invest_loss | decimal(20,4) | 投资损失 |  |
| invest_proceeds | decimal(20,4) | 取得投资收益收到的现金 |  |
| invest_withdrawal_cash | decimal(20,4) | 收回投资收到的现金 |  |
| investment_property_depreciation | decimal(20,4) | 投资性房地产的折旧及摊销 |  |
| net_borrowing_from_central_bank | decimal(20,4) | 向中央银行借款净增加额 |  |
| net_borrowing_from_finance_co | decimal(20,4) | 向其他金融机构拆入资金净增加额 |  |
| net_buyback | decimal(20,4) | 回购业务资金净增加额 |  |
| net_cash_deal_subcompany | decimal(20,4) | 处置子公司及其他营业单位收到的现金净额 |  |
| net_cash_from_sub_company | decimal(20,4) | 取得子公司及其他营业单位支付的现金净额 |  |
| net_cash_received_from_         reinsurance_business | decimal(20,4) | 收到再保险业务现金净额 |  |
| net_deal_trading_assets | decimal(20,4) | 处置以公允价值计量且其变动计入当期损益的金融资产净增加额 |  |
| net_deposit_in_cb_and_ib | decimal(20,4) | 存放中央银行和同业款项净增加额 |  |
| net_deposit_increase | decimal(20,4) | 客户存款和同业存放款项净增加额 |  |
| net_finance_cash_flow | decimal(20,4) | 筹资活动现金流量净额 |  |
| net_increase_in_placements | decimal(20,4) | 拆入资金净增加额 |  |
| net_insurer_deposit_investment | decimal(20,4) | 保户储金及投资款净增加额 |  |
| net_invest_cash_flow | decimal(20,4) | 投资活动现金流量净额 |  |
| net_loan_and_advance_increase | decimal(20,4) | 客户贷款及垫款净增加额 |  |
| net_operate_cash_flow | decimal(20,4) | 经营活动现金流量净额 |  |
| net_operate_cash_flow_indirect | decimal(20,4) | 经营活动现金流量净额_间接法 |  |
| net_original_insurance_cash | decimal(20,4) | 收到原保险合同保费取得的现金 |  |
| net_profit | decimal(20,4) | 净利润 |  |
| operate_payable_increase | decimal(20,4) | 经营性应付项目的增加 |  |
| operate_receivables_decrease | decimal(20,4) | 经营性应收项目的减少 |  |
| original_compensation_paid | decimal(20,4) | 支付原保险合同赔付款项的现金 |  |
| other_reason_effect_cash | decimal(20,4) | 其他原因对现金的影响 |  |
| other_reason_effect_cash_indirect | decimal(20,4) | 其他原因对现金的影响_间接法 |  |
| others | decimal(20,4) | 其他 |  |
| policy_dividend_cash_paid | decimal(20,4) | 支付保单红利的现金 |  |
| proceeds_from_sub_to_mino_s | decimal(20,4) | 子公司支付给少数股东的股利、利润 |  |
| pub_date | date | 公告日期 |  |
| report_date | date | 报告期 |  |
| report_type | int | 报告期类型 | 0本期，1上期 |
| source | varchar(60) | 报表来源 |  |
| source_id | int | 报表来源编码 | 如下报表来源编码 |
| staff_behalf_paid | decimal(20,4) | 支付给职工以及为职工支付的现金 |  |
| start_date | date | 开始日期 |  |
| subtotal_finance_cash_inflow | decimal(20,4) | 筹资活动现金流入小计 |  |
| subtotal_finance_cash_outflow | decimal(20,4) | 筹资活动现金流出小计 |  |
| subtotal_invest_cash_inflow | decimal(20,4) | 投资活动现金流入小计 |  |
| subtotal_invest_cash_outflow | decimal(20,4) | 投资活动现金流出小计 |  |
| subtotal_operate_cash_inflow | decimal(20,4) | 经营活动现金流入小计 |  |
| subtotal_operate_cash_outflow | decimal(20,4) | 经营活动现金流出小计 |  |
| tax_levy_refund | decimal(20,4) | 收到的税费返还 |  |
| tax_payments | decimal(20,4) | 支付的各项税费 |  |

## STK_CASHFLOW_STATEMENT_PARENT

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_code | varchar(12) | A股代码 |  |
| assets_depreciation_reserves | decimal(20,4) | 资产减值准备 |  |
| b_code | varchar(12) | B股代码 |  |
| borrowing_repayment | decimal(20,4) | 偿还债务支付的现金 |  |
| cash_and_equivalents_at_end | decimal(20,4) | 期末现金及现金等价物余额 |  |
| cash_at_beginning | decimal(20,4) | 现金的期初余额 |  |
| cash_at_end | decimal(20,4) | 现金的期末余额 |  |
| cash_equivalent_increase | decimal(20,4) | 现金及现金等价物净增加额 |  |
| cash_equivalent_increase_indirect | decimal(20,4) | 现金及现金等价物净增加额_间接法 |  |
| cash_equivalents_at_beginning | decimal(20,4) | 期初现金及现金等价物余额 |  |
| cash_from_bonds_issue | decimal(20,4) | 发行债券收到的现金 |  |
| cash_from_borrowing | decimal(20,4) | 取得借款收到的现金 |  |
| cash_from_invest | decimal(20,4) | 吸收投资收到的现金 |  |
| cash_from_mino_s_invest_sub | decimal(20,4) | 子公司吸收少数股东投资收到的现金 |  |
| cbs_expiring_in_one_year | decimal(20,4) | 一年内到期的可转换公司债券 |  |
| code | varchar(12) | 股票主证券代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| credit_impairment_loss | decimal(20,4) | 信用减值损失(现金流量表补充科目) |  |
| debt_to_capital | decimal(20,4) | 债务转为资本 |  |
| deffered_tax_asset_decrease | decimal(20,4) | 递延所得税资产减少 |  |
| deffered_tax_liability_increase | decimal(20,4) | 递延所得税负债增加 |  |
| defferred_expense_amortization | decimal(20,4) | 长期待摊费用摊销 |  |
| dividend_interest_payment | decimal(20,4) | 分配股利、利润或偿付利息支付的现金 |  |
| end_date | date | 截止日期 |  |
| equivalents_at_beginning | decimal(20,4) | 现金等价物的期初余额 |  |
| equivalents_at_end | decimal(20,4) | 现金等价物的期末余额 |  |
| exchange_rate_change_effect | decimal(20,4) | 汇率变动对现金的影响 |  |
| fair_value_change_loss | decimal(20,4) | 公允价值变动损失 |  |
| financial_cost | decimal(20,4) | 财务费用 |  |
| financial_lease_fixed_assets | decimal(20,4) | 融资租入固定资产 |  |
| fix_intan_other_asset_acqui_cash | decimal(20,4) | 购建固定资产、无形资产和其他长期资产支付的现金 |  |
| fix_intan_other_asset_dispo_cash | decimal(20,4) | 处置固定资产、无形资产和其他长期资产收回的现金净额 |  |
| fix_intan_other_asset_dispo_loss | decimal(20,4) | 处置固定资产、无形资产和其他长期资产的损失 |  |
| fixed_asset_scrap_loss | decimal(20,4) | 固定资产报废损失 |  |
| fixed_assets_depreciation | decimal(20,4) | 固定资产折旧、油气资产折耗、生产性生物资产折旧 |  |
| goods_and_services_cash_paid | decimal(20,4) | 购买商品、接受劳务支付的现金 |  |
| goods_sale_and_service_render_cash | decimal(20,4) | 销售商品、提供劳务收到的现金 |  |
| h_code | varchar(12) | H股代码 |  |
| handling_charges_and_commission | decimal(20,4) | 支付利息、手续费及佣金的现金 |  |
| impawned_loan_net_increase | decimal(20,4) | 质押贷款净增加额 |  |
| intangible_assets_amortization | decimal(20,4) | 无形资产摊销 |  |
| interest_and_commission_cashin | decimal(20,4) | 收取利息、手续费及佣金的现金 |  |
| inventory_decrease | decimal(20,4) | 存货的减少 |  |
| invest_cash_paid | decimal(20,4) | 投资支付的现金 |  |
| invest_loss | decimal(20,4) | 投资损失 |  |
| invest_proceeds | decimal(20,4) | 取得投资收益收到的现金 |  |
| invest_withdrawal_cash | decimal(20,4) | 收回投资收到的现金 |  |
| investment_property_depreciation | decimal(20,4) | 投资性房地产的折旧及摊销 |  |
| net_borrowing_from_central_bank | decimal(20,4) | 向中央银行借款净增加额 |  |
| net_borrowing_from_finance_co | decimal(20,4) | 向其他金融机构拆入资金净增加额 |  |
| net_buyback | decimal(20,4) | 回购业务资金净增加额 |  |
| net_cash_deal_subcompany | decimal(20,4) | 处置子公司及其他营业单位收到的现金净额 |  |
| net_cash_from_sub_company | decimal(20,4) | 取得子公司及其他营业单位支付的现金净额 |  |
| net_cash_received_from_         reinsurance_business | decimal(20,4) | 收到再保险业务现金净额 |  |
| net_deal_trading_assets | decimal(20,4) | 处置以公允价值计量且其变动计入当期损益的金融资产净增加额 |  |
| net_deposit_in_cb_and_ib | decimal(20,4) | 存放中央银行和同业款项净增加额 |  |
| net_deposit_increase | decimal(20,4) | 客户存款和同业存放款项净增加额 |  |
| net_finance_cash_flow | decimal(20,4) | 筹资活动现金流量净额 |  |
| net_increase_in_placements | decimal(20,4) | 拆入资金净增加额 |  |
| net_insurer_deposit_investment | decimal(20,4) | 保户储金及投资款净增加额 |  |
| net_invest_cash_flow | decimal(20,4) | 投资活动现金流量净额 |  |
| net_loan_and_advance_increase | decimal(20,4) | 客户贷款及垫款净增加额 |  |
| net_operate_cash_flow | decimal(20,4) | 经营活动现金流量净额 |  |
| net_operate_cash_flow_indirect | decimal(20,4) | 经营活动现金流量净额_间接法 |  |
| net_original_insurance_cash | decimal(20,4) | 收到原保险合同保费取得的现金 |  |
| net_profit | decimal(20,4) | 净利润 |  |
| operate_payable_increase | decimal(20,4) | 经营性应付项目的增加 |  |
| operate_receivables_decrease | decimal(20,4) | 经营性应收项目的减少 |  |
| original_compensation_paid | decimal(20,4) | 支付原保险合同赔付款项的现金 |  |
| other_reason_effect_cash | decimal(20,4) | 其他原因对现金的影响 |  |
| other_reason_effect_cash_indirect | decimal(20,4) | 其他原因对现金的影响_间接法 |  |
| others | decimal(20,4) | 其他 |  |
| policy_dividend_cash_paid | decimal(20,4) | 支付保单红利的现金 |  |
| proceeds_from_sub_to_mino_s | decimal(20,4) | 子公司支付给少数股东的股利、利润 |  |
| pub_date | date | 公告日期 |  |
| report_date | date | 报告期 |  |
| report_type | int | 报告期类型 | 0本期，1上期 |
| source | varchar(60) | 报表来源 |  |
| source_id | int | 报表来源编码 | 如下报表来源编码 |
| staff_behalf_paid | decimal(20,4) | 支付给职工以及为职工支付的现金 |  |
| start_date | date | 开始日期 |  |
| subtotal_finance_cash_inflow | decimal(20,4) | 筹资活动现金流入小计 |  |
| subtotal_finance_cash_outflow | decimal(20,4) | 筹资活动现金流出小计 |  |
| subtotal_invest_cash_inflow | decimal(20,4) | 投资活动现金流入小计 |  |
| subtotal_invest_cash_outflow | decimal(20,4) | 投资活动现金流出小计 |  |
| subtotal_operate_cash_inflow | decimal(20,4) | 经营活动现金流入小计 |  |
| subtotal_operate_cash_outflow | decimal(20,4) | 经营活动现金流出小计 |  |
| tax_levy_refund | decimal(20,4) | 收到的税费返还 |  |
| tax_payments | decimal(20,4) | 支付的各项税费 |  |

## STK_COMPANY_INFO

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_code | varchar(12) | A股股票代码 |  |
| b_code | varchar(12) | B股股票代码 |  |
| business_scope | varchar(4000) | 经营范围 |  |
| ceo | varchar(100) | 总经理 |  |
| city | varchar(60) | 所属城市 |  |
| city_id | varchar(12) | 所属城市编码 |  |
| code | varchar(12) | 证券代码 | 多证券代码的优先级：A股>B股 |
| comments | varchar(300) | 备注 |  |
| company_id | int | 公司ID |  |
| contact_number | varchar(60) | 联系电话 |  |
| cpafirm | varchar(200) | 会计师事务所 |  |
| currency | varchar(32) | 货币名称 |  |
| currency_id | int | 货币编码 |  |
| description | varchar(4000) | 机构简介 |  |
| email | varchar(80) | 电子信箱 |  |
| establish_date | date | 成立日期 |  |
| fax_number | varchar(60) | 联系传真 |  |
| full_name | varchar(100) | 公司名称 |  |
| fullname_en | varchar(100) | 英文名称 |  |
| h_code | varchar(12) | H股股票代码 |  |
| industry_1 | varchar(60) | 行业一级分类 |  |
| industry_2 | varchar(60) | 行业二级分类 |  |
| industry_id | varchar(12) | 行业编码 | 证监会行业分类 |
| lawfirm | varchar(200) | 律师事务所 |  |
| legal_representative | varchar(40) | 法人代表 |  |
| license_number | varchar(40) | 法人营业执照号 |  |
| main_business | varchar(500) | 主营业务 |  |
| office_address | varchar(150) | 办公地址 |  |
| province | varchar(60) | 所属省份 |  |
| province_id | varchar(12) | 所属省份编码 |  |
| pub_newspaper | varchar(120) | 指定信息披露报刊 |  |
| pub_website | varchar(120) | 指定信息披露网站 |  |
| register_capital | decimal(20,4) | 注册资金 | 单位：万元 |
| register_location | varchar(100) | 注册地址 |  |
| secretary | varchar(40) | 董事会秘书 |  |
| secretary_email | varchar(80) | 董秘电子邮箱 |  |
| secretary_fax | varchar(60) | 董秘联系传真 |  |
| secretary_number | varchar(60) | 董秘联系电话 |  |
| security_representative | varchar(40) | 证券事务代表 |  |
| short_name | varchar(40) | 公司简称 |  |
| shortname_en | varchar(40) | 英文简称 |  |
| tax_number | varchar(50) | 税务登记号 |  |
| website | varchar(80) | 机构网址 |  |
| zipcode | varchar(10) | 邮政编码 |  |

## STK_EL_CONST_CHANGE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| change_date | date | 变更日期 |  |
| code | varchar(12) | 证券代码 |  |
| direction | varchar(6) | 变更方向 | IN/OUT（分别为纳入和剔除） |
| exchange | varchar(12) | 该股票所在的交易所 | 上海市场:XSHG/深圳市场:XSHE/香港市场:XHKG |
| link_id | int | 交易类型编码 | 同市场通编码 |
| link_name | varchar(12) | 交易类型名称 |  |
| name_ch | varchar(30) | 中文简称 |  |
| name_en | varchar(120) | 英文简称 |  |

## STK_EL_TOP_ACTIVATE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| buy | decimal(20, 4) | 买入金额(元) |  |
| code | varchar(12) | 股票代码 |  |
| day | date | 日期 |  |
| exchange | varchar(12) | 交易所名称 |  |
| link_id | int | 市场通编码 |  |
| link_name | varchar(32) | 市场通名称 | 包括以下四个名称：沪股通， 深股通， 港股通(沪)，港股通(深) |
| name | varchar(100) | 股票名称 |  |
| rank | int | 排名 |  |
| sell | decimal(20, 4) | 卖出金额(元) |  |
| total | decimal(20, 4) | 买入及卖出金额(元) |  |
| 字段 | 类型 | 名称 | 备注/示例 |

## STK_EMPLOYEE_INFO

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 证券代码 | '600276.XSHG'，'000001.XSHE' |
| college_rate | decimal(10,4) | 大学专科以上人员比例 | % |
| company_id | int | 公司ID |  |
| employee | int | 在职员工总数 | 人 |
| end_date | date | 报告期截止日 | 统计截止该报告期的员工信息 |
| graduate_rate | decimal(10,4) | 研究生以上人员比例 | % |
| middle_rate | decimal(10,4) | 中专及以下人员比例 | % |
| name | varchar(64) | 证券名称 |  |
| pub_date | date | 公告日期 |  |
| retirement | int | 离退休人员 | 人 |

## STK_EXCHANGE_LINK_CALENDAR

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| day | date | 交易日期 |  |
| link_id | int | 市场通编码 |  |
| link_name | varchar(32) | 市场通名称 | 包括以下四个名称：沪股通， 深股通，港股通(沪)， 港股通(深) |
| type | varchar(32) | 交易日类型 |  |
| type_id | int | 交易日类型编码 | 如下 交易日类型编码 |
| 字段 | 类型 | 名称 | 备注/示例 |

## STK_EXCHANGE_LINK_RATE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| day | Date | 日期 |  |
| domestic_currency | varchar(12) | 本币 | RMB |
| foreign_currency | varchar(12) | 外币 | HKD |
| link_id | int | 市场通编码 |  |
| link_name | varchar(32) | 市场通名称 | 以“港股通(沪)”为代表 |
| refer_ask_rate | decimal(10, 5) | 卖出参考汇率 |  |
| refer_bid_rate | decimal(10, 5) | 买入参考汇率 |  |
| settle_ask_rate | decimal(10, 5) | 卖出结算汇率 |  |
| settle_bid_rate | decimal(10, 5) | 买入结算汇率 |  |

## STK_EXCHANGE_TRADE_INFO

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| circulating_market_cap | decimal(20,8) | 流通市值 | 单位：亿 |
| date | date | 交易日期 |  |
| deal_number | decimal(20,4) | 成交笔数 | 单位：万笔 |
| exchange_code | varchar(12) | 市场编码 | 编码规则见下表 |
| exchange_name | varchar(100) | 市场名称 | 上海市场，上海A股，上海B股深圳市场，深市主板中小企业板，创业板 |
| money | decimal(20,8) | 成交金额 | 单位：亿 |
| pe_average | decimal(20,4) | 平均市盈率 | 上海市场市盈率计算方法：市盈率＝∑(收盘价×发行数量)/∑(每股收益×发行数量)，统计时剔除亏损及暂停上市的上市公司。深圳市场市盈率计算方法：市盈率＝∑市价总值/∑(总股本×上年每股利润)，剔除上年利润为负的公司。 |
| total_market_cap | decimal(20,8) | 市价总值 | 单位：亿 |
| turnover_ratio | decimal(10,4) | 换手率 | 单位：％ |
| volume | decimal(20,4) | 成交量 | 单位：万 |

## STK_FIN_FORCAST

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| content | varchar(2048) | 预告内容 |  |
| end_date | date | 报告期 |  |
| name | varchar(64) | 公司名称 |  |
| profit_last | decimal(22,6) | 去年同期净利润 |  |
| profit_max | decimal(22,6) | 预告净利润（上限） |  |
| profit_min | decimal(22,6) | 预告净利润（下限） |  |
| profit_ratio_max | decimal(10,4) | 预告净利润变动幅度(上限) | 单位：% |
| profit_ratio_min | decimal(10,4) | 预告净利润变动幅度(下限) | 单位：% |
| pub_date | date | 公布日期 |  |
| report_type | varchar(32) | 预告期类型 |  |
| report_type_id | int | 预告期类型编码 | 如下 预告期类型编码 |
| type | varchar(32) | 预告类型 |  |
| type_id | int | 预告类型编码 | 如下 业绩类型编码 |

## STK_HK_HOLD_INFO

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 股票代码 |  |
| day | date | 日期 |  |
| link_id | int | 市场通编码 | 三种类型：310001-沪股通，310002-深股通，310005-港股通 |
| link_name | varchar(32) | 市场通名称 | 三种类型：沪股通，深股通，港股通 |
| name | varchar(100) | 股票名称 |  |
| share_number | int | 持股数量 | 单位：股，于中央结算系统的持股量 |
| share_ratio | decimal(10,4) | 持股比例 | 单位：％，沪股通：占于上交所上市及交易的A股总数的百分比；深股通：占于深交所上市及交易的A股总数的百分比；港股通：占已发行股份百分比 |

## STK_HOLDER_NUM

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_share_holders | int | A股股东总户数 |  |
| b_share_holders | int | B股股东总户数 |  |
| code | varchar(12) | 股票代码 |  |
| end_date | date | 截止日期 |  |
| h_share_holders | int | H股股东总户数 |  |
| pub_date | date | 公告日期 |  |
| share_holders | int | 股东总户数 |  |

## STK_INCOME_STATEMENT

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_code | varchar(12) | A股代码 |  |
| administration_expense | decimal(20,4) | 管理费用 |  |
| asset_deal_income | decimal(20,4) | 资产处置收益 |  |
| asset_impairment_loss | decimal(20,4) | 资产减值损失 |  |
| b_code | varchar(12) | B股代码 |  |
| basic_eps | decimal(20,4) | 基本每股收益 |  |
| ci_minority_owners | decimal(20,4) | 归属于少数股东的综合收益总额 |  |
| ci_parent_company_owners | decimal(20,4) | 归属于母公司所有者的综合收益总额 |  |
| code | varchar(12) | 股票代码 |  |
| commission_expense | decimal(20,4) | 手续费及佣金支出 |  |
| commission_income | decimal(20,4) | 手续费及佣金收入 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| credit_impairment_loss | decimal(20,4) | 信用减值损失 |  |
| diluted_eps | decimal(20,4) | 稀释每股收益 |  |
| discon_operate_net_profit | decimal(20,4) | 终止经营净利润 |  |
| disposal_loss_non_current_liability | decimal(20,4) | 非流动资产处置净损失 |  |
| end_date | date | 截止日期 |  |
| eps | decimal(20,4) | 每股收益 |  |
| exchange_income | decimal(20,4) | 汇兑收益 |  |
| exploration_expense | decimal(20,4) | 堪探费用 | 勘探费用用于核算企业（石油天然气开采）核算的油气勘探过程中发生的地质调查、物理化学勘探各项支出和非成功探井等支出。 |
| fair_value_variable_income | decimal(20,4) | 公允价值变动净收益 |  |
| financial_expense | decimal(20,4) | 财务费用 |  |
| h_code | varchar(12) | H股代码 |  |
| income_tax | decimal(20,4) | 所得税 |  |
| interest_cost_fin | decimal(20,4) | 财务费用-利息费用 |  |
| interest_expense | decimal(20,4) | 利息支出 |  |
| interest_income | decimal(20,4) | 利息收入 |  |
| interest_income_fin | decimal(20,4) | 财务费用-利息收入 |  |
| invest_income_associates | decimal(20,4) | 对联营企业和合营企业的投资收益 |  |
| investment_income | decimal(20,4) | 投资收益 |  |
| minority_profit | decimal(20,4) | 少数股东损益 |  |
| net_open_hedge_income | decimal(20,4) | 净敞口套期收益 |  |
| net_pay_insurance_claims | decimal(20,4) | 赔付支出净额 |  |
| net_profit | decimal(20,4) | 净利润 |  |
| non_current_asset_disposed | decimal(20,4) | 非流动资产处置利得 |  |
| non_operating_expense | decimal(20,4) | 营业外支出 |  |
| non_operating_revenue | decimal(20,4) | 营业外收入 |  |
| np_parent_company_owners | decimal(20,4) | 归属于母公司所有者的净利润 |  |
| operating_cost | decimal(20,4) | 营业成本 |  |
| operating_profit | decimal(20,4) | 营业利润 |  |
| operating_revenue | decimal(20,4) | 营业收入 |  |
| operating_tax_surcharges | decimal(20,4) | 营业税金及附加 |  |
| other_composite_income | decimal(20,4) | 其他综合收益 |  |
| other_earnings | decimal(20,4) | 其他收益 |  |
| other_items_influenced_income | decimal(20,4) | 影响营业利润的其他科目 |  |
| other_items_influenced_net_profit | decimal(20,4) | 影响净利润的其他科目 |  |
| other_items_influenced_profit | decimal(20,4) | 影响利润总额的其他科目 |  |
| policy_dividend_payout | decimal(20,4) | 保单红利支出 |  |
| premiums_earned | decimal(20,4) | 已赚保费 |  |
| pub_date | date | 公告日期 |  |
| rd_expenses | decimal(20,4) | 研发费用 |  |
| refunded_premiums | decimal(20,4) | 退保金 |  |
| reinsurance_cost | decimal(20,4) | 分保费用 |  |
| report_date | date | 报告期 |  |
| report_type | int | 报告期类型 | 0：本期，1：上期 |
| sale_expense | decimal(20,4) | 销售费用 |  |
| source | varchar(60) | 报表来源 | 选择时程序自动填入 |
| source_id | int | 报表来源编码 | 如下 报表来源编码 |
| start_date | date | 开始日期 |  |
| subsidy_income | decimal(20,4) | 补贴收入 |  |
| sust_operate_net_profit | decimal(20,4) | 持续经营净利润 |  |
| total_composite_income | decimal(20,4) | 综合收益总额 |  |
| total_operating_cost | decimal(20,4) | 营业总成本 |  |
| total_operating_revenue | decimal(20,4) | 营业总收入 |  |
| total_profit | decimal(20,4) | 利润总额 |  |
| withdraw_insurance_contract_reserve | decimal(20,4) | 提取保险合同准备金净额 |  |

## STK_INCOME_STATEMENT_PARENT

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_code | varchar(12) | A股代码 |  |
| administration_expense | decimal(20,4) | 管理费用 |  |
| asset_deal_income | decimal(20,4) | 资产处置收益 |  |
| asset_impairment_loss | decimal(20,4) | 资产减值损失 |  |
| b_code | varchar(12) | B股代码 |  |
| basic_eps | decimal(20,4) | 基本每股收益 |  |
| ci_minority_owners | decimal(20,4) | 归属于少数股东的综合收益总额 |  |
| ci_parent_company_owners | decimal(20,4) | 归属于母公司所有者的综合收益总额 |  |
| code | varchar(12) | 股票代码 |  |
| commission_expense | decimal(20,4) | 手续费及佣金支出 |  |
| commission_income | decimal(20,4) | 手续费及佣金收入 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| credit_impairment_loss | decimal(20,4) | 信用减值损失 |  |
| diluted_eps | decimal(20,4) | 稀释每股收益 |  |
| discon_operate_net_profit | decimal(20,4) | 终止经营净利润 |  |
| disposal_loss_non_current_liability | decimal(20,4) | 非流动资产处置净损失 |  |
| end_date | date | 截止日期 |  |
| eps | decimal(20,4) | 每股收益 |  |
| exchange_income | decimal(20,4) | 汇兑收益 |  |
| exploration_expense | decimal(20,4) | 堪探费用 | 勘探费用用于核算企业（石油天然气开采）核算的油气勘探过程中发生的地质调查、物理化学勘探各项支出和非成功探井等支出。 |
| fair_value_variable_income | decimal(20,4) | 公允价值变动净收益 |  |
| financial_expense | decimal(20,4) | 财务费用 |  |
| h_code | varchar(12) | H股代码 |  |
| income_tax | decimal(20,4) | 所得税 |  |
| interest_cost_fin | decimal(20,4) | 财务费用-利息费用 |  |
| interest_expense | decimal(20,4) | 利息支出 |  |
| interest_income | decimal(20,4) | 利息收入 |  |
| interest_income_fin | decimal(20,4) | 财务费用-利息收入 |  |
| invest_income_associates | decimal(20,4) | 对联营企业和合营企业的投资收益 |  |
| investment_income | decimal(20,4) | 投资收益 |  |
| minority_profit | decimal(20,4) | 少数股东损益 |  |
| net_open_hedge_income | decimal(20,4) | 净敞口套期收益 |  |
| net_pay_insurance_claims | decimal(20,4) | 赔付支出净额 |  |
| net_profit | decimal(20,4) | 净利润 |  |
| non_current_asset_disposed | decimal(20,4) | 非流动资产处置利得 |  |
| non_operating_expense | decimal(20,4) | 营业外支出 |  |
| non_operating_revenue | decimal(20,4) | 营业外收入 |  |
| np_parent_company_owners | decimal(20,4) | 归属于母公司所有者的净利润 |  |
| operating_cost | decimal(20,4) | 营业成本 |  |
| operating_profit | decimal(20,4) | 营业利润 |  |
| operating_revenue | decimal(20,4) | 营业收入 |  |
| operating_tax_surcharges | decimal(20,4) | 营业税金及附加 |  |
| other_composite_income | decimal(20,4) | 其他综合收益 |  |
| other_earnings | decimal(20,4) | 其他收益 |  |
| other_items_influenced_income | decimal(20,4) | 影响营业利润的其他科目 |  |
| other_items_influenced_net_profit | decimal(20,4) | 影响净利润的其他科目 |  |
| other_items_influenced_profit | decimal(20,4) | 影响利润总额的其他科目 |  |
| policy_dividend_payout | decimal(20,4) | 保单红利支出 |  |
| premiums_earned | decimal(20,4) | 已赚保费 |  |
| pub_date | date | 公告日期 |  |
| rd_expenses | decimal(20,4) | 研发费用 |  |
| refunded_premiums | decimal(20,4) | 退保金 |  |
| reinsurance_cost | decimal(20,4) | 分保费用 |  |
| report_date | date | 报告期 |  |
| report_type | int | 报告期类型 | 0：本期，1：上期 |
| sale_expense | decimal(20,4) | 销售费用 |  |
| source | varchar(60) | 报表来源 | 选择时程序自动填入 |
| source_id | int | 报表来源编码 | 如下 报表来源编码 |
| start_date | date | 开始日期 |  |
| subsidy_income | decimal(20,4) | 补贴收入 |  |
| sust_operate_net_profit | decimal(20,4) | 持续经营净利润 |  |
| total_composite_income | decimal(20,4) | 综合收益总额 |  |
| total_operating_cost | decimal(20,4) | 营业总成本 |  |
| total_operating_revenue | decimal(20,4) | 营业总收入 |  |
| total_profit | decimal(20,4) | 利润总额 |  |
| withdraw_insurance_contract_reserve | decimal(20,4) | 提取保险合同准备金净额 |  |

## STK_LIMITED_SHARES_LIST

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| actual_unlimited_date | date | 实际解除限售日期 |  |
| actual_unlimited_number | int | 实际解除限售数量 | 单位：股 |
| actual_unlimited_ratio | decimal(10,4) | 实际解除限售比例 | 单位：％；实际解除限售数量占总股本比例 |
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| expected_unlimited_date | date | 预计解除限售日期 |  |
| expected_unlimited_number | int | 预计解除限售数量 | 单位：股 |
| expected_unlimited_ratio | decimal(10,4) | 预计解除限售比例 | 单位：％；预计解除限售数量占总股本比例 |
| limited_reason | varchar(60) | 限售原因 | 用户选择：股改限售；发行限售 |
| limited_reason_id | int | 限售原因编码 | 如下 限售原因编码 |
| pub_date | date | 公告日期 | 上市流通方案公布日期 |
| shareholder_name | varchar(100) | 股东名称 |  |
| trade_condition | varchar(500) | 上市交易条件 | 股份上市交易的条件限制 |

## STK_LIMITED_SHARES_UNLIMIT

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| actual_trade_number | int | 实际可流通数量 |  |
| actual_unlimited_date | date | 实际解除限售日期 |  |
| actual_unlimited_number | int | 实际解除限售数量 | 股 |
| actual_unlimited_ratio | decimal(10,4) | 实际解除限售比例 | 实际解除限售数量占总股本比例，单位% |
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| limited_reason | varchar(60) | 限售原因 |  |
| limited_reason_id | int | 限售原因编码 |  |
| pub_date | date | 公告日期 |  |
| shareholder_name | varchar(100) | 股东名称 |  |

## STK_LIST

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| book_price | decimal(20,4) | 发行价格 | 元 |
| category | varchar(4) | 证券类别 | A/B |
| code | varchar(12) | 证券代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| end_date | date | 终止上市日期 |  |
| exchange | varchar(12) | 交易所 | XSHG/XSHE |
| ipo_shares | decimal(20,2) | 初始上市数量 | 股 |
| name | varchar(40) | 证券简称 |  |
| par_value | decimal(20,4) | 面值 | 元 |
| short_name | varchar(20) | 拼音简称 |  |
| start_date | date | 上市日期 |  |
| state | varchar(32) | 上市状态 |  |
| state_id | int | 上市状态编码 |  |

## STK_MANAGEMENT_INFO

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| birth_year | varchar(8) | 出生年份 |  |
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| gender | char(1) | 性别 | F-女；M-男 |
| highest_degree | varchar(60) | 最高学历 |  |
| highest_degree_id | int | 最高学历编码 |  |
| leave_date | date | 离职日期 |  |
| leave_reason | varchar(255) | 离职原因 |  |
| name | varchar(40) | 姓名 |  |
| nationality | varchar(60) | 国籍 |  |
| on_job | char(1) | 是否在职 | 0-否，1-是 |
| person_id | int | 个人ID |  |
| profession_certificate | varchar(120) | 专业技术资格 |  |
| pub_date | date | 公告日期 |  |
| resume | varchar(3000) | 个人简历 |  |
| security_career_start_year | varchar(8) | 从事证券业开始年份 |  |
| start_date | date | 任职日期 |  |
| titile_level | varchar(120) | 职级 | 职级代表工作的难易程度、责任轻重以及所需的资格条件相同或充分相似的职系的集合。如初级、中级、高级。 |
| title | varchar(60) | 职务名称 |  |
| title_class | varchar(60) | 职务类别 |  |
| title_class_id | int | 职务类别编码 |  |
| title_level_id | int | 职级编码 |  |

## STK_ML_QUOTA

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| buy_amount | decimal(20,4) | 买入成交额 | 亿 |
| buy_volume | decimal(20,4) | 买入成交数 | 笔 |
| currency | varchar(16) | 货币名称 |  |
| currency_id | int | 货币编码 |  |
| day | date | 交易日期 |  |
| link_id | int | 市场通编码 |  |
| link_name | varchar(32) | 市场通名称 | 包括以下四个名称： 沪股通，深股通，港股通(沪）,港股通(深）；其中沪股通和深股通属于北向资金，港股通（沪）和港股通（深）属于南向资金。 |
| quota | decimal(20, 4) | 总额度 | 亿（2016-08-16号起，沪港通和深港通不再设总额度限制） |
| quota_balance | decimal(20, 4) | 总额度余额 | 亿 |
| quota_daily | decimal(20, 4) | 每日额度 | 亿 |
| quota_daily_balance | decimal(20, 4) | 每日额度余额 | 亿 |
| sell_amount | decimal(20,4) | 卖出成交额 | 亿 |
| sell_volume | decimal(20,4) | 卖出成交数 | 笔 |
| sum_amount | decimal(20,4) | 累计成交额 | 买入成交额+卖出成交额 |
| sum_volume | decimal(20,4) | 累计成交数目 | 买入成交量+卖出成交量 |
| 字段 | 类型 | 名称 | 备注/示例 |

## STK_MT_TOTAL

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| change_pct |  | 涨跌幅(%) |  |
| date |  | 日期 |  |
| net_amount_l | 大单：大于等于10万股或者20万元且小于50万股或者100万元的成交单 | 大单净额(万) |  |
| net_amount_m | 中单：大于等于2万股或者4万元且小于10万股或者20万元的成交单 | 中单净额(万) |  |
| net_amount_main | 主力净额 = 超大单净额 + 大单净额 | 主力净额(万) |  |
| net_amount_s | 小单：小于2万股或者4万元的成交单 | 小单净额(万) |  |
| net_amount_xl | 超大单：大于等于50万股或者100万元的成交单 | 超大单净额(万) |  |
| net_pct_l | 大单净占比 = 大单净额 / 成交额 | 大单净占比(%) |  |
| net_pct_m | 中单净占比 = 中单净额 / 成交额 | 中单净占比(%) |  |
| net_pct_main | 主力净占比 = 主力净额 / 成交额 | 主力净占比(%) |  |
| net_pct_s | 小单净占比 = 小单净额 / 成交额 | 小单净占比(%) |  |
| net_pct_xl | 超大单净占比 = 超大单净额 / 成交额 | 超大单净占比(%) |  |
| sec_code |  | 股票代码 |  |

## STK_NAME_HISTORY

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| new_name | varchar(40) | 新股票简称 |  |
| new_spelling | varchar(40) | 新英文简称 |  |
| org_name | varchar(40) | 原证券简称 |  |
| org_spelling | varchar(40) | 原证券英文简称 |  |
| pub_date | date | 公告日期 |  |
| reason | varchar(255) | 变更原因 |  |
| start_date | date | 开始日期 |  |

## STK_PERFORMANCE_LETTERS

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| basic_eps | DECIMAL(20, 4) | 基本每股收益 |  |
| code | VARCHAR(12) | 股票代码 |  |
| company_id | INTEGER(11) | 机构ID |  |
| company_name | VARCHAR(100) | 公司名称 |  |
| end_date | DATE | 截至日期 |  |
| equities_parent_company_owners | DECIMAL(20, 4) | 归属于上市公司股东的所有者权益 |  |
| name | VARCHAR(12) | 股票简称 |  |
| np_parent_company_owners | DECIMAL(20, 4) | 归属于母公司所有者的净利润 |  |
| operating_profit | DECIMAL(20, 4) | 营业利润 |  |
| operating_revenue | DECIMAL(20, 4) | 营业收入 |  |
| pub_date | DATE | 公布日期 |  |
| report_date | DATE | 报告期 |  |
| report_type | int | 报告期类型 | 0：本期，1：上期 |
| start_date | DATE | 开始日期 |  |
| total_assets | DECIMAL(20, 4) | 总资产 |  |
| total_operating_revenue | DECIMAL(20, 4) | 营业总收入 |  |
| total_profit | DECIMAL(20, 4) | 利润总额 |  |
| weight_roe | DECIMAL(20, 4) | 净资产收益(加权) | 披露值 |

## STK_REPORT_DISCLOSURE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| appoint_date | DATE | 预约披露日 |  |
| code | VARCHAR(12) | 公司代码 |  |
| end_date | DATE | 截止日期 |  |
| first_date | DATE | 首次变更日 |  |
| pub_date | DATE | 实际披露日 |  |
| second_date | DATE | 二次变更日 |  |
| third_date | DATE | 三次变更日 |  |

## STK_SHAREHOLDERS_SHARE_CHANGE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| after_change_ratio | decimal(10,4) | 变动后占比 | %，变动后持股数量占总股本比例 |
| change_number | int | 变动数量 | 股 |
| change_ratio | decimal(10,4) | 变动数量占总股本比例 | 录入变动数量后，系统自动计算变动比例，持股比例可以用持股数量除以股本情况表中的总股本 |
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| end_date | date | 增（减）持截止日 | 变动截止日期 |
| price_ceiling | varchar(100) | 增（减）持价格上限 | 公告里面一般会给一个增持或者减持的价格区间，上限就是增持价格或减持价格的最高价。如果公告中只披露了平均价，那price_ceiling即为成交均价 |
| pub_date | date | 公告日期 |  |
| shareholder_id | int | 股东ID |  |
| shareholder_name | varchar(100) | 股东名称 |  |
| type | int | 增（减）持类型 | 0--增持;1--减持 |

## STK_SHAREHOLDER_FLOATING_TOP10

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| change_reason | varchar(120) | 变动原因 |  |
| change_reason_id | int | 变动原因编码 |  |
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| end_date | date | 截止日期 |  |
| pub_date | date | 公告日期 |  |
| share_number | int | 持股数量 | 股 |
| share_ratio | decimal(10,4) | 持股比例 | % |
| shareholder_class | varchar(150) | 股东类别 |  |
| shareholder_class_id | int | 股东类别编码 |  |
| shareholder_id | int | 股东ID |  |
| shareholder_name | varchar(200) | 股东名称 |  |
| shareholder_name_en | varchar(150) | 股东名称（英文） |  |
| shareholder_rank | int | 股东名次 |  |
| sharesnature | varchar(120) | 股份性质 |  |
| sharesnature_id | int | 股份性质编码 |  |

## STK_SHAREHOLDER_TOP10

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| change_reason | varchar(120) | 变动原因 |  |
| change_reason_id | int | 变动原因编码 |  |
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 | 在此是指上市公司的名称 |
| end_date | date | 截止日期 | 公告中统计的十大股东截止到某一日期的更新情况。 |
| pub_date | date | 公告日期 | 公告中会提到十大股东的更新情况。 |
| share_freeze | decimal(10,4) | 股份冻结数量 |  |
| share_number | decimal(10,4) | 持股数量 | 股 |
| share_pledge | decimal(10,4) | 股份质押数量 |  |
| share_pledge_freeze | decimal(10,4) | 股份质押冻结数量 | 如果股份质押数量和股份冻结数量任意一个字段有值，则等于后两者之和 |
| share_ratio | decimal(10,4) | 持股比例 | % |
| shareholder_class | varchar(150) | 股东类别 | 包括:券商、社保基金、证券投资基金、保险公司、QFII、其它机构、个人等 |
| shareholder_class_id | int | 股东类别编码 |  |
| shareholder_id | int | 股东ID |  |
| shareholder_name | varchar(200) | 股东名称 |  |
| shareholder_name_en | varchar(200) | 股东名称（英文） |  |
| shareholder_rank | int | 股东名次 |  |
| sharesnature | varchar(120) | 股份性质 | 包括:国家股、法人股、个人股外资股、流通A股、流通B股、职工股、发起人股、转配股等 |
| sharesnature_id | int | 股份性质编码 |  |

## STK_SHARES_FROZEN

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| end_date | date | 冻结终止日 |  |
| freeze_applicant | varchar(100) | 冻结申请人 |  |
| freeze_executor | varchar(100) | 冻结执行人 |  |
| frozen_number | int | 冻结数量 | 股 |
| frozen_person | varchar(100) | 被冻结当事人 |  |
| frozen_person_id | int | 被冻结当事人ID |  |
| frozen_reason | varchar(600) | 冻结事项 |  |
| frozen_share_nature | varchar(120) | 被冻结股份性质 | 包括:国家股、法人股、个人股、外资股、流通A股、流通B股、职工股、发起人股、转配股 |
| frozen_share_nature_id | int | 被冻结股份性质编码 |  |
| frozen_total_ratio | decimal(10,4) | 占总股份比例 | % |
| pub_date | date | 公告日期 |  |
| start_date | date | 冻结起始日 |  |
| unfrozen_date | date | 解冻日期 | 分批解冻的为最近一次解冻日期 |
| unfrozen_detail | varchar(1000) | 解冻处理说明 | 冻结过程及结束后的处理结果 |
| unfrozen_number | int | 累计解冻数量 | 原解冻数量 |

## STK_SHARES_PLEDGE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| code | varchar(12) | 股票代码 |  |
| company_id | int | 公司ID |  |
| company_name | varchar(100) | 公司名称 |  |
| end_date | date | 质押终止日 |  |
| is_buy_back | char(1) | 是否质押式回购交易 |  |
| pledge_item | varchar(500) | 质押事项 | 质押原因，记录借款人、借款金额、币种等内容 |
| pledge_nature | varchar(120) | 质押股份性质 |  |
| pledge_nature_id | int | 质押股份性质编码 |  |
| pledge_number | int | 质押数量 | 股 |
| pledge_total_ratio | decimal(10,4) | 占总股本比例 | % |
| pledgee | varchar(100) | 质权人 |  |
| pledgor | varchar(100) | 出质人 | 将资产质押出去的人成为出质人 |
| pledgor_id | int | 出质人ID |  |
| pub_date | date | 公告日期 |  |
| start_date | date | 质押起始日 |  |
| unpledged _detail | varchar(1000) | 解除质押说明 |  |
| unpledged_date | date | 质押解除日 |  |
| unpledged_number | int | 质押解除数量 |  |

## STK_STATUS_CHANGE

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| change_date | date | 变更日期(实际变动日期) |  |
| change_reason | varchar(500) | 变更原因 |  |
| change_type | varchar(60) | 变更类型 |  |
| change_type_id | int | 变更类型编码 | 如下变更类型编码 |
| code | varchar(12) | 股票代码 |  |
| comments | varchar(255) | 备注 |  |
| company_id | int | 机构ID |  |
| name | varchar(40) | 股票名称 |  |
| pub_date | date | 公告日期 |  |
| public_status | varchar(32) | 上市状态 |  |
| public_status_id | int | 上市状态编码 | 如下上市状态编码 |

## STK_XR_XD

| 字段名 | 类型 | 含义 | 说明 |
|--------|------|------|------|
| a_bonus_date | date | 派息日(A) |  |
| a_increment_listing_date | date | A股新增股份上市日 |  |
| a_registration_date | date | A股股权登记日 |  |
| a_transfer_arrival_date | date | A股转增股份到帐日 |  |
| a_xr_date | date | A股除权日 |  |
| at_bonus_ratio_rmb | decimal(20,4) | 税后派息比例（人民币） |  |
| b_bonus_date | date | 派息日(B) |  |
| b_dividend_arrival_date | date | B股送红股到帐日 | 20080801新增 |
| b_final_trade_date | date | B股最后交易日 |  |
| b_increment_listing_date | date | B股新增股份上市日 |  |
| b_registration_date | date | B股股权登记日 | B股股权登记存在最后交易日，除权基准日以及股权登记日三个日期，由于B股实行T+3制度，最后交易日持有的股份需要在3个交易日之后确定股东身份，然后在除权基准日进行除权。 |
| b_transfer_arrival_date | date | B股转增股份到帐日 |  |
| b_xr_baseday | date | B股除权基准日 | 根据B股实行T＋3交收制度,则B股的“股权登记日”是“最后交易日”后的第 三个交易日,直至“股权登记日”这一日为止,B股投资者的股权登记才告完成,也 就意味着B股股份至股权登记日为止,才真正划入B股投资者的名下。 |
| board_plan_bonusnote | varchar(500) | 董事会预案分红说明 | 每10股送XX转增XX派XX元 |
| board_plan_pub_date | date | 董事会预案公告日期 |  |
| bonus_amount_rmb | decimal(20,4) | 派息金额(人民币) | 单位：万元 |
| bonus_cancel_pub_date | date | 取消分红公告日期 |  |
| bonus_ratio_hkd | decimal(20,4) | 派息比例（港币） | 每10股派 XX。说明：这里的比例为最新的分配比例，预案公布的时候，预案的分配基数在此维护，如果股东大会或实施方案发生变化，再次进行修改，保证此处为最新的分配基数 如果这里只告诉了汇率，没有公布具体的外币派息，则要计算出； |
| bonus_ratio_rmb | decimal(20,4) | 派息比例(人民币) | 每10股派 XX。说明：这里的比例为最新的分配比例，预案公布的时候，预案的分配基数在此维护，如果股东大会或实施方案发生变化，再次进行修改，保证此处为最新的分配基数 |
| bonus_ratio_usd | decimal(20,4) | 派息比例（美元） | 每10股派 XX。说明：这里的比例为最新的分配比例，预案公布的时候，预案的分配基数在此维护，如果股东大会或实施方案发生变化，再次进行修改，保证此处为最新的分配基数 如果这里只告诉了汇率，没有公布具体的外币派息，则要计算出； |
| bonus_type | varchar(60) | 分红类型 | 201102新增,类型如下：年度分红 中期分红 季度分红 特别分红 向公众股东赠送 股改分红 |
| code | varchar(12) | 股票代码 | 加后缀 |
| company_id | int | 机构ID |  |
| company_name | varchar(100) | 机构名称 |  |
| distributed_share_base_board | decimal(20,4) | 分配股本基数（董事会） | 单位:万股 |
| distributed_share_base_implement |  | 分配股本基数（实施） | 单位:万股 |
| distributed_share_base_shareholders | decimal(20,4) | 分配股本基数（股东大会） | 单位:万股 |
| dividend_arrival_date | date | 红股到帐日 |  |
| dividend_number | decimal(20,4) | 送股数量 | 单位：万股 |
| dividend_ratio | decimal(20,4) | 送股比例 | 每10股送XX股 |
| exchange_rate | decimal(20,4) | 汇率 | 当日以外币（美元或港币）计价的B股价格兑换成人民币的汇率 |
| float_capital_after_transfer | decimal(20,4) | 送转后流通股本 | 单位：万股 |
| float_capital_before_transfer | decimal(20,4) | 送转前流通股本 | 单位：万股 |
| implementation_bonusnote | varchar(200) | 实施方案分红说明 | 维护规则: 每10股送XX转增XX派XX元 或:不分配不转赠 |
| implementation_pub_date | date | 实施方案公告日期 |  |
| note | varchar(500) | 备注 |  |
| note_of_no_dividend | varchar(1000) | 有关不分配的说明 |  |
| plan_progress | varchar(60) | 方案进度 | 董事会预案 实施方案 股东大会预案 取消分红 公司预案 |
| plan_progress_code | int | 方案进度编码 |  |
| report_date | date | 分红报告期 | 一般为：一季报:YYYY-03-31;中报:YYYY-06-30;三季报:YYYY-09-30;年报:YYYY-12-31同时也可能存在其他日期 |
| shareholders_plan_bonusnote | varchar(200) | 股东大会预案分红说明 |  |
| shareholders_plan_pub_date | date | 股东大会预案公告日期 |  |
| total_capital_after_transfer | decimal(20,4) | 送转后总股本 | 单位：万股 |
| total_capital_before_transfer | decimal(20,4) | 送转前总股本 | 单位：万股 |
| transfer_number | decimal(20,4) | 转增数量 | 单位：万股 |
| transfer_ratio | decimal(20,4) | 转增比例 | 每10股转增 XX股 ； |
