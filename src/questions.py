#!/usr/bin/env python3
"""BankRegBench-v2 question set (chunk 1: single-table and two-table retrieval).

Every item is authored by hand: no template expansion, no generator.  Each entry
carries the natural-language question, the gold SQL, a difficulty tier and the
SQL features it exercises.  `src/build_dataset.py` executes every gold query and
refuses to ship an item that errors, returns no row where a row is required, or
is non-deterministic.

Schema notes the questions rely on (BankRegSQL v4):
  * 五级分类 codes live in classification_grade (grade_code / grade_name_zh).
  * 行业中文名在 industry_sector.sector_name_zh。
  * 贷款品种中文名在 loan_product_catalog.product_name_zh。
  * 业务状态中文名在 status_catalog。
"""

ITEMS = [
    dict(
        id="BRB2-0001", difficulty="easy", features=[],
        question="列出所有风险分类等级为“次级”的借据编号及其分类日期，按借据编号升序排列。",
        sql="""SELECT rc.loan_id, rc.as_of_date
FROM risk_classification rc
JOIN classification_grade g ON g.grade_code = rc.grade_code
WHERE g.grade_name_zh = '次级'
ORDER BY rc.loan_id;"""),
    dict(
        id="BRB2-0002", difficulty="easy", features=[],
        question="列出本金逾期天数超过 360 天的借据编号、逾期天数与逾期本金金额，按逾期天数从大到小排列。",
        sql="""SELECT loan_id, principal_overdue_days, overdue_principal
FROM delinquency_snapshot
WHERE principal_overdue_days > 360
ORDER BY principal_overdue_days DESC, loan_id;"""),
    dict(
        id="BRB2-0003", difficulty="easy", features=[],
        question="列出所有余额（账面余额）超过 500 万元的存款账户编号与账面余额，按余额从高到低排列。",
        sql="""SELECT account_id, ledger_balance
FROM account_balance_snapshot
WHERE ledger_balance > 5000000
ORDER BY ledger_balance DESC, account_id;"""),
    dict(
        id="BRB2-0004", difficulty="easy", features=[],
        question="列出所有处于“久悬”状态的账户编号及其开户机构名称。",
        sql="""SELECT a.account_id, i.institution_name
FROM account a
JOIN institution i ON i.institution_id = a.institution_id
JOIN status_catalog s ON s.entity = 'account' AND s.status_code = a.status
WHERE s.name_zh = '久悬'
ORDER BY a.account_id;"""),
    dict(
        id="BRB2-0005", difficulty="easy", features=[],
        question="列出注册行业为“房地产业”的对公客户编号与客户名称，按客户编号升序排列。",
        sql="""SELECT p.party_id, p.display_name
FROM party p
JOIN organization_profile op ON op.party_id = p.party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
WHERE s.sector_name_zh = '房地产业'
ORDER BY p.party_id;"""),
    dict(
        id="BRB2-0006", difficulty="easy", features=[],
        question="列出风险等级为 R5 且当前仍处于在售状态的理财产品编号、产品名称与计划募集金额。",
        sql="""SELECT product_id, product_name, planned_raise_amount
FROM wealth_product
WHERE risk_level = 'R5' AND status = 'ON_SALE'
ORDER BY product_id;"""),
    dict(
        id="BRB2-0007", difficulty="easy", features=[],
        question="列出所有已核销的借据编号及其放款金额。",
        sql="""SELECT ld.loan_id, ld.disbursed_amount
FROM loan_drawdown ld
JOIN status_catalog s ON s.entity = 'loan_drawdown' AND s.status_code = ld.status
WHERE s.name_zh = '已核销'
ORDER BY ld.loan_id;"""),
    dict(
        id="BRB2-0008", difficulty="easy", features=[],
        question="列出现金支取类交易中金额超过 500 万元的交易编号、业务日期与金额，按金额降序排列。",
        sql="""SELECT pe.payment_id, pe.business_date, pe.amount
FROM payment_event pe
JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
WHERE t.name_zh = '现金支取' AND pe.amount > 5000000
ORDER BY pe.amount DESC, pe.payment_id;"""),
    dict(
        id="BRB2-0009", difficulty="easy", features=[],
        question="列出所有已终止的理财产品编号、成立日期与实际终止日期。",
        sql="""SELECT product_id, inception_on, actual_termination_on
FROM wealth_product
WHERE actual_termination_on IS NOT NULL
ORDER BY product_id;"""),
    dict(
        id="BRB2-0010", difficulty="easy", features=[],
        question="列出所有担保方式为“信用”的授信协议编号及其合同金额。",
        sql="""SELECT agreement_id, contract_amount
FROM credit_agreement
WHERE security_type = 'CREDIT'
ORDER BY agreement_id;"""),
    dict(
        id="BRB2-0011", difficulty="easy", features=[],
        question="列出抵押物编号、抵押物名称及其最近一次评估价值，按评估价值从高到低排列。",
        sql="""SELECT ca.collateral_id, ca.asset_label, cv.valuation_amount
FROM collateral_asset ca
JOIN collateral_valuation cv ON cv.collateral_id = ca.collateral_id
WHERE cv.valued_on = (SELECT MAX(cv2.valued_on) FROM collateral_valuation cv2
                      WHERE cv2.collateral_id = ca.collateral_id)
ORDER BY cv.valuation_amount DESC, ca.collateral_id;"""),
    dict(
        id="BRB2-0012", difficulty="easy", features=[],
        question="列出年收入超过 100 万元的个人客户编号及其年收入，按年收入降序排列。",
        sql="""SELECT party_id, annual_income
FROM person_profile
WHERE annual_income > 1000000
ORDER BY annual_income DESC, party_id;"""),
    dict(
        id="BRB2-0013", difficulty="easy", features=[],
        question="列出所有贷记卡的卡号、发卡日期与到期日期，按发卡日期升序排列。",
        sql="""SELECT card_id, issued_on, expires_on
FROM payment_card
WHERE card_type = 'CREDIT'
ORDER BY issued_on, card_id;"""),
    dict(
        id="BRB2-0014", difficulty="easy", features=[],
        question="列出注册地区与“上海分行”所在地区相同的对公客户编号、名称与其经营状态，按客户编号升序排列。",
        sql="""SELECT p.party_id, p.display_name, op.operating_status
FROM party p
JOIN organization_profile op ON op.party_id = p.party_id
WHERE op.registered_region IN (SELECT region_code FROM organization_unit WHERE unit_name = '上海分行')
ORDER BY p.party_id;"""),
    dict(
        id="BRB2-0015", difficulty="easy", features=[],
        question="列出所有已到期的授信协议编号、到期日与合同金额，按到期日升序排列。",
        sql="""SELECT agreement_id, maturity_on, contract_amount
FROM credit_agreement
WHERE status = 'MATURED'
ORDER BY maturity_on, agreement_id;"""),
    dict(
        id="BRB2-0016", difficulty="medium", features=[],
        question="统计每家机构名下的贷款借据笔数，输出机构名称与借据笔数，按笔数从多到少排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS loan_count
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY loan_count DESC, i.institution_name;"""),
    dict(
        id="BRB2-0017", difficulty="medium", features=[],
        question="统计每个营业机构单元开立的账户数量，输出机构单元编号、机构单元名称与账户数，按账户数降序排列。",
        sql="""SELECT ou.org_unit_id, ou.unit_name, COUNT(*) AS account_count
FROM account a
JOIN organization_unit ou ON ou.org_unit_id = a.org_unit_id
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY account_count DESC, ou.org_unit_id;"""),
    dict(
        id="BRB2-0018", difficulty="medium", features=[],
        question="统计各行业的对公客户数量，输出行业中文名称与客户数，按客户数从多到少排列。",
        sql="""SELECT s.sector_name_zh, COUNT(*) AS customer_count
FROM organization_profile op
JOIN industry_sector s ON s.sector_code = op.industry_code
GROUP BY s.sector_code, s.sector_name_zh
ORDER BY customer_count DESC, s.sector_name_zh;"""),
    dict(
        id="BRB2-0019", difficulty="medium", features=[],
        question="按员工岗位分配表关联员工所在的营业机构单元，统计每个员工所在机构单元作为经办管理机构单元的授信协议数量，输出员工工号与协议数，取前 10 名，按协议数降序排列。",
        sql="""SELECT sm.staff_id, COUNT(*) AS agreement_count
FROM credit_agreement a
JOIN organization_unit ou ON ou.org_unit_id = a.managing_org_unit_id
JOIN staff_assignment sa ON sa.org_unit_id = ou.org_unit_id
JOIN staff_member sm ON sm.staff_id = sa.staff_id
GROUP BY sm.staff_id
ORDER BY agreement_count DESC, sm.staff_id
LIMIT 10;"""),
    dict(
        id="BRB2-0020", difficulty="medium", features=[],
        question="统计每家机构的贷款发放金额合计，输出机构名称与发放金额合计，按合计金额降序排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(ld.disbursed_amount), 2) AS total_disbursed
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY total_disbursed DESC, i.institution_name;"""),
    dict(
        id="BRB2-0021", difficulty="medium", features=[],
        question="统计各贷款品种的借据笔数与平均放款金额，输出品种中文名称、笔数、平均放款金额，按笔数降序排列。",
        sql="""SELECT lp.product_name_zh, COUNT(*) AS loan_count,
       ROUND(AVG(ld.disbursed_amount), 2) AS avg_amount
FROM loan_drawdown ld
JOIN loan_product_catalog lp ON lp.product_code = ld.drawdown_type
GROUP BY lp.product_code, lp.product_name_zh
ORDER BY loan_count DESC, lp.product_name_zh;"""),
    dict(
        id="BRB2-0022", difficulty="medium", features=[],
        question="统计各行业对公客户的授信合同金额合计，输出行业中文名称与合同金额合计，按合计金额降序排列。",
        sql="""SELECT s.sector_name_zh, ROUND(SUM(a.contract_amount), 2) AS total_contract
FROM credit_agreement a
JOIN organization_profile op ON op.party_id = a.borrower_party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
GROUP BY s.sector_code, s.sector_name_zh
ORDER BY total_contract DESC, s.sector_name_zh;"""),
    dict(
        id="BRB2-0023", difficulty="medium", features=[],
        question="统计每个客户持有的账户数量，输出客户编号、客户名称与账户数，只保留持有 3 个及以上账户的客户，按账户数降序排列。",
        sql="""SELECT p.party_id, p.display_name, COUNT(*) AS account_count
FROM account_holder ah
JOIN party p ON p.party_id = ah.party_id
GROUP BY p.party_id, p.display_name
HAVING COUNT(*) >= 3
ORDER BY account_count DESC, p.party_id;"""),
    dict(
        id="BRB2-0024", difficulty="medium", features=[],
        question="统计各担保方式下的授信协议数量，输出担保方式代码与协议数，按协议数降序排列。",
        sql="""SELECT security_type, COUNT(*) AS agreement_count
FROM credit_agreement
GROUP BY security_type
ORDER BY agreement_count DESC, security_type;"""),
    dict(
        id="BRB2-0025", difficulty="medium", features=[],
        question="统计各理财产品底层资产的持仓市值合计，输出产品名称与持仓市值合计，取前 10 名，按合计金额降序排列。",
        sql="""SELECT wp.product_name, ROUND(SUM(phs.fair_value), 2) AS total_fair_value
FROM product_holding_snapshot phs
JOIN wealth_product wp ON wp.product_id = phs.product_id
GROUP BY wp.product_id, wp.product_name
ORDER BY total_fair_value DESC, wp.product_name
LIMIT 10;"""),
    dict(
        id="BRB2-0026", difficulty="medium", features=[],
        question="按关联方关系中源主体客户的归属营业机构单元，统计各机构单元名下的关联方关系记录数量，输出机构单元编号、机构单元名称与关联方关系数量，按数量降序排列。",
        sql="""SELECT ou.org_unit_id, ou.unit_name, COUNT(*) AS relation_count
FROM party_relation pr
JOIN party p ON p.party_id = pr.source_party_id
JOIN organization_unit ou ON ou.org_unit_id = p.home_org_unit_id
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY relation_count DESC, ou.org_unit_id;"""),
    dict(
        id="BRB2-0027", difficulty="medium", features=[],
        question="统计各机构的资本净额与风险加权资产，输出机构名称、资本净额、风险加权资产，按资本净额降序排列。",
        sql="""SELECT i.institution_name, cs.net_capital, cs.risk_weighted_assets
FROM capital_snapshot cs
JOIN institution i ON i.institution_id = cs.institution_id
ORDER BY cs.net_capital DESC, i.institution_name;"""),
    dict(
        id="BRB2-0028", difficulty="medium", features=[],
        question="按借款人注册行业统计各行业的贷款余额合计，输出行业中文名称与贷款本金余额合计，按余额合计降序排列。",
        sql="""SELECT s.sector_name_zh, ROUND(SUM(lbs.principal_balance), 2) AS total_balance
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN organization_profile op ON op.party_id = a.borrower_party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
GROUP BY s.sector_code, s.sector_name_zh
ORDER BY total_balance DESC, s.sector_name_zh;"""),
    dict(
        id="BRB2-0029", difficulty="medium", features=[],
        question="统计每张贷记卡（信用卡）的交易笔数（以卡对应的结算账户上的卡消费交易计），输出卡号与交易笔数，按笔数降序排列。",
        sql="""SELECT pc.card_id, COUNT(*) AS txn_count
FROM payment_card pc
JOIN payment_event pe ON pe.from_account_id = pc.settlement_account_id
JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
WHERE pc.card_type = 'CREDIT' AND t.name_zh = '卡消费'
GROUP BY pc.card_id
ORDER BY txn_count DESC, pc.card_id;"""),
    dict(
        id="BRB2-0030", difficulty="medium", features=[],
        question="统计各机构的存款余额合计（以储蓄类账户的账面余额计），输出机构名称与存款余额合计，按合计金额降序排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(abs.ledger_balance), 2) AS total_deposit
FROM account_balance_snapshot abs
JOIN account a ON a.account_id = abs.account_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE a.account_kind = 'SAVINGS'
GROUP BY i.institution_id, i.institution_name
ORDER BY total_deposit DESC, i.institution_name;"""),
    dict(
        id="BRB2-0031", difficulty="medium", features=[],
        question="统计各机构的贷款本金余额合计，输出机构名称与余额合计，只保留余额合计超过 10 亿元的机构，按余额合计降序排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(lbs.principal_balance), 2) AS total_balance
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
HAVING SUM(lbs.principal_balance) > 1000000000
ORDER BY total_balance DESC, i.institution_name;"""),
    dict(
        id="BRB2-0032", difficulty="hard", features=[],
        question="统计各机构的平均本金逾期天数（仅统计存在逾期台账的借据），输出机构名称与平均逾期天数，只保留平均逾期天数超过 90 天的机构，按平均逾期天数降序排列。",
        sql="""SELECT i.institution_name, ROUND(AVG(d.principal_overdue_days), 2) AS avg_overdue_days
FROM delinquency_snapshot d
JOIN loan_drawdown ld ON ld.loan_id = d.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
HAVING AVG(d.principal_overdue_days) > 90
ORDER BY avg_overdue_days DESC, i.institution_name;"""),
    dict(
        id="BRB2-0033", difficulty="hard", features=[],
        question="计算各机构的不良贷款率（不良贷款本金余额 ÷ 全部贷款本金余额，不良口径为五级分类中的次级、可疑、损失），输出机构名称与不良贷款率，按不良率降序排列。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(CASE WHEN g.is_nonperforming = 1 THEN lbs.principal_balance ELSE 0 END)
             * 1.0 / SUM(lbs.principal_balance), 6) AS npl_ratio
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
JOIN risk_classification rc ON rc.loan_id = ld.loan_id
JOIN classification_grade g ON g.grade_code = rc.grade_code
GROUP BY i.institution_id, i.institution_name
ORDER BY npl_ratio DESC, i.institution_name;"""),
    dict(
        id="BRB2-0034", difficulty="hard", features=[],
        question="计算各机构的拨备覆盖率（已计提拨备金额合计 ÷ 计提要求金额合计），输出机构名称与拨备覆盖率，只保留拨备覆盖率低于 1.5 的机构，按拨备覆盖率升序排列。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(ps.recognized_amount) * 1.0 / SUM(ps.required_amount), 6) AS coverage
FROM provision_snapshot ps
JOIN loan_drawdown ld ON ld.loan_id = ps.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
HAVING SUM(ps.recognized_amount) * 1.0 / SUM(ps.required_amount) < 1.5
ORDER BY coverage, i.institution_name;"""),
    dict(
        id="BRB2-0035", difficulty="hard", features=[],
        question="计算各机构已计提拨备金额低于计提要求金额的借据笔数，输出机构名称与借据笔数，只保留笔数不少于 100 笔的机构，按笔数降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS under_provisioned
FROM provision_snapshot ps
JOIN loan_drawdown ld ON ld.loan_id = ps.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE ps.recognized_amount < ps.required_amount
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(*) >= 100
ORDER BY under_provisioned DESC, i.institution_name;"""),
    dict(
        id="BRB2-0036", difficulty="hard", features=[],
        question="计算各对公客户的贷款本金余额合计占其所属机构资本净额的比重，输出客户编号、客户名称、余额合计、机构名称与该比重，取比重最高的前 10 名，按比重降序排列。",
        sql="""SELECT p.party_id, p.display_name, ROUND(SUM(lbs.principal_balance), 2) AS total_balance,
       i.institution_name,
       ROUND(SUM(lbs.principal_balance) * 1.0 / cs.net_capital, 6) AS exposure_ratio
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
JOIN institution i ON i.institution_id = a.institution_id
JOIN capital_snapshot cs ON cs.institution_id = i.institution_id
WHERE p.party_type = 'CORPORATE'
GROUP BY p.party_id, p.display_name, i.institution_id, i.institution_name, cs.net_capital
ORDER BY exposure_ratio DESC, p.party_id
LIMIT 10;"""),
    dict(
        id="BRB2-0037", difficulty="hard", features=[],
        question="按敞口集团统计各集团的授信敞口金额（以集团成员在本行的贷款本金余额合计计）占该集团主办机构资本净额的比重，输出集团编号、集团名称、敞口金额与敞口占资本净额比重，按比重降序排列。",
        sql="""SELECT eg.exposure_group_id, eg.group_name,
       ROUND(SUM(lbs.principal_balance), 2) AS exposure_amount,
       ROUND(SUM(lbs.principal_balance) * 1.0 / cs.net_capital, 6) AS exposure_ratio
FROM exposure_group_member egm
JOIN exposure_group eg ON eg.exposure_group_id = egm.exposure_group_id
JOIN credit_agreement a ON a.borrower_party_id = egm.party_id
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
JOIN capital_snapshot cs ON cs.institution_id = eg.institution_id
GROUP BY eg.exposure_group_id, eg.group_name, cs.net_capital
ORDER BY exposure_ratio DESC, eg.exposure_group_id;"""),
    dict(
        id="BRB2-0038", difficulty="medium", features=[],
        question="计算各机构的存贷比（贷款本金余额合计 ÷ 储蓄账户账面余额合计），输出机构名称与存贷比，按存贷比降序排列。",
        sql="""SELECT i.institution_name,
       ROUND((SELECT SUM(lbs.principal_balance)
              FROM loan_balance_snapshot lbs
              JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
              JOIN credit_agreement a2 ON a2.agreement_id = ld.agreement_id
              WHERE a2.institution_id = i.institution_id) * 1.0
             / NULLIF((SELECT SUM(abs.ledger_balance)
                       FROM account_balance_snapshot abs
                       JOIN account ac ON ac.account_id = abs.account_id
                       WHERE ac.institution_id = i.institution_id
                         AND ac.account_kind = 'SAVINGS'), 0), 6) AS loan_to_deposit
FROM institution i
ORDER BY loan_to_deposit DESC, i.institution_name;"""),
    dict(
        id="BRB2-0039", difficulty="hard", features=[],
        question="计算各机构的逾期 90 天以上贷款本金余额与不良贷款本金余额的偏离度（逾期 90 天以上本金余额 ÷ 不良贷款本金余额），输出机构名称、逾期 90 天以上余额、不良余额与偏离度，按偏离度降序排列。",
        sql="""WITH loan_base AS (
    SELECT ld.loan_id, a.institution_id, lbs.principal_balance,
           COALESCE(d.principal_overdue_days, 0) AS overdue_days,
           g.is_nonperforming
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    LEFT JOIN delinquency_snapshot d ON d.loan_id = ld.loan_id
    JOIN risk_classification rc ON rc.loan_id = ld.loan_id
    JOIN classification_grade g ON g.grade_code = rc.grade_code
)
SELECT i.institution_name,
       ROUND(SUM(CASE WHEN overdue_days > 90 THEN principal_balance ELSE 0 END), 2) AS overdue90_balance,
       ROUND(SUM(CASE WHEN is_nonperforming = 1 THEN principal_balance ELSE 0 END), 2) AS npl_balance,
       ROUND(SUM(CASE WHEN overdue_days > 90 THEN principal_balance ELSE 0 END) * 1.0
             / NULLIF(SUM(CASE WHEN is_nonperforming = 1 THEN principal_balance ELSE 0 END), 0), 6) AS deviation
FROM loan_base lb
JOIN institution i ON i.institution_id = lb.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY deviation DESC, i.institution_name;"""),
    dict(
        id="BRB2-0040", difficulty="medium", features=[],
        question="统计各机构的现金交易笔数（现金存入与现金支取合计），输出机构名称与笔数，按笔数降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS cash_txn_count
FROM payment_event pe
JOIN account ac ON ac.account_id = COALESCE(pe.from_account_id, pe.to_account_id)
JOIN institution i ON i.institution_id = ac.institution_id
JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
WHERE pe.is_cash = 1
GROUP BY i.institution_id, i.institution_name
ORDER BY cash_txn_count DESC, i.institution_name;"""),
    dict(
        id="BRB2-0041", difficulty="medium", features=[],
        question="统计各账户的现金支取金额合计，输出账户编号与金额合计，只保留金额合计超过 1000 万元的账户，按金额合计降序排列并取前 20 名。",
        sql="""SELECT pe.from_account_id AS account_id, ROUND(SUM(pe.amount), 2) AS cash_out
FROM payment_event pe
JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
WHERE t.name_zh = '现金支取' AND pe.status = 'SETTLED'
GROUP BY pe.from_account_id
HAVING SUM(pe.amount) > 10000000
ORDER BY cash_out DESC, account_id
LIMIT 20;"""),
    dict(
        id="BRB2-0042", difficulty="hard", features=[],
        question="计算各机构的受托支付金额占比（受托支付方式下的支付指令金额合计 ÷ 全部支付指令金额合计），输出机构名称与占比，按占比升序排列。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(CASE WHEN pi.payment_mode = 'ENTRUSTED_PAYMENT' THEN pi.instruction_amount ELSE 0 END)
             * 1.0 / SUM(pi.instruction_amount), 6) AS entrusted_ratio
FROM payment_instruction pi
JOIN loan_drawdown ld ON ld.loan_id = pi.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY entrusted_ratio, i.institution_name;"""),
    dict(
        id="BRB2-0043", difficulty="medium", features=[],
        question="按借款人注册行业统计各行业的不良贷款（五级分类为次级、可疑、损失）笔数占该行业贷款笔数的比重，输出行业名称、贷款笔数、不良笔数与不良笔数占比，只保留贷款笔数不少于 20 笔的行业，按占比降序排列。",
        sql="""SELECT s.sector_name_zh, COUNT(*) AS loan_count,
       SUM(CASE WHEN g.is_nonperforming = 1 THEN 1 ELSE 0 END) AS npl_count,
       ROUND(SUM(CASE WHEN g.is_nonperforming = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 6) AS npl_ratio
FROM risk_classification rc
JOIN classification_grade g ON g.grade_code = rc.grade_code
JOIN loan_drawdown ld ON ld.loan_id = rc.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN organization_profile op ON op.party_id = a.borrower_party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
GROUP BY s.sector_code, s.sector_name_zh
HAVING COUNT(*) >= 20
ORDER BY npl_ratio DESC, s.sector_name_zh;"""),
    dict(
        id="BRB2-0044", difficulty="medium", features=[],
        question="统计各客户在全部机构的授信合同金额合计，输出客户编号、客户名称与合同金额合计，取前 15 名，按合计金额降序排列。",
        sql="""SELECT p.party_id, p.display_name, ROUND(SUM(a.contract_amount), 2) AS total_contract
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
GROUP BY p.party_id, p.display_name
ORDER BY total_contract DESC, p.party_id
LIMIT 15;"""),
    dict(
        id="BRB2-0045", difficulty="hard", features=[],
        question="找出在两家及以上机构获得授信的客户，输出客户编号、客户名称与授信机构家数，按机构家数降序排列。",
        sql="""SELECT p.party_id, p.display_name, COUNT(DISTINCT a.institution_id) AS inst_count
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
GROUP BY p.party_id, p.display_name
HAVING COUNT(DISTINCT a.institution_id) >= 2
ORDER BY inst_count DESC, p.party_id;"""),
    dict(
        id="BRB2-0046", difficulty="medium", features=[],
        question="统计各贷款品种的平均合同利率，输出品种中文名称、借据笔数与平均合同利率，只保留笔数不少于 50 笔的品种，按平均利率降序排列。",
        sql="""SELECT lp.product_name_zh, COUNT(*) AS loan_count,
       ROUND(AVG(a.annual_interest_rate), 4) AS avg_rate
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN loan_product_catalog lp ON lp.product_code = ld.drawdown_type
GROUP BY lp.product_code, lp.product_name_zh
HAVING COUNT(*) >= 50
ORDER BY avg_rate DESC, lp.product_name_zh;"""),
    dict(
        id="BRB2-0047", difficulty="hard", features=[],
        question="统计各机构理财产品的实际募集金额合计与计划募集金额合计，输出机构名称、实际募集合计、计划募集合计与募集完成率（实际 ÷ 计划），按募集完成率升序排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(wp.actual_raise_amount), 2) AS actual_total,
       ROUND(SUM(wp.planned_raise_amount), 2) AS planned_total,
       ROUND(SUM(wp.actual_raise_amount) * 1.0 / SUM(wp.planned_raise_amount), 6) AS completion_rate
FROM wealth_product wp
JOIN institution i ON i.institution_id = wp.issuer_institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY completion_rate, i.institution_name;"""),
    dict(
        id="BRB2-0048", difficulty="medium", features=[],
        question="统计各风险等级理财产品的产品数量与平均管理费率，输出风险等级、产品数量与平均管理费率，按风险等级升序排列。",
        sql="""SELECT risk_level, COUNT(*) AS product_count,
       ROUND(AVG(management_fee_rate), 6) AS avg_fee_rate
FROM wealth_product
GROUP BY risk_level
ORDER BY risk_level;"""),
    dict(
        id="BRB2-0049", difficulty="hard", features=[],
        question="统计各担保人当前有效担保承诺（状态为有效）的在保余额合计（担保承诺金额合计），输出担保人编号、担保人名称与在保余额合计，只保留在保余额合计超过 5 亿元的担保人，按合计金额降序排列。",
        sql="""SELECT gc.guarantor_party_id, p.display_name,
       ROUND(SUM(gc.guaranteed_amount), 2) AS total_guaranteed
FROM guarantor_commitment gc
JOIN party p ON p.party_id = gc.guarantor_party_id
WHERE gc.status = 'ACTIVE'
GROUP BY gc.guarantor_party_id, p.display_name
HAVING SUM(gc.guaranteed_amount) > 500000000
ORDER BY total_guaranteed DESC, gc.guarantor_party_id;"""),
    dict(
        id="BRB2-0050", difficulty="medium", features=[],
        question="统计各抵押物类型的评估价值合计（取每个抵押物最近一次评估值），输出抵押物类型、抵押物数量与评估价值合计，按评估价值合计降序排列。",
        sql="""SELECT ca.collateral_type, COUNT(DISTINCT ca.collateral_id) AS collateral_count,
       ROUND(SUM(cv.valuation_amount), 2) AS total_valuation
FROM collateral_asset ca
JOIN collateral_valuation cv ON cv.collateral_id = ca.collateral_id
WHERE cv.valued_on = (SELECT MAX(cv2.valued_on) FROM collateral_valuation cv2
                      WHERE cv2.collateral_id = ca.collateral_id)
GROUP BY ca.collateral_type
ORDER BY total_valuation DESC, ca.collateral_type;"""),
    dict(
        id="BRB2-0051", difficulty="hard", features=[],
        question="计算各机构的贷存比监管缺口：以贷款本金余额合计 ÷ 储蓄账面余额合计作为存贷比，输出机构名称、存贷比与监管上限 0.75 的差额，只保留存贷比超过 0.75 的机构，按存贷比降序排列。",
        sql="""WITH loan_side AS (
    SELECT a.institution_id, SUM(lbs.principal_balance) AS loan_balance
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    GROUP BY a.institution_id
), deposit_side AS (
    SELECT ac.institution_id, SUM(abs.ledger_balance) AS deposit_balance
    FROM account_balance_snapshot abs
    JOIN account ac ON ac.account_id = abs.account_id
    WHERE ac.account_kind = 'SAVINGS'
    GROUP BY ac.institution_id
)
SELECT i.institution_name,
       ROUND(l.loan_balance * 1.0 / d.deposit_balance, 6) AS loan_to_deposit,
       ROUND(l.loan_balance * 1.0 / d.deposit_balance - 0.75, 6) AS gap_over_limit
FROM loan_side l
JOIN deposit_side d ON d.institution_id = l.institution_id
JOIN institution i ON i.institution_id = l.institution_id
WHERE l.loan_balance * 1.0 / d.deposit_balance > 0.75
ORDER BY loan_to_deposit DESC, i.institution_name;"""),
    dict(
        id="BRB2-0052", difficulty="medium", features=[],
        question="统计各渠道的交易笔数与金额合计，输出渠道代码、交易笔数与金额合计，按金额合计降序排列。",
        sql="""SELECT channel, COUNT(*) AS txn_count, ROUND(SUM(amount), 2) AS total_amount
FROM payment_event
GROUP BY channel
ORDER BY total_amount DESC, channel;"""),
    dict(
        id="BRB2-0053", difficulty="hard", features=[],
        question="统计各机构的还款计划中已逾期未还的分期笔数与应还本金合计，输出机构名称、分期笔数与应还本金合计，只保留分期笔数不少于 150 笔的机构，按应还本金合计降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS overdue_installments,
       ROUND(SUM(rs.principal_due), 2) AS principal_due
FROM repayment_schedule rs
JOIN loan_drawdown ld ON ld.loan_id = rs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE rs.status = 'OVERDUE'
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(*) >= 150
ORDER BY principal_due DESC, i.institution_name;"""),
    dict(
        id="BRB2-0054", difficulty="medium", features=[],
        question="统计各行业对公客户中经营状态并非正常经营（如已吊销、经营异常）的客户数量，输出行业中文名称与被吊销或异常经营的客户数，按客户数降序排列。",
        sql="""SELECT s.sector_name_zh, COUNT(*) AS abnormal_count
FROM organization_profile op
JOIN industry_sector s ON s.sector_code = op.industry_code
WHERE op.operating_status <> 'OPERATING'
GROUP BY s.sector_code, s.sector_name_zh
ORDER BY abnormal_count DESC, s.sector_name_zh;"""),
    dict(
        id="BRB2-0055", difficulty="hard", features=[],
        question="计算各机构理财资金投向非标准化债权类资产的持仓市值占比，输出机构名称、非标持仓市值与总持仓市值、非标占比，按非标占比降序排列。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(CASE WHEN ma.asset_scope = 'NON_STANDARDIZED' THEN phs.fair_value ELSE 0 END), 2) AS nonstd_value,
       ROUND(SUM(phs.fair_value), 2) AS total_value,
       ROUND(SUM(CASE WHEN ma.asset_scope = 'NON_STANDARDIZED' THEN phs.fair_value ELSE 0 END)
             * 1.0 / SUM(phs.fair_value), 6) AS nonstd_ratio
FROM product_holding_snapshot phs
JOIN managed_asset ma ON ma.asset_id = phs.asset_id
JOIN wealth_product wp ON wp.product_id = phs.product_id
JOIN institution i ON i.institution_id = wp.issuer_institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY nonstd_ratio DESC, i.institution_name;"""),
    dict(
        id="BRB2-0056", difficulty="medium", features=[],
        question="统计各客户经理（员工）经办的现金交易笔数，输出员工工号与笔数，取前 10 名，按笔数降序排列。",
        sql="""SELECT so.staff_id, COUNT(*) AS cash_txn_count
FROM payment_event pe
JOIN service_operator so ON so.operator_id = pe.operator_id
WHERE pe.is_cash = 1
GROUP BY so.staff_id
ORDER BY cash_txn_count DESC, so.staff_id
LIMIT 10;"""),
    dict(
        id="BRB2-0057", difficulty="hard", features=[],
        question="统计各关联方（在关联方关系中作为源主体且关系类型不为“非关联方”）在本行获得的授信合同金额合计，输出客户编号、客户名称与合同金额合计，只保留合计超过 3 亿元的客户，按合计金额降序排列。",
        sql="""SELECT p.party_id, p.display_name, ROUND(SUM(a.contract_amount), 2) AS total_contract
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
WHERE EXISTS (
    SELECT 1 FROM party_relation pr
    JOIN relation_type_catalog rt ON rt.relation_type = pr.relation_type
    WHERE pr.source_party_id = p.party_id
      AND rt.relation_name_zh <> '非关联方'
)
GROUP BY p.party_id, p.display_name
HAVING SUM(a.contract_amount) > 300000000
ORDER BY total_contract DESC, p.party_id;"""),
    dict(
        id="BRB2-0058", difficulty="medium", features=[],
        question="统计各机构在数据安全事件台账中带有异常标记的记录数与行为观测值合计，输出机构名称、记录数与观测值合计，按观测值合计降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS record_count,
       ROUND(SUM(r.observed_value), 4) AS total_observed
FROM data_security_event_v3 r
JOIN institution i ON i.institution_id = r.institution_id
WHERE r.exception_flag = 1
GROUP BY i.institution_id, i.institution_name
ORDER BY total_observed DESC, i.institution_name;"""),
    dict(
        id="BRB2-0059", difficulty="hard", features=[],
        question="统计各机构监管报送事项中已逾期未完成（完成日期为空或晚于截止日期）的记录数，输出机构名称与逾期记录数，只保留逾期记录数不少于 20 条的机构，按逾期记录数降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS overdue_records
FROM regulatory_submission_event_v3 r
JOIN institution i ON i.institution_id = r.institution_id
WHERE r.completion_date IS NULL OR r.completion_date > r.deadline_date
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(*) >= 20
ORDER BY overdue_records DESC, i.institution_name;"""),
    dict(
        id="BRB2-0060", difficulty="medium", features=[],
        question="统计各机构的资本充足率（资本净额 ÷ 风险加权资产），输出机构名称与资本充足率，按资本充足率升序排列。",
        sql="""SELECT i.institution_name, ROUND(cs.net_capital * 1.0 / cs.risk_weighted_assets, 6) AS car
FROM capital_snapshot cs
JOIN institution i ON i.institution_id = cs.institution_id
ORDER BY car, i.institution_name;"""),
    dict(
        id="BRB2-0061", difficulty="hard", features=[],
        question="找出五级分类不实的借据：本金逾期天数已超过 90 天，但最近一次风险分类仍为“正常”或“关注”。输出借据编号、逾期天数、分类名称与分类日期，按逾期天数降序排列。",
        sql="""SELECT d.loan_id, d.principal_overdue_days, g.grade_name_zh, rc.as_of_date
FROM delinquency_snapshot d
JOIN risk_classification rc ON rc.loan_id = d.loan_id
JOIN classification_grade g ON g.grade_code = rc.grade_code
WHERE d.principal_overdue_days > 90
  AND g.is_nonperforming = 0
ORDER BY d.principal_overdue_days DESC, d.loan_id;"""),
    dict(
        id="BRB2-0062", difficulty="hard", features=[],
        question="找出拨备计提严重不足的借据：已计提拨备金额低于计提要求金额的 80%。输出借据编号、计提要求金额、已计提金额与缺口金额（要求金额 − 已计提金额），按缺口金额降序排列。",
        sql="""SELECT ps.loan_id, ps.required_amount, ps.recognized_amount,
       ROUND(ps.required_amount - ps.recognized_amount, 2) AS shortfall
FROM provision_snapshot ps
WHERE ps.recognized_amount < ps.required_amount * 0.8
ORDER BY shortfall DESC, ps.loan_id;"""),
    dict(
        id="BRB2-0063", difficulty="hard", features=[],
        question="统计各机构中拨备计提不足的借据所涉及的贷款本金余额合计，输出机构名称与不足拨备贷款余额，只保留不足拨备贷款余额超过 1 亿元的机构，按余额降序排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(lbs.principal_balance), 2) AS under_prov_balance
FROM provision_snapshot ps
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ps.loan_id
JOIN loan_drawdown ld ON ld.loan_id = ps.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE ps.recognized_amount < ps.required_amount
GROUP BY i.institution_id, i.institution_name
HAVING SUM(lbs.principal_balance) > 100000000
ORDER BY under_prov_balance DESC, i.institution_name;"""),
    dict(
        id="BRB2-0064", difficulty="hard", features=[],
        question="找出信贷资金违规流入限制类行业的支付指令：收款方所属行业的风险类别为限制类或退出类，且支付指令已执行。输出支付指令编号、借据编号、收款方名称、行业中文名称与指令金额，按指令金额降序排列。",
        sql="""SELECT pi.instruction_id, pi.loan_id, p.display_name, s.sector_name_zh, pi.instruction_amount
FROM payment_instruction pi
JOIN organization_profile op ON op.party_id = pi.intended_payee_party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
JOIN party p ON p.party_id = pi.intended_payee_party_id
WHERE s.risk_category IN ('RESTRICTED', 'EXIT')
  AND pi.status = 'EXECUTED'
ORDER BY pi.instruction_amount DESC, pi.instruction_id;"""),
    dict(
        id="BRB2-0065", difficulty="hard", features=[],
        question="计算各机构支付指令中收款方所属行业为限制类或退出类的指令金额占该机构全部支付指令金额的比重，输出机构名称、违规流入金额、指令金额合计与占比，按占比降序排列。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(CASE WHEN s.risk_category IN ('RESTRICTED','EXIT')
                      THEN pi.instruction_amount ELSE 0 END), 2) AS restricted_amount,
       ROUND(SUM(pi.instruction_amount), 2) AS total_amount,
       ROUND(SUM(CASE WHEN s.risk_category IN ('RESTRICTED','EXIT')
                      THEN pi.instruction_amount ELSE 0 END) * 1.0
             / SUM(pi.instruction_amount), 6) AS restricted_ratio
FROM payment_instruction pi
JOIN loan_drawdown ld ON ld.loan_id = pi.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
LEFT JOIN organization_profile op ON op.party_id = pi.intended_payee_party_id
LEFT JOIN industry_sector s ON s.sector_code = op.industry_code
GROUP BY i.institution_id, i.institution_name
ORDER BY restricted_ratio DESC, i.institution_name;"""),
    dict(
        id="BRB2-0066", difficulty="hard", features=[],
        question="找出单一客户贷款集中度超标的机构：以单个对公客户在本行的贷款本金余额合计 ÷ 本行资本净额计算，输出机构名称、客户名称、余额合计、资本净额与集中度，只保留集中度超过 0.10 的记录，按集中度降序排列。",
        sql="""SELECT i.institution_name, p.display_name,
       ROUND(SUM(lbs.principal_balance), 2) AS total_balance,
       cs.net_capital,
       ROUND(SUM(lbs.principal_balance) * 1.0 / cs.net_capital, 6) AS concentration
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
JOIN institution i ON i.institution_id = a.institution_id
JOIN capital_snapshot cs ON cs.institution_id = i.institution_id
WHERE p.party_type = 'CORPORATE'
GROUP BY i.institution_id, i.institution_name, p.party_id, p.display_name, cs.net_capital
HAVING SUM(lbs.principal_balance) * 1.0 / cs.net_capital > 0.10
ORDER BY concentration DESC, p.display_name;"""),
    dict(
        id="BRB2-0067", difficulty="hard", features=[],
        question="找出集团客户授信集中度超标的机构：以敞口集团成员在本行的贷款本金余额合计 ÷ 本行资本净额计算，输出机构名称、集团名称、敞口金额、资本净额与集中度，只保留集中度超过 0.15 的记录，按集中度降序排列。",
        sql="""SELECT i.institution_name, eg.group_name,
       ROUND(SUM(lbs.principal_balance), 2) AS exposure_amount,
       cs.net_capital,
       ROUND(SUM(lbs.principal_balance) * 1.0 / cs.net_capital, 6) AS concentration
FROM exposure_group eg
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
JOIN credit_agreement a ON a.borrower_party_id = egm.party_id AND a.institution_id = eg.institution_id
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
JOIN institution i ON i.institution_id = eg.institution_id
JOIN capital_snapshot cs ON cs.institution_id = i.institution_id
GROUP BY i.institution_id, i.institution_name, eg.exposure_group_id, eg.group_name, cs.net_capital
HAVING SUM(lbs.principal_balance) * 1.0 / cs.net_capital > 0.15
ORDER BY concentration DESC, eg.group_name;"""),
    dict(
        id="BRB2-0068", difficulty="hard", features=[],
        question="找出理财产品期限错配的情形：底层资产到期日晚于理财产品实际终止日。输出产品编号、产品名称、底层资产编号、资产到期日与产品终止日，按资产到期日降序排列。",
        sql="""SELECT wp.product_id, wp.product_name, ma.asset_id, ma.maturity_on, wp.actual_termination_on
FROM product_holding_snapshot phs
JOIN wealth_product wp ON wp.product_id = phs.product_id
JOIN managed_asset ma ON ma.asset_id = phs.asset_id
WHERE ma.maturity_on > wp.actual_termination_on
ORDER BY ma.maturity_on DESC, wp.product_id, ma.asset_id;"""),
    dict(
        id="BRB2-0069", difficulty="hard", features=[],
        question="找出通过两层及以上嵌套（穿透层级达到两层及以上）持有底层资产的理财产品，输出产品编号、产品名称与嵌套持仓笔数，按笔数降序排列。",
        sql="""SELECT wp.product_id, wp.product_name, COUNT(*) AS nested_holdings
FROM product_holding_snapshot phs
JOIN wealth_product wp ON wp.product_id = phs.product_id
WHERE phs.lookthrough_depth >= 2
GROUP BY wp.product_id, wp.product_name
ORDER BY nested_holdings DESC, wp.product_id;"""),
    dict(
        id="BRB2-0070", difficulty="hard", features=[],
        question="统计各机构通过特殊目的载体（含多层嵌套载体）持有的底层资产市值合计，输出机构名称与嵌套持仓市值合计，按市值降序排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(phs.fair_value), 2) AS spv_value
FROM product_holding_snapshot phs
JOIN wealth_product wp ON wp.product_id = phs.product_id
JOIN institution i ON i.institution_id = wp.issuer_institution_id
WHERE phs.investment_path IN ('SPV', 'NESTED_SPV')
GROUP BY i.institution_id, i.institution_name
ORDER BY spv_value DESC, i.institution_name;"""),
    dict(
        id="BRB2-0071", difficulty="hard", features=[],
        question="找出员工自办业务的疑点：现金交易的经办人与交易对手账户持有人为同一自然人。输出交易编号、业务日期、经办人所属员工账号（工号）、账户编号与金额，按金额降序排列。",
        sql="""SELECT pe.payment_id, pe.business_date, so.staff_id, ah.account_id, pe.amount
FROM payment_event pe
JOIN service_operator so ON so.operator_id = pe.operator_id
JOIN staff_member sm ON sm.staff_id = so.staff_id
JOIN account_holder ah ON ah.account_id IN (pe.from_account_id, pe.to_account_id)
WHERE pe.is_cash = 1
  AND ah.party_id = sm.person_party_id
ORDER BY pe.amount DESC, pe.payment_id;"""),
    dict(
        id="BRB2-0072", difficulty="hard", features=[],
        question="统计各员工（客户经理）作为经办人办理的现金交易金额合计，输出员工工号、现金交易笔数与金额合计，只保留金额合计超过 5000 万元的员工，按金额合计降序排列。",
        sql="""SELECT so.staff_id, COUNT(*) AS txn_count, ROUND(SUM(pe.amount), 2) AS total_amount
FROM payment_event pe
JOIN service_operator so ON so.operator_id = pe.operator_id
WHERE pe.is_cash = 1
GROUP BY so.staff_id
HAVING SUM(pe.amount) > 50000000
ORDER BY total_amount DESC, so.staff_id;"""),
    dict(
        id="BRB2-0073", difficulty="hard", features=[],
        question="找出押品覆盖不足的担保合同：担保合同的担保债权金额高于其关联押品最近一次评估价值。输出担保合同编号、担保债权金额、押品编号、押品最近评估价值与缺口金额，按缺口金额降序排列。",
        sql="""SELECT sa.security_id, sa.secured_amount, cl.collateral_id, cv.valuation_amount,
       ROUND(sa.secured_amount - cv.valuation_amount, 2) AS shortfall
FROM security_agreement sa
JOIN collateral_link cl ON cl.security_id = sa.security_id
JOIN collateral_valuation cv ON cv.collateral_id = cl.collateral_id
WHERE cv.valued_on = (SELECT MAX(cv2.valued_on) FROM collateral_valuation cv2
                      WHERE cv2.collateral_id = cl.collateral_id)
  AND sa.secured_amount > cv.valuation_amount
ORDER BY shortfall DESC, sa.security_id;"""),
    dict(
        id="BRB2-0074", difficulty="hard", features=[],
        question="找出互保情形：同一主体既是某笔授信的担保人，本身又是本行借款客户。输出该主体编号、名称、其作为担保人的承诺笔数与其作为借款人的协议笔数，按担保笔数降序排列。",
        sql="""SELECT p.party_id, p.display_name, g.guarantee_count, b.agreement_count
FROM party p
JOIN (SELECT guarantor_party_id AS pid, COUNT(*) AS guarantee_count
      FROM guarantor_commitment GROUP BY guarantor_party_id) g ON g.pid = p.party_id
JOIN (SELECT borrower_party_id AS pid, COUNT(*) AS agreement_count
      FROM credit_agreement GROUP BY borrower_party_id) b ON b.pid = p.party_id
ORDER BY g.guarantee_count DESC, p.party_id;"""),
    dict(
        id="BRB2-0075", difficulty="hard", features=[],
        question="找出大额现金交易：单笔现金交易金额超过 500 万元且交易状态为已清算。输出交易编号、业务日期、交易类型中文名称、金额与经办机构单元名称，按金额降序排列。",
        sql="""SELECT pe.payment_id, pe.business_date, t.name_zh, pe.amount, ou.unit_name
FROM payment_event pe
JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
JOIN organization_unit ou ON ou.org_unit_id = pe.origin_org_unit_id
WHERE pe.is_cash = 1 AND pe.amount > 5000000 AND pe.status = 'SETTLED'
ORDER BY pe.amount DESC, pe.payment_id;"""),
    dict(
        id="BRB2-0076", difficulty="hard", features=[],
        question="找出风险等级与投资者类型不匹配的理财产品：风险等级为 R4 或 R5，但目标投资者为普通投资者。输出产品编号、产品名称、风险等级与目标投资者类型，按产品编号升序排列。",
        sql="""SELECT product_id, product_name, risk_level, target_investor_type
FROM wealth_product
WHERE risk_level IN ('R4', 'R5') AND target_investor_type = 'GENERAL'
ORDER BY product_id;"""),
    dict(
        id="BRB2-0077", difficulty="hard", features=[],
        question="找出贷款投向与借款人所属行业不符的授信协议：授信协议约定的资金投向行业与借款人注册行业不一致。输出协议编号、借款人名称、借款人注册行业名称、协议投向行业名称与合同金额，按合同金额降序排列。",
        sql="""SELECT a.agreement_id, p.display_name, s1.sector_name_zh AS borrower_sector,
       s2.sector_name_zh AS target_sector, a.contract_amount
FROM credit_agreement a
JOIN organization_profile op ON op.party_id = a.borrower_party_id
JOIN industry_sector s1 ON s1.sector_code = op.industry_code
JOIN industry_sector s2 ON s2.sector_code = a.target_industry_code
JOIN party p ON p.party_id = a.borrower_party_id
WHERE a.target_industry_code <> op.industry_code
ORDER BY a.contract_amount DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0078", difficulty="hard", features=[],
        question="找出协议已到期但借据仍未结清的授信：授信协议状态为已到期，且其项下存在状态为正常的借据。输出协议编号、协议到期日、借据编号与放款金额，按协议到期日升序排列。",
        sql="""SELECT a.agreement_id, a.maturity_on, ld.loan_id, ld.disbursed_amount
FROM credit_agreement a
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
WHERE a.status = 'MATURED' AND ld.status = 'ACTIVE'
ORDER BY a.maturity_on, a.agreement_id, ld.loan_id;"""),
    dict(
        id="BRB2-0079", difficulty="hard", features=[],
        question="找出长期不动户发生大额交易的疑点：账户状态为“久悬”，但其在 2026 年的交易中存在单笔金额超过 100 万元的交易。输出账户编号、交易编号、业务日期与金额，按金额降序排列。",
        sql="""SELECT ac.account_id, pe.payment_id, pe.business_date, pe.amount
FROM payment_event pe
JOIN account ac ON ac.account_id = COALESCE(pe.from_account_id, pe.to_account_id)
WHERE ac.status = 'DORMANT' AND pe.amount > 1000000
ORDER BY pe.amount DESC, pe.payment_id;"""),
    dict(
        id="BRB2-0080", difficulty="hard", features=[],
        question="找出对已被吊销或经营异常的对公客户仍在发放贷款的情形：客户经营状态并非正常经营，但其名下仍有状态为正常的借据。输出客户编号、客户名称、经营状态与正常借据笔数，按借据笔数降序排列。",
        sql="""SELECT p.party_id, p.display_name, op.operating_status, COUNT(*) AS active_loans
FROM organization_profile op
JOIN party p ON p.party_id = op.party_id
JOIN credit_agreement a ON a.borrower_party_id = op.party_id
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
WHERE op.operating_status <> 'OPERATING' AND ld.status = 'ACTIVE'
GROUP BY p.party_id, p.display_name, op.operating_status
ORDER BY active_loans DESC, p.party_id;"""),
    dict(
        id="BRB2-0081", difficulty="hard", features=[],
        question="找出关联方之间的已清算资金往来：付款账户与收款账户的主持有人之间存在非“非关联方”的关联关系记录。输出交易编号、业务日期、金额、付款方客户编号与收款方客户编号，按金额降序排列。",
        sql="""SELECT pe.payment_id, pe.business_date, pe.amount,
       ah1.party_id AS payer_party_id, ah2.party_id AS payee_party_id
FROM payment_event pe
JOIN account_holder ah1 ON ah1.account_id = pe.from_account_id AND ah1.holder_role = 'PRIMARY'
JOIN account_holder ah2 ON ah2.account_id = pe.to_account_id AND ah2.holder_role = 'PRIMARY'
JOIN party_relation pr ON pr.source_party_id = ah1.party_id AND pr.target_party_id = ah2.party_id
WHERE pe.status = 'SETTLED' AND pr.relation_type <> 'NON_RELATED'
ORDER BY pe.amount DESC, pe.payment_id;"""),
    dict(
        id="BRB2-0082", difficulty="hard", features=[],
        question="找出“一边逾期、一边继续用信”的客户：客户名下存在本金逾期天数超过 90 天的借据，同时在同一机构仍有状态为正常的其他借据。输出客户编号、客户名称、机构名称、逾期借据笔数与正常其他借据笔数，按逾期借据笔数降序排列。",
        sql="""SELECT p.party_id, p.display_name, i.institution_name,
       COUNT(DISTINCT d.loan_id) AS overdue_loans,
       COUNT(DISTINCT ld2.loan_id) AS active_loans
FROM delinquency_snapshot d
JOIN loan_drawdown ld1 ON ld1.loan_id = d.loan_id
JOIN credit_agreement a1 ON a1.agreement_id = ld1.agreement_id
JOIN institution i ON i.institution_id = a1.institution_id
JOIN party p ON p.party_id = a1.borrower_party_id
JOIN credit_agreement a2 ON a2.borrower_party_id = a1.borrower_party_id
                        AND a2.institution_id = a1.institution_id
JOIN loan_drawdown ld2 ON ld2.agreement_id = a2.agreement_id
                      AND ld2.loan_id <> ld1.loan_id
WHERE d.principal_overdue_days > 90
  AND ld2.status = 'ACTIVE'
GROUP BY p.party_id, p.display_name, i.institution_id, i.institution_name
ORDER BY overdue_loans DESC, p.party_id;"""),
    dict(
        id="BRB2-0083", difficulty="hard", features=[],
        question="找出多次展期的借据：同一授信协议项下的借据放款笔数不少于 3 笔。输出协议编号、借款人名称与借据笔数，按借据笔数降序排列。",
        sql="""SELECT a.agreement_id, p.display_name, COUNT(*) AS loan_count
FROM credit_agreement a
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
GROUP BY a.agreement_id, p.display_name
HAVING COUNT(*) >= 3
ORDER BY loan_count DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0084", difficulty="hard", features=[],
        question="统计各机构现金交易中单笔金额超过 500 万元的大额现金交易笔数与金额合计，输出机构名称、笔数与金额合计，只保留笔数不少于 50 笔的机构，按金额合计降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS large_cash_count,
       ROUND(SUM(pe.amount), 2) AS total_amount
FROM payment_event pe
JOIN account ac ON ac.account_id = COALESCE(pe.from_account_id, pe.to_account_id)
JOIN institution i ON i.institution_id = ac.institution_id
WHERE pe.is_cash = 1 AND pe.amount > 5000000
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(*) >= 50
ORDER BY total_amount DESC, i.institution_name;"""),
    dict(
        id="BRB2-0085", difficulty="hard", features=[],
        question="找出受托支付资金流向受限行业的借据：支付指令采用受托支付方式，但收款方所属行业与授信合同约定的目标投向行业不一致，且收款方行业风险类别为限制类或退出类。输出借据编号、借款方名称、收款方名称、收款行业与指令金额，按指令金额降序排列。",
        sql="""SELECT pi.loan_id, p1.display_name AS borrower, p2.display_name AS payee,
       s.sector_name_zh, pi.instruction_amount
FROM payment_instruction pi
JOIN loan_drawdown ld ON ld.loan_id = pi.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party p1 ON p1.party_id = a.borrower_party_id
JOIN party p2 ON p2.party_id = pi.intended_payee_party_id
JOIN organization_profile op ON op.party_id = pi.intended_payee_party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
WHERE pi.payment_mode = 'ENTRUSTED_PAYMENT'
  AND op.industry_code <> a.target_industry_code
  AND s.risk_category IN ('RESTRICTED', 'EXIT')
ORDER BY pi.instruction_amount DESC, pi.loan_id;"""),
    dict(
        id="BRB2-0086", difficulty="hard", features=[],
        question="统计各客户经理（员工）经办业务中收款账户主持有人所属行业为限制类或退出类的交易笔数，输出员工工号与笔数，取前 10 名，按笔数降序排列。",
        sql="""SELECT so.staff_id, COUNT(*) AS restricted_txn_count
FROM payment_event pe
JOIN service_operator so ON so.operator_id = pe.operator_id
JOIN account_holder ah ON ah.account_id = pe.to_account_id AND ah.holder_role = 'PRIMARY'
JOIN organization_profile op ON op.party_id = ah.party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
WHERE s.risk_category IN ('RESTRICTED', 'EXIT')
GROUP BY so.staff_id
ORDER BY restricted_txn_count DESC, so.staff_id
LIMIT 10;"""),
    dict(
        id="BRB2-0087", difficulty="hard", features=[],
        question="统计各机构关联方（在关联方关系中作为源主体且关系类型不为“非关联方”）授信合同金额合计占该机构全部授信合同金额的比重，输出机构名称、关联方授信金额、全部授信金额与占比，按占比降序排列。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(CASE WHEN EXISTS (
           SELECT 1 FROM party_relation pr
           JOIN relation_type_catalog rt ON rt.relation_type = pr.relation_type
           WHERE pr.source_party_id = a.borrower_party_id
             AND rt.relation_name_zh <> '非关联方'
       ) THEN a.contract_amount ELSE 0 END), 2) AS related_amount,
       ROUND(SUM(a.contract_amount), 2) AS total_amount,
       ROUND(SUM(CASE WHEN EXISTS (
           SELECT 1 FROM party_relation pr
           JOIN relation_type_catalog rt ON rt.relation_type = pr.relation_type
           WHERE pr.source_party_id = a.borrower_party_id
             AND rt.relation_name_zh <> '非关联方'
       ) THEN a.contract_amount ELSE 0 END) * 1.0 / SUM(a.contract_amount), 6) AS related_ratio
FROM credit_agreement a
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY related_ratio DESC, i.institution_name;"""),
    dict(
        id="BRB2-0088", difficulty="hard", features=[],
        question="找出押品被重复抵押的情形：同一抵押物被有效关联到两份及以上的担保合同。输出抵押物编号、抵押物名称、被关联的担保合同数量与担保债权金额合计，按担保合同数量降序排列。",
        sql="""SELECT ca.collateral_id, ca.asset_label, COUNT(*) AS link_count,
       ROUND(SUM(sa.secured_amount), 2) AS total_secured
FROM collateral_asset ca
JOIN collateral_link cl ON cl.collateral_id = ca.collateral_id
JOIN security_agreement sa ON sa.security_id = cl.security_id
WHERE cl.status = 'ACTIVE'
GROUP BY ca.collateral_id, ca.asset_label
HAVING COUNT(*) >= 2
ORDER BY link_count DESC, ca.collateral_id;"""),
    dict(
        id="BRB2-0089", difficulty="hard", features=[],
        question="统计各机构在信贷管控事项台账中未按期完成（完成日期为空或晚于截止日期）的记录所涉及的行为观测值合计，输出机构名称与观测值合计，取前 5 名，按合计值降序排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(r.observed_value), 4) AS total_observed
FROM lending_control_event_v3 r
JOIN institution i ON i.institution_id = r.institution_id
WHERE r.completion_date IS NULL OR r.completion_date > r.deadline_date
GROUP BY i.institution_id, i.institution_name
ORDER BY total_observed DESC, i.institution_name
LIMIT 5;"""),
    dict(
        id="BRB2-0090", difficulty="hard", features=[],
        question="找出理财产品实际终止日晚于计划到期日超过 30 天的情形。输出产品编号、产品名称、计划到期日、实际终止日与延期天数，按延期天数降序排列。",
        sql="""SELECT product_id, product_name, scheduled_maturity_on, actual_termination_on,
       CAST(julianday(actual_termination_on) - julianday(scheduled_maturity_on) AS INTEGER) AS delay_days
FROM wealth_product
WHERE julianday(actual_termination_on) - julianday(scheduled_maturity_on) > 30
ORDER BY delay_days DESC, product_id;"""),
    dict(
        id="BRB2-0091", difficulty="hard", features=[],
        question="找出客户尽职调查事项台账中截至审计基准日 2026-06-30 仍未完成（完成日期为空）的记录，输出台账记录编号、机构名称、事项发生日期、法定截止日期与距截止日的天数差（以 2026-06-30 减去法定截止日期计算），按天数差降序排列并取前 20 条。",
        sql="""SELECT r.record_id, i.institution_name, r.event_date, r.deadline_date,
       CAST(julianday('2026-06-30') - julianday(r.deadline_date) AS INTEGER) AS overdue_days
FROM customer_due_diligence_event_v3 r
JOIN institution i ON i.institution_id = r.institution_id
WHERE r.completion_date IS NULL
ORDER BY overdue_days DESC, r.record_id
LIMIT 20;"""),
    dict(
        id="BRB2-0092", difficulty="hard", features=[],
        question="统计各机构在 2026 年上半年（2026-01-01 至 2026-06-30）贷款发放金额合计，输出机构名称与发放金额合计，只保留发放金额合计超过 50 亿元的机构，按合计金额降序排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(ld.disbursed_amount), 2) AS total_disbursed
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE ld.disbursed_on BETWEEN '2026-01-01' AND '2026-06-30'
GROUP BY i.institution_id, i.institution_name
HAVING SUM(ld.disbursed_amount) > 5000000000
ORDER BY total_disbursed DESC, i.institution_name;"""),
    dict(
        id="BRB2-0093", difficulty="hard", features=[],
        question="找出抵押物已释放但担保合同仍为有效的冲突记录。输出担保合同编号、抵押物编号、抵押物状态与担保合同状态，按担保合同编号升序排列。",
        sql="""SELECT sa.security_id, cl.collateral_id, ca.status AS collateral_status, sa.status AS security_status
FROM security_agreement sa
JOIN collateral_link cl ON cl.security_id = sa.security_id
JOIN collateral_asset ca ON ca.collateral_id = cl.collateral_id
WHERE ca.status = 'RELEASED' AND sa.status = 'ACTIVE'
ORDER BY sa.security_id;"""),
    dict(
        id="BRB2-0094", difficulty="hard", features=[],
        question="统计各机构对公客户中按借款人所属行业划分的授信合同金额合计，仅统计风险类别为限制类或退出类的行业，输出机构名称、行业名称与合同金额合计，按合计金额降序排列。",
        sql="""SELECT i.institution_name, s.sector_name_zh, ROUND(SUM(a.contract_amount), 2) AS total_contract
FROM credit_agreement a
JOIN institution i ON i.institution_id = a.institution_id
JOIN organization_profile op ON op.party_id = a.borrower_party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
WHERE s.risk_category IN ('RESTRICTED', 'EXIT')
GROUP BY i.institution_id, i.institution_name, s.sector_code, s.sector_name_zh
ORDER BY total_contract DESC, i.institution_name, s.sector_name_zh;"""),
    dict(
        id="BRB2-0095", difficulty="hard", features=[],
        question="找出借据已核销但其所属授信协议关联的担保合同仍在有效状态的记录。输出借据编号、协议编号、担保合同编号与担保债权金额，按担保债权金额降序排列。",
        sql="""SELECT ld.loan_id, a.agreement_id, sa.security_id, sa.secured_amount
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN secured_obligation so ON so.agreement_id = a.agreement_id
JOIN security_agreement sa ON sa.security_id = so.security_id
WHERE ld.status = 'WRITTEN_OFF' AND sa.status = 'ACTIVE'
ORDER BY sa.secured_amount DESC, ld.loan_id;"""),
    dict(
        id="BRB2-0096", difficulty="extra", features=[],
        question="找出每家机构贷款本金余额最大的那笔借据，输出机构名称、借据编号、本金余额与该机构内的余额排名（并列时编号小者在前），按机构名称升序排列。",
        sql="""WITH ranked AS (
    SELECT i.institution_name, lbs.loan_id, lbs.principal_balance,
           ROW_NUMBER() OVER (PARTITION BY i.institution_id
                              ORDER BY lbs.principal_balance DESC, lbs.loan_id) AS rn
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN institution i ON i.institution_id = a.institution_id
)
SELECT institution_name, loan_id, principal_balance, rn
FROM ranked WHERE rn = 1
ORDER BY institution_name;"""),
    dict(
        id="BRB2-0097", difficulty="extra", features=[],
        question="按借款人注册行业列出贷款本金余额排名前三的借据，输出行业中文名称、借据编号、本金余额与该行业内的排名，按行业名称升序、排名升序排列。",
        sql="""WITH ranked AS (
    SELECT s.sector_name_zh, lbs.loan_id, lbs.principal_balance,
           RANK() OVER (PARTITION BY s.sector_code ORDER BY lbs.principal_balance DESC) AS rnk
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN organization_profile op ON op.party_id = a.borrower_party_id
    JOIN industry_sector s ON s.sector_code = op.industry_code
)
SELECT sector_name_zh, loan_id, principal_balance, rnk
FROM ranked WHERE rnk <= 3
ORDER BY sector_name_zh, rnk, loan_id;"""),
    dict(
        id="BRB2-0098", difficulty="extra", features=[],
        question="按机构计算各借据本金余额占该机构贷款本金余额合计的比重，输出机构名称、借据编号、本金余额与占比，只保留占比超过 0.4% 的借据，按占比降序排列。",
        sql="""WITH base AS (
    SELECT i.institution_name, i.institution_id, lbs.loan_id,
           lbs.principal_balance,
           SUM(lbs.principal_balance) OVER (PARTITION BY i.institution_id) AS inst_total
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN institution i ON i.institution_id = a.institution_id
)
SELECT institution_name, loan_id, principal_balance,
       ROUND(principal_balance * 1.0 / inst_total, 6) AS share
FROM base
WHERE principal_balance * 1.0 / inst_total > 0.004
ORDER BY share DESC, loan_id;"""),
    dict(
        id="BRB2-0099", difficulty="extra", features=[],
        question="按业务日期统计现金支取交易的逐日累计金额，输出业务日期、当日金额与累计金额，只保留累计金额首次超过 5 亿元之前的日期（含首次超过的日期），按业务日期升序排列。",
        sql="""WITH daily AS (
    SELECT pe.business_date, SUM(pe.amount) AS day_amount
    FROM payment_event pe
    JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
    WHERE t.name_zh = '现金支取' AND pe.status = 'SETTLED'
    GROUP BY pe.business_date
), running AS (
    SELECT business_date, day_amount,
           SUM(day_amount) OVER (ORDER BY business_date) AS cumulative
    FROM daily
)
SELECT business_date, ROUND(day_amount, 2) AS day_amount, ROUND(cumulative, 2) AS cumulative
FROM running
WHERE business_date <= (SELECT MIN(business_date) FROM running WHERE cumulative > 500000000)
ORDER BY business_date;"""),
    dict(
        id="BRB2-0100", difficulty="extra", features=[],
        question="按业务日期统计每日交易笔数，并用窗口函数计算与前一日相比的笔数变化量，输出业务日期、当日笔数与较前一日的笔数变化，按业务日期升序排列。",
        sql="""WITH daily AS (
    SELECT business_date, COUNT(*) AS txn_count
    FROM payment_event
    GROUP BY business_date
)
SELECT business_date, txn_count,
       txn_count - LAG(txn_count) OVER (ORDER BY business_date) AS delta
FROM daily
ORDER BY business_date;"""),
    dict(
        id="BRB2-0101", difficulty="extra", features=[],
        question="找出本金余额高于本机构平均本金余额的借据，输出机构名称、借据编号、本金余额、本机构平均余额与该借据超出平均值的金额，按超出金额降序排列。",
        sql="""SELECT i.institution_name, lbs.loan_id, lbs.principal_balance,
       ROUND((SELECT AVG(lbs2.principal_balance)
              FROM loan_balance_snapshot lbs2
              JOIN loan_drawdown ld2 ON ld2.loan_id = lbs2.loan_id
              JOIN credit_agreement a2 ON a2.agreement_id = ld2.agreement_id
              WHERE a2.institution_id = a.institution_id), 2) AS inst_avg,
       ROUND(lbs.principal_balance - (SELECT AVG(lbs3.principal_balance)
              FROM loan_balance_snapshot lbs3
              JOIN loan_drawdown ld3 ON ld3.loan_id = lbs3.loan_id
              JOIN credit_agreement a3 ON a3.agreement_id = ld3.agreement_id
              WHERE a3.institution_id = a.institution_id), 2) AS excess
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE lbs.principal_balance > (SELECT AVG(lbs4.principal_balance)
                              FROM loan_balance_snapshot lbs4
                              JOIN loan_drawdown ld4 ON ld4.loan_id = lbs4.loan_id
                              JOIN credit_agreement a4 ON a4.agreement_id = ld4.agreement_id
                              WHERE a4.institution_id = a.institution_id)
ORDER BY excess DESC, lbs.loan_id;"""),
    dict(
        id="BRB2-0102", difficulty="extra", features=[],
        question="找出既关联了抵押物登记、又取得了第三方保证承诺的授信协议（通过被担保主债权桥接表关联），输出协议编号、借款人名称与合同金额，按合同金额降序排列。",
        sql="""SELECT a.agreement_id, p.display_name, a.contract_amount
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
WHERE EXISTS (SELECT 1 FROM secured_obligation so
              JOIN security_agreement sa ON sa.security_id = so.security_id
              JOIN collateral_link cl ON cl.security_id = sa.security_id
              WHERE so.agreement_id = a.agreement_id)
  AND EXISTS (SELECT 1 FROM secured_obligation so2
              JOIN security_agreement sa2 ON sa2.security_id = so2.security_id
              JOIN guarantor_commitment gc ON gc.security_id = sa2.security_id
              WHERE so2.agreement_id = a.agreement_id)
ORDER BY a.contract_amount DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0103", difficulty="extra", features=[],
        question="找出仅有第三方保证、没有任何抵押物关联的担保合同，输出担保合同编号、担保债权金额与担保人数量，按担保债权金额降序排列。",
        sql="""SELECT sa.security_id, sa.secured_amount,
       (SELECT COUNT(*) FROM guarantor_commitment gc WHERE gc.security_id = sa.security_id) AS guarantor_count
FROM security_agreement sa
WHERE NOT EXISTS (SELECT 1 FROM collateral_link cl WHERE cl.security_id = sa.security_id)
  AND EXISTS (SELECT 1 FROM guarantor_commitment gc WHERE gc.security_id = sa.security_id)
ORDER BY sa.secured_amount DESC, sa.security_id;"""),
    dict(
        id="BRB2-0104", difficulty="extra", features=[],
        question="汇总各机构的监管事项逾期情况：将信贷管控事项台账与公司治理控制台账中未按期完成（完成日期为空或晚于截止日期）的记录合并统计，输出机构名称、事项来源（分别标注为“信贷控制”与“治理控制”）与逾期记录数，按机构名称升序、来源升序排列。",
        sql="""SELECT i.institution_name, '信贷控制' AS source, COUNT(*) AS overdue_count
FROM lending_control_event_v3 r
JOIN institution i ON i.institution_id = r.institution_id
WHERE r.completion_date IS NULL OR r.completion_date > r.deadline_date
GROUP BY i.institution_id, i.institution_name
UNION ALL
SELECT i.institution_name, '治理控制' AS source, COUNT(*) AS overdue_count
FROM governance_control_record_v3 r
JOIN institution i ON i.institution_id = r.institution_id
WHERE r.completion_date IS NULL OR r.completion_date > r.deadline_date
GROUP BY i.institution_id, i.institution_name
ORDER BY institution_name, source;"""),
    dict(
        id="BRB2-0105", difficulty="extra", features=[],
        question="找出已签署授信协议但从未发生放款的客户（即其名下所有授信协议均无对应借据记录），输出客户编号与客户名称，按客户编号升序排列。",
        sql="""SELECT DISTINCT p.party_id, p.display_name
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
WHERE NOT EXISTS (SELECT 1 FROM loan_drawdown ld2
                  JOIN credit_agreement a2 ON a2.agreement_id = ld2.agreement_id
                  WHERE a2.borrower_party_id = a.borrower_party_id)
ORDER BY p.party_id;"""),
    dict(
        id="BRB2-0106", difficulty="extra", features=[],
        question="找出既有现金支取交易又有转账交易的账户编号，按账户编号升序排列。",
        sql="""SELECT ac.account_id
FROM account ac
JOIN payment_event pe ON pe.from_account_id = ac.account_id
JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
WHERE t.name_zh = '现金支取'
INTERSECT
SELECT ac.account_id
FROM account ac
JOIN payment_event pe ON pe.from_account_id = ac.account_id
JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
WHERE t.name_zh = '转账'
ORDER BY account_id;"""),
    dict(
        id="BRB2-0107", difficulty="extra", features=[],
        question="分两步统计：先按客户汇总其在本行的贷款本金余额合计，再筛出余额合计位于全部对公客户前 10% 的客户（以余额合计不低于全部对公客户余额合计的 90% 分位数为界），输出客户编号、客户名称与余额合计，按余额合计降序排列。",
        sql="""WITH per_customer AS (
    SELECT p.party_id, p.display_name, SUM(lbs.principal_balance) AS total_balance
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN party p ON p.party_id = a.borrower_party_id
    WHERE p.party_type = 'CORPORATE'
    GROUP BY p.party_id, p.display_name
), threshold AS (
    SELECT total_balance AS cut
    FROM per_customer
    ORDER BY total_balance DESC
    LIMIT 1 OFFSET (SELECT CAST(COUNT(*) * 0.1 AS INTEGER) FROM per_customer)
)
SELECT party_id, display_name, ROUND(total_balance, 2) AS total_balance
FROM per_customer, threshold
WHERE total_balance >= cut
ORDER BY total_balance DESC, party_id;"""),
    dict(
        id="BRB2-0108", difficulty="extra", features=[],
        question="按本金逾期天数区间（未逾期为 0、1-30 天、31-90 天、91-180 天、181-360 天、360 天以上）统计借据笔数，输出逾期区间与借据笔数，按区间下限升序排列。",
        sql="""SELECT CASE
         WHEN d.principal_overdue_days IS NULL THEN '未逾期'
         WHEN d.principal_overdue_days <= 30 THEN '1-30天'
         WHEN d.principal_overdue_days <= 90 THEN '31-90天'
         WHEN d.principal_overdue_days <= 180 THEN '91-180天'
         WHEN d.principal_overdue_days <= 360 THEN '181-360天'
         ELSE '360天以上' END AS bucket,
       COUNT(*) AS loan_count
FROM loan_drawdown ld
LEFT JOIN delinquency_snapshot d ON d.loan_id = ld.loan_id
GROUP BY bucket
ORDER BY CASE bucket
         WHEN '未逾期' THEN 0 WHEN '1-30天' THEN 1 WHEN '31-90天' THEN 2
         WHEN '91-180天' THEN 3 WHEN '181-360天' THEN 4 ELSE 5 END;"""),
    dict(
        id="BRB2-0109", difficulty="extra", features=[],
        question="先计算各机构的不良贷款率，再输出不良率高于全部机构不良率中位数的机构。输出机构名称与不良贷款率，按不良率降序排列。",
        sql="""WITH inst_npl AS (
    SELECT i.institution_name,
           SUM(CASE WHEN g.is_nonperforming = 1 THEN lbs.principal_balance ELSE 0 END) * 1.0
           / SUM(lbs.principal_balance) AS npl_ratio
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN institution i ON i.institution_id = a.institution_id
    JOIN risk_classification rc ON rc.loan_id = ld.loan_id
    JOIN classification_grade g ON g.grade_code = rc.grade_code
    GROUP BY i.institution_id, i.institution_name
), med AS (
    SELECT AVG(npl_ratio) AS median_ratio FROM (
        SELECT npl_ratio FROM inst_npl ORDER BY npl_ratio
        LIMIT 2 - (SELECT COUNT(*) FROM inst_npl) % 2
        OFFSET (SELECT (COUNT(*) - 1) / 2 FROM inst_npl))
)
SELECT institution_name, ROUND(npl_ratio, 6) AS npl_ratio
FROM inst_npl, med
WHERE npl_ratio > median_ratio
ORDER BY npl_ratio DESC, institution_name;"""),
    dict(
        id="BRB2-0110", difficulty="extra", features=[],
        question="找出同一抵押物在同一评估日存在两条评估记录的情形。输出抵押物编号、评估日期与被重复的评估记录条数，按抵押物编号升序排列。",
        sql="""SELECT cv.collateral_id, cv.valued_on, COUNT(*) AS duplicate_count
FROM collateral_valuation cv
GROUP BY cv.collateral_id, cv.valued_on
HAVING COUNT(*) > 1
ORDER BY cv.collateral_id;"""),
    dict(
        id="BRB2-0111", difficulty="extra", features=[],
        question="找出本人作为授信协议借款人、且该授信协议的经办管理机构单元正是其所属机构单元的本行员工。输出员工工号、员工姓名与所在机构单元名称，按员工工号升序排列。",
        sql="""SELECT DISTINCT sm.staff_id, p.display_name, ou.unit_name
FROM staff_member sm
JOIN party p ON p.party_id = sm.person_party_id
JOIN organization_unit ou ON ou.org_unit_id = sm.home_org_unit_id
JOIN credit_agreement a ON a.managing_org_unit_id = sm.home_org_unit_id
WHERE a.borrower_party_id = sm.person_party_id
ORDER BY sm.staff_id;"""),
    dict(
        id="BRB2-0112", difficulty="extra", features=[],
        question="按担保合同所属机构汇总其关联抵押物的最新评估价值合计，并输出评估价值最高的三家机构的名称、评估价值合计及其在全部机构中的排名，按评估价值合计降序排列。",
        sql="""WITH inst_coll AS (
    SELECT i.institution_name, SUM(cv.valuation_amount) AS total_valuation
    FROM collateral_valuation cv
    JOIN collateral_asset ca ON ca.collateral_id = cv.collateral_id
    JOIN collateral_link cl ON cl.collateral_id = ca.collateral_id
    JOIN security_agreement sa ON sa.security_id = cl.security_id
    JOIN institution i ON i.institution_id = sa.institution_id
    WHERE cv.valued_on = (SELECT MAX(cv2.valued_on) FROM collateral_valuation cv2
                          WHERE cv2.collateral_id = ca.collateral_id)
    GROUP BY i.institution_id, i.institution_name
)
SELECT institution_name, ROUND(total_valuation, 2) AS total_valuation,
       RANK() OVER (ORDER BY total_valuation DESC) AS rnk
FROM inst_coll
ORDER BY total_valuation DESC
LIMIT 3;"""),
    dict(
        id="BRB2-0113", difficulty="extra", features=[],
        question="统计每位对公客户在本行的贷款笔数、本金余额合计与平均单笔金额，并输出平均单笔金额最高的前 5 名客户，按平均单笔金额降序排列。",
        sql="""SELECT p.party_id, p.display_name, COUNT(*) AS loan_count,
       ROUND(SUM(lbs.principal_balance), 2) AS total_balance,
       ROUND(AVG(lbs.principal_balance), 2) AS avg_balance
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
WHERE p.party_type = 'CORPORATE'
GROUP BY p.party_id, p.display_name
ORDER BY avg_balance DESC, p.party_id
LIMIT 5;"""),
    dict(
        id="BRB2-0114", difficulty="extra", features=[],
        question="汇总每个机构的监管台账记录总量：将信贷控制、治理控制、监管报送三类台账的记录数相加，输出机构名称、三类台账记录数合计，按合计降序排列。",
        sql="""WITH all_records AS (
    SELECT institution_id FROM lending_control_event_v3
    UNION ALL
    SELECT institution_id FROM governance_control_record_v3
    UNION ALL
    SELECT institution_id FROM regulatory_submission_event_v3
)
SELECT i.institution_name, COUNT(*) AS record_count
FROM all_records ar
JOIN institution i ON i.institution_id = ar.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY record_count DESC, i.institution_name;"""),
    dict(
        id="BRB2-0115", difficulty="extra", features=[],
        question="找出交易金额超过其付款账户平均付款交易金额 10 倍的大额交易，输出付款账户编号、交易编号、金额与该账户平均交易金额，按金额降序排列并取前 20 条。",
        sql="""SELECT pe.from_account_id AS account_id, pe.payment_id, pe.amount,
       ROUND((SELECT AVG(pe2.amount) FROM payment_event pe2
              WHERE pe2.from_account_id = pe.from_account_id), 2) AS account_avg
FROM payment_event pe
WHERE pe.amount > 10 * (SELECT AVG(pe3.amount) FROM payment_event pe3
                        WHERE pe3.from_account_id = pe.from_account_id)
ORDER BY pe.amount DESC, pe.payment_id
LIMIT 20;"""),
    dict(
        id="BRB2-0116", difficulty="extra", features=[],
        question="找出同时满足以下两个条件的机构：现金交易笔数位于全部机构前 3 名，且平均单笔现金交易金额超过 1150 万元。输出机构名称、现金交易笔数与平均单笔金额，按平均单笔金额降序排列。",
        sql="""WITH cash AS (
    SELECT i.institution_id, i.institution_name, COUNT(*) AS cash_count,
           AVG(pe.amount) AS avg_amount
    FROM payment_event pe
    JOIN account ac ON ac.account_id = COALESCE(pe.from_account_id, pe.to_account_id)
    JOIN institution i ON i.institution_id = ac.institution_id
    WHERE pe.is_cash = 1
    GROUP BY i.institution_id, i.institution_name
), top3 AS (
    SELECT institution_id FROM cash ORDER BY cash_count DESC, institution_id LIMIT 3
)
SELECT c.institution_name, c.cash_count, ROUND(c.avg_amount, 2) AS avg_amount
FROM cash c
JOIN top3 t ON t.institution_id = c.institution_id
WHERE c.avg_amount > 11500000
ORDER BY c.avg_amount DESC, c.institution_name;"""),
    dict(
        id="BRB2-0117", difficulty="extra", features=[],
        question="统计每个营业机构单元下辖员工的现金交易经办笔数（按员工所属机构单元汇总，通过员工经办交易归属），输出机构单元名称、员工人数与经办笔数，按经办笔数降序排列，取前 10 名。",
        sql="""SELECT ou.unit_name, COUNT(DISTINCT sm.staff_id) AS staff_count,
       COUNT(*) AS txn_count
FROM payment_event pe
JOIN service_operator so ON so.operator_id = pe.operator_id
JOIN staff_member sm ON sm.staff_id = so.staff_id
JOIN organization_unit ou ON ou.org_unit_id = sm.home_org_unit_id
WHERE pe.is_cash = 1
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY txn_count DESC, ou.unit_name
LIMIT 10;"""),
    dict(
        id="BRB2-0118", difficulty="extra", features=[],
        question="按客户分层统计个人客户的数量、平均年收入与年收入超过 100 万元的客户占比，输出客户分层、客户数量、平均年收入与高收入客户占比，按客户分层升序排列。",
        sql="""SELECT p.customer_segment, COUNT(*) AS customer_count,
       ROUND(AVG(pp.annual_income), 2) AS avg_income,
       ROUND(SUM(CASE WHEN pp.annual_income > 1000000 THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 6) AS high_income_ratio
FROM party p
JOIN person_profile pp ON pp.party_id = p.party_id
WHERE p.party_type = 'INDIVIDUAL'
GROUP BY p.customer_segment
ORDER BY p.customer_segment;"""),
    dict(
        id="BRB2-0119", difficulty="extra", features=[],
        question="计算每家机构按贷款品种划分的本金余额合计，并输出各机构内余额最高的品种及其占比，按占比降序排列。",
        sql="""WITH combo AS (
    SELECT i.institution_name, lp.product_name_zh,
           SUM(lbs.principal_balance) AS total_balance
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN institution i ON i.institution_id = a.institution_id
    JOIN loan_product_catalog lp ON lp.product_code = ld.drawdown_type
    GROUP BY i.institution_id, i.institution_name, lp.product_code, lp.product_name_zh
), ranked AS (
    SELECT institution_name, product_name_zh, total_balance,
           SUM(total_balance) OVER (PARTITION BY institution_name) AS inst_total,
           ROW_NUMBER() OVER (PARTITION BY institution_name ORDER BY total_balance DESC) AS rn
    FROM combo
)
SELECT institution_name, product_name_zh, ROUND(total_balance, 2) AS total_balance,
       ROUND(total_balance * 1.0 / inst_total, 6) AS share
FROM ranked
WHERE rn = 1
ORDER BY share DESC, institution_name;"""),
    dict(
        id="BRB2-0120", difficulty="extra", features=[],
        question="按机构统计关联方交易金额（付款账户与收款账户的主持有人之间存在非“非关联方”的关联关系记录）及其占全部交易金额的比重，输出机构名称、关联方交易金额、全部交易金额与占比，按占比降序排列；机构按付款账户所属机构归属（无付款账户时取收款账户所属机构），关联关系以付款账户主持有人为发起方、收款账户主持有人为目标方的方向判定。",
        sql="""WITH txn AS (
    SELECT i.institution_id, i.institution_name, pe.amount,
           CASE WHEN EXISTS (
               SELECT 1 FROM account_holder ah1
               JOIN account_holder ah2 ON ah2.account_id = pe.to_account_id AND ah2.holder_role = 'PRIMARY'
               JOIN party_relation pr ON pr.source_party_id = ah1.party_id AND pr.target_party_id = ah2.party_id
               WHERE ah1.account_id = pe.from_account_id AND pr.relation_type <> 'NON_RELATED'
           ) THEN 1 ELSE 0 END AS is_related
    FROM payment_event pe
    JOIN account ac ON ac.account_id = COALESCE(pe.from_account_id, pe.to_account_id)
    JOIN institution i ON i.institution_id = ac.institution_id
)
SELECT institution_name,
       ROUND(SUM(CASE WHEN is_related = 1 THEN amount ELSE 0 END), 2) AS related_amount,
       ROUND(SUM(amount), 2) AS total_amount,
       ROUND(SUM(CASE WHEN is_related = 1 THEN amount ELSE 0 END) * 1.0 / SUM(amount), 8) AS related_ratio
FROM txn
GROUP BY institution_id, institution_name
ORDER BY related_ratio DESC, institution_name;"""),
    dict(
        id="BRB2-0121", difficulty="extra", features=[],
        question="统计各机构截至审计基准日的贷款客户数、贷款笔数与户均贷款本金余额，输出机构名称、客户数、贷款笔数与户均余额，按户均余额降序排列。",
        sql="""SELECT i.institution_name, COUNT(DISTINCT a.borrower_party_id) AS borrower_count,
       COUNT(*) AS loan_count,
       ROUND(SUM(lbs.principal_balance) / COUNT(DISTINCT a.borrower_party_id), 2) AS avg_per_borrower
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY avg_per_borrower DESC, i.institution_name;"""),
    dict(
        id="BRB2-0122", difficulty="extra", features=[],
        question="找出同时满足下列条件的理财产品：持有底层资产笔数不少于 3 笔，且非标准化资产持仓市值占比超过 30%。输出产品编号、产品名称、底层资产笔数与非标占比，按非标占比降序排列。",
        sql="""SELECT wp.product_id, wp.product_name, COUNT(*) AS asset_count,
       ROUND(SUM(CASE WHEN ma.asset_scope = 'NON_STANDARDIZED' THEN phs.fair_value ELSE 0 END)
             * 1.0 / SUM(phs.fair_value), 6) AS nonstd_ratio
FROM product_holding_snapshot phs
JOIN wealth_product wp ON wp.product_id = phs.product_id
JOIN managed_asset ma ON ma.asset_id = phs.asset_id
GROUP BY wp.product_id, wp.product_name
HAVING COUNT(*) >= 3
   AND SUM(CASE WHEN ma.asset_scope = 'NON_STANDARDIZED' THEN phs.fair_value ELSE 0 END)
       * 1.0 / SUM(phs.fair_value) > 0.3
ORDER BY nonstd_ratio DESC, wp.product_id;"""),
    dict(
        id="BRB2-0123", difficulty="extra", features=[],
        question="按月份统计 2026 年上半年（2026-01-01 至 2026-06-30）各机构的贷款发放笔数与金额，输出月份、机构名称、发放笔数与发放金额，按月份升序、发放金额降序排列。",
        sql="""SELECT substr(ld.disbursed_on, 1, 7) AS month, i.institution_name,
       COUNT(*) AS loan_count, ROUND(SUM(ld.disbursed_amount), 2) AS total_amount
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE ld.disbursed_on BETWEEN '2026-01-01' AND '2026-06-30'
GROUP BY month, i.institution_id, i.institution_name
ORDER BY month, total_amount DESC, i.institution_name;"""),
    dict(
        id="BRB2-0124", difficulty="extra", features=[],
        question="找出在本行既持有贷记卡（信用卡）又开立了定期存款账户的个人客户，输出客户编号、客户名称、持有贷记卡数量与定期存款账户数量，按定期存款账户数量降序排列。",
        sql="""SELECT p.party_id, p.display_name, c.card_count, td.deposit_count
FROM party p
JOIN (SELECT holder_party_id AS pid, COUNT(*) AS card_count
      FROM payment_card
      WHERE card_type = 'CREDIT'
      GROUP BY holder_party_id) c ON c.pid = p.party_id
JOIN (SELECT ah.party_id AS pid, COUNT(DISTINCT t.account_id) AS deposit_count
      FROM term_deposit t
      JOIN account_holder ah ON ah.account_id = t.account_id
      GROUP BY ah.party_id) td ON td.pid = p.party_id
ORDER BY td.deposit_count DESC, p.party_id;"""),
    dict(
        id="BRB2-0125", difficulty="extra", features=[],
        question="计算各机构现金支取金额占全部交易金额的比重，并按比重从高到低给出排名，输出机构名称、现金支取金额、全部交易金额、占比与排名，按排名升序排列。",
        sql="""WITH inst_txn AS (
    SELECT i.institution_id, i.institution_name,
           SUM(CASE WHEN t.name_zh = '现金支取' THEN pe.amount ELSE 0 END) AS cash_out,
           SUM(pe.amount) AS total_amount
    FROM payment_event pe
    JOIN account ac ON ac.account_id = COALESCE(pe.from_account_id, pe.to_account_id)
    JOIN institution i ON i.institution_id = ac.institution_id
    JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
    GROUP BY i.institution_id, i.institution_name
)
SELECT institution_name, ROUND(cash_out, 2) AS cash_out_amount,
       ROUND(total_amount, 2) AS total_amount,
       ROUND(cash_out * 1.0 / total_amount, 6) AS cash_ratio,
       RANK() OVER (ORDER BY cash_out * 1.0 / total_amount DESC) AS rnk
FROM inst_txn
ORDER BY rnk, institution_name;"""),
    dict(
        id="BRB2-0126", difficulty="easy", features=[],
        question="列出名称中包含“科技”的客户编号与客户名称，按客户编号升序排列。",
        sql="""SELECT party_id, display_name
FROM party
WHERE display_name LIKE '%科技%'
ORDER BY party_id;"""),
    dict(
        id="BRB2-0127", difficulty="medium", features=[],
        question="列出所有尚未完成客户尽职调查（完成日期为空）的台账记录编号、事项发生日期与法定截止日期，按法定截止日期升序排列。",
        sql="""SELECT record_id, event_date, deadline_date
FROM customer_due_diligence_event_v3
WHERE completion_date IS NULL
ORDER BY deadline_date, record_id;"""),
    dict(
        id="BRB2-0128", difficulty="medium", features=[],
        question="列出所有借据的编号、本金余额与逾期天数（无逾期台账的按 0 天处理），仅列出余额不为零的借据，按逾期天数降序排列并取前 30 条。",
        sql="""SELECT lbs.loan_id, lbs.principal_balance,
       COALESCE(d.principal_overdue_days, 0) AS overdue_days
FROM loan_balance_snapshot lbs
LEFT JOIN delinquency_snapshot d ON d.loan_id = lbs.loan_id
WHERE lbs.principal_balance <> 0
ORDER BY overdue_days DESC, lbs.loan_id
LIMIT 30;"""),
    dict(
        id="BRB2-0129", difficulty="hard", features=[],
        question="计算各机构贷款的平均账龄（审计基准日 2026-06-30 与放款日之间的天数），输出机构名称与平均账龄天数，按平均账龄降序排列。",
        sql="""SELECT i.institution_name,
       ROUND(AVG(julianday('2026-06-30') - julianday(ld.disbursed_on)), 2) AS avg_age_days
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY avg_age_days DESC, i.institution_name;"""),
    dict(
        id="BRB2-0130", difficulty="hard", features=[],
        question="列出截至审计基准日 2026-06-30 距到期日剩余 0 至 90 天且仍未结清的借据编号、放款日、到期日与剩余天数，按剩余天数升序排列。",
        sql="""SELECT loan_id, disbursed_on, current_maturity_on,
       CAST(julianday(current_maturity_on) - julianday('2026-06-30') AS INTEGER) AS days_left
FROM loan_drawdown
WHERE status = 'ACTIVE'
  AND julianday(current_maturity_on) - julianday('2026-06-30') BETWEEN 0 AND 90
ORDER BY days_left, loan_id;"""),
    dict(
        id="BRB2-0131", difficulty="extra", features=[],
        question="按本金余额将全部借据等分为四个组（四分位），输出借据编号、本金余额与所属分位组编号，按分位组升序、余额降序、借据编号升序排列并只取前 40 条；分位组 1 为本金余额最高的一组。",
        sql="""SELECT loan_id, principal_balance, quartile
FROM (
    SELECT loan_id, principal_balance,
           NTILE(4) OVER (ORDER BY principal_balance DESC) AS quartile
    FROM loan_balance_snapshot
)
ORDER BY quartile, principal_balance DESC, loan_id
LIMIT 40;"""),
    dict(
        id="BRB2-0132", difficulty="extra", features=[],
        question="按借款人注册行业计算各行业贷款本金余额由高到低的累计占比，输出行业名称、余额合计与累计占比，只保留累计占比不超过 0.8 的行业，按累计占比升序排列。",
        sql="""WITH sector_balance AS (
    SELECT s.sector_name_zh, SUM(lbs.principal_balance) AS total_balance
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN organization_profile op ON op.party_id = a.borrower_party_id
    JOIN industry_sector s ON s.sector_code = op.industry_code
    GROUP BY s.sector_code, s.sector_name_zh
), cumulative AS (
    SELECT sector_name_zh, total_balance,
           SUM(total_balance) OVER (ORDER BY total_balance DESC, sector_name_zh
                                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
           * 1.0 / SUM(total_balance) OVER () AS cum_share
    FROM sector_balance
)
SELECT sector_name_zh, ROUND(total_balance, 2) AS total_balance,
       ROUND(cum_share, 6) AS cumulative_share
FROM cumulative
WHERE cum_share <= 0.8
ORDER BY cumulative_share;"""),
    dict(
        id="BRB2-0133", difficulty="hard", features=[],
        question="找出同一客户在同一机构存在两笔及以上未结清借据的情形，输出客户编号、客户名称、机构名称与未结清借据笔数，按笔数降序排列。",
        sql="""SELECT p.party_id, p.display_name, i.institution_name, COUNT(*) AS active_loans
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE ld.status = 'ACTIVE'
GROUP BY p.party_id, p.display_name, i.institution_id, i.institution_name
HAVING COUNT(*) >= 2
ORDER BY active_loans DESC, p.party_id;"""),
    dict(
        id="BRB2-0134", difficulty="hard", features=[],
        question="制作存贷款交叉表：按机构统计对公贷款本金余额合计、个人贷款本金余额合计与储蓄存款余额合计，输出机构名称与三项金额，按对公贷款余额降序排列。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(CASE WHEN p.party_type = 'CORPORATE' THEN lbs.principal_balance ELSE 0 END), 2) AS corp_loan,
       ROUND(SUM(CASE WHEN p.party_type = 'INDIVIDUAL' THEN lbs.principal_balance ELSE 0 END), 2) AS retail_loan,
       (SELECT ROUND(SUM(abs.ledger_balance), 2)
        FROM account_balance_snapshot abs
        JOIN account ac ON ac.account_id = abs.account_id
        WHERE ac.institution_id = i.institution_id AND ac.account_kind = 'SAVINGS') AS savings
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY corp_loan DESC, i.institution_name;"""),
    dict(
        id="BRB2-0135", difficulty="hard", features=[],
        question="按机构与贷款品种两个维度统计借据笔数与放款金额合计，输出机构名称、品种中文名称、借据笔数与放款金额合计，按机构名称升序、放款金额降序排列。",
        sql="""SELECT i.institution_name, lp.product_name_zh, COUNT(*) AS loan_count,
       ROUND(SUM(ld.disbursed_amount), 2) AS total_disbursed
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
JOIN loan_product_catalog lp ON lp.product_code = ld.drawdown_type
GROUP BY i.institution_id, i.institution_name, lp.product_code, lp.product_name_zh
ORDER BY i.institution_name, total_disbursed DESC, lp.product_name_zh;"""),
    dict(
        id="BRB2-0136", difficulty="hard", features=[],
        question="列出风险类别为限制类或退出类的行业中的全部对公客户，输出客户编号、客户名称、行业名称与风险类别，按风险类别升序、客户编号升序排列。",
        sql="""SELECT p.party_id, p.display_name, s.sector_name_zh, s.risk_category
FROM party p
JOIN organization_profile op ON op.party_id = p.party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
WHERE s.risk_category IN ('RESTRICTED', 'EXIT')
ORDER BY s.risk_category, p.party_id;"""),
    dict(
        id="BRB2-0137", difficulty="hard", features=[],
        question="找出没有任何交易记录的账户编号、账户类型与开户机构名称，按账户编号升序排列并只取前 30 条。",
        sql="""SELECT ac.account_id, ac.account_kind, i.institution_name
FROM account ac
JOIN institution i ON i.institution_id = ac.institution_id
WHERE NOT EXISTS (SELECT 1 FROM payment_event pe
                  WHERE pe.from_account_id = ac.account_id OR pe.to_account_id = ac.account_id)
ORDER BY ac.account_id
LIMIT 30;"""),
    dict(
        id="BRB2-0138", difficulty="hard", features=[],
        question="统计各月份现金交易与转账交易的笔数对比，输出月份、现金交易笔数与转账交易笔数，按月份升序排列。",
        sql="""SELECT substr(pe.business_date, 1, 7) AS month,
       SUM(CASE WHEN t.name_zh IN ('现金存入', '现金支取') THEN 1 ELSE 0 END) AS cash_count,
       SUM(CASE WHEN t.name_zh = '转账' THEN 1 ELSE 0 END) AS transfer_count
FROM payment_event pe
JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
GROUP BY month
ORDER BY month;"""),
    dict(
        id="BRB2-0139", difficulty="extra", features=[],
        question="找出抵押物最新评估价值高于其所在担保合同担保债权金额 2 倍的担保合同，输出担保合同编号、担保债权金额、抵押物编号与最新评估价值，按评估价值与担保债权金额的差额降序排列。",
        sql="""SELECT sa.security_id, sa.secured_amount, cl.collateral_id, cv.valuation_amount
FROM security_agreement sa
JOIN collateral_link cl ON cl.security_id = sa.security_id
JOIN collateral_valuation cv ON cv.collateral_id = cl.collateral_id
WHERE cv.valued_on = (SELECT MAX(cv2.valued_on) FROM collateral_valuation cv2
                      WHERE cv2.collateral_id = cl.collateral_id)
  AND cv.valuation_amount > sa.secured_amount * 2
ORDER BY cv.valuation_amount - sa.secured_amount DESC, sa.security_id;"""),
    dict(
        id="BRB2-0140", difficulty="hard", features=[],
        question="找出在两家以上机构开立账户的个人客户，输出客户编号、客户名称与开户机构家数，按机构家数降序排列。",
        sql="""SELECT p.party_id, p.display_name, COUNT(DISTINCT ac.institution_id) AS inst_count
FROM account_holder ah
JOIN account ac ON ac.account_id = ah.account_id
JOIN party p ON p.party_id = ah.party_id
WHERE p.party_type = 'INDIVIDUAL'
GROUP BY p.party_id, p.display_name
HAVING COUNT(DISTINCT ac.institution_id) >= 2
ORDER BY inst_count DESC, p.party_id;"""),
    dict(
        id="BRB2-0141", difficulty="hard", features=[],
        question="找出同一天在同一付款账户上发生三笔及以上交易的账户与日期组合，输出账户编号、交易日期与该日交易笔数，按笔数降序排列并只取前 20 条。",
        sql="""SELECT pe.from_account_id AS account_id, pe.business_date, COUNT(*) AS txn_count
FROM payment_event pe
WHERE pe.from_account_id IS NOT NULL
GROUP BY pe.from_account_id, pe.business_date
HAVING COUNT(*) >= 3
ORDER BY txn_count DESC, account_id, pe.business_date
LIMIT 20;"""),
    dict(
        id="BRB2-0142", difficulty="extra", features=[],
        question="按机构计算现金支取金额的月度合计，并给出各机构内月度金额最高的月份及其金额，输出机构名称、月份与当月现金支取金额，按金额降序排列。",
        sql="""WITH monthly AS (
    SELECT i.institution_name, substr(pe.business_date, 1, 7) AS month,
           SUM(pe.amount) AS month_amount,
           ROW_NUMBER() OVER (PARTITION BY i.institution_id
                              ORDER BY SUM(pe.amount) DESC, substr(pe.business_date, 1, 7)) AS rn
    FROM payment_event pe
    JOIN account ac ON ac.account_id = COALESCE(pe.from_account_id, pe.to_account_id)
    JOIN institution i ON i.institution_id = ac.institution_id
    JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
    WHERE t.name_zh = '现金支取'
    GROUP BY i.institution_id, i.institution_name, month
)
SELECT institution_name, month, ROUND(month_amount, 2) AS month_amount
FROM monthly WHERE rn = 1
ORDER BY month_amount DESC, institution_name;"""),
    dict(
        id="BRB2-0143", difficulty="hard", features=[],
        question="统计各机构客户中属于敞口集团成员的户数与这些成员在本行的贷款本金余额合计，输出机构名称、集团成员户数与余额合计，按余额合计降序排列。",
        sql="""SELECT i.institution_name, COUNT(DISTINCT egm.party_id) AS member_count,
       ROUND(SUM(lbs.principal_balance), 2) AS total_balance
FROM exposure_group eg
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
JOIN credit_agreement a ON a.borrower_party_id = egm.party_id AND a.institution_id = eg.institution_id
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
JOIN institution i ON i.institution_id = eg.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY total_balance DESC, i.institution_name;"""),
    dict(
        id="BRB2-0144", difficulty="hard", features=[],
        question="找出放款金额与名下支付指令金额合计差异超过 5% 的借据（以放款金额为基准），输出借据编号、放款金额、支付指令金额合计与差异比例，按差异比例降序排列并只取前 20 条。",
        sql="""SELECT ld.loan_id, ld.disbursed_amount, ROUND(SUM(pi.instruction_amount), 2) AS instructed,
       ROUND(ABS(SUM(pi.instruction_amount) - ld.disbursed_amount) * 1.0 / ld.disbursed_amount, 6) AS diff_ratio
FROM loan_drawdown ld
JOIN payment_instruction pi ON pi.loan_id = ld.loan_id
GROUP BY ld.loan_id, ld.disbursed_amount
HAVING ABS(SUM(pi.instruction_amount) - ld.disbursed_amount) * 1.0 / ld.disbursed_amount > 0.05
ORDER BY diff_ratio DESC, ld.loan_id
LIMIT 20;"""),
    dict(
        id="BRB2-0145", difficulty="hard", features=[],
        question="统计各机构理财产品中面向普通投资者发行的产品数量与其实际募集金额合计，输出机构名称、产品数量与募集金额合计，按募集金额合计降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS product_count,
       ROUND(SUM(wp.actual_raise_amount), 2) AS total_raised
FROM wealth_product wp
JOIN institution i ON i.institution_id = wp.issuer_institution_id
WHERE wp.target_investor_type = 'GENERAL'
GROUP BY i.institution_id, i.institution_name
ORDER BY total_raised DESC, i.institution_name;"""),
    dict(
        id="BRB2-0146", difficulty="extra", features=[],
        question="找出同一借款人在同一机构既有受托支付又有自主支付借据的情形，输出客户编号、客户名称、机构名称、受托支付笔数与自主支付笔数，按客户编号升序排列。",
        sql="""SELECT p.party_id, p.display_name, i.institution_name,
       SUM(CASE WHEN ld.payment_mode = 'ENTRUSTED_PAYMENT' THEN 1 ELSE 0 END) AS entrusted,
       SUM(CASE WHEN ld.payment_mode = 'SELF_PAYMENT' THEN 1 ELSE 0 END) AS self_pay
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY p.party_id, p.display_name, i.institution_id, i.institution_name
HAVING SUM(CASE WHEN ld.payment_mode = 'ENTRUSTED_PAYMENT' THEN 1 ELSE 0 END) > 0
   AND SUM(CASE WHEN ld.payment_mode = 'SELF_PAYMENT' THEN 1 ELSE 0 END) > 0
ORDER BY p.party_id;"""),
    dict(
        id="BRB2-0147", difficulty="hard", features=[],
        question="找出担保人同时为多个担保合同提供担保且担保金额合计超过 3 亿元的情形，输出担保人编号、担保人名称、担保合同数量与担保金额合计，按金额合计降序排列。",
        sql="""SELECT gc.guarantor_party_id, p.display_name, COUNT(DISTINCT gc.security_id) AS security_count,
       ROUND(SUM(gc.guaranteed_amount), 2) AS total_guaranteed
FROM guarantor_commitment gc
JOIN party p ON p.party_id = gc.guarantor_party_id
GROUP BY gc.guarantor_party_id, p.display_name
HAVING COUNT(DISTINCT gc.security_id) >= 2 AND SUM(gc.guaranteed_amount) > 300000000
ORDER BY total_guaranteed DESC, gc.guarantor_party_id;"""),
    dict(
        id="BRB2-0148", difficulty="hard", features=[],
        question="统计各机构的贷款客户中个人客户与对公客户的户数占比，输出机构名称、对公客户数、个人客户数与个人客户占比，按个人客户占比降序排列。",
        sql="""SELECT i.institution_name,
       COUNT(DISTINCT CASE WHEN p.party_type = 'CORPORATE' THEN p.party_id END) AS corp_count,
       COUNT(DISTINCT CASE WHEN p.party_type = 'INDIVIDUAL' THEN p.party_id END) AS retail_count,
       ROUND(COUNT(DISTINCT CASE WHEN p.party_type = 'INDIVIDUAL' THEN p.party_id END) * 1.0
             / COUNT(DISTINCT p.party_id), 6) AS retail_ratio
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY retail_ratio DESC, i.institution_name;"""),
    dict(
        id="BRB2-0149", difficulty="extra", features=[],
        question="找出各机构中拨备覆盖率最低的贷款品种，输出机构名称、品种中文名称、已计提拨备合计、计提要求合计与覆盖率，按覆盖率升序排列。",
        sql="""WITH combo AS (
    SELECT i.institution_name, lp.product_name_zh,
           SUM(ps.recognized_amount) AS recognized, SUM(ps.required_amount) AS required,
           ROW_NUMBER() OVER (PARTITION BY i.institution_id
                              ORDER BY SUM(ps.recognized_amount) * 1.0 / SUM(ps.required_amount),
                                       lp.product_name_zh) AS rn
    FROM provision_snapshot ps
    JOIN loan_drawdown ld ON ld.loan_id = ps.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN institution i ON i.institution_id = a.institution_id
    JOIN loan_product_catalog lp ON lp.product_code = ld.drawdown_type
    GROUP BY i.institution_id, i.institution_name, lp.product_code, lp.product_name_zh
)
SELECT institution_name, product_name_zh, ROUND(recognized, 2) AS recognized,
       ROUND(required, 2) AS required_amount,
       ROUND(recognized * 1.0 / required, 6) AS coverage
FROM combo WHERE rn = 1
ORDER BY coverage, institution_name;"""),
    dict(
        id="BRB2-0150", difficulty="extra", features=[],
        question="综合评分：对每家机构统计不良贷款率、拨备覆盖率与资本充足率三项指标，输出机构名称与三项指标，仅保留不良贷款率低于 0.25 且资本充足率高于 0.1 的机构，按不良贷款率升序排列。",
        sql="""WITH npl AS (
    SELECT a.institution_id,
           SUM(CASE WHEN g.is_nonperforming = 1 THEN lbs.principal_balance ELSE 0 END) * 1.0
           / SUM(lbs.principal_balance) AS npl_ratio
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN risk_classification rc ON rc.loan_id = ld.loan_id
    JOIN classification_grade g ON g.grade_code = rc.grade_code
    GROUP BY a.institution_id
), cov AS (
    SELECT a.institution_id, SUM(ps.recognized_amount) * 1.0 / SUM(ps.required_amount) AS coverage
    FROM provision_snapshot ps
    JOIN loan_drawdown ld ON ld.loan_id = ps.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    GROUP BY a.institution_id
)
SELECT i.institution_name, ROUND(npl.npl_ratio, 6) AS npl_ratio,
       ROUND(cov.coverage, 6) AS provision_coverage,
       ROUND(cs.net_capital * 1.0 / cs.risk_weighted_assets, 6) AS capital_adequacy
FROM npl
JOIN cov ON cov.institution_id = npl.institution_id
JOIN capital_snapshot cs ON cs.institution_id = npl.institution_id
JOIN institution i ON i.institution_id = npl.institution_id
WHERE npl.npl_ratio < 0.25
  AND cs.net_capital * 1.0 / cs.risk_weighted_assets > 0.1
ORDER BY npl.npl_ratio, i.institution_name;"""),
    dict(
        id="BRB2-0151", difficulty="easy", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第二十四条、第二十六条；《固定资产贷款管理暂行办法》第二十五条",
        penalty_fact_zh="流动资金贷款受托支付要求未落实，规避受托支付审查",
        question="统计各机构采用受托支付方式且当前仍有效的借据笔数，输出机构名称与借据笔数，按借据笔数降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS cnt
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE ld.payment_mode = 'ENTRUSTED_PAYMENT' AND ld.status = 'ACTIVE'
GROUP BY i.institution_id, i.institution_name
ORDER BY cnt DESC, i.institution_name;"""),
    dict(
        id="BRB2-0152", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第二十七条、第三十条；《商业银行授信工作尽职指引》第四十一条",
        penalty_fact_zh="受托支付资金划付管理不到位，放款与支付指令脱节",
        question="找出放款金额大于其名下当期支付指令金额合计的借据（放款金额未被足额指令覆盖，疑似受托支付管控缺失），输出借据编号、放款金额、支付指令合计与差额，按差额降序排列。",
        sql="""SELECT ld.loan_id, ld.disbursed_amount,
       ROUND(SUM(pi.instruction_amount), 2) AS instructed,
       ROUND(ld.disbursed_amount - SUM(pi.instruction_amount), 2) AS gap
FROM loan_drawdown ld
JOIN payment_instruction pi ON pi.loan_id = ld.loan_id
GROUP BY ld.loan_id, ld.disbursed_amount
HAVING SUM(pi.instruction_amount) < ld.disbursed_amount
ORDER BY gap DESC, ld.loan_id;"""),
    dict(
        id="BRB2-0153", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第三十条、第三十二条；《个人贷款管理暂行办法》第三十五条",
        penalty_fact_zh="贷后跟踪检查缺失，逾期贷款未及时发现处置",
        question="统计各机构贷款余额快照中截至审计基准日（2026-06-30）自逾期起始日起算已满九十天的借据笔数，输出机构名称与借据笔数，按笔数降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS cnt
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE julianday('2026-06-30') - julianday(lbs.overdue_since) >= 90
GROUP BY i.institution_id, i.institution_name
ORDER BY cnt DESC, i.institution_name;"""),
    dict(
        id="BRB2-0154", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、第二十四条；《固定资产贷款管理暂行办法》第七条",
        penalty_fact_zh="受托支付资金回流借款人，贷款未按约定用途使用",
        question="找出采用受托支付方式、而支付指令收款方与借款方为同一主体的放款借据（受托资金疑似回流借款人），输出借据编号、借款方名称、指令金额与收款方名称，按指令金额降序排列，只取前两百条。",
        sql="""SELECT ld.loan_id, pb.display_name AS borrower, pi.instruction_amount,
       pp.display_name AS payee
FROM payment_instruction pi
JOIN loan_drawdown ld ON ld.loan_id = pi.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party pb ON pb.party_id = a.borrower_party_id
JOIN party pp ON pp.party_id = pi.intended_payee_party_id
WHERE pi.payment_mode = 'ENTRUSTED_PAYMENT'
  AND pi.intended_payee_party_id = a.borrower_party_id
ORDER BY pi.instruction_amount DESC, pi.instruction_id
LIMIT 200;"""),
    dict(
        id="BRB2-0155", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第二十四条、第二十五条；《个人贷款管理暂行办法》第二十九条",
        penalty_fact_zh="受托支付金额标准执行不审慎",
        question="统计各机构受托支付指令的平均金额与指令笔数，输出机构名称、平均金额与笔数，按平均金额降序排列。",
        sql="""SELECT i.institution_name,
       ROUND(AVG(pi.instruction_amount), 2) AS avg_amt,
       COUNT(*) AS cnt
FROM payment_instruction pi
JOIN loan_drawdown ld ON ld.loan_id = pi.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE pi.payment_mode = 'ENTRUSTED_PAYMENT'
GROUP BY i.institution_id, i.institution_name
ORDER BY avg_amt DESC, i.institution_name;"""),
    dict(
        id="BRB2-0156", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第十五条、第十六条；《商业银行法》第三十五条",
        penalty_fact_zh="贷前调查不尽职，向资质异常客户继续放款",
        question="找出向主体状态为冻结的对公客户发放、且授信仍生效的合同，输出合同编号、借款方名称与合同金额，按合同金额降序排列。",
        sql="""SELECT a.agreement_id, p.display_name, a.contract_amount
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
WHERE p.party_type = 'CORPORATE' AND p.status = 'FROZEN' AND a.status = 'ACTIVE'
ORDER BY a.contract_amount DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0157", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第二十条及相关授信集中度管理要求：授信额度为对该户核定之最高限额，任一时点融资余额不得突破核定额度。",
        penalty_fact_zh="检测发现存在授信额度项下多份合同签约金额合计超过核定额度的超限签约情形，形成越权超限额授信敞口。",
        question="在授信管理中，同一授信额度下多份授信合同的签约金额合计不得超过核定授信额度，超限签约属违规。输出授信额度编号、授信主体名称、授信类型、核定授信额度、累计签约金额，仅列出累计签约金额大于核定授信额度的记录，按累计签约金额降序排列，再按授信额度编号升序排列。",
        sql="""SELECT f.facility_id, p.display_name, f.facility_type,
       ROUND(f.limit_amount,2) AS limit_amount,
       ROUND(SUM(a.contract_amount),2) AS signed_total
FROM credit_agreement a
JOIN credit_facility f ON f.facility_id=a.facility_id
JOIN party p ON p.party_id=f.obligor_party_id
GROUP BY f.facility_id, p.display_name, f.facility_type, f.limit_amount
HAVING SUM(a.contract_amount) > f.limit_amount
ORDER BY signed_total DESC, f.facility_id;"""),
    dict(
        id="BRB2-0158", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第四十一条；《贷款通则》第三十一条",
        penalty_fact_zh="贷后监控与催收不力，逾期本息持续攀升",
        question="针对由至少两名不同客户共同持有的有效状态人民币存款账户，按账户种类统计联名账户数量及关联持有人总人次，仅保留联名账户数量超过一百个的账户种类，输出账户种类、联名账户数量与关联持有人总人次，按联名账户数量降序、账户种类升序排列。",
        sql="""WITH multi_holders AS (
  SELECT account_id, COUNT(DISTINCT party_id) AS holder_cnt
  FROM account_holder
  GROUP BY account_id
  HAVING COUNT(DISTINCT party_id) >= 2
)
SELECT a.account_kind,
       COUNT(*) AS joint_accts,
       SUM(m.holder_cnt) AS total_holder_links
FROM account a
JOIN multi_holders m ON m.account_id = a.account_id
WHERE a.status = 'ACTIVE'
  AND a.currency_code = 'CNY'
GROUP BY a.account_kind
HAVING COUNT(*) > 100
ORDER BY joint_accts DESC, a.account_kind;"""),
    dict(
        id="BRB2-0159", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第二十七条；《固定资产贷款管理暂行办法》第二十六条",
        penalty_fact_zh="受托支付审核不严，支付金额超出合同约定用途",
        question="找出采用受托支付、且支付指令金额合计超过授信合同金额的借据（受托支付金额超出合同约定），输出借据编号、合同金额、支付指令合计与超出金额，按超出金额降序排列，只取前两百条。",
        sql="""SELECT ld.loan_id, a.contract_amount,
       ROUND(SUM(pi.instruction_amount), 2) AS paid,
       ROUND(SUM(pi.instruction_amount) - a.contract_amount, 2) AS exceed
FROM loan_drawdown ld
JOIN payment_instruction pi ON pi.loan_id = ld.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
WHERE ld.payment_mode = 'ENTRUSTED_PAYMENT'
GROUP BY ld.loan_id, a.agreement_id, a.contract_amount
HAVING SUM(pi.instruction_amount) > a.contract_amount
ORDER BY exceed DESC, ld.loan_id
LIMIT 200;"""),
    dict(
        id="BRB2-0160", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条；《固定资产贷款管理暂行办法》第三十五条第(四)项",
        penalty_fact_zh="流动资金贷款违规投向禁止经营与退出类领域",
        question="找出产品类型为流动资金类且投向行业属于退出类的借据（流动资金被禁用于禁止经营领域），输出借据编号、产品中文名称、投向行业与放款金额，按放款金额降序排列，只取前两百条（借据状态须为正常）。",
        sql="""SELECT ld.loan_id, lpc.product_name_zh, s.sector_name_zh, ld.disbursed_amount
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN loan_product_catalog lpc ON lpc.product_code = ld.drawdown_type
JOIN industry_sector s ON s.sector_code = a.target_industry_code
WHERE lpc.is_working_capital = 1 AND s.risk_category = 'EXIT' AND ld.status = 'ACTIVE'
ORDER BY ld.disbursed_amount DESC, ld.loan_id
LIMIT 200;"""),
    dict(
        id="BRB2-0161", difficulty="medium", features=[],
        penalty_law_zh="《固定资产贷款管理暂行办法》第二十五条、第二十六条；《流动资金贷款管理暂行办法》第二十六条",
        penalty_fact_zh="固定资产贷款违规自主支付，规避受托支付审查",
        question="找出当前仍处于有效状态且采用自主支付方式的固定资产贷款借据，输出借据编号、放款金额与支付方式，按放款金额降序排列，只取前两百条。",
        sql="""SELECT ld.loan_id, ld.disbursed_amount, ld.payment_mode
FROM loan_drawdown ld
WHERE ld.payment_mode = 'SELF_PAYMENT' AND ld.drawdown_type = 'FIXED_ASSET'
  AND ld.status = 'ACTIVE'
ORDER BY ld.disbursed_amount DESC, ld.loan_id
LIMIT 200;"""),
    dict(
        id="BRB2-0162", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第三十条；《商业银行授信工作尽职指引》第四十一条",
        penalty_fact_zh="放款与资金支付管理脱节，信贷资金去向失管",
        question="统计各机构放款金额合计与支付指令金额合计的差异（放款合计减指令合计），输出机构名称与差异额，按差异额降序排列。",
        sql="""WITH pi_tot AS (
    SELECT loan_id, SUM(instruction_amount) AS instr_amt
    FROM payment_instruction
    GROUP BY loan_id
)
SELECT i.institution_name,
       ROUND(SUM(ld.disbursed_amount) - SUM(pi_tot.instr_amt), 2) AS gap
FROM loan_drawdown ld
JOIN pi_tot ON pi_tot.loan_id = ld.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY gap DESC, i.institution_name;"""),
    dict(
        id="BRB2-0163", difficulty="easy", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第二十七条；《固定资产贷款管理暂行办法》第二十六条",
        penalty_fact_zh="受托支付指令积压未及时办理",
        question="统计各机构处于待处理状态且采用受托支付的支付指令笔数，输出机构名称与笔数，按笔数降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS cnt
FROM payment_instruction pi
JOIN loan_drawdown ld ON ld.loan_id = pi.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE pi.status = 'PENDING' AND pi.payment_mode = 'ENTRUSTED_PAYMENT'
GROUP BY i.institution_id, i.institution_name
ORDER BY cnt DESC, i.institution_name;"""),
    dict(
        id="BRB2-0164", difficulty="extra", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第三十条；《个人贷款管理暂行办法》第三十二条",
        penalty_fact_zh="信贷资金支付与用途监控机制不健全",
        question="计算各机构名下每笔借据支付偏差率的平均水平（偏差率以放款金额为基准，为支付指令合计与放款金额之差的绝对值占放款金额的比例），输出机构名称与平均偏差率，按平均偏差率降序排列。",
        sql="""WITH dev AS (
    SELECT i.institution_id, i.institution_name, ld.loan_id, ld.disbursed_amount,
           SUM(pi.instruction_amount) AS paid
    FROM loan_drawdown ld
    JOIN payment_instruction pi ON pi.loan_id = ld.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN institution i ON i.institution_id = a.institution_id
    GROUP BY i.institution_id, i.institution_name, ld.loan_id, ld.disbursed_amount
)
SELECT institution_name,
       ROUND(AVG(ABS(paid - disbursed_amount) * 1.0 / disbursed_amount), 6) AS avg_dev
FROM dev
GROUP BY institution_id, institution_name
ORDER BY avg_dev DESC, institution_name;"""),
    dict(
        id="BRB2-0165", difficulty="medium", features=[],
        penalty_law_zh="《商业银行法》第四十条、第七十四条第(八)项；《金融违法行为处罚办法》第十六条第(一)项",
        penalty_fact_zh="向关系人违规发放信用贷款",
        question="找出向关系人发放的担保方式为信用的合同（不得向关系人发放信用贷款），输出合同编号、借款方名称与合同金额，按合同金额降序排列。",
        sql="""SELECT a.agreement_id, p.display_name, a.contract_amount
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
WHERE a.security_type = 'CREDIT'
  AND EXISTS (
      SELECT 1 FROM party_relation pr
      JOIN relation_type_catalog rt ON rt.relation_type = pr.relation_type
      WHERE pr.source_party_id = a.borrower_party_id
        AND rt.relation_name_zh <> '非关联方'
  )
ORDER BY a.contract_amount DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0166", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》及《商业银行授信工作尽职指引》：一次性（非循环）授信不得重复提款，签约与提款合计不得超过核定额度。",
        penalty_fact_zh="检测发现一次性授信额度项下签约金额超出核定额度，且通过倍率评估确认越权放大，属超限额授信风险。",
        question="对一次性（非循环）授信，核定额度内签约金额超出限度的倍率越高、越权越严重。输出授信额度编号、授信类型、核定授信额度、累计签约金额、签约超限倍率（签约合计除以核定额度），仅列出授信类型为一次性授信且签约金额超过核定额度的记录，按签约超限倍率降序排列，再按授信额度编号升序排列。",
        sql="""WITH agg AS (
  SELECT a.facility_id, SUM(a.contract_amount) AS tot
  FROM credit_agreement a GROUP BY a.facility_id
)
SELECT f.facility_id, f.facility_type, ROUND(f.limit_amount,2) AS limit_amount,
       ROUND(agg.tot,2) AS signed_total,
       ROUND(agg.tot * 1.0 / f.limit_amount, 4) AS over_ratio
FROM agg JOIN credit_facility f ON f.facility_id=agg.facility_id
WHERE f.facility_type='TERM' AND agg.tot > f.limit_amount
ORDER BY over_ratio DESC, f.facility_id;"""),
    dict(
        id="BRB2-0167", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第十四条；《商业银行与内部人和股东关联交易管理办法》第二十五条",
        penalty_fact_zh="关系人授信过度集中、约束不审慎",
        question="计算各对公客户中属于关联关系的客户（作为关联关系中任一方）的授信合同金额合计，只保留合计超过五亿元的客户，输出客户编号、客户名称与合同金额合计，按合计降序排列，取前十名。",
        sql="""SELECT p.party_id, p.display_name, ROUND(SUM(a.contract_amount), 2) AS tot
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
WHERE EXISTS (
    SELECT 1 FROM party_relation pr
    JOIN relation_type_catalog rt ON rt.relation_type = pr.relation_type
    WHERE (pr.source_party_id = a.borrower_party_id OR pr.target_party_id = a.borrower_party_id)
      AND rt.relation_name_zh <> '非关联方'
)
GROUP BY p.party_id, p.display_name
HAVING SUM(a.contract_amount) > 500000000
ORDER BY tot DESC, p.party_id
LIMIT 10;"""),
    dict(
        id="BRB2-0168", difficulty="hard", features=[],
        penalty_law_zh="《商业银行法》第四十条；《商业银行与内部人和股东关联交易管理办法》第二十五条",
        penalty_fact_zh="借助关联方转移信贷资金，规避受托支付管控",
        question="找出受托支付指令中收款方与借款方存在非‘非关联方’关系的指令（疑似通过关联方转移信贷资金），输出借据编号、借款方名称、收款方名称与指令金额，按指令金额降序排列，取前两百条。",
        sql="""SELECT ld.loan_id, pb.display_name AS borrower, pp.display_name AS payee,
       pi.instruction_amount
FROM payment_instruction pi
JOIN loan_drawdown ld ON ld.loan_id = pi.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party pb ON pb.party_id = a.borrower_party_id
JOIN party pp ON pp.party_id = pi.intended_payee_party_id
WHERE EXISTS (
    SELECT 1 FROM party_relation pr
    WHERE pr.relation_type <> 'NON_RELATED'
      AND ((pr.source_party_id = a.borrower_party_id AND pr.target_party_id = pi.intended_payee_party_id)
        OR (pr.source_party_id = pi.intended_payee_party_id AND pr.target_party_id = a.borrower_party_id))
)
ORDER BY pi.instruction_amount DESC, pi.instruction_id
LIMIT 200;"""),
    dict(
        id="BRB2-0169", difficulty="medium", features=[],
        penalty_law_zh="《固定资产贷款管理暂行办法》第二十八条及《流动资金贷款管理暂行办法》第二十六条：固定资产/流动资金贷款应一次性实贷实付，非循环授信不得拆分贷款。",
        penalty_fact_zh="检测发现非循环授信同一合同下被拆分为多笔借据反复提款，涉嫌化整为零规避受托支付管理与超额度提款。",
        question="一次性（非循环）授信只能一次性提款，同一授信合同下多笔放款借据涉嫌化整为零或重复提款。输出授信合同编号、授信类型、借据笔数、累计放款金额，仅列出授信类型不属于循环授信且同一合同下借据笔数大于等于3的记录，按借据笔数降序排列，再按授信合同编号升序排列。",
        sql="""SELECT a.agreement_id, f.facility_type,
       COUNT(DISTINCT d.loan_id) AS drawdown_cnt,
       ROUND(SUM(d.disbursed_amount),2) AS total_disbursed
FROM credit_agreement a
JOIN credit_facility f ON f.facility_id=a.facility_id
JOIN loan_drawdown d ON d.agreement_id=a.agreement_id
WHERE f.facility_type <> 'REVOLVING'
GROUP BY a.agreement_id, f.facility_type
HAVING COUNT(DISTINCT d.loan_id) >= 3
ORDER BY drawdown_cnt DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0170", difficulty="hard", features=[],
        penalty_law_zh="《个人贷款管理暂行办法》第二十七条、《流动资金贷款管理暂行办法》第二十六条：符合受托支付条件的贷款应受托支付，不得以自主支付变相规避。",
        penalty_fact_zh="检测发现约定受托支付的授信合同实际操作中采用自主支付放款，未落实受托支付监管要求，形成化整为零规避受托支付。",
        question="应执行受托支付的授信合同在实际放款中却采用自主支付，属未落实受托支付监管要求的违规。输出授信合同编号、借款人名称、合同金额、自主支付借据笔数、累计自主支付金额，仅列出约定受托支付但实际放款采用自主支付的记录，按累计自主支付金额降序排列，再按授信合同编号升序排列。",
        sql="""SELECT a.agreement_id, p.display_name, ROUND(a.contract_amount,2) AS contract_amount,
       COUNT(DISTINCT ld.loan_id) AS self_pay_cnt,
       ROUND(SUM(ld.disbursed_amount),2) AS self_pay_amount
FROM credit_agreement a
JOIN loan_drawdown ld ON ld.agreement_id=a.agreement_id
JOIN party p ON p.party_id=a.borrower_party_id
WHERE a.payment_mode='ENTRUSTED_PAYMENT' AND ld.payment_mode='SELF_PAYMENT'
GROUP BY a.agreement_id, p.display_name, a.contract_amount
ORDER BY self_pay_amount DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0171", difficulty="hard", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》第四条、第二十五条",
        penalty_fact_zh="关联关系识别与名单管理不完善",
        question="找出本金余额高出其放款机构平均贷款余额两倍以上的借据，输出机构名称、借据编号、本金余额、机构平均余额与超出差额，按差额降序排列。",
        sql="""SELECT i.institution_name, ld.loan_id,
       ROUND(lbs.principal_balance,2) AS bal,
       ROUND((SELECT AVG(x.principal_balance) FROM loan_balance_snapshot x JOIN loan_drawdown d2 ON d2.loan_id=x.loan_id JOIN credit_agreement a2 ON a2.agreement_id=d2.agreement_id WHERE a2.institution_id=a.institution_id),2) AS inst_avg,
       ROUND(lbs.principal_balance - (SELECT AVG(x.principal_balance) FROM loan_balance_snapshot x JOIN loan_drawdown d2 ON d2.loan_id=x.loan_id JOIN credit_agreement a2 ON a2.agreement_id=d2.agreement_id WHERE a2.institution_id=a.institution_id),2) AS gap
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id=lbs.loan_id
JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
JOIN institution i ON i.institution_id=a.institution_id
WHERE lbs.principal_balance > 2*(SELECT AVG(x.principal_balance) FROM loan_balance_snapshot x JOIN loan_drawdown d2 ON d2.loan_id=x.loan_id JOIN credit_agreement a2 ON a2.agreement_id=d2.agreement_id WHERE a2.institution_id=a.institution_id)
ORDER BY gap DESC, ld.loan_id;"""),
    dict(
        id="BRB2-0172", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第十四条；《商业银行与内部人和股东关联交易管理办法》第十三条",
        penalty_fact_zh="关系人授信审批与集中度管控不到位",
        question="找出授信额度池中向关联关系客户开立且仍生效的授信额度，输出客户编号、客户名称与额度金额，按额度金额降序排列，只取前两百条。",
        sql="""SELECT p.party_id, p.display_name, cf.limit_amount
FROM credit_facility cf
JOIN party p ON p.party_id = cf.obligor_party_id
WHERE cf.status = 'ACTIVE' AND EXISTS (
    SELECT 1 FROM party_relation pr
    JOIN relation_type_catalog rt ON rt.relation_type = pr.relation_type
    WHERE (pr.source_party_id = cf.obligor_party_id OR pr.target_party_id = cf.obligor_party_id)
      AND rt.relation_name_zh <> '非关联方'
)
ORDER BY cf.limit_amount DESC, cf.facility_id
LIMIT 200;"""),
    dict(
        id="BRB2-0173", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第十四条；《商业银行与内部人和股东关联交易管理办法》第二十五条",
        penalty_fact_zh="未有效识别并单独管控关联客户授信",
        question="统计各机构非关联客户（不存在非‘非关联方’关联关系）授信合同金额占该机构全部授信合同金额的比重，输出机构名称、非关联金额、全部金额与占比，按占比降序排列（关联关系以客户作为关联发起方的记录为准）。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(CASE WHEN NOT EXISTS (
           SELECT 1 FROM party_relation pr
           WHERE pr.source_party_id = a.borrower_party_id AND pr.relation_type <> 'NON_RELATED'
       ) THEN a.contract_amount ELSE 0 END), 2) AS nonrel_amt,
       ROUND(SUM(a.contract_amount), 2) AS total_amt,
       ROUND(SUM(CASE WHEN NOT EXISTS (
           SELECT 1 FROM party_relation pr
           WHERE pr.source_party_id = a.borrower_party_id AND pr.relation_type <> 'NON_RELATED'
       ) THEN a.contract_amount ELSE 0 END) * 1.0 / SUM(a.contract_amount), 6) AS ratio
FROM credit_agreement a
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY ratio DESC, i.institution_name;"""),
    dict(
        id="BRB2-0174", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》及《商业银行授信工作尽职指引》：不得通过借新还旧、循环融资掩盖借款人风险，新增授信应评估实际偿债能力。",
        penalty_fact_zh="检测发现同一借款人在上一笔授信到期后短期内连续新签授信，间隔异常，涉嫌借新还旧掩盖违约或规避风险分类。",
        question="同一借款人按合同签署日期先后顺序排列的相邻两笔授信合同中，后一笔合同签署日早于上一笔合同到期日（即在旧合同尚未到期前又叠加签署新授信合同，形成存续期重叠的多头授信）。输出借款人名称、新授信合同编号、新合同签署日期、上一笔合同到期日与两日期之差（新合同签署日减上一笔合同到期日的天数，为负值表示提前叠加天数），仅列出新合同签署日早于上一笔合同到期日的记录，按天数差升序、新授信合同编号升序排列，只取前三百条。",
        sql="""WITH hist AS (
  SELECT a.borrower_party_id, a.agreement_id, a.signed_on, a.maturity_on,
         LAG(a.maturity_on) OVER (PARTITION BY a.borrower_party_id ORDER BY a.signed_on, a.agreement_id) AS prev_maturity
  FROM credit_agreement a
)
SELECT p.display_name, h.agreement_id, h.signed_on, h.prev_maturity,
       CAST(julianday(h.signed_on) - julianday(h.prev_maturity) AS INTEGER) AS gap_days
FROM hist h
JOIN party p ON p.party_id = h.borrower_party_id
WHERE julianday(h.signed_on) < julianday(h.prev_maturity)
ORDER BY gap_days, h.agreement_id
LIMIT 300;"""),
    dict(
        id="BRB2-0175", difficulty="easy", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》第四条；《商业银行授信工作尽职指引》第十四条",
        penalty_fact_zh="影子股东穿透识别不到位",
        question="列出存在“影子股东”关联关系记录的源主体客户名称、目标主体客户名称与关系中文名称，输出源主体名称、目标主体名称与关系名称，按源主体名称、目标主体名称升序排列。",
        sql="""SELECT p1.display_name AS src_name, p2.display_name AS tgt_name, rt.relation_name_zh
FROM party_relation pr
JOIN party p1 ON p1.party_id = pr.source_party_id
JOIN party p2 ON p2.party_id = pr.target_party_id
JOIN relation_type_catalog rt ON rt.relation_type = pr.relation_type
WHERE rt.relation_name_zh = '影子股东'
ORDER BY src_name, tgt_name;"""),
    dict(
        id="BRB2-0176", difficulty="hard", features=[],
        penalty_law_zh="《商业银行法》第三十九条第(三)项；《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="单一客户授信集中度超监管比例",
        question="计算各对公借款人的贷款本金余额合计占其开办机构资本净额的比重，找出单一客户贷款集中度超过百分之十的记录，输出机构名称、客户名称、余额合计、资本净额与占比，按占比降序排列，只取前两百条。",
        sql="""SELECT i.institution_name, p.display_name,
       ROUND(SUM(lbs.principal_balance), 2) AS bal,
       cs.net_capital,
       ROUND(SUM(lbs.principal_balance) * 1.0 / cs.net_capital, 6) AS ratio
FROM loan_balance_snapshot lbs
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
JOIN institution i ON i.institution_id = a.institution_id
JOIN capital_snapshot cs ON cs.institution_id = i.institution_id
WHERE p.party_type = 'CORPORATE'
GROUP BY i.institution_id, i.institution_name, p.party_id, p.display_name, cs.net_capital
HAVING SUM(lbs.principal_balance) * 1.0 / cs.net_capital > 0.10
ORDER BY ratio DESC, p.party_id
LIMIT 200;"""),
    dict(
        id="BRB2-0177", difficulty="hard", features=[],
        penalty_law_zh="《个人贷款管理暂行办法》第二十七条、《商业银行授信工作尽职指引》：贷款利率定价应遵循市场与风险定价原则，不得畸高或变相转嫁成本。",
        penalty_fact_zh="检测发现部分授信合同执行利率显著高于同目标行业均值，定价偏离异常，涉嫌变相提价或风险识别不足。",
        question="授信定价明显高于同行业（同一目标行业）平均执行利率，涉嫌变相提高融资成本或定价失当。输出授信合同编号、借款人名称、执行年利率、所属目标行业平均利率、较行业平均上浮百分比，仅列出执行利率高于同行业平均利率10%以上的记录，按上浮百分比降序排列，再按授信合同编号升序排列（上浮百分比以百分数表示，例如 12.5 表示上浮 12.5%，保留两位小数）。",
        sql="""WITH ia AS (
  SELECT a.target_industry_code, AVG(a.annual_interest_rate) AS avg_rate
  FROM credit_agreement a GROUP BY a.target_industry_code
)
SELECT a.agreement_id, p.display_name, ROUND(a.annual_interest_rate,4) AS annual_rate,
       ROUND(ia.avg_rate,4) AS industry_avg,
       ROUND(a.annual_interest_rate*100 / ia.avg_rate - 100, 2) AS deviation_pct
FROM credit_agreement a
JOIN ia ON ia.target_industry_code=a.target_industry_code
JOIN party p ON p.party_id=a.borrower_party_id
WHERE a.annual_interest_rate > 1.1 * ia.avg_rate
ORDER BY deviation_pct DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0178", difficulty="hard", features=[],
        penalty_law_zh="《商业银行法》第三十九条第(三)项；《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="单一客户集中度超限户数众多",
        question="统计各机构中贷款本金余额占本机构资本净额超过百分之十的对公客户数量，输出机构名称与超限客户数，按超限客户数降序排列。",
        sql="""WITH bal AS (
    SELECT i.institution_id, i.institution_name, p.party_id, p.display_name,
           SUM(lbs.principal_balance) AS b, cs.net_capital
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN party p ON p.party_id = a.borrower_party_id
    JOIN institution i ON i.institution_id = a.institution_id
    JOIN capital_snapshot cs ON cs.institution_id = i.institution_id
    WHERE p.party_type = 'CORPORATE'
    GROUP BY i.institution_id, i.institution_name, p.party_id, p.display_name, cs.net_capital
)
SELECT institution_name, COUNT(*) AS cnt
FROM bal
WHERE b * 1.0 / net_capital > 0.10
GROUP BY institution_id, institution_name
ORDER BY cnt DESC, institution_name;"""),
    dict(
        id="BRB2-0179", difficulty="hard", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第十二条；《商业银行法》第三十九条",
        penalty_fact_zh="集团客户授信集中度超过规定比例",
        question="找出集团客户授信集中度超过监管上限（按资本净额百分之十计）的敞口集团，输出集团编号、集团名称、余额合计、资本净额与占比，按占比降序排列（资本净额取集团主办机构的资本净额，仅统计该主办机构自身签署的授信合同项下借据）。",
        sql="""SELECT eg.exposure_group_id, eg.group_name,
       ROUND(SUM(lbs.principal_balance), 2) AS bal,
       cs.net_capital,
       ROUND(SUM(lbs.principal_balance) * 1.0 / cs.net_capital, 6) AS ratio
FROM exposure_group eg
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
JOIN credit_agreement a ON a.borrower_party_id = egm.party_id AND a.institution_id = eg.institution_id
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
JOIN capital_snapshot cs ON cs.institution_id = eg.institution_id
WHERE eg.group_type = 'GROUP_CUSTOMER'
GROUP BY eg.exposure_group_id, eg.group_name, cs.net_capital
HAVING SUM(lbs.principal_balance) * 1.0 / cs.net_capital > 0.10
ORDER BY ratio DESC, eg.exposure_group_id;"""),
    dict(
        id="BRB2-0180", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》及流动资金/固定资产贷款管理办法：授信合同到期后应及时回收或按程序展期确权，不得长期维持正常而掩盖风险。",
        penalty_fact_zh="检测发现授信合同已到期但其项下借据仍登记为正常状态，到期贷款未确权，涉嫌掩盖逾期或不规范展期。",
        question="授信合同状态已标记为到期但其项下放款借据状态仍登记为正常未结清，反映合同状态与借据生命周期状态脱节。输出授信合同编号、合同到期日、未结清借据编号、借据状态与合同金额，仅列出授信合同状态为已到期且借据状态为正常的记录，按借据编号升序排列。",
        sql="""SELECT a.agreement_id, a.maturity_on, ldp.loan_id, ldp.status,
       ROUND(a.contract_amount,2) AS contract_amount
FROM credit_agreement a
JOIN loan_drawdown ldp ON ldp.agreement_id=a.agreement_id
WHERE a.status='MATURED' AND ldp.status='ACTIVE'
ORDER BY ldp.loan_id;"""),
    dict(
        id="BRB2-0181", difficulty="hard", features=[],
        penalty_law_zh="《商业银行法》第三十九条第(三)项；《商业银行授信工作尽职指引》第十四条",
        penalty_fact_zh="授信集中度事前计量与限额管理缺失",
        question="计算各授信额度中单一借款主体的授信额度金额占其开办机构资本净额的比例，找出超过百分之十的额度记录，输出额度编号、客户名称、额度金额、资本净额与占比，按占比降序排列，只取前两百条。",
        sql="""SELECT cf.facility_id, p.display_name, cf.limit_amount, cs.net_capital,
       ROUND(cf.limit_amount * 1.0 / cs.net_capital, 6) AS ratio
FROM credit_facility cf
JOIN party p ON p.party_id = cf.obligor_party_id
JOIN institution i ON i.institution_id = cf.institution_id
JOIN capital_snapshot cs ON cs.institution_id = cf.institution_id
WHERE cf.limit_amount * 1.0 / cs.net_capital > 0.10
ORDER BY ratio DESC, cf.facility_id
LIMIT 200;"""),
    dict(
        id="BRB2-0182", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第十四条；《商业银行与内部人和股东关联交易管理办法》第二十五条",
        penalty_fact_zh="关联客户集团授信集中度超标",
        question="找出关联客户型敞口集团中集团成员贷款余额合计占其净资本超过监管上限（按资本净额百分之十五计）的集团，输出机构名称、集团名称、余额合计、成员数、资本净额与占比，按占比降序排列。",
        sql="""SELECT i.institution_name, eg.group_name,
       ROUND(SUM(lbs.principal_balance), 2) AS bal,
       COUNT(DISTINCT egm.party_id) AS members,
       cs.net_capital,
       ROUND(SUM(lbs.principal_balance) * 1.0 / cs.net_capital, 6) AS ratio
FROM exposure_group eg
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
JOIN credit_agreement a ON a.borrower_party_id = egm.party_id AND a.institution_id = eg.institution_id
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
JOIN capital_snapshot cs ON cs.institution_id = eg.institution_id
JOIN institution i ON i.institution_id = eg.institution_id
WHERE eg.group_type = 'CONNECTED_CUSTOMER'
GROUP BY i.institution_id, i.institution_name, eg.exposure_group_id, eg.group_name, cs.net_capital
HAVING SUM(lbs.principal_balance) * 1.0 / cs.net_capital > 0.15
ORDER BY ratio DESC, i.institution_name, eg.group_name;"""),
    dict(
        id="BRB2-0183", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第二十六条及《商业银行授信工作尽职指引》：贷款发放应监督资金投向约定用途，不得挪用或回流。",
        penalty_fact_zh="检测发现贷款发放账户在放款后短期内发生资金转出，资金去向需穿透核查，涉嫌挪用或回流关联方。",
        question="贷款发放账户在放款后短期内即有大额资金转出，涉嫌放款资金被挪用或回流入关联方。输出借据编号、发放账户编号、放款日期、转账流水号、转账日期、转账金额、放款至转出的间隔天数，仅列出发放账户在放款后7天内发生转账的记录，按间隔天数升序、转账金额降序、再按借据编号升序排列（转账流水须为已结算状态）。",
        sql="""SELECT ld.loan_id, ld.disbursement_account_id, ld.disbursed_on, pe.payment_id,
       pe.business_date, ROUND(pe.amount,2) AS transferred,
       CAST(julianday(pe.business_date)-julianday(ld.disbursed_on) AS INTEGER) AS days_lapse
FROM loan_drawdown ld
JOIN payment_event pe ON pe.from_account_id=ld.disbursement_account_id
WHERE pe.payment_type='TRANSFER' AND pe.status='SETTLED'
  AND julianday(pe.business_date)-julianday(ld.disbursed_on) BETWEEN 0 AND 7
ORDER BY days_lapse, transferred DESC, ld.loan_id;"""),
    dict(
        id="BRB2-0184", difficulty="extra", features=[],
        penalty_law_zh="《商业银行法》第三十九条；《商业银行授信工作尽职指引》第十四条",
        penalty_fact_zh="单一客户集中度最高户未重点管控",
        question="找出各机构中贷款本金余额占本机构资本净额比重最高的对公客户，每家机构各取第一名，输出机构名称、客户名称与占比，按机构名称升序排列。",
        sql="""WITH co AS (
    SELECT i.institution_id, i.institution_name, p.party_id, p.display_name,
           SUM(lbs.principal_balance) * 1.0 / cs.net_capital AS ratio
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    JOIN party p ON p.party_id = a.borrower_party_id
    JOIN institution i ON i.institution_id = a.institution_id
    JOIN capital_snapshot cs ON cs.institution_id = i.institution_id
    WHERE p.party_type = 'CORPORATE'
    GROUP BY i.institution_id, i.institution_name, p.party_id, p.display_name, cs.net_capital
), rk AS (
    SELECT institution_name, display_name, ratio,
           ROW_NUMBER() OVER (PARTITION BY institution_id ORDER BY ratio DESC) AS rn
    FROM co
)
SELECT institution_name, display_name, ROUND(ratio, 6) AS ratio
FROM rk
WHERE rn = 1
ORDER BY institution_name;"""),
    dict(
        id="BRB2-0185", difficulty="easy", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条；《固定资产贷款管理暂行办法》第三十五条",
        penalty_fact_zh="向退出类行业违规发放授信",
        question="列出资金投向属于退出类行业且授信仍生效的合同，输出合同编号、借款方名称、投向行业与合同金额，按合同金额降序排列。",
        sql="""SELECT a.agreement_id, p.display_name, s.sector_name_zh, a.contract_amount
FROM credit_agreement a
JOIN industry_sector s ON s.sector_code = a.target_industry_code
JOIN party p ON p.party_id = a.borrower_party_id
WHERE s.risk_category = 'EXIT' AND a.status = 'ACTIVE'
ORDER BY a.contract_amount DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0186", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第三十五条；《流动资金贷款管理暂行办法》第九条",
        penalty_fact_zh="向退出类行业客户违规授信",
        question="按机构与客户注册行业统计向退出类行业企业（组织画像中注册行业风险类别为退出类）发放的授信合同金额合计，输出机构名称、行业名称与合同金额合计，按金额合计降序排列。",
        sql="""SELECT i.institution_name, s.sector_name_zh, ROUND(SUM(a.contract_amount), 2) AS amt
FROM credit_agreement a
JOIN institution i ON i.institution_id = a.institution_id
JOIN organization_profile op ON op.party_id = a.borrower_party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
WHERE s.risk_category = 'EXIT'
GROUP BY i.institution_id, i.institution_name, s.sector_code, s.sector_name_zh
ORDER BY amt DESC, i.institution_name, s.sector_name_zh;"""),
    dict(
        id="BRB2-0187", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第三十五条；《固定资产贷款管理暂行办法》第九条第(六)项",
        penalty_fact_zh="限制退出类行业授信占比异常偏高",
        question="按授信产品线统计合同总量与其中以抵押担保方式发放的合同数量，并计算抵押式合同占比，仅保留占比低于百分之十九的产品线，输出产品线、合同总量与抵押式合同数量，按合同总量降序、产品线升序排列。",
        sql="""SELECT ca.product_family,
       COUNT(DISTINCT ca.agreement_id) AS total_agr,
       COUNT(DISTINCT CASE WHEN ca.security_type = 'MORTGAGE' THEN ca.agreement_id END) AS secured_agr
FROM credit_agreement ca
JOIN credit_facility cf ON cf.facility_id = ca.facility_id
JOIN institution i ON i.institution_id = ca.institution_id
GROUP BY ca.product_family
HAVING (100.0 * COUNT(DISTINCT CASE WHEN ca.security_type = 'MORTGAGE' THEN ca.agreement_id END) / COUNT(DISTINCT ca.agreement_id)) < 19.0
ORDER BY total_agr DESC, ca.product_family;"""),
    dict(
        id="BRB2-0188", difficulty="medium", features=[],
        penalty_law_zh="《商业银行房地产贷款风险管理指引》；《商业银行法》第三十四条",
        penalty_fact_zh="房地产限制类行业授信管控不审慎",
        question="在每家机构内部按本金余额从高到低将借据等分为四档，输出借据编号、本金余额与档位，按档位升序、余额降序排列，只取前三百条。",
        sql="""SELECT loan_id, principal_balance, quartile FROM (
    SELECT lbs.loan_id, ROUND(lbs.principal_balance,2) AS principal_balance,
           NTILE(4) OVER (PARTITION BY a.institution_id ORDER BY lbs.principal_balance DESC) AS quartile
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id=lbs.loan_id
    JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
)
ORDER BY quartile ASC, principal_balance DESC
LIMIT 300;"""),
    dict(
        id="BRB2-0189", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》及贷款五级分类办法：逾期状况应如实反映并计提，不得以还息不还本或挂账方式掩盖违约事实。",
        penalty_fact_zh="检测发现既存在逾期分期又未在期末余额中确认逾期本金，涉嫌通过只收息不收本或台账调整掩盖真实逾期。",
        question="借据存在逾期分期但期末余额中逾期本金仍为零，即逾期只挂账不确认、只收息不提逾期本金，涉嫌掩盖违约。输出借据编号、应还逾期本金合计、期末账载逾期本金、逾期期次数，仅列出存在逾期分期但期末账载逾期本金为零的记录，按应还逾期本金合计降序排列，再按借据编号升序排列。",
        sql="""SELECT rs.loan_id, ROUND(SUM(rs.principal_due),2) AS overdue_principal_due,
       ROUND(MAX(lb.overdue_principal),2) AS reported_overdue,
       COUNT(*) AS overdue_installments
FROM repayment_schedule rs
JOIN loan_balance_snapshot lb ON lb.loan_id=rs.loan_id
WHERE rs.status='OVERDUE'
GROUP BY rs.loan_id
HAVING MAX(lb.overdue_principal) = 0
ORDER BY overdue_principal_due DESC, rs.loan_id;"""),
    dict(
        id="BRB2-0190", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第三十五条；《流动资金贷款管理暂行办法》第九条",
        penalty_fact_zh="向退出类行业客户发放授信",
        question="列出注册行业属于退出类且获得授信的对公客户，输出客户编号、客户名称与所在行业名称，按行业名称、客户编号升序排列。",
        sql="""SELECT p.party_id, p.display_name, s.sector_name_zh
FROM party p
JOIN organization_profile op ON op.party_id = p.party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
JOIN credit_agreement a ON a.borrower_party_id = p.party_id
WHERE s.risk_category = 'EXIT'
GROUP BY p.party_id, p.display_name, s.sector_code, s.sector_name_zh
ORDER BY s.sector_name_zh, p.party_id;"""),
    dict(
        id="BRB2-0191", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条；《固定资产贷款管理暂行办法》第六条",
        penalty_fact_zh="退出类行业在贷余额未压缩退出",
        question="列出属于贵宾或大型客户群且名下不存在任何关联关系记录的有效客户，输出客户编号与客户分群，按客户分群升序、客户编号升序排列。",
        sql="""SELECT p.party_id,
       p.customer_segment
FROM party p
WHERE p.customer_segment IN ('AFFLUENT','LARGE')
  AND p.status = 'ACTIVE'
  AND NOT EXISTS (
    SELECT 1 FROM party_relation pr
    WHERE pr.source_party_id = p.party_id
  )
ORDER BY p.customer_segment, p.party_id;"""),
    dict(
        id="BRB2-0192", difficulty="extra", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第三十五条；《固定资产贷款管理暂行办法》第三十五条第(四)项",
        penalty_fact_zh="限制类行业集中投放未设限额",
        question="按投向行业为限制类的授信合同，列出合同金额排名前五的合同，输出投向行业、合同编号、合同金额与排名，按行业名称、排名升序排列。",
        sql="""WITH ranked AS (
    SELECT s.sector_name_zh, a.agreement_id, a.contract_amount,
           ROW_NUMBER() OVER (PARTITION BY s.sector_code ORDER BY a.contract_amount DESC) AS rnk
    FROM credit_agreement a
    JOIN industry_sector s ON s.sector_code = a.target_industry_code
    WHERE s.risk_category = 'RESTRICTED'
)
SELECT sector_name_zh, agreement_id, contract_amount, rnk
FROM ranked
WHERE rnk <= 5
ORDER BY sector_name_zh, rnk, agreement_id;"""),
    dict(
        id="BRB2-0193", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第三十五条；《流动资金贷款管理暂行办法》第九条",
        penalty_fact_zh="限制退出类行业授信获批笔数偏多",
        question="对仍有效状态的账户，按账户种类统计除该种类最早开立账户之外的其他账户数量，仅保留数量少于九百的种类，输出账户种类与账户数量，按账户数量降序、账户种类升序排列。",
        sql="""WITH acct AS (
  SELECT a.account_id, a.account_kind, a.opened_on,
         LAG(a.opened_on) OVER (PARTITION BY a.account_kind ORDER BY a.opened_on) AS prev_open
  FROM account a
  WHERE a.status = 'ACTIVE'
)
SELECT account_kind,
       COUNT(*) AS cnt
FROM acct
WHERE prev_open IS NOT NULL
GROUP BY account_kind
HAVING COUNT(*) < 900
ORDER BY cnt DESC, account_kind;"""),
    dict(
        id="BRB2-0194", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第十四条、第三十五条",
        penalty_fact_zh="受限行业集团客户授信叠加集中",
        question="找出既是敞口集团成员、又在限制类或退出类行业获得授信的对公客户，输出客户编号、客户名称、行业名称与授信合同金额合计，按金额合计降序排列。",
        sql="""SELECT p.party_id, p.display_name, s.sector_name_zh, ROUND(SUM(a.contract_amount), 2) AS amt
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
JOIN organization_profile op ON op.party_id = p.party_id
JOIN industry_sector s ON s.sector_code = op.industry_code
JOIN exposure_group_member egm ON egm.party_id = a.borrower_party_id
WHERE s.risk_category IN ('RESTRICTED', 'EXIT')
GROUP BY p.party_id, p.display_name, s.sector_code, s.sector_name_zh
ORDER BY amt DESC, p.party_id;"""),
    dict(
        id="BRB2-0195", difficulty="medium", features=[],
        penalty_law_zh="《商业银行房地产贷款风险管理指引》第十五条；《商业银行法》第三十四条",
        penalty_fact_zh="房地产融资集中度高、授信管控不严",
        question="统计各机构投向为房地产业的授信合同笔数与合同金额合计，输出机构名称、笔数与金额合计，按笔数降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS cnt, ROUND(SUM(a.contract_amount), 2) AS amt
FROM credit_agreement a
JOIN institution i ON i.institution_id = a.institution_id
JOIN industry_sector s ON s.sector_code = a.target_industry_code
WHERE s.sector_name_zh = '房地产业'
GROUP BY i.institution_id, i.institution_name
ORDER BY cnt DESC, i.institution_name;"""),
    dict(
        id="BRB2-0196", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第三十五条；《固定资产贷款管理暂行办法》第九条第(六)项",
        penalty_fact_zh="向退出类行业发放大额授信",
        question="计算各借据本金余额占其所属机构全部贷款本金余额的比重，输出借据编号、机构名称、本金余额与占比，同一机构内占比从高到低排列，只取前三百条（占比以百分数表示并保留两位小数，机构按名称升序、同机构内同占比时按借据编号升序）。",
        sql="""SELECT q.loan_id, q.inst_name, ROUND(q.principal_balance,2) AS bal,
       ROUND(q.principal_balance*100.0/SUM(q.principal_balance) OVER (PARTITION BY q.inst_id),2) AS share
FROM (SELECT a.institution_id inst_id, i.institution_name inst_name, ld.loan_id, lbs.principal_balance
      FROM loan_balance_snapshot lbs JOIN loan_drawdown ld ON ld.loan_id=lbs.loan_id
      JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
      JOIN institution i ON i.institution_id=a.institution_id) q
ORDER BY q.inst_name, share DESC, q.loan_id
LIMIT 300;"""),
    dict(
        id="BRB2-0197", difficulty="extra", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》第四条；《商业银行法》第四十条",
        penalty_fact_zh="关键管理人员、实际控制人关联授信未审慎识别",
        question="按源主体所属营业单元统计关系类型为“关键管理人员”或“实际控制人”的关联关系记录中的源客户不重复数量，输出营业单元编号、营业单元名称与源客户不重复数量，按数量降序排列。",
        sql="""SELECT ou.org_unit_id, ou.unit_name, COUNT(DISTINCT pr.source_party_id) AS cnt
FROM party_relation pr
JOIN party p ON p.party_id = pr.source_party_id
JOIN organization_unit ou ON ou.org_unit_id = p.home_org_unit_id
JOIN relation_type_catalog rt ON rt.relation_type = pr.relation_type
WHERE rt.relation_name_zh IN ('关键管理人员', '实际控制人')
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY cnt DESC, ou.org_unit_id;"""),
    dict(
        id="BRB2-0198", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》及贷款风险分类监管要求：出现两期以上逾期的借据应及时下调分类并计提，不得维持正常状态。",
        penalty_fact_zh="检测发现部分借据已出现多期逾期却仍被登记为正常状态，涉嫌隐瞒违约、延迟下调风险分类。",
        question="借据已经出现多期逾期但借据状态仍为正常，涉嫌违规隐瞒违约并维持正常分类。输出借据编号、累计放款金额、借据状态、逾期本金合计、逾期期次数，仅列出状态为正常且逾期期次数大于等于2的记录，按逾期期次数降序、逾期本金合计降序、再按借据编号升序排列。",
        sql="""SELECT ld.loan_id, ROUND(ld.disbursed_amount,2) AS disbursed_amount, ld.status,
       ROUND(SUM(rs.principal_due),2) AS overdue_principal,
       COUNT(*) AS overdue_installments
FROM loan_drawdown ld
JOIN repayment_schedule rs ON rs.loan_id=ld.loan_id
WHERE ld.status='ACTIVE' AND rs.status='OVERDUE'
GROUP BY ld.loan_id, ld.disbursed_amount, ld.status
HAVING COUNT(*) >= 2
ORDER BY overdue_installments DESC, overdue_principal DESC, ld.loan_id;"""),
    dict(
        id="BRB2-0199", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第三十五条；《商业银行法》第七条",
        penalty_fact_zh="限制类行业无担保信用放款等叠加违规",
        question="找出同一放款账户在同一天发生两笔及以上放款的借据组合，疑似化整为零拆分放款，输出放款账户编号、放款日期与该日放款借据笔数，按笔数降序排列并只取前两百条。",
        sql="""SELECT a.loan_account_id, a.disbursed_on, COUNT(DISTINCT a.loan_id) AS cnt
FROM loan_drawdown a JOIN loan_drawdown b
  ON b.loan_account_id=a.loan_account_id AND b.disbursed_on=a.disbursed_on AND b.loan_id<>a.loan_id
GROUP BY a.loan_account_id, a.disbursed_on
HAVING COUNT(DISTINCT a.loan_id)>=2
ORDER BY cnt DESC, a.loan_account_id
LIMIT 200;"""),
    dict(
        id="BRB2-0200", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第三十七条、第四十四条；《贷款通则》第十二条",
        penalty_fact_zh="贷款期限与结清管理不规范",
        question="找出结清时间晚于授信到期日的借据（放款期限管理异常），输出借据编号、放款日期、结清日期与到期日，按结清日期降序排列，只取前两百条。",
        sql="""SELECT ld.loan_id, ld.disbursed_on, ld.closed_on, ld.current_maturity_on
FROM loan_drawdown ld
WHERE ld.closed_on > ld.current_maturity_on
ORDER BY ld.closed_on DESC, ld.loan_id
LIMIT 200;"""),
    dict(
        id="BRB2-0201", difficulty="easy", features=[],
        penalty_law_zh="《贷款风险分类指引》第十八条、《农村合作金融机构信贷资产风险分类指引》",
        penalty_fact_zh="五级分类不准确，已出现逾期本金却仍划分为正常，掩盖不良资产",
        question="列出本金逾期天数已满四十五天但仍被划分为风险分类等级“正常”的借据，输出借据编号、本金逾期天数与逾期本金，按本金逾期天数从高到低排列。",
        sql="""SELECT rc.loan_id, d.principal_overdue_days, d.overdue_principal
FROM risk_classification rc
JOIN classification_grade g ON g.grade_code = rc.grade_code
JOIN delinquency_snapshot d ON d.loan_id = rc.loan_id
WHERE g.grade_name_zh = '正常' AND d.principal_overdue_days >= 45
ORDER BY d.principal_overdue_days DESC, rc.loan_id;"""),
    dict(
        id="BRB2-0202", difficulty="hard", features=[],
        penalty_law_zh="《农村合作金融机构信贷资产风险分类指引》、《贷款风险分类指引》",
        penalty_fact_zh="人为将已逾期贷款划分为关注类，掩盖不良资产形成风险",
        question="按账户子类型统计处于久悬状态的账户数量，仅保留数量不少于五十五的子类型，输出账户子类型与数量，按数量降序、账户子类型升序排列。",
        sql="""SELECT a.account_subtype,
       COUNT(*) AS cnt
FROM account a
WHERE a.status = 'DORMANT'
GROUP BY a.account_subtype
HAVING COUNT(*) >= 55
ORDER BY cnt DESC, a.account_subtype;"""),
    dict(
        id="BRB2-0203", difficulty="hard", features=[],
        penalty_law_zh="《贷款风险分类指引》",
        penalty_fact_zh="信贷资产风险分类管理不到位，五级分类数据不真实",
        question="对每个抵质押物按其评估日期排序，计算相邻两次评估价值的涨幅，找出评估价值较上一次评估上涨超过百分之五十的评估记录，疑似人为抬高估值，输出抵质押物编号、本次评估价值、上一次评估价值与涨幅，按涨幅降序排列。",
        sql="""SELECT collateral_id, val, prev_val, incr FROM (
  SELECT cv.collateral_id,
         ROUND(cv.valuation_amount,2) AS val,
         ROUND(LAG(cv.valuation_amount) OVER (PARTITION BY cv.collateral_id ORDER BY cv.valued_on),2) AS prev_val,
         ROUND(cv.valuation_amount/NULLIF(LAG(cv.valuation_amount) OVER (PARTITION BY cv.collateral_id ORDER BY cv.valued_on),0),2) AS incr
  FROM collateral_valuation cv
)
WHERE val > 1.5*prev_val
ORDER BY incr DESC, collateral_id;"""),
    dict(
        id="BRB2-0204", difficulty="medium", features=[],
        penalty_law_zh="《农村合作金融机构信贷资产风险分类指引》、《商业银行内部控制指引》第八条",
        penalty_fact_zh="风险分类认定依据记录不完整，人工复评占比过高，存在人为调高风险分类",
        question="按评估营业单元与分类认定方式统计借据风险分类记录数量，输出营业单元名称、分类认定方式与记录数量，按数量从多到少排列。",
        sql="""SELECT ou.unit_name, rc.classification_basis, COUNT(*) AS cnt
FROM risk_classification rc
JOIN organization_unit ou ON ou.org_unit_id = rc.assessed_org_unit_id
GROUP BY ou.org_unit_id, ou.unit_name, rc.classification_basis
ORDER BY cnt DESC, ou.unit_name, rc.classification_basis;"""),
    dict(
        id="BRB2-0205", difficulty="hard", features=[],
        penalty_law_zh="《不良金融资产处置尽职指引》第二十八条、《贷款风险分类指引》",
        penalty_fact_zh="不良资产余额不真实，掩盖不良资产规模，处置不尽职",
        question="按机构汇总不良类（次级、可疑、损失）借据对应的未清偿本金余额合计，输出机构名称与不良本金余额合计，按余额从高到低排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(lbs.principal_balance), 2) AS bad_balance
FROM loan_balance_snapshot lbs
JOIN risk_classification rc ON rc.loan_id = lbs.loan_id
JOIN classification_grade g ON g.grade_code = rc.grade_code
JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE g.is_nonperforming = 1
GROUP BY i.institution_id, i.institution_name
ORDER BY bad_balance DESC;"""),
    dict(
        id="BRB2-0206", difficulty="medium", features=[],
        penalty_law_zh="《商业银行风险监管核心指标(试行)》",
        penalty_fact_zh="信贷资产拨备计提不足，拨备覆盖率不达标",
        question="找出既作为账户持有人持有定期存款、又在本行作为借款人签署过授信合同的存贷交叉客户，输出客户编号，按客户编号升序排列。",
        sql="""SELECT ah.party_id AS party_id FROM account_holder ah JOIN term_deposit td ON td.account_id=ah.account_id
INTERSECT
SELECT a.borrower_party_id AS party_id FROM credit_agreement a
ORDER BY party_id;"""),
    dict(
        id="BRB2-0207", difficulty="medium", features=[],
        penalty_law_zh="《贷款风险分类指引》、《不良贷款认定暂行办法》第九条",
        penalty_fact_zh="损失类贷款认定与核销管理不审慎，风险资产处置不真实",
        question="按机构统计被划分为“损失”等级的借据数量，输出机构名称与借据数量，按数量从多到少排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS loss_count
FROM risk_classification rc
JOIN classification_grade g ON g.grade_code = rc.grade_code
JOIN loan_drawdown ld ON ld.loan_id = rc.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE g.grade_name_zh = '损失'
GROUP BY i.institution_id, i.institution_name
ORDER BY loss_count DESC, i.institution_name;"""),
    dict(
        id="BRB2-0208", difficulty="hard", features=[],
        penalty_law_zh="《商业银行风险监管核心指标(试行)》",
        penalty_fact_zh="拨备覆盖率不足，风险抵补能力下降，掩盖资产质量恶化",
        question="按机构计算贷款拨备覆盖比（已计提金额合计除以应计提金额合计，四舍五入保留四位小数），输出机构名称与拨备覆盖比，按覆盖比从低到高排列。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(ps.recognized_amount) * 1.0 / SUM(ps.required_amount), 4) AS coverage
FROM provision_snapshot ps
JOIN loan_drawdown ld ON ld.loan_id = ps.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
ORDER BY coverage ASC, i.institution_name;"""),
    dict(
        id="BRB2-0209", difficulty="medium", features=[],
        penalty_law_zh="《商业银行内部控制指引》第五条",
        penalty_fact_zh="拨备计提方式选择不审慎，计提政策执行不统一",
        question="列出仍处于在职状态但在本行无任何账户持有人记录的本行员工（反映员工账户关系档案缺失），输出员工客户编号，按员工客户编号升序排列。",
        sql="""SELECT party_id
FROM (
    SELECT sm.person_party_id AS party_id
    FROM staff_member sm
    WHERE sm.employment_status = 'ACTIVE'
    EXCEPT
    SELECT ah.party_id AS party_id
    FROM account_holder ah
)
ORDER BY party_id;"""),
    dict(
        id="BRB2-0210", difficulty="medium", features=[],
        penalty_law_zh="《商业银行内部控制指引》第十五条",
        penalty_fact_zh="信贷资产分类与拨备计提不审慎，拨备覆盖不足",
        question="列出从未发生任何现金支取记录的储蓄类账户，疑似长期只收不支、资金沉淀异常，输出账户编号，按账户编号升序排列，只取前三百条。",
        sql="""SELECT a.account_id FROM account a
WHERE a.account_kind='SAVINGS'
  AND NOT EXISTS (SELECT 1 FROM payment_event e WHERE e.from_account_id=a.account_id AND e.is_cash=1)
ORDER BY a.account_id
LIMIT 300;"""),
    dict(
        id="BRB2-0211", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》、《商业银行授信工作尽职指引》第三十八条",
        penalty_fact_zh="押品评估价值不审慎，评估价值低于其担保金额，高估押品缓释作用",
        question="列出评估价值低于其质押担保金额的押品，输出押品编号、押品名称、评估价值与质押担保金额，按评估价值从低到高排列。",
        sql="""SELECT c.collateral_id, c.asset_label, v.valuation_amount, lk.pledged_amount
FROM collateral_asset c
JOIN collateral_link lk ON lk.collateral_id = c.collateral_id
JOIN collateral_valuation v ON v.collateral_id = c.collateral_id
WHERE v.valuation_amount < lk.pledged_amount
ORDER BY v.valuation_amount ASC, c.collateral_id;"""),
    dict(
        id="BRB2-0212", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》、《中华人民共和国担保法》",
        penalty_fact_zh="担保事项与押品登记不衔接，担保桥接缺失，押品缓释落空",
        question="列出采用抵押或质押方式但未登记任何押品关联记录的有效担保协议，输出担保协议编号与担保金额，按担保金额从高到低排列。",
        sql="""SELECT s.security_id, s.secured_amount
FROM security_agreement s
LEFT JOIN collateral_link lk ON lk.security_id = s.security_id
WHERE s.security_type IN ('MORTGAGE', 'PLEDGE')
  AND s.status = 'ACTIVE'
  AND lk.security_id IS NULL
ORDER BY s.secured_amount DESC, s.security_id;"""),
    dict(
        id="BRB2-0213", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国担保法》、《个人贷款管理暂行办法》第二十六条",
        penalty_fact_zh="保证担保缺乏有效保证承诺，担保效力不足，担保桥接违规",
        question="列出开户后缺少主持有人记录的储蓄类账户，反映账户控制人与账务登记脱节，输出账户编号，按账户编号升序排列，只取前三百条。",
        sql="""SELECT a.account_id FROM account a
LEFT JOIN account_holder ah ON ah.account_id=a.account_id AND ah.holder_role='PRIMARY'
WHERE ah.account_id IS NULL
ORDER BY a.account_id
LIMIT 300;"""),
    dict(
        id="BRB2-0214", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》、《商业银行授信工作尽职指引》",
        penalty_fact_zh="抵质押比率过高，第二还款来源不充足，押品管理不审慎",
        question="列出处于第一顺位且质押率超过百分之七十的有效押品关联记录，输出押品编号、顺位等级与质押率，按质押率从高到低排列。",
        sql="""SELECT lk.collateral_id, lk.lien_priority, lk.pledge_ratio
FROM collateral_link lk
WHERE lk.lien_priority = 1 AND lk.pledge_ratio > 0.7 AND lk.status = 'ACTIVE'
ORDER BY lk.pledge_ratio DESC, lk.collateral_id;"""),
    dict(
        id="BRB2-0215", difficulty="hard", features=[],
        penalty_law_zh="《商业银行内部控制指引》第八条",
        penalty_fact_zh="担保业务管理不审慎，担保金额统计与缓释作用失真",
        question="按机构与担保方式汇总有效担保协议的担保金额合计，输出机构名称、担保方式与担保金额合计，按金额从高到低排列。",
        sql="""SELECT i.institution_name, s.security_type, ROUND(SUM(s.secured_amount), 2) AS total
FROM security_agreement s
JOIN institution i ON i.institution_id = s.institution_id
WHERE s.status = 'ACTIVE'
GROUP BY i.institution_id, i.institution_name, s.security_type
ORDER BY total DESC, i.institution_name, s.security_type;"""),
    dict(
        id="BRB2-0216", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》、《银行抵债资产管理办法》",
        penalty_fact_zh="押品缓释失效后未及时处置更新，押品状态管理不审慎",
        question="列出担保协议状态已过期但所关联押品仍处于正常状态的记录，输出担保协议编号与押品编号，按担保协议编号、押品编号升序排列。",
        sql="""SELECT s.security_id, c.collateral_id
FROM security_agreement s
JOIN collateral_link lk ON lk.security_id = s.security_id
JOIN collateral_asset c ON c.collateral_id = lk.collateral_id
WHERE s.status = 'EXPIRED' AND c.status = 'ACTIVE'
ORDER BY s.security_id, c.collateral_id;"""),
    dict(
        id="BRB2-0217", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国担保法》、《商业银行授信工作尽职指引》",
        penalty_fact_zh="保证承诺过期后未落实新的增信措施，担保效力丧失",
        question="列出状态已过期的保证人承诺记录，输出担保协议编号与保证金额，按保证金额从高到低排列。",
        sql="""SELECT g.security_id, g.guaranteed_amount
FROM guarantor_commitment g
WHERE g.status = 'EXPIRED'
ORDER BY g.guaranteed_amount DESC, g.security_id;"""),
    dict(
        id="BRB2-0218", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》",
        penalty_fact_zh="担保业务结构不审慎，风险缓释措施运用失当",
        question="按距审计基准日（2026-06-30）的剩余期限将借据分为已到期（小于0天）、临期（0至90天）与常态（大于90天）三档并统计各档笔数，输出档位与笔数，按常态、临期、已到期的顺序排列。",
        sql="""SELECT bucket, COUNT(*) AS cnt FROM (
  SELECT CASE WHEN julianday(ld.current_maturity_on)-julianday('2026-06-30')<0 THEN '已到期'
              WHEN julianday(ld.current_maturity_on)-julianday('2026-06-30')<=90 THEN '临期'
              ELSE '常态' END AS bucket
  FROM loan_drawdown ld
)
GROUP BY bucket
ORDER BY CASE bucket WHEN '常态' THEN 1 WHEN '临期' THEN 2 ELSE 3 END;"""),
    dict(
        id="BRB2-0219", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》",
        penalty_fact_zh="同一押品被重复用于多笔担保，担保金额超出押品价值，风险缓释虚增",
        question="列出同时被多份有效担保协议关联质押的押品，输出押品编号与关联次数，按关联次数从多到少排列（关联记录状态须为有效）。",
        sql="""SELECT lk.collateral_id, COUNT(*) AS uses
FROM collateral_link lk
WHERE lk.status = 'ACTIVE'
GROUP BY lk.collateral_id
HAVING COUNT(*) > 1
ORDER BY uses DESC, lk.collateral_id;"""),
    dict(
        id="BRB2-0220", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》、《商业银行授信工作尽职指引》第三十八条",
        penalty_fact_zh="押品评估独立性不足，内部评估管理不审慎",
        question="按押品种类统计由银行内部评估的押品平均评估价值与评估笔数，输出押品种类、平均评估价值与评估笔数，按平均评估价值从高到低排列。",
        sql="""SELECT c.collateral_type, ROUND(AVG(v.valuation_amount), 2) AS avg_val, COUNT(*) AS cnt
FROM collateral_valuation v
JOIN collateral_asset c ON c.collateral_id = v.collateral_id
WHERE v.appraiser_kind = 'BANK_INTERNAL'
GROUP BY c.collateral_type
ORDER BY avg_val DESC;"""),
    dict(
        id="BRB2-0221", difficulty="hard", features=[],
        penalty_law_zh="《固定资产贷款管理暂行办法》第二十五条及《流动资金贷款管理暂行办法》第二十四条：应先行落实受托支付指令，指令未执行不得提前发放贷款。",
        penalty_fact_zh="检测发现贷款已放款但受托支付指令仍待处理，指令状态与放款进度不符，涉嫌逆程序操作规避受托支付。",
        question="贷款已全额提款且状态正常，但对应的受托支付指令仍处于待处理状态，指令未执行贷款却已发放，涉嫌逆程序放款。输出借据编号、累计放款金额、支付指令编号、待处理指令金额、指令状态，仅列出指令为待处理且借据状态为正常的记录，按指令金额降序排列，再按借据编号升序排列。",
        sql="""SELECT ld.loan_id, ROUND(ld.disbursed_amount,2) AS disbursed_amount,
       pi.instruction_id, ROUND(pi.instruction_amount,2) AS pending_amount, pi.status
FROM loan_drawdown ld
JOIN payment_instruction pi ON pi.loan_id=ld.loan_id
WHERE pi.status='PENDING' AND ld.status='ACTIVE'
ORDER BY pending_amount DESC, ld.loan_id;"""),
    dict(
        id="BRB2-0222", difficulty="hard", features=[],
        penalty_law_zh="《个人贷款管理暂行办法》第二十七条及《流动资金贷款管理暂行办法》第二十六条：自主支付应限定于小额分散情形，超比例大规模自主支付属规避受托支付。",
        penalty_fact_zh="检测发现自主支付累计金额显著超过合同金额约定比重，涉嫌化整为零拆分支付规避受托支付管理。",
        question="同一授信合同下自主支付累计放款金额占合同金额比例过高，涉嫌化整为零拆分支付规避受托支付上限。输出授信合同编号、借款人名称、合同金额、累计自主支付金额、自主支付占比，仅列出自主支付累计金额超过合同金额30%的记录，按授信合同编号升序排列。",
        sql="""WITH sp AS (
  SELECT d.agreement_id, SUM(d.disbursed_amount) AS self_amount
  FROM loan_drawdown d
  WHERE d.payment_mode='SELF_PAYMENT'
  GROUP BY d.agreement_id
)
SELECT a.agreement_id, p.display_name, ROUND(a.contract_amount,2) AS contract_amount,
       ROUND(sp.self_amount,2) AS self_amount,
       ROUND(sp.self_amount * 1.0 / a.contract_amount, 4) AS self_ratio
FROM sp JOIN credit_agreement a ON a.agreement_id=sp.agreement_id
JOIN party p ON p.party_id=a.borrower_party_id
WHERE sp.self_amount > 0.3 * a.contract_amount
ORDER BY a.agreement_id;"""),
    dict(
        id="BRB2-0223", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：单一客户贷款归集还款账户开展借新还旧或循环操作，掩盖真实偿债能力，属违规操作。",
        penalty_fact_zh="检测发现存在单个还款账户短期内承接多笔借据的归集情形，疑为借新还旧或他贷还本，需穿透核查资金来源。",
        question="同一还款账户在短期内承接多笔不同借据的还款，资金高度归集，涉嫌借新还旧或以他贷还本。输出还款账户编号、借据编号、放款日期、放款金额、该账户承接借据笔数，仅列出承接笔数不少于3笔的账户中放款先后顺序居前2笔的借据，按还款账户编号及放款日期升序排列。",
        sql="""WITH rk AS (
  SELECT d.loan_id, d.repayment_account_id, d.disbursed_on, d.disbursed_amount,
         ROW_NUMBER() OVER (PARTITION BY d.repayment_account_id ORDER BY d.disbursed_on, d.loan_id) AS rn,
         COUNT(*) OVER (PARTITION BY d.repayment_account_id) AS loan_cnt
  FROM loan_drawdown d
)
SELECT r.repayment_account_id, r.loan_id, r.disbursed_on, ROUND(r.disbursed_amount,2) AS amount, r.loan_cnt
FROM rk r
WHERE r.loan_cnt >= 3 AND r.rn <= 2
ORDER BY r.repayment_account_id, r.disbursed_on;"""),
    dict(
        id="BRB2-0224", difficulty="easy", features=[],
        penalty_law_zh="《严禁柜台违规行为防范案件风险的工作意见》",
        penalty_fact_zh="柜面经办人授权管理不审慎，权限设置存在操作风险",
        question="列出授权等级最高（L3级）的柜员类系统操作员，输出操作员编号与对应员工编号，按操作员编号升序排列。",
        sql="""SELECT so.operator_id, so.staff_id
FROM service_operator so
WHERE so.operator_kind = 'TELLER' AND so.authority_level = 'L3'
ORDER BY so.operator_id;"""),
    dict(
        id="BRB2-0225", difficulty="easy", features=[],
        penalty_law_zh="《商业银行内部控制指引》第四十六条",
        penalty_fact_zh="员工岗位职责与轮岗管理不到位，存在不相容岗位兼任",
        question="按岗位名称统计任职的不重复员工人数，输出岗位名称与员工人数，按人数从多到少排列。",
        sql="""SELECT sa.role_title, COUNT(DISTINCT sa.staff_id) AS staff_count
FROM staff_assignment sa
GROUP BY sa.role_title
ORDER BY staff_count DESC, sa.role_title;"""),
    dict(
        id="BRB2-0226", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：授信须在额度批复并生效后方可发放，未生效即放款属越权逆程序操作。",
        penalty_fact_zh="检测发现多笔贷款在授信额度生效日前即已发放，放款时间早于额度生效时间，涉嫌越权逆流程投放。",
        question="授信额度未生效前即已投放贷款，涉嫌越权或逆流程放款。输出借据编号、放款日期、授信额度编号、额度生效日、批复日、放款金额，仅列出放款日期早于授信额度生效日的记录，按授信额度编号升序排列。",
        sql="""SELECT ld.loan_id, ld.disbursed_on, f.facility_id, f.effective_from, f.approved_on,
       ROUND(ld.disbursed_amount,2) AS disbursed_amount
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
JOIN credit_facility f ON f.facility_id=a.facility_id
WHERE ld.disbursed_on < f.effective_from
ORDER BY f.facility_id, ld.loan_id;"""),
    dict(
        id="BRB2-0227", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》及《商业银行授信工作尽职指引》：贷款投放金额不得超过合同约定金额与批复金额。",
        penalty_fact_zh="检测发现同一授信合同累计放款超过合同约定金额，形成超批复超合同投放的越权风险。",
        question="同一授信合同项下累计放款金额超过合同金额，超批复金额投放或未按合同控制放款规模。输出授信合同编号、合同金额、累计放款金额、超合同投放金额、放款笔数，仅列出累计放款金额大于合同金额的记录，按授信合同编号升序排列。",
        sql="""WITH ds AS (
  SELECT d.agreement_id, SUM(d.disbursed_amount) AS total_disbursed, COUNT(DISTINCT d.loan_id) AS drawdown_cnt
  FROM loan_drawdown d GROUP BY d.agreement_id
)
SELECT a.agreement_id, ROUND(a.contract_amount,2) AS contract_amount,
       ROUND(ds.total_disbursed,2) AS total_disbursed,
       ROUND(ds.total_disbursed - a.contract_amount,2) AS excess_amount,
       ds.drawdown_cnt
FROM ds JOIN credit_agreement a ON a.agreement_id=ds.agreement_id
WHERE ds.total_disbursed > a.contract_amount
ORDER BY a.agreement_id;"""),
    dict(
        id="BRB2-0228", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：贷款资金应通过借款人归集的放款账户发放，账户集中承载多笔贷款涉嫌资金归集或冒名发放。",
        penalty_fact_zh="检测发现同一放款账户承载多笔借据，资金高度归集，疑为同一主体或关联主体循环放款。",
        question="同一放款账户承载过多笔贷款资金，涉嫌资金归集或账户被循环利用发放关联贷款。输出放款账户编号、承载借据笔数、累计放款金额，仅列出承载借据笔数不少于5笔的账户，按承载借据笔数降序排列，再按放款账户编号升序排列。",
        sql="""SELECT ld.disbursement_account_id, COUNT(DISTINCT ld.loan_id) AS loan_cnt,
       ROUND(SUM(ld.disbursed_amount),2) AS total_disbursed
FROM loan_drawdown ld
GROUP BY ld.disbursement_account_id
HAVING COUNT(DISTINCT ld.loan_id) >= 5
ORDER BY loan_cnt DESC, ld.disbursement_account_id;"""),
    dict(
        id="BRB2-0229", difficulty="medium", features=[],
        penalty_law_zh="《个人贷款管理暂行办法》及《流动资金贷款管理暂行办法》：同一合同应一次性受托支付，拆分多笔自主提款属化整为零规避监管。",
        penalty_fact_zh="检测发现同一授信合同被拆分多笔自主支付借据反复提款，涉嫌化整为零规避受托支付限额管理。",
        question="同一授信合同下自主支付拆分为多笔借据反复提款，涉嫌化整为零规避受托支付。输出授信合同编号、借款人名称、自主支付借据笔数，仅列出同一合同下自主支付借据笔数不少于5笔的记录，按自主支付借据笔数降序排列，再按授信合同编号升序排列。",
        sql="""SELECT a.agreement_id, p.display_name, COUNT(DISTINCT ld.loan_id) AS self_installments
FROM credit_agreement a
JOIN loan_drawdown ld ON ld.agreement_id=a.agreement_id AND ld.payment_mode='SELF_PAYMENT'
JOIN party p ON p.party_id=a.borrower_party_id
GROUP BY a.agreement_id, p.display_name
HAVING COUNT(DISTINCT ld.loan_id) >= 5
ORDER BY self_installments DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0230", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第六条",
        penalty_fact_zh="存款资金被占用或长期冻结，存款人合法权益保障不足",
        question="按机构统计账面余额高于可用余额且差额超过五百万元的账户数量及差额合计，输出机构名称、账户数量与差额合计，按差额合计从高到低排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS frozen_cnt, ROUND(SUM(s.ledger_balance - s.available_balance), 2) AS frozen_amt
FROM account_balance_snapshot s
JOIN account a ON a.account_id = s.account_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE (s.ledger_balance - s.available_balance) > 5000000
GROUP BY i.institution_id, i.institution_name
ORDER BY frozen_amt DESC;"""),
    dict(
        id="BRB2-0231", difficulty="medium", features=[],
        penalty_law_zh="《储蓄管理条例》第三条",
        penalty_fact_zh="定期存款到期未及时兑付处理，存款权益保护与账户管理不审慎",
        question="列出截至 2026 年 6 月 30 日之前已到期但关联账户仍处于正常状态的定期存款，输出账户编号、开户本金、到期日期与年利率，按到期日期升序排列。",
        sql="""SELECT t.account_id, t.opening_principal, t.maturity_on, t.annual_interest_rate
FROM term_deposit t
JOIN account a ON a.account_id = t.account_id
WHERE a.status = 'ACTIVE' AND t.maturity_on < '2026-06-30'
ORDER BY t.maturity_on, t.account_id;"""),
    dict(
        id="BRB2-0232", difficulty="medium", features=[],
        penalty_law_zh="《中国银监会办公厅关于加强农村合作金融机构现金、存款和联行业务风险管理的通知》",
        penalty_fact_zh="大额现金支取审核不严，现金业务操作风险管理不到位",
        question="按机构统计已结算且单笔金额超过一百万元的大额现金支取交易笔数与金额合计，输出机构名称、交易笔数与金额合计，按金额合计从高到低排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS cnt, ROUND(SUM(pe.amount), 2) AS total
FROM payment_event pe
JOIN payment_type_catalog t ON t.payment_type = pe.payment_type
JOIN account ac ON ac.account_id = COALESCE(pe.from_account_id, pe.to_account_id)
JOIN institution i ON i.institution_id = ac.institution_id
WHERE t.name_zh = '现金支取' AND pe.amount > 1000000 AND pe.status = 'SETTLED'
GROUP BY i.institution_id, i.institution_name
ORDER BY total DESC;"""),
    dict(
        id="BRB2-0233", difficulty="hard", features=[],
        penalty_law_zh="《个人存款账户实名制规定》第七条",
        penalty_fact_zh="联名账户持有人实名信息管理不审慎，存款账户真实性不足",
        question="列出在 2025 年 1 月 31 日及之前签发且当前仍有效的借记卡片，输出卡片编号、卡片种类与签发日期，按签发日期升序、卡片编号升序排列。",
        sql="""SELECT pc.card_id,
       pc.card_type,
       pc.issued_on
FROM payment_card pc
WHERE pc.card_type = 'DEBIT'
  AND pc.status = 'ACTIVE'
  AND pc.issued_on <= '2025-01-31'
ORDER BY pc.issued_on, pc.card_id;"""),
    dict(
        id="BRB2-0234", difficulty="extra", features=[],
        penalty_law_zh="《固定资产贷款管理暂行办法》与《流动资金贷款管理暂行办法》：大额贷款原则上应受托支付，机构层面受托支付占比过低表明监督机制失效。",
        penalty_fact_zh="检测发现部分机构受托支付占比显著偏低、自主支付占比过高，反映受托支付监督管理未有效落实。",
        question="机构层面受托支付占比过低反映整体自主支付过度，受托支付监督失效。输出机构名称、累计受托支付金额、累计自主支付金额、受托支付占比，仅列出受托支付占比低于52%的机构，按受托支付占比升序排列，再按机构名称升序排列（金额口径为借据放款金额，按借据的支付方式汇总）。",
        sql="""WITH ratio AS (
  SELECT i.institution_name,
         ROUND(SUM(CASE WHEN d.payment_mode='ENTRUSTED_PAYMENT' THEN d.disbursed_amount ELSE 0 END),2) AS entrusted_amt,
         ROUND(SUM(CASE WHEN d.payment_mode='SELF_PAYMENT' THEN d.disbursed_amount ELSE 0 END),2) AS self_amt
  FROM loan_drawdown d
  JOIN credit_agreement a ON a.agreement_id=d.agreement_id
  JOIN institution i ON i.institution_id=a.institution_id
  GROUP BY i.institution_name
)
SELECT institution_name, entrusted_amt, self_amt,
       ROUND(entrusted_amt * 1.0 / (entrusted_amt + self_amt), 4) AS entrusted_ratio
FROM ratio
WHERE entrusted_amt * 1.0 / (entrusted_amt + self_amt) < 0.52
ORDER BY entrusted_ratio, institution_name;"""),
    dict(
        id="BRB2-0235", difficulty="extra", features=[],
        penalty_law_zh="《固定资产贷款管理暂行办法》第二十八条：固定资产贷款应按项目进度分批投放并落实受托支付，一次性足额提款属未尽职管理。",
        penalty_fact_zh="检测发现部分授信合同单笔放款几乎占据全部投放金额，未进行分次审批与受托支付安排，风险集中。",
        question="同一授信合同下单笔放款金额占合同全部放款金额比例超过90%，一次性足额投放未尽分次审批与受托支付责任。输出授信合同编号、借据编号、单笔放款金额、合同内累计放款金额、单笔占比，仅列出单笔占比大于90%的借据，按授信合同编号升序排列（占比以百分数表示并保留两位小数）。",
        sql="""WITH share AS (
  SELECT d.agreement_id, d.loan_id, ROUND(d.disbursed_amount,2) AS amount,
         ROUND(SUM(d.disbursed_amount) OVER (PARTITION BY d.agreement_id),2) AS agg_total
  FROM loan_drawdown d
)
SELECT s.agreement_id, s.loan_id, s.amount, s.agg_total,
       ROUND(s.amount * 100.0 / s.agg_total, 2) AS pct_share
FROM share s
WHERE s.amount * 100.0 / s.agg_total > 90
ORDER BY s.agreement_id, s.loan_id;"""),
    dict(
        id="BRB2-0236", difficulty="medium", features=[],
        penalty_law_zh="《储蓄管理条例》第三条、《中华人民共和国商业银行法》第三十三条",
        penalty_fact_zh="销户账户余额清理与兑付不及时，存款权益保护存在缺陷",
        question="列出账户状态为已销户的账户余额快照，输出账户编号与账面余额，按账面余额从高到低排列。",
        sql="""SELECT a.account_id, s.ledger_balance
FROM account a
JOIN account_balance_snapshot s ON s.account_id = a.account_id
WHERE a.status = 'CLOSED'
ORDER BY s.ledger_balance DESC, a.account_id;"""),
    dict(
        id="BRB2-0237", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第四十七条",
        penalty_fact_zh="违规高息吸收存款，存款利率管理不审慎",
        question="按发行机构汇总在售理财产品的计划募集与全部产品的实际募集金额，计算实际募集合计占计划募集合计的完成率，输出机构名称、实际募集合计、计划募集合计与完成率，只保留完成率超过一点二的机构，按完成率降序排列（计划募集金额只计入在售产品，实际募集金额计入全部产品）。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(wp.actual_raise_amount),2) AS actual,
       ROUND(SUM(CASE WHEN wp.status='ON_SALE' THEN wp.planned_raise_amount ELSE 0 END),2) AS planned,
       ROUND(SUM(wp.actual_raise_amount)*1.0/NULLIF(SUM(CASE WHEN wp.status='ON_SALE' THEN wp.planned_raise_amount ELSE 0 END),0),4) AS ratio
FROM wealth_product wp JOIN institution i ON i.institution_id=wp.issuer_institution_id
GROUP BY i.institution_id, i.institution_name
HAVING SUM(wp.actual_raise_amount)*1.0/NULLIF(SUM(CASE WHEN wp.status='ON_SALE' THEN wp.planned_raise_amount ELSE 0 END),0)>1.2
ORDER BY ratio DESC, i.institution_name;"""),
    dict(
        id="BRB2-0238", difficulty="hard", features=[],
        penalty_law_zh="《个人存款账户实名制规定》第六条",
        penalty_fact_zh="存款账户状态管理混乱，久悬账户清理不到位",
        question="按放款机构交叉统计受托支付与自主支付两类支付指令的数量与受托指令金额合计，输出机构名称、受托笔数、自主笔数与受托金额合计，只保留受托与自主均有指令的机构，按受托金额合计降序排列。",
        sql="""SELECT i.institution_name,
       COUNT(DISTINCT CASE WHEN pi.payment_mode='ENTRUSTED_PAYMENT' THEN pi.instruction_id END) AS ent_cnt,
       COUNT(DISTINCT CASE WHEN pi.payment_mode='SELF_PAYMENT' THEN pi.instruction_id END) AS self_cnt,
       ROUND(SUM(CASE WHEN pi.payment_mode='ENTRUSTED_PAYMENT' THEN pi.instruction_amount ELSE 0 END),2) AS ent_amt
FROM payment_instruction pi JOIN loan_drawdown ld ON ld.loan_id=pi.loan_id
JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
JOIN institution i ON i.institution_id=a.institution_id
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(DISTINCT CASE WHEN pi.payment_mode='SELF_PAYMENT' THEN pi.instruction_id END)>0
ORDER BY ent_amt DESC, i.institution_name;"""),
    dict(
        id="BRB2-0239", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第六条",
        penalty_fact_zh="存款规模统计与结构管理不审慎，存款业务治理不到位",
        question="按月份与付款账户汇总现金支取金额，找出单月现金支取合计超过五百万元的账户月份组合，输出月份、账户编号与现金支取合计，按合计降序排列，只取前两百条。",
        sql="""SELECT SUBSTR(e.business_date,1,7) AS ym, a.account_id, ROUND(SUM(e.amount),2) AS tot
FROM payment_event e JOIN account a ON a.account_id=e.from_account_id
WHERE e.is_cash=1
GROUP BY ym, a.account_id
HAVING SUM(e.amount)>5000000
ORDER BY tot DESC, ym, a.account_id
LIMIT 200;"""),
    dict(
        id="BRB2-0240", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》与《流动资金贷款管理暂行办法》：对已出现不良的客户不得新增授信，严禁带病投放掩盖风险。",
        penalty_fact_zh="检测发现部分借款人在存在逾期借据的同时仍持有新增借据，涉嫌带病新增授信或借新还旧。",
        question="借款人在已有逾期借据的同时仍新增授信并放款，涉嫌带病投放、借新还旧掩盖风险。输出借款人编号、借款人名称、逾期借据笔数、全部借据笔数，仅列出既有逾期借据又有未逾期新增借据的借款人，按逾期借据笔数降序排列，再按借款人编号升序排列（逾期以还款计划中状态为逾期的期次判定）。",
        sql="""SELECT a.borrower_party_id, p.display_name,
       COUNT(DISTINCT CASE WHEN rs.status='OVERDUE' THEN ld.loan_id END) AS overdue_loans,
       COUNT(DISTINCT ld.loan_id) AS total_loans
FROM credit_agreement a
JOIN party p ON p.party_id=a.borrower_party_id
JOIN loan_drawdown ld ON ld.agreement_id=a.agreement_id
JOIN repayment_schedule rs ON rs.loan_id=ld.loan_id
GROUP BY a.borrower_party_id, p.display_name
HAVING COUNT(DISTINCT CASE WHEN rs.status='OVERDUE' THEN ld.loan_id END) >= 1
   AND COUNT(DISTINCT CASE WHEN rs.status='OVERDUE' THEN ld.loan_id END) < COUNT(DISTINCT ld.loan_id)
ORDER BY overdue_loans DESC, a.borrower_party_id;"""),
    dict(
        id="BRB2-0241", difficulty="extra", features=[],
        penalty_law_zh="贷款五级分类与《商业银行授信工作尽职指引》：本金逾期90天以上应下调为不良并足额计提，不得维持正常分类。",
        penalty_fact_zh="检测发现本金逾期已超90天的借据仍被登记为正常状态，涉嫌隐瞒不良、推迟风险分类下调。",
        question="借据期末账载逾期本金超过一千万元且截至快照基准日（2026-06-30）自逾期起始日起算已超过90天，但借据状态仍维持正常，涉嫌推迟大额不良暴露。输出借据编号、逾期起始日、期末逾期本金与截至基准日的已逾期天数，仅列出借据状态为正常、期末逾期本金超过一千万元且已逾期天数超过90天的记录，按借据编号升序排列，只取前三百条。",
        sql="""WITH o AS (
  SELECT lb.loan_id, lb.overdue_since, lb.overdue_principal,
         CAST(julianday('2026-06-30') - julianday(lb.overdue_since) AS INTEGER) AS overdue_days,
         ld.status
  FROM loan_balance_snapshot lb
  JOIN loan_drawdown ld ON ld.loan_id = lb.loan_id
)
SELECT loan_id, overdue_since, ROUND(overdue_principal, 2) AS overdue_principal, overdue_days
FROM o
WHERE status = 'ACTIVE' AND overdue_principal > 10000000 AND overdue_days > 90
ORDER BY loan_id
LIMIT 300;"""),
    dict(
        id="BRB2-0242", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：正常贷款应挂于正常账户核算，贷款账户被销户或久悬而借据仍正常属账务不一致。",
        penalty_fact_zh="检测发现借据登记为正常但其贷款账户已销户或久悬，账户与贷款状态矛盾，账务管理存在异常。",
        question="借据状态正常但对应的贷款账户已被销户或久悬，账户状态与贷款状态矛盾。输出借据编号、贷款账户编号、累计放款金额、账户状态，仅列出借据状态为正常但贷款账户状态非正常的记录，按账户状态及借据编号升序排列。",
        sql="""SELECT ld.loan_id, ac.account_id, ROUND(ld.disbursed_amount,2) AS disbursed_amount, ac.status AS account_status
FROM loan_drawdown ld
JOIN account ac ON ac.account_id=ld.loan_account_id
WHERE ac.status <> 'ACTIVE' AND ld.status='ACTIVE'
ORDER BY ac.status, ld.loan_id;"""),
    dict(
        id="BRB2-0243", difficulty="hard", features=[],
        penalty_law_zh="《商业银行贷款损失准备管理办法》：存在逾期风险的贷款应按风险程度足额计提拨备，拨备覆盖率不足将削弱风险抵补能力。",
        penalty_fact_zh="检测发现已有逾期分期的借据拨备计提仍低于应提金额，风险抵补不足，需补提拨备。",
        question="名下存在逾期分期还款计划的借据，其已计提拨备金额仍低于应计提拨备金额，存在拨备计提缺口。输出借据编号、应计提拨备金额、已计提拨备金额与拨备缺口金额（应计提减已计提，保留两位小数），仅列出存在逾期分期且已计提低于应计提的借据，按借据编号升序排列，只取前两百条。",
        sql="""SELECT p.loan_id, ROUND(p.required_amount, 2) AS required_amount,
       ROUND(p.recognized_amount, 2) AS recognized_amount,
       ROUND(p.required_amount - p.recognized_amount, 2) AS shortfall
FROM provision_snapshot p
JOIN loan_drawdown ld ON ld.loan_id = p.loan_id
WHERE p.recognized_amount < p.required_amount
  AND EXISTS (SELECT 1 FROM repayment_schedule rs WHERE rs.loan_id = p.loan_id AND rs.status = 'OVERDUE')
ORDER BY p.loan_id
LIMIT 200;"""),
    dict(
        id="BRB2-0244", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》及《商业银行授信工作尽职指引》：受托支付应径付真实交易对手，指令收款人异常流向需穿透核查实际用款人。",
        penalty_fact_zh="检测发现受托支付指令收款人与借款人不一致，资金流向异方第三方，实际用款人与借款人不符。",
        question="受托支付指令的收款人与借款人本人不一致，贷款资金流向异方第三方，需穿透核查实际用款人。输出支付指令编号、借据编号、借款人名称、实际收款人名称、指令金额，仅列出已执行的指令其收款人与借款人不一致的记录，按指令金额降序排列，再按支付指令编号升序排列。",
        sql="""SELECT pi.instruction_id, ld.loan_id, p1.display_name AS borrower, p2.display_name AS payee,
       ROUND(pi.instruction_amount,2) AS amount
FROM payment_instruction pi
JOIN loan_drawdown ld ON ld.loan_id=pi.loan_id
JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
JOIN party p1 ON p1.party_id=a.borrower_party_id
JOIN party p2 ON p2.party_id=pi.intended_payee_party_id
WHERE pi.intended_payee_party_id <> a.borrower_party_id AND pi.status='EXECUTED'
ORDER BY amount DESC, pi.instruction_id;"""),
    dict(
        id="BRB2-0245", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》及《商业银行授信工作尽职指引》：贷款应一次性实贷实付，同一借款人极短间隔连续放款涉嫌拆分规避审批。",
        penalty_fact_zh="检测发现同一借款人在极短时间内连续发放多笔借据，放款间隔不合常理，涉嫌化整为零规避管理。",
        question="同一借款人在极短时间内连续发放多笔借据，同日或次日连放涉嫌化整为零拆分提款。输出借款人名称、借据编号、放款日期、上一笔放款日期、两笔放款间隔天数，仅列出同一借款人上一笔放款距本笔放款不超过3天的记录，按间隔天数升序排列，再按借据编号升序排列。",
        sql="""WITH seq AS (
  SELECT a.borrower_party_id, ld.loan_id, ld.disbursed_on,
         LAG(ld.disbursed_on) OVER (PARTITION BY a.borrower_party_id ORDER BY ld.disbursed_on, ld.loan_id) AS prev_disbursed
  FROM loan_drawdown ld
  JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
)
SELECT p.display_name, s.loan_id, s.disbursed_on, s.prev_disbursed,
       CAST(julianday(s.disbursed_on)-julianday(s.prev_disbursed) AS INTEGER) AS gap_days
FROM seq s JOIN party p ON p.party_id=s.borrower_party_id
WHERE julianday(s.disbursed_on)-julianday(s.prev_disbursed) <= 3
ORDER BY gap_days, s.loan_id;"""),
    dict(
        id="BRB2-0246", difficulty="extra", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》：循环授信余额受合同金额约束，余额超合同表明支用超限或风险敞口失控。",
        penalty_fact_zh="检测发现循环授信项下借据期末余额超过合同金额，循环支用失控，超额资产负债敞口。",
        question="循环授信项下借据期末余额超过授信合同金额，余额超合同反映循环支用失控。输出授信合同编号、合同金额、期末借据余额合计、超合同余额，仅列出循环授信项下期末余额大于合同金额的记录，按超合同余额降序排列，再按授信合同编号升序排列。",
        sql="""WITH bal AS (
  SELECT ld.agreement_id, SUM(lbs.principal_balance) AS cur_balance
  FROM loan_balance_snapshot lbs
  JOIN loan_drawdown ld ON ld.loan_id=lbs.loan_id
  JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
  JOIN credit_facility f ON f.facility_id=a.facility_id AND f.facility_type='REVOLVING'
  GROUP BY ld.agreement_id
)
SELECT a.agreement_id, ROUND(a.contract_amount,2) AS contract_amount,
       ROUND(bal.cur_balance,2) AS current_balance,
       ROUND(bal.cur_balance - a.contract_amount,2) AS excess
FROM bal JOIN credit_agreement a ON a.agreement_id=bal.agreement_id
WHERE bal.cur_balance > a.contract_amount
ORDER BY excess DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0247", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》：流动资金贷款期限应与生产经营周期匹配，原则上原则一年期以内，短贷长用属期限错配违规。",
        penalty_fact_zh="检测发现流动资金类借据配置超长期限，短期资金长期占用，期限错配加大流动性风险。",
        question="流动资金类贷款被配置为超过730天的超长期限，短期流动资金被用作长期用途，存在短贷长用风险。输出借据编号、贷款品种中文名称、放款日期、原始到期日、按30天折算的期限月数（取整）与放款金额，仅列出属于流动资金贷款品种且原始到期日与放款日相差超过730天的借据，按折算期限月数降序、借据编号升序排列，只取前两百条。",
        sql="""SELECT ld.loan_id, lp.product_name_zh, ld.disbursed_on, ld.original_maturity_on,
       CAST((julianday(ld.original_maturity_on)-julianday(ld.disbursed_on))/30.0 AS INTEGER) AS tenor_months,
       ROUND(ld.disbursed_amount,2) AS amount
FROM loan_drawdown ld
JOIN loan_product_catalog lp ON lp.product_code=ld.drawdown_type
WHERE lp.is_working_capital=1
  AND (julianday(ld.original_maturity_on)-julianday(ld.disbursed_on)) > 730
ORDER BY tenor_months DESC, ld.loan_id
LIMIT 200;"""),
    dict(
        id="BRB2-0248", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：授信合同应先行签署生效后方可放款，先放后签属逆程序授信操作。",
        penalty_fact_zh="检测发现多笔贷款放款日期早于授信合同签署日期，逆流程放款，合同时效性存疑。",
        question="贷款放款日期早于授信合同签署日期，先放款后补签合同，属逆流程操作。输出借据编号、放款日期、授信合同编号、合同签署日期、放款金额，仅列出放款日期早于合同签署日期的记录，按借据编号升序排列。",
        sql="""SELECT ld.loan_id, ld.disbursed_on, a.agreement_id, a.signed_on, ROUND(ld.disbursed_amount,2) AS amount
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
WHERE ld.disbursed_on < a.signed_on
ORDER BY ld.loan_id;"""),
    dict(
        id="BRB2-0249", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》",
        penalty_fact_zh="押品实物与状态管理不审慎，抵质押品存续期监控不到位",
        question="按押品种类统计处于正常状态的押品数量，输出押品种类与押品数量，按数量从多到少排列。",
        sql="""SELECT collateral_type, COUNT(*) AS cnt
FROM collateral_asset
WHERE status = 'ACTIVE'
GROUP BY collateral_type
ORDER BY cnt DESC, collateral_type;"""),
    dict(
        id="BRB2-0250", difficulty="hard", features=[],
        penalty_law_zh="《商业银行内部控制指引》第四十六条",
        penalty_fact_zh="用工与员工行为管理不到位，员工行为监控机制不健全",
        question="在处于有效或已结清状态的借据中，汇总各借据已归还的到期本金，并依放款金额由高到低排序后仅取前三十名，输出借据编号、放款金额与已归还本金合计，按放款金额降序排列。",
        sql="""WITH base AS (
  SELECT loan_id, disbursed_amount FROM loan_drawdown WHERE status IN ('ACTIVE','SETTLED')
),
paid AS (
  SELECT loan_id, SUM(principal_due) AS tot FROM repayment_schedule WHERE status = 'PAID' GROUP BY loan_id
),
ranked AS (
  SELECT loan_id, disbursed_amount,
         ROW_NUMBER() OVER (ORDER BY disbursed_amount DESC) AS rr
  FROM base
)
SELECT r.loan_id, r.disbursed_amount, p.tot
FROM ranked r
JOIN paid p ON p.loan_id = r.loan_id
WHERE r.rr <= 30
ORDER BY r.rr;"""),
    dict(
        id="BRB2-0251", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：同一授信合同项下新旧借据首尾衔接式更新，可能以新贷还旧贷掩盖真实风险。",
        penalty_fact_zh="检测发现同一授信合同下新借据放款紧接旧借据到期，形成借新还旧衔接，疑似掩盖违约。",
        question="同一授信合同下新旧借据首尾衔接，新借据放款日紧接旧借据到期日，涉嫌以新贷还旧贷。输出授信合同编号、前手借据编号、前手原到期日、后手借据编号、后手放款日、衔接间隔天数，仅列出后手放款日不早于前手到期日且间隔小于30天的记录，按衔接间隔升序排列，再按授信合同编号升序排列。",
        sql="""SELECT a.agreement_id, d1.loan_id AS old_loan_id, d1.original_maturity_on AS old_maturity,
       d2.loan_id AS new_loan_id, d2.disbursed_on AS new_disbursed,
       CAST(julianday(d2.disbursed_on)-julianday(d1.original_maturity_on) AS INTEGER) AS gap_days
FROM loan_drawdown d1
JOIN credit_agreement a ON a.agreement_id=d1.agreement_id
JOIN loan_drawdown d2 ON d2.agreement_id=d1.agreement_id AND d2.loan_id<>d1.loan_id
WHERE julianday(d2.disbursed_on)-julianday(d1.original_maturity_on) < 30
  AND julianday(d2.disbursed_on)-julianday(d1.original_maturity_on) >= 0
ORDER BY gap_days, a.agreement_id;"""),
    dict(
        id="BRB2-0252", difficulty="extra", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：应收集汇总客户多头授信情况，多头大额授信存在集中度与过度负债风险。",
        penalty_fact_zh="检测发现同一借款人在多家机构同时持有未结清借据，多头授信集中，存在过度负债风险。",
        question="借款人在多家不同机构同时持有未结清借据，多头授信风险敞口集中。输出借款人编号、借款人名称、涉及机构家数、借据笔数、累计放款金额，仅列出同时在2家及以上机构持有正常借据的借款人，按借据笔数降序排列，再按借款人编号升序排列。",
        sql="""SELECT a.borrower_party_id, p.display_name, COUNT(DISTINCT a.institution_id) AS inst_cnt,
       COUNT(DISTINCT ld.loan_id) AS loan_cnt, ROUND(SUM(ld.disbursed_amount),2) AS total_disbursed
FROM credit_agreement a
JOIN party p ON p.party_id=a.borrower_party_id
JOIN loan_drawdown ld ON ld.agreement_id=a.agreement_id
WHERE ld.status='ACTIVE'
GROUP BY a.borrower_party_id, p.display_name
HAVING COUNT(DISTINCT a.institution_id) >= 2
ORDER BY loan_cnt DESC, a.borrower_party_id;"""),
    dict(
        id="BRB2-0253", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：借据各期均违约未按期还款，表明借款人丧失履约能力，应及时下调分类并催收。",
        penalty_fact_zh="检测发现部分借据全部还款期次均逾期、从未按期归还，借款人严重违约。",
        question="分期还款计划中没有任何一期处于已结清状态的借据，反映借款人从未完成整期正常结清。输出借据编号、未结清期次数与应还本金合计（保留两位小数），仅列出名下所有分期计划均无已结清记录的借据，按应还本金合计降序、借据编号升序排列，只取前两百条。",
        sql="""SELECT rs.loan_id, COUNT(*) AS overdue_cnt,
       ROUND(SUM(rs.principal_due),2) AS overdue_principal
FROM repayment_schedule rs
GROUP BY rs.loan_id
HAVING SUM(CASE WHEN rs.status='PAID' THEN 1 ELSE 0 END) = 0
ORDER BY overdue_principal DESC, rs.loan_id
LIMIT 200;"""),
    dict(
        id="BRB2-0254", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》及反洗钱监管要求：贷款资金应流入约定用途账户，大规模转入储蓄户涉嫌资金挪用回流。",
        penalty_fact_zh="检测发现贷款发放账户大额资金转入储蓄类账户，资金去向与借款用途不符，需穿透核查。",
        question="作为借据放款账户的银行账户发生单笔超过十万元的已结算转账交易，且收款账户为储蓄账户，疑似信贷资金从放款账户回流或挪用至储蓄账户。输出转账流水编号、转出放款账户编号、收款储蓄账户编号、收款账户种类与转账金额（保留两位小数），仅列出转出账户存在于借据放款账户中、已结算、转账类型且收款账户为储蓄账户的单笔超十万元交易，按转账流水编号升序排列，只取前三百条。",
        sql="""SELECT pe.payment_id, pe.from_account_id, ac2.account_id AS dest_account,
       ac2.account_kind AS dest_kind, ROUND(pe.amount, 2) AS amount
FROM payment_event pe
JOIN account ac2 ON ac2.account_id = pe.to_account_id
WHERE pe.payment_type = 'TRANSFER' AND pe.status = 'SETTLED'
  AND ac2.account_kind = 'SAVINGS' AND pe.amount > 100000
  AND EXISTS (SELECT 1 FROM loan_drawdown ld WHERE ld.disbursement_account_id = pe.from_account_id)
ORDER BY pe.payment_id
LIMIT 300;"""),
    dict(
        id="BRB2-0255", difficulty="extra", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：逾期本金与分期还款计划应一致真实，两者矛盾反映台账管理混乱或数据造假。",
        penalty_fact_zh="检测发现余额口径显示存在逾期本金但分期还款计划无逾期记录，逾期数据矛盾，台账可信度存疑。",
        question="贷后余额显示存在逾期本金，但借据的分期还款计划中并无任何逾期期次，逾期信息台账间矛盾。输出借据编号、期末账载逾期本金，仅列出账载有逾期本金但还款计划无逾期期次的借据，按期末账载逾期本金降序排列，再按借据编号升序排列。",
        sql="""SELECT lb.loan_id, ROUND(lb.overdue_principal,2) AS overdue_principal
FROM loan_balance_snapshot lb
WHERE lb.overdue_principal > 0
  AND NOT EXISTS (SELECT 1 FROM repayment_schedule rs WHERE rs.loan_id=lb.loan_id AND rs.status='OVERDUE')
ORDER BY overdue_principal DESC, lb.loan_id;"""),
    dict(
        id="BRB2-0256", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》及《商业银行授信工作尽职指引》：单笔放款不得超过合同批复金额，超金额投放属越权。",
        penalty_fact_zh="检测发现单笔借据放款金额即超过授信合同金额，超批复投放风险突出。",
        question="授信合同中借据放款金额超过合同金额的单笔投放，单笔即超批复规模。输出借据编号、放款日期、授信合同编号、合同金额、单笔放款金额，仅列出单笔放款金额大于合同金额的记录，按单笔放款金额降序排列，再按借据编号升序排列。",
        sql="""SELECT ld.loan_id, ld.disbursed_on, a.agreement_id, ROUND(a.contract_amount,2) AS contract_amount,
       ROUND(ld.disbursed_amount,2) AS disbursed_amount
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id=ld.agreement_id
WHERE ld.disbursed_amount > a.contract_amount
ORDER BY disbursed_amount DESC, ld.loan_id;"""),
    dict(
        id="BRB2-0257", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：利率定价应反映风险成本，显著低于同业平均执行利率涉嫌低息竞争或利益输送。",
        penalty_fact_zh="检测发现部分授信合同执行利率显著低于同目标行业均值，定价异常偏低，涉嫌变相让利或定价失当。",
        question="授信合同定价低于同行业（同一目标行业）平均执行利率的九成，涉嫌低息放贷或变相让利。输出授信合同编号、借款人名称、执行年利率、所属目标行业平均利率、较行业平均下浮百分比，仅列出执行利率低于同行业均值九成的记录，按下浮百分比升序排列，再按授信合同编号升序排列。",
        sql="""WITH ia AS (
  SELECT target_industry_code, AVG(annual_interest_rate) AS avg_rate
  FROM credit_agreement GROUP BY target_industry_code
)
SELECT a.agreement_id, p.display_name, ROUND(a.annual_interest_rate,4) AS annual_rate,
       ROUND(ia.avg_rate,4) AS industry_avg,
       ROUND(a.annual_interest_rate*100/ia.avg_rate-100,2) AS discount_pct
FROM credit_agreement a
JOIN ia ON ia.target_industry_code=a.target_industry_code
JOIN party p ON p.party_id=a.borrower_party_id
WHERE a.annual_interest_rate < 0.9 * ia.avg_rate
ORDER BY discount_pct, a.agreement_id;"""),
    dict(
        id="BRB2-0258", difficulty="extra", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》及绿色/产业结构政策：对限制类、退出类行业应压降授信，不得新增盲目投放。",
        penalty_fact_zh="检测发现存在授信投向限制类或退出类行业的合同，行业政策顺应性不足，需限期压降退出。",
        question="授信资金投向监管限制类或退出类行业，贷款投向脱离产业政策导向。输出授信合同编号、借款投向行业名称、行业风险类别、合同金额、借款人名称，仅列出借款投向行业属于限制类或退出类的授信合同，按授信合同编号升序排列。",
        sql="""SELECT a.agreement_id, s.sector_name_zh, s.risk_category,
       ROUND(a.contract_amount,2) AS contract_amount, p.display_name
FROM credit_agreement a
JOIN industry_sector s ON s.sector_code=a.target_industry_code
JOIN party p ON p.party_id=a.borrower_party_id
WHERE s.risk_category IN ('EXIT','RESTRICTED')
ORDER BY a.agreement_id;"""),
    dict(
        id="BRB2-0259", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》及核销管理规定：核销后应停止核算，仍挂账表明核销或账务处理不当。",
        penalty_fact_zh="检测发现已核销借据仍存在期末余额与逾期挂账，核销处理不彻底，账实不符。",
        question="借据状态已标记为核销，但在贷款余额快照中期末剩余本金仍超过一千万元，反映大额核销后账面本金未清零。输出借据编号、期末剩余本金与期末逾期本金（保留两位小数），仅列出已核销且期末剩余本金超过一千万元的借据，按期末剩余本金降序、借据编号升序排列，只取前两百条。",
        sql="""SELECT ld.loan_id, ROUND(lbs.principal_balance, 2) AS balance, ROUND(lbs.overdue_principal, 2) AS overdue_principal
FROM loan_drawdown ld
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
WHERE ld.status = 'WRITTEN_OFF' AND lbs.principal_balance > 10000000
ORDER BY lbs.principal_balance DESC, ld.loan_id
LIMIT 200;"""),
    dict(
        id="BRB2-0260", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：贷款应发放至已开立的借款人账户，账户未开即放款属操作时序异常。",
        penalty_fact_zh="检测发现多笔借据放款日期早于发放账户的开立日期，放款时序倒挂，账户管理异常。",
        question="贷款放款日期早于发放账户的账户开立日期，账户未开立即发放贷款，账户与放款时序倒挂。输出借据编号、放款日期、发放账户编号、账户开立日期，仅列出放款日期早于发放账户开立日期的记录，按放款日期升序排列，再按借据编号升序排列。",
        sql="""SELECT ld.loan_id, ld.disbursed_on, ac.account_id, ac.opened_on
FROM loan_drawdown ld
JOIN account ac ON ac.account_id=ld.disbursement_account_id
WHERE ld.disbursed_on < ac.opened_on
ORDER BY ld.disbursed_on, ld.loan_id;"""),
    dict(
        id="BRB2-0261", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》及资金用途监管：贷款资金应进入对公结算账户按约定用途支付，进入储蓄户涉嫌挪用归集。",
        penalty_fact_zh="检测发现多笔贷款发放至储蓄类账户，资金归集形态异常，需穿透核查真实投向。",
        question="贷款发放账户为储蓄类账户，贷款资金进入个人储蓄户，疑为资金归集或挪用。输出借据编号、发放账户编号、账户类型、放款金额，仅列出发放账户为储蓄类的借据，按放款金额降序排列，再按借据编号升序排列。",
        sql="""SELECT ld.loan_id, ac.account_id, ac.account_kind, ROUND(ld.disbursed_amount,2) AS amount
FROM loan_drawdown ld
JOIN account ac ON ac.account_id=ld.disbursement_account_id
WHERE ac.account_kind='SAVINGS'
ORDER BY amount DESC, ld.loan_id;"""),
    dict(
        id="BRB2-0262", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》：大额授信应配置足额担保落实第二还款来源，纯信用大额放款风险缓释缺失。",
        penalty_fact_zh="检测发现多笔大额授信采用纯信用方式且无抵押质押，缺乏有效风险缓释，风险敞口偏大。",
        question="无抵质押担保的信用放款金额过大，授信缺乏风险缓释安排。输出授信合同编号、担保方式、合同金额、借款人名称，仅列出采用信用方式且合同金额超过800万元的记录，按合同金额降序排列，再按授信合同编号升序排列。",
        sql="""SELECT a.agreement_id, a.security_type, ROUND(a.contract_amount,2) AS contract_amount,
       p.display_name
FROM credit_agreement a
JOIN party p ON p.party_id=a.borrower_party_id
WHERE a.security_type='CREDIT' AND a.contract_amount > 8000000
ORDER BY contract_amount DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0263", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第四十条、《商业银行与内部人和股东关联交易管理办法》",
        penalty_fact_zh="向关联方发放优惠利率贷款，利率显著低于同机构同类产品平均水平，构成违反公允原则的关联交易",
        question="针对本行存在关联关系的借款客户（剔除“非关联方”记录），查出其贷款合同年利率低于所在机构同类产品平均年利率的合同，输出借款人名称、客户编号、合同年利率、同机构同类产品平均年利率与利率价差，按利率价差降序排列。",
        sql="""WITH fam_avg AS (
  SELECT institution_id, product_family, AVG(annual_interest_rate) AS fam_rate
  FROM credit_agreement
  GROUP BY institution_id, product_family
)
SELECT p.display_name AS 借款人名称, a.borrower_party_id AS 客户编号,
       a.annual_interest_rate AS 合同年利率,
       ROUND(fa.fam_rate, 4) AS 同类产品平均利率,
       ROUND(fa.fam_rate - a.annual_interest_rate, 4) AS 利率价差
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
JOIN fam_avg fa ON fa.institution_id = a.institution_id AND fa.product_family = a.product_family
WHERE a.annual_interest_rate < fa.fam_rate
  AND EXISTS (SELECT 1 FROM party_relation pr
              JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
              WHERE (pr.source_party_id = a.borrower_party_id OR pr.target_party_id = a.borrower_party_id)
                AND rc.relation_name_zh <> '非关联方')
ORDER BY 利率价差 DESC, a.borrower_party_id;"""),
    dict(
        id="BRB2-0264", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第四十条、《商业银行与内部人和股东关联交易管理办法》",
        penalty_fact_zh="向关联方违规发放信用（无担保）贷款，未执行担保要求即发放贷款",
        question="针对被本行确认为关联方的借款客户（剔除“非关联方”），统计其以信用方式（无担保）取得的贷款合同，输出借款人名称、客户编号、信用贷款笔数、授信金额合计，按授信金额合计降序排列。",
        sql="""WITH related AS (
  SELECT DISTINCT pr.source_party_id AS pid FROM party_relation pr
  JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
  WHERE rc.relation_name_zh <> '非关联方'
  UNION
  SELECT DISTINCT pr.target_party_id FROM party_relation pr
  JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
  WHERE rc.relation_name_zh <> '非关联方'
)
SELECT p.display_name AS 借款人名称, a.borrower_party_id AS 客户编号,
       COUNT(DISTINCT a.agreement_id) AS 信用贷款笔数,
       ROUND(SUM(a.contract_amount), 2) AS 授信金额合计
FROM related r
JOIN credit_agreement a ON a.borrower_party_id = r.pid
JOIN party p ON p.party_id = a.borrower_party_id
WHERE a.security_type = 'CREDIT'
GROUP BY p.display_name, a.borrower_party_id
ORDER BY 授信金额合计 DESC, a.borrower_party_id;"""),
    dict(
        id="BRB2-0265", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第四十条、《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="关联企业对公授信集中度过高，未按关联集团统一授信管控",
        question="按理财产品计算其持仓资产的公允价值排名与平均公允价值，找出单笔持仓公允价值超过其产品平均持仓公允价值一点五倍的资产，输出产品名称、资产编号、公允价值、排名与该产品平均公允价值，按排名升序排列。",
        sql="""WITH scores AS (
  SELECT hl.product_id, hl.asset_id, ROUND(hl.fair_value,2) AS fair_value,
         RANK() OVER (PARTITION BY hl.product_id ORDER BY hl.fair_value DESC) AS rk,
         ROUND(AVG(hl.fair_value) OVER (PARTITION BY hl.product_id),2) AS avg_v
  FROM product_holding_snapshot hl
)
SELECT p.product_name, hp.asset_id, hp.fair_value, hp.rk, hp.avg_v
FROM scores hp JOIN wealth_product p ON p.product_id=hp.product_id
WHERE hp.fair_value > 1.5*hp.avg_v
ORDER BY hp.rk ASC, hp.product_id;"""),
    dict(
        id="BRB2-0266", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》、《中华人民共和国商业银行法》第三十九条",
        penalty_fact_zh="关联方双方均在本行借款，存在连环授信、风险叠加未统一识别",
        question="查出存在关联关系且双方客户均在本行取得贷款的关系对（剔除“非关联方”记录），输出关联方甲方编号、关联方乙方编号与关联关系名称，按关联关系名称、关系记录编号升序排列。",
        sql="""WITH borrowers AS (
  SELECT DISTINCT borrower_party_id AS pid FROM credit_agreement
)
SELECT pr.source_party_id AS 甲方编号, pr.target_party_id AS 乙方编号,
       rc.relation_name_zh AS 关联关系名称
FROM party_relation pr
JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
JOIN borrowers b1 ON b1.pid = pr.source_party_id
JOIN borrowers b2 ON b2.pid = pr.target_party_id
WHERE rc.relation_name_zh <> '非关联方'
ORDER BY rc.relation_name_zh, pr.relation_id;"""),
    dict(
        id="BRB2-0267", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第四十条、《商业银行与内部人和股东关联交易管理办法》",
        penalty_fact_zh="关联方授信形成逾期，关联贷款风险敞口未及时预警与压降",
        question="按敞口集团汇总其成员在本行的贷款本金余额合计，并与其主办机构资本净额比较计算占比，输出集团名称、成员数、余额合计、资本净额与占比，只保留成员不少于两人且占比超过一成的集团，按占比降序排列，只取前两百条（仅统计主办机构自身签署的授信合同项下借据）。",
        sql="""SELECT eg.group_name, COUNT(DISTINCT egm.party_id) AS members,
       ROUND(SUM(lbs.principal_balance),2) AS bal, ROUND(cs.net_capital,2) AS cap,
       ROUND(SUM(lbs.principal_balance)*1.0/cs.net_capital,6) AS ratio
FROM exposure_group eg
JOIN exposure_group_member egm ON egm.exposure_group_id=eg.exposure_group_id
JOIN credit_agreement a ON a.borrower_party_id=egm.party_id AND a.institution_id=eg.institution_id
JOIN loan_drawdown ld ON ld.agreement_id=a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id=ld.loan_id
JOIN capital_snapshot cs ON cs.institution_id=eg.institution_id
GROUP BY eg.exposure_group_id, eg.group_name
HAVING COUNT(DISTINCT egm.party_id)>=2 AND SUM(lbs.principal_balance)*1.0/cs.net_capital>0.1
ORDER BY ratio DESC, eg.group_name
LIMIT 200;"""),
    dict(
        id="BRB2-0268", difficulty="extra", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="关联方之间异常资金往来未识别，可能存在资金回流出借或虚增流水的关联交易",
        question="通过账户持有人关系与客户关联关系穿透，查出转账资金往来双方存在关联关系的交易（剔除“非关联方”记录），输出付款方姓名、收款方姓名、转账笔数与转账金额合计，按转账金额合计降序排列。",
        sql="""SELECT pf.display_name AS 付款方姓名, pt.display_name AS 收款方姓名,
       COUNT(*) AS 转账笔数,
       ROUND(SUM(pe.amount), 2) AS 转账金额合计
FROM payment_event pe
JOIN account_holder hf ON hf.account_id = pe.from_account_id AND hf.holder_role = 'PRIMARY'
JOIN party pf ON pf.party_id = hf.party_id
JOIN account_holder ht ON ht.account_id = pe.to_account_id AND ht.holder_role = 'PRIMARY'
JOIN party pt ON pt.party_id = ht.party_id
JOIN party_relation pr ON ((pr.source_party_id = hf.party_id AND pr.target_party_id = ht.party_id)
                        OR (pr.source_party_id = ht.party_id AND pr.target_party_id = hf.party_id))
JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
WHERE rc.relation_name_zh <> '非关联方'
GROUP BY pf.display_name, pt.display_name, hf.party_id, ht.party_id
ORDER BY 转账金额合计 DESC, hf.party_id, ht.party_id;"""),
    dict(
        id="BRB2-0269", difficulty="easy", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="多种关联关系客户群均在本行获贷，关联授信未按集团统一识别",
        question="统计各类关联关系下在本行实际取得贷款的目标方客户数量，输出关联关系名称与借到款的目标客户数，按目标客户数降序排列。",
        sql="""SELECT rc.relation_name_zh AS 关联关系名称,
       COUNT(DISTINCT pr.target_party_id) AS 目标借款客户数
FROM party_relation pr
JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
WHERE rc.relation_name_zh <> '非关联方'
  AND EXISTS (SELECT 1 FROM credit_agreement a WHERE a.borrower_party_id = pr.target_party_id)
GROUP BY rc.relation_name_zh
ORDER BY 目标借款客户数 DESC, rc.relation_name_zh;"""),
    dict(
        id="BRB2-0270", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行理财业务监督管理办法》",
        penalty_fact_zh="理财产品销售适当性失当、向不合格投资者错配高风险产品或底层非标资产穿透违规",
        question="筛选底层持仓路径为多层嵌套且产品风险等级为最高级（R5级）的在售理财产品，输出产品编号、产品名称与对应底层资产名称，按产品编号升序排列。",
        sql="""SELECT wp.product_id, wp.product_name, ma.asset_name
FROM wealth_product wp
JOIN product_holding_snapshot ph ON ph.product_id = wp.product_id
JOIN managed_asset ma ON ma.asset_id = ph.asset_id
WHERE ph.investment_path = 'NESTED_SPV' AND wp.risk_level = 'R5' AND wp.status = 'ON_SALE'
ORDER BY wp.product_id, ma.asset_id;"""),
    dict(
        id="BRB2-0271", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行理财业务监督管理办法》",
        penalty_fact_zh="理财产品销售适当性失当、向不合格投资者错配高风险产品或底层非标资产穿透违规",
        question="统计各金融机构发行的、其底层资产为负债类目的产品数量，只保留产品数量不少于二十只的发行机构，输出机构名称与产品数量，按产品数量降序排列。",
        sql="""SELECT i.institution_name, COUNT(DISTINCT wp.product_id) AS prod_cnt
FROM wealth_product wp
JOIN product_holding_snapshot ph ON ph.product_id = wp.product_id
JOIN managed_asset ma ON ma.asset_id = ph.asset_id
JOIN institution i ON i.institution_id = wp.issuer_institution_id
WHERE ma.is_liability = 1
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(DISTINCT wp.product_id) >= 20
ORDER BY prod_cnt DESC, i.institution_name;"""),
    dict(
        id="BRB2-0272", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行理财业务监督管理办法》",
        penalty_fact_zh="理财产品销售适当性失当、向不合格投资者错配高风险产品或底层非标资产穿透违规",
        question="按发卡年份统计贷记卡与借记卡的发卡数量，输出发卡年份、贷记卡发卡量、借记卡发卡量，按发卡年份升序排列。",
        sql="""SELECT SUBSTR(c.issued_on,1,4) AS yr,
       SUM(CASE WHEN t.name_zh='贷记卡' THEN 1 ELSE 0 END) AS credit_cnt,
       SUM(CASE WHEN t.name_zh='借记卡' THEN 1 ELSE 0 END) AS debit_cnt
FROM payment_card c JOIN card_type_catalog t ON t.card_type=c.card_type
GROUP BY SUBSTR(c.issued_on,1,4)
ORDER BY yr;"""),
    dict(
        id="BRB2-0273", difficulty="hard", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="集团客户成员在多个分支行多头分散授信，规避单一客户限额管理",
        question="查出其成员客户在五个及以上不同经办营业机构单元获得贷款合同的敞口集团，输出集团编号、集团名称、敞口类型、涉及经办分支行数与集团授信金额合计，按涉及经办分支行数降序排列。",
        sql="""WITH grp_branch AS (
  SELECT egm.exposure_group_id AS gid,
         COUNT(DISTINCT a.managing_org_unit_id) AS branch_cnt,
         ROUND(SUM(a.contract_amount), 2) AS group_amount
  FROM exposure_group_member egm
  JOIN credit_agreement a ON a.borrower_party_id = egm.party_id
  GROUP BY egm.exposure_group_id
)
SELECT eg.exposure_group_id AS 集团编号, eg.group_name AS 集团名称,
       egt.name_zh AS 敞口类型, g.branch_cnt AS 涉及经办分支行数,
       g.group_amount AS 集团授信合计
FROM grp_branch g
JOIN exposure_group eg ON eg.exposure_group_id = g.gid
JOIN exposure_group_type_catalog egt ON egt.group_type = eg.group_type
WHERE g.branch_cnt >= 5
ORDER BY g.branch_cnt DESC, eg.exposure_group_id;"""),
    dict(
        id="BRB2-0274", difficulty="extra", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行理财业务监督管理办法》",
        penalty_fact_zh="理财产品销售适当性失当、向不合格投资者错配高风险产品或底层非标资产穿透违规",
        question="统计每只理财产品所配置的底层投资路径为多层中介产品的资产数量，只输出资产数量最多的前二十只产品，给出产品编号与资产数量，按资产数量降序排列。",
        sql="""SELECT ph.product_id, COUNT(*) AS asset_cnt
FROM product_holding_snapshot ph
WHERE ph.investment_path = 'NESTED_SPV'
GROUP BY ph.product_id
ORDER BY asset_cnt DESC, ph.product_id
LIMIT 20;"""),
    dict(
        id="BRB2-0275", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行理财业务监督管理办法》",
        penalty_fact_zh="理财产品销售适当性失当、向不合格投资者错配高风险产品或底层非标资产穿透违规",
        question="汇总账面本金余额高于九千万且存在逾期本金的借据，统计其最长逾期天数，仅保留最长逾期天数不低于二百天的借据，输出借据编号、账面本金余额与最长逾期天数，按最长逾期天数降序、借据编号升序排列（逾期本金以贷款余额快照中的逾期本金为准，最长逾期天数取该借据全部逾期快照记录的最大值）。",
        sql="""SELECT lb.loan_id,
       lb.principal_balance,
       MAX(ds.principal_overdue_days) AS max_days
FROM loan_balance_snapshot lb
JOIN delinquency_snapshot ds ON ds.loan_id = lb.loan_id
WHERE lb.overdue_principal > 0
  AND lb.principal_balance > 90000000
GROUP BY lb.loan_id, lb.principal_balance
HAVING MAX(ds.principal_overdue_days) >= 200
ORDER BY max_days DESC, lb.loan_id;"""),
    dict(
        id="BRB2-0276", difficulty="extra", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》、《中华人民共和国商业银行法》第三十九条",
        penalty_fact_zh="集团客户授信集中度超过机构资本净额比例上限，大额风险暴露失控",
        question="统计各敞口集团成员在本行的授信金额合计，并与所在机构资本净额比对，查出集团授信占资本净额比重过高的集团，输出集团编号、集团名称、机构名称、集团授信合计、机构资本净额与集中度占比，按集中度占比降序排列。",
        sql="""WITH grp_amt AS (
  SELECT egm.exposure_group_id AS gid, SUM(a.contract_amount) AS group_amount
  FROM exposure_group_member egm
  JOIN credit_agreement a ON a.borrower_party_id = egm.party_id
  GROUP BY egm.exposure_group_id
)
SELECT eg.exposure_group_id AS 集团编号, eg.group_name AS 集团名称,
       i.institution_name AS 机构名称,
       ROUND(g.group_amount, 2) AS 集团授信合计,
       ROUND(cs.net_capital, 2) AS 机构资本净额,
       ROUND(g.group_amount * 100 / cs.net_capital, 2) AS 集中度占比
FROM grp_amt g
JOIN exposure_group eg ON eg.exposure_group_id = g.gid
JOIN institution i ON i.institution_id = eg.institution_id
JOIN capital_snapshot cs ON cs.institution_id = eg.institution_id
WHERE g.group_amount * 100 > cs.net_capital
ORDER BY 集中度占比 DESC, eg.exposure_group_id;"""),
    dict(
        id="BRB2-0277", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="集团客户跨机构多头授信，未实现联网联合审批与集团限额共享",
        question="查出成员客户在两个及以上不同机构取得贷款的敞口集团，输出集团编号、集团名称、涉及机构数与取得授信的成员数，按涉及机构数降序排列。",
        sql="""SELECT eg.exposure_group_id AS 集团编号, eg.group_name AS 集团名称,
       COUNT(DISTINCT a.institution_id) AS 涉及机构数,
       COUNT(DISTINCT egm.party_id) AS 授信成员数
FROM exposure_group eg
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
JOIN credit_agreement a ON a.borrower_party_id = egm.party_id
GROUP BY eg.exposure_group_id, eg.group_name
HAVING COUNT(DISTINCT a.institution_id) >= 2
ORDER BY 涉及机构数 DESC, eg.exposure_group_id;"""),
    dict(
        id="BRB2-0278", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="集团内多头借款户数庞大，集团整体授信管理缺失",
        question="按集团类型统计成员授信规模最大的集团，输出集团类型、集团名称、成员数与借款合同数，按借款合同数降序排列并取前十五条。",
        sql="""SELECT egt.name_zh AS 集团类型, eg.group_name AS 集团名称,
       COUNT(DISTINCT egm.party_id) AS 成员数,
       COUNT(DISTINCT a.agreement_id) AS 借款合同数
FROM exposure_group eg
JOIN exposure_group_type_catalog egt ON egt.group_type = eg.group_type
LEFT JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
LEFT JOIN credit_agreement a ON a.borrower_party_id = egm.party_id
GROUP BY egt.name_zh, eg.exposure_group_id, eg.group_name
ORDER BY 借款合同数 DESC, eg.exposure_group_id
LIMIT 15;"""),
    dict(
        id="BRB2-0279", difficulty="hard", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="集团客户内部风险交叉传染，多个成员同时逾期而未及时压缩集团授信",
        question="统计各敞口集团成员中发生本金逾期的客户情况，输出集团编号、集团名称、逾期成员数与逾期本金合计，按逾期本金合计降序排列（逾期以贷款余额快照中的逾期本金大于零为准）。",
        sql="""WITH grp_ovd AS (
  SELECT egm.exposure_group_id AS gid,
         COUNT(DISTINCT egm.party_id) AS ovd_members,
         ROUND(SUM(lbs.overdue_principal), 2) AS ovd_amount
  FROM exposure_group_member egm
  JOIN credit_agreement a ON a.borrower_party_id = egm.party_id
  JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
  JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
  WHERE lbs.overdue_principal > 0
  GROUP BY egm.exposure_group_id
)
SELECT eg.exposure_group_id AS 集团编号, eg.group_name AS 集团名称,
       g.ovd_members AS 逾期成员数, g.ovd_amount AS 逾期本金合计
FROM grp_ovd g
JOIN exposure_group eg ON eg.exposure_group_id = g.gid
ORDER BY g.ovd_amount DESC, eg.exposure_group_id;"""),
    dict(
        id="BRB2-0280", difficulty="extra", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="集团成员间互保联保，风险在集团内部相互传染且对外担保过度",
        question="穿透集团成员担保链条，查出保证人与被担保授信合同的借款人同属于同一个敞口集团的保证人承诺记录，按保证人汇总输出保证人名称、保证人客户编号、集团内担保承诺笔数与保证金额合计（保留两位小数），按保证金额合计降序、保证人客户编号升序排列。",
        sql="""SELECT p.display_name AS 保证人名称, gc.guarantor_party_id AS 客户编号,
       COUNT(DISTINCT gc.commitment_id) AS 集团内担保笔数,
       ROUND(SUM(gc.guaranteed_amount), 2) AS 担保金额合计
FROM guarantor_commitment gc
JOIN party p ON p.party_id = gc.guarantor_party_id
WHERE EXISTS (
    SELECT 1
    FROM security_agreement sa
    JOIN secured_obligation so ON so.security_id = sa.security_id
    JOIN credit_agreement a ON a.agreement_id = so.agreement_id
    JOIN exposure_group_member egm1 ON egm1.party_id = gc.guarantor_party_id
    JOIN exposure_group_member egm2 ON egm2.party_id = a.borrower_party_id
    WHERE sa.security_id = gc.security_id
      AND egm1.exposure_group_id = egm2.exposure_group_id
)
GROUP BY p.display_name, gc.guarantor_party_id
ORDER BY 担保金额合计 DESC, gc.guarantor_party_id;"""),
    dict(
        id="BRB2-0281", difficulty="extra", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="排名靠前的巨量集团客户未加特别风险管控",
        question="对敞口集团的成员授信金额合计进行排名，输出名次、集团名称、集团授信合计与成员数，按授信金额合计降序排列并取前八名。",
        sql="""WITH grp AS (
  SELECT eg.exposure_group_id AS gid, eg.group_name AS gname,
         COUNT(DISTINCT egm.party_id) AS members,
         SUM(a.contract_amount) AS amount
  FROM exposure_group eg
  JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
  JOIN credit_agreement a ON a.borrower_party_id = egm.party_id
  GROUP BY eg.exposure_group_id, eg.group_name
)
SELECT ROW_NUMBER() OVER (ORDER BY grp.amount DESC, grp.gid) AS 名次,
       grp.gname AS 集团名称, ROUND(grp.amount, 2) AS 集团授信合计,
       grp.members AS 成员数
FROM grp
ORDER BY 集团授信合计 DESC, grp.gid
LIMIT 8;"""),
    dict(
        id="BRB2-0282", difficulty="extra", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="企业同时超额加杠杆对外担保，或有负债与表内授信风险重叠失控",
        question="查出既在本行取得贷款又对外提供担保的企业客户，且其对外担保金额合计高于自身贷款金额合计的客户，输出企业名称、客户编号、对外担保合计、自身借款合计与担保负债差额，按担保负债差额降序排列（对外担保金额指保证承诺的担保金额；自身借款合计按其作为借款人的授信合同金额汇总）。",
        sql="""WITH gs AS (
  SELECT gc.guarantor_party_id AS pid, SUM(gc.guaranteed_amount) AS g_total
  FROM guarantor_commitment gc
  GROUP BY gc.guarantor_party_id
),
bs AS (
  SELECT a.borrower_party_id AS pid, SUM(a.contract_amount) AS b_total
  FROM credit_agreement a
  GROUP BY a.borrower_party_id
)
SELECT p.display_name AS 企业名称, g.pid AS 客户编号,
       ROUND(g.g_total, 2) AS 对外担保合计,
       ROUND(bs.b_total, 2) AS 自身借款合计,
       ROUND(g.g_total - bs.b_total, 2) AS 担保负债差额
FROM gs g
JOIN bs ON bs.pid = g.pid
JOIN party p ON p.party_id = g.pid
WHERE p.party_type = 'CORPORATE' AND g.g_total > bs.b_total
ORDER BY 担保负债差额 DESC, g.pid;"""),
    dict(
        id="BRB2-0283", difficulty="easy", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》",
        penalty_fact_zh="关联方借款人通过外部担保变相规避关联授信限制",
        question="统计本行在职员工中同时又作为借款人取得授信合同的员工，输出员工姓名、员工编号与授信合同笔数，按合同笔数降序排列。",
        sql="""SELECT p.display_name, sm.staff_id, COUNT(a.agreement_id) AS cnt
FROM staff_member sm JOIN party p ON p.party_id=sm.person_party_id
JOIN credit_agreement a ON a.borrower_party_id=p.party_id
GROUP BY p.party_id
ORDER BY cnt DESC, sm.staff_id;"""),
    dict(
        id="BRB2-0284", difficulty="hard", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》、《中华人民共和国商业银行法》第三十五条",
        penalty_fact_zh="信贷档案担保属性与担保登记台账不一致，存在数据造假或担保管理疏漏",
        question="查出标注为无担保（信用）方式的贷款合同却存在担保覆盖记录的内部不一致情形，输出合同编号、借款人编号、担保方式与担保覆盖金额合计，按担保覆盖金额合计降序排列。",
        sql="""SELECT a.agreement_id AS 合同编号, a.borrower_party_id AS 借款人编号,
       a.security_type AS 担保方式,
       ROUND(SUM(so.covered_amount), 2) AS 担保覆盖合计
FROM credit_agreement a
JOIN secured_obligation so ON so.agreement_id = a.agreement_id
WHERE a.security_type = 'NONE'
GROUP BY a.agreement_id, a.borrower_party_id, a.security_type
HAVING SUM(so.covered_amount) > 0
ORDER BY 担保覆盖合计 DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0285", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="超额担保或重复担保导致单笔债权获得多重覆盖，或有负债虚增",
        question="查出单个担保合同担保覆盖金额高于借款人合同金额的记录，输出保证人名称、借款人名称、合同金额与担保覆盖金额，按担保覆盖金额降序排列。",
        sql="""SELECT pg.display_name AS 保证人名称, pb.display_name AS 借款人名称,
       ROUND(a.contract_amount, 2) AS 合同金额,
       ROUND(so.covered_amount, 2) AS 担保覆盖金额
FROM secured_obligation so
JOIN security_agreement sa ON sa.security_id = so.security_id
JOIN credit_agreement a ON a.agreement_id = so.agreement_id
JOIN party pb ON pb.party_id = a.borrower_party_id
JOIN guarantor_commitment gc ON gc.security_id = sa.security_id
JOIN party pg ON pg.party_id = gc.guarantor_party_id
WHERE so.covered_amount > a.contract_amount
  AND gc.status = 'ACTIVE'
ORDER BY so.covered_amount DESC, so.secured_obligation_id;"""),
    dict(
        id="BRB2-0286", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第五十二条、《严禁柜台违规行为防范案件风险的工作意见》",
        penalty_fact_zh="向本行员工发放优惠利率贷款，利益输送与内控缺陷",
        question="针对个人借款人汇总其在贷本金余额合计，并计算该余额合计占其个人画像年收入的倍数，输出借款人姓名、客户编号、本金余额合计、年收入与倍数，只保留倍数超过二的借款人，按倍数降序排列，只取前两百条（倍数保留两位小数）。",
        sql="""SELECT p.display_name, p.party_id, ROUND(SUM(lbs.principal_balance),2) AS bal, pp.annual_income,
       ROUND(SUM(lbs.principal_balance)*1.0/pp.annual_income,2) AS multiple
FROM person_profile pp JOIN party p ON p.party_id=pp.party_id
JOIN credit_agreement a ON a.borrower_party_id=p.party_id
JOIN loan_drawdown ld ON ld.agreement_id=a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id=ld.loan_id
GROUP BY p.party_id, pp.annual_income
HAVING SUM(lbs.principal_balance)*1.0/pp.annual_income>2
ORDER BY multiple DESC, p.party_id
LIMIT 200;"""),
    dict(
        id="BRB2-0287", difficulty="hard", features=[],
        penalty_law_zh="《严禁柜台违规行为防范案件风险的工作意见》、《中华人民共和国商业银行法》第五十二条",
        penalty_fact_zh="本行员工向对公客户异常转账，可能涉嫌协助资金体外循环或账外经营",
        question="查出本行员工个人账户向对公客户账户转账形成的资金往来，输出员工姓名、收款企业名称、转账笔数与转账金额合计，按转账金额合计降序排列并取前二十条。",
        sql="""WITH staff_acct AS (
  SELECT ah.account_id AS aid FROM account_holder ah
  JOIN party p ON p.party_id = ah.party_id
  WHERE p.party_type = 'STAFF' AND ah.holder_role = 'PRIMARY'
),
corp_acct AS (
  SELECT ah.account_id AS aid FROM account_holder ah
  JOIN party p ON p.party_id = ah.party_id
  WHERE p.party_type = 'CORPORATE' AND ah.holder_role = 'PRIMARY'
)
SELECT pf.display_name AS 员工姓名, pt.display_name AS 收款企业名称,
       COUNT(*) AS 转账笔数,
       ROUND(SUM(pe.amount), 2) AS 转账金额合计
FROM payment_event pe
JOIN staff_acct sf ON sf.aid = pe.from_account_id
JOIN corp_acct co ON co.aid = pe.to_account_id
JOIN account_holder hf ON hf.account_id = pe.from_account_id AND hf.holder_role = 'PRIMARY'
JOIN party pf ON pf.party_id = hf.party_id
JOIN account_holder ht ON ht.account_id = pe.to_account_id AND ht.holder_role = 'PRIMARY'
JOIN party pt ON pt.party_id = ht.party_id
GROUP BY pf.display_name, pt.display_name, hf.party_id, ht.party_id
ORDER BY 转账金额合计 DESC, hf.party_id, ht.party_id
LIMIT 20;"""),
    dict(
        id="BRB2-0288", difficulty="easy", features=[],
        penalty_law_zh="《严禁柜台违规行为防范案件风险的工作意见》、《中华人民共和国商业银行法》第五十二条",
        penalty_fact_zh="信贷岗位员工自贷，审贷不分、利益冲突未隔离",
        question="查出担任信贷客户经理角色的本行员工自身也在本行借款的情形，输出员工姓名、操作员编号、权限级别与自贷合同数，按自贷合同数降序排列（信贷客户经理指操作员类型为信贷经办员）。",
        sql="""SELECT p.display_name AS 员工姓名, so.operator_id AS 操作员编号,
       so.authority_level AS 权限级别, COUNT(DISTINCT a.agreement_id) AS 自贷合同数
FROM service_operator so
JOIN staff_member sm ON sm.staff_id = so.staff_id
JOIN party p ON p.party_id = sm.person_party_id
JOIN credit_agreement a ON a.borrower_party_id = p.party_id
WHERE so.operator_kind = 'CREDIT_OFFICER'
GROUP BY p.display_name, so.operator_id, sm.person_party_id, so.authority_level
ORDER BY 自贷合同数 DESC, so.operator_id;"""),
    dict(
        id="BRB2-0289", difficulty="hard", features=[],
        penalty_law_zh="《严禁柜台违规行为防范案件风险的工作意见》",
        penalty_fact_zh="员工与对公客户共用账户，存在代客理财/账外经营的账户操作风险",
        question="查出本行员工与对公客户共同持有同一账户的账户，输出员工姓名、机构名称、员工客户编号、涉事对公账户数，按涉事对公账户数降序排列。",
        sql="""SELECT p.display_name AS 员工姓名, p.party_id AS 员工客户编号,
       i.institution_name AS 机构名称,
       COUNT(DISTINCT ah.account_id) AS 涉事对公账户数
FROM account_holder ah
JOIN party p ON p.party_id = ah.party_id AND p.party_type = 'STAFF'
JOIN account a ON a.account_id = ah.account_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE EXISTS (SELECT 1 FROM account_holder ah2
              JOIN party p2 ON p2.party_id = ah2.party_id
              WHERE ah2.account_id = ah.account_id AND p2.party_type = 'CORPORATE')
GROUP BY p.display_name, p.party_id, i.institution_name
ORDER BY 涉事对公账户数 DESC, p.party_id;"""),
    dict(
        id="BRB2-0290", difficulty="medium", features=[],
        penalty_law_zh="《严禁柜台违规行为防范案件风险的工作意见》",
        penalty_fact_zh="贷款资金直接发放至员工账户，存在资金挪用与套取信贷资金风险",
        question="查出贷款放款款进入本行员工账户的借据，输出员工姓名、借据编号、放款金额与放款日期，按放款金额降序排列（仅统计员工作为账户主持有人的账户）。",
        sql="""SELECT p.display_name AS 员工姓名, ld.loan_id AS 借据编号,
       ROUND(ld.disbursed_amount, 2) AS 放款金额, ld.disbursed_on AS 放款日期
FROM loan_drawdown ld
JOIN account ac ON ac.account_id = ld.disbursement_account_id
JOIN account_holder ah ON ah.account_id = ac.account_id AND ah.holder_role = 'PRIMARY'
JOIN party p ON p.party_id = ah.party_id AND p.party_type = 'STAFF'
ORDER BY ld.disbursed_amount DESC, ld.loan_id;"""),
    dict(
        id="BRB2-0291", difficulty="hard", features=[],
        penalty_law_zh="《个人贷款管理暂行办法》第九条",
        penalty_fact_zh="个人借款人偿债能力失控，贷款余额远超年收入，贷前收入核验失真",
        question="针对个人借款人，查出其名下贷款本金余额合计超过其年收入两倍的借款人，输出借款人姓名、客户编号、年收入、贷款本金余额与债务收入倍数，按债务收入倍数降序排列。",
        sql="""SELECT p.display_name AS 借款人姓名, pp.party_id AS 客户编号,
       ROUND(pp.annual_income, 2) AS 年收入,
       ROUND(SUM(lbs.principal_balance), 2) AS 贷款本金余额,
       ROUND(SUM(lbs.principal_balance) / pp.annual_income, 2) AS 债务收入倍数
FROM person_profile pp
JOIN party p ON p.party_id = pp.party_id
JOIN credit_agreement a ON a.borrower_party_id = pp.party_id
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
GROUP BY p.display_name, pp.party_id, pp.annual_income
HAVING SUM(lbs.principal_balance) > 2 * pp.annual_income
ORDER BY 债务收入倍数 DESC, pp.party_id;"""),
    dict(
        id="BRB2-0292", difficulty="extra", features=[],
        penalty_law_zh="《个人贷款管理暂行办法》第九条",
        penalty_fact_zh="个人借款人年还款负担超过收入一半，还款能力严重不足仍发放贷款",
        question="针对个人借款人，按借款人汇总其名下全部分期还款计划的应还本息总额（应还本金加应还利息合计），并计算该应还本息总额占其个人画像年收入的倍数（保留两位小数），输出借款人姓名、借款人客户编号、个人年收入、应还本息总额与占年收入倍数，按占年收入倍数降序、客户编号升序排列，只取前五十名。",
        sql="""WITH borrower_due AS (
  SELECT a.borrower_party_id, SUM(rs.principal_due + rs.interest_due) AS total_due
  FROM repayment_schedule rs
  JOIN loan_drawdown ld ON ld.loan_id = rs.loan_id
  JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
  GROUP BY a.borrower_party_id
)
SELECT p.display_name AS 借款人姓名, pp.party_id AS 客户编号,
       ROUND(pp.annual_income, 2) AS 年收入,
       ROUND(bd.total_due, 2) AS 应还本息总额,
       ROUND(bd.total_due / pp.annual_income, 2) AS 占年收入倍数
FROM borrower_due bd
JOIN person_profile pp ON pp.party_id = bd.borrower_party_id
JOIN party p ON p.party_id = pp.party_id
ORDER BY 占年收入倍数 DESC, pp.party_id
LIMIT 50;"""),
    dict(
        id="BRB2-0293", difficulty="easy", features=[],
        penalty_law_zh="《个人贷款管理暂行办法》第九条",
        penalty_fact_zh="特定产品类别贷款逾期集中，贷后管理与资产质量下滑",
        question="按贷款产品类别统计逾期未归还的分期期数与逾期本金合计，输出产品类别名称、逾期期数与逾期本金合计，按逾期本金合计降序排列。",
        sql="""SELECT lpc.product_name_zh AS 产品类别名称,
       COUNT(rs.installment_id) AS 逾期期数,
       ROUND(SUM(rs.principal_due), 2) AS 逾期本金合计
FROM repayment_schedule rs
JOIN loan_drawdown ld ON ld.loan_id = rs.loan_id
JOIN loan_product_catalog lpc ON lpc.product_code = ld.drawdown_type
WHERE rs.status = 'OVERDUE'
GROUP BY lpc.product_name_zh
ORDER BY 逾期本金合计 DESC, lpc.product_name_zh;"""),
    dict(
        id="BRB2-0294", difficulty="medium", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》",
        penalty_fact_zh="关联方贷款逾期压力未能及时识别与催收",
        question="按月份分别统计现金交易与转账交易的笔数与金额合计，输出月份、交易类别、笔数与金额合计，按月份及类别升序排列。",
        sql="""SELECT ym, kind, COUNT(*) AS cnt, ROUND(SUM(amount),2) AS tot FROM (
  SELECT SUBSTR(e.business_date,1,7) AS ym, '现金' AS kind, e.amount FROM payment_event e WHERE e.is_cash=1
  UNION ALL
  SELECT SUBSTR(e.business_date,1,7), '转账', e.amount FROM payment_event e WHERE e.payment_type='TRANSFER'
)
GROUP BY ym, kind ORDER BY ym, kind;"""),
    dict(
        id="BRB2-0295", difficulty="easy", features=[],
        penalty_law_zh="《严禁柜台违规行为防范案件风险的工作意见》",
        penalty_fact_zh="员工账户高频大额现金交易，存在私自代客存取与现金案件风险",
        question="按开户机构将全部定期存款根据到期日距审计基准日（2026-06-30）的远近划分为已过期（到期日早于基准日）、九十天内到期（0至90天）与九十天以上到期三类池子，分别统计各机构在这三类池子中的定期存款笔数，仅保留已过期定期存款笔数不少于二十笔的机构，输出机构名称、已过期笔数、九十天内到期笔数与九十天以上到期笔数，按已过期笔数降序、机构名称升序排列。",
        sql="""SELECT i.institution_name,
       SUM(CASE WHEN julianday(td.maturity_on)-julianday('2026-06-30')<0 THEN 1 ELSE 0 END) AS expired_cnt,
       SUM(CASE WHEN julianday(td.maturity_on)-julianday('2026-06-30') BETWEEN 0 AND 90 THEN 1 ELSE 0 END) AS soon_cnt,
       SUM(CASE WHEN julianday(td.maturity_on)-julianday('2026-06-30')>90 THEN 1 ELSE 0 END) AS far_cnt
FROM term_deposit td
JOIN account a ON a.account_id = td.account_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_id, i.institution_name
HAVING SUM(CASE WHEN julianday(td.maturity_on)-julianday('2026-06-30')<0 THEN 1 ELSE 0 END) >= 20
ORDER BY expired_cnt DESC, i.institution_name;"""),
    dict(
        id="BRB2-0296", difficulty="easy", features=[],
        penalty_law_zh="《人民币银行结算账户管理办法》、《严禁柜台违规行为防范案件风险的工作意见》",
        penalty_fact_zh="联合账户数量异常，账户实名制与共管机制执行不到位",
        question="统计各营业机构单元名下由多个客户共同持有的联合账户数量，输出营业单元编号、营业单元名称与联合账户数量，按联合账户数量降序排列。",
        sql="""WITH multi AS (
  SELECT account_id FROM account_holder GROUP BY account_id HAVING COUNT(*) > 1
)
SELECT ou.org_unit_id AS 营业单元编号, ou.unit_name AS 营业单元名称,
       COUNT(DISTINCT m.account_id) AS 联合账户数量
FROM multi m
JOIN account a ON a.account_id = m.account_id
JOIN organization_unit ou ON ou.org_unit_id = a.org_unit_id
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY 联合账户数量 DESC, ou.org_unit_id;"""),
    dict(
        id="BRB2-0297", difficulty="medium", features=[],
        penalty_law_zh="《人民币银行结算账户管理办法》",
        penalty_fact_zh="账户资金净流入显著高于流出，疑似资金归集过渡账户，存在洗钱与账外经营嫌疑",
        question="对同时存在转入流水和转出流水的银行账户，对比其累計转入金额与累计转出金额，找出净流入金额（转入合计减转出合计）最高的前二十个账户，输出账户编号、转入笔数、转入金额合计、转出金额合计与净流入金额（保留两位小数），按净流入金额降序、账户编号升序排列。",
        sql="""WITH inflow AS (
  SELECT to_account_id AS aid, COUNT(*) AS c, SUM(amount) AS amt
  FROM payment_event GROUP BY to_account_id
),
outflow AS (
  SELECT from_account_id AS aid, SUM(amount) AS amt
  FROM payment_event GROUP BY from_account_id
)
SELECT i.aid AS 账户编号, i.c AS 流入笔数,
       ROUND(i.amt, 2) AS 流入金额合计,
       ROUND(o.amt, 2) AS 流出金额合计,
       ROUND(i.amt - o.amt, 2) AS 净流入金额
FROM inflow i
JOIN outflow o ON o.aid = i.aid
ORDER BY 净流入金额 DESC, i.aid
LIMIT 20;"""),
    dict(
        id="BRB2-0298", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第三十九条",
        penalty_fact_zh="部分分支机构不良资产集中，风险管控与经营稳健性不足",
        question="按经办营业机构单元统计贷款本金逾期余额，输出营业单元编号、营业单元名称、逾期笔数与逾期本金合计，按逾期本金合计降序排列（逾期以贷款余额快照中的逾期本金大于零为准）。",
        sql="""SELECT ou.org_unit_id AS 营业单元编号, ou.unit_name AS 营业单元名称,
       COUNT(DISTINCT ld.loan_id) AS 逾期笔数,
       ROUND(SUM(lbs.overdue_principal), 2) AS 逾期本金合计
FROM credit_agreement a
JOIN organization_unit ou ON ou.org_unit_id = a.managing_org_unit_id
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
WHERE lbs.overdue_principal > 0
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY 逾期本金合计 DESC, ou.org_unit_id;"""),
    dict(
        id="BRB2-0299", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》第三十九条",
        penalty_fact_zh="特定分支行贷款催收执行不力、逾期期数高企",
        question="按经办营业机构单元统计逾期未归还的分期期数，输出营业单元编号、营业单元名称与逾期分期期数，按逾期分期期数降序排列。",
        sql="""SELECT ou.org_unit_id AS 营业单元编号, ou.unit_name AS 营业单元名称,
       COUNT(rs.installment_id) AS 逾期分期期数
FROM repayment_schedule rs
JOIN loan_drawdown ld ON ld.loan_id = rs.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN organization_unit ou ON ou.org_unit_id = a.managing_org_unit_id
WHERE rs.status = 'OVERDUE'
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY 逾期分期期数 DESC, ou.org_unit_id;"""),
    dict(
        id="BRB2-0300", difficulty="easy", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="分支行贷款发放过度集中于部分机构，授信资源配置失衡",
        question="按经办营业机构单元统计贷款发放情况，输出营业单元编号、营业单元名称、发放笔数与发放金额合计，按发放金额合计降序排列。",
        sql="""SELECT ou.org_unit_id AS 营业单元编号, ou.unit_name AS 营业单元名称,
       COUNT(DISTINCT ld.loan_id) AS 发放笔数,
       ROUND(SUM(ld.disbursed_amount), 2) AS 发放金额合计
FROM loan_drawdown ld
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN organization_unit ou ON ou.org_unit_id = a.managing_org_unit_id
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY 发放金额合计 DESC, ou.org_unit_id;"""),
    dict(
        id="BRB2-0301", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="将处于有效状态的定期存款按其年化利率划分为高、中、低三档（不低于百分之三为高档、其余不低于百分之二点四为中档、之下为低档），按档位统计账户数量与平均开户本金，仅保留数量少于一百二十的档位，输出档位、账户数量与平均开户本金，按平均开户本金降序、档位升序排列。",
        sql="""SELECT CASE WHEN td.annual_interest_rate >= 3.0 THEN 'HIGH'
            WHEN td.annual_interest_rate >= 2.4 THEN 'MID'
            ELSE 'LOW' END AS band,
       COUNT(*) AS cnt,
       ROUND(AVG(td.opening_principal), 2) AS avg_principal
FROM term_deposit td
JOIN account a ON a.account_id = td.account_id
WHERE a.status = 'ACTIVE'
GROUP BY band
HAVING COUNT(*) < 120
ORDER BY avg_principal DESC, band;"""),
    dict(
        id="BRB2-0302", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="统计分期还款计划中已逾期且逾期本金金额合计超过一亿两千万元的贷款笔数、对应期数合计与逾期本金合计，输出贷款编号、逾期期数与逾期本金合计，按逾期本金合计降序排列。",
        sql="""SELECT r.loan_id, COUNT(*) AS 逾期期数, ROUND(SUM(r.principal_due), 2) AS 逾期本金合计
FROM repayment_schedule r
WHERE r.status = 'OVERDUE'
GROUP BY r.loan_id
HAVING SUM(r.principal_due) > 120000000
ORDER BY 逾期本金合计 DESC, r.loan_id;"""),
    dict(
        id="BRB2-0303", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="按发放机构统计客户所属机构发放贷款的分期还款计划中其逾期未归还的期数合计与应还利息合计，保留逾期期数不少于三十期的机构，输出机构名称、逾期期数与利息合计，按逾期期数降序排列。",
        sql="""SELECT i.institution_name, COUNT(rs.installment_id) AS 逾期期数, ROUND(SUM(rs.interest_due), 2) AS 利息合计
FROM repayment_schedule rs
JOIN loan_drawdown ld ON ld.loan_id = rs.loan_id
JOIN credit_agreement ca ON ca.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = ca.institution_id
WHERE rs.status = 'OVERDUE'
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(rs.installment_id) >= 30
ORDER BY 逾期期数 DESC, i.institution_name;"""),
    dict(
        id="BRB2-0304", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="统计自有资金支付与受托方式支付的分期还款计划违约情况，输出支付方式中文名称、对应的逾期未归还期数与本金合计，保留期数超过四百五十期的支付方式，按逾期本金合计降序排列。",
        sql="""SELECT pm.payment_mode_name_zh AS 支付方式, COUNT(rs.installment_id) AS 逾期期数, ROUND(SUM(rs.principal_due), 2) AS 本金合计
FROM repayment_schedule rs
JOIN loan_drawdown ld ON ld.loan_id = rs.loan_id
JOIN payment_mode_catalog pm ON pm.payment_mode = ld.payment_mode
WHERE rs.status = 'OVERDUE'
GROUP BY pm.payment_mode_name_zh
HAVING COUNT(rs.installment_id) > 450
ORDER BY 本金合计 DESC, pm.payment_mode_name_zh;"""),
    dict(
        id="BRB2-0305", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="对仍然有效的抵质押品，以其外部评估价值为基准计算最高质押金额与最高评估价值，仅保留质押率（最高质押金额除以最高评估价值）介于百分之五十至百分之九十八之间的抵质押品，输出抵质押品编号、最高质押金额与最高评估价值，按最高评估价值降序排列。",
        sql="""SELECT cl.collateral_id,
       MAX(cv.valuation_amount) AS latest_val,
       MAX(cl.pledged_amount) AS pledged
FROM collateral_link cl
JOIN collateral_valuation cv ON cv.collateral_id = cl.collateral_id
JOIN collateral_asset bc ON bc.collateral_id = cl.collateral_id
WHERE bc.status = 'ACTIVE'
  AND cv.valuation_type = 'EXTERNAL'
GROUP BY cl.collateral_id
HAVING (MAX(cl.pledged_amount) / MAX(cv.valuation_amount)) BETWEEN 0.5 AND 0.98
ORDER BY latest_val DESC;"""),
    dict(
        id="BRB2-0306", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="统计每家机构名下发生分期还款逾期的贷款数量，只保留发生逾期的贷款数量不低于两百四十笔的机构，输出机构名称与逾期贷款数，按逾期贷款数降序排列。",
        sql="""SELECT i.institution_name, COUNT(DISTINCT rs.loan_id) AS 逾期贷款数
FROM repayment_schedule rs
JOIN loan_drawdown ld ON ld.loan_id = rs.loan_id
JOIN credit_agreement ca ON ca.agreement_id = ld.agreement_id
JOIN institution i ON i.institution_id = ca.institution_id
WHERE rs.status = 'OVERDUE'
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(DISTINCT rs.loan_id) >= 240
ORDER BY 逾期贷款数 DESC, i.institution_name;"""),
    dict(
        id="BRB2-0307", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="列出分期还款计划中已发生逾期未归还且当期应还本金超过九千万元的期次，输出贷款编号、期次序号、应还本金与应还利息，按应还本金从高到低排列。",
        sql="""SELECT rs.loan_id, rs.installment_no, rs.principal_due, rs.interest_due
FROM repayment_schedule rs
WHERE rs.status = 'OVERDUE' AND rs.principal_due > 90000000
ORDER BY rs.principal_due DESC, rs.loan_id;"""),
    dict(
        id="BRB2-0308", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="针对分期还款计划存在逾期未归还的贷款，统计其当前未偿还本金余额合计不超过五千万元但逾期未归还期数至少两期涉及的贷款笔数集合，输出贷款编号、逾期期数与当前本金余额，按当前本金余额降序排列。",
        sql="""WITH cnte AS (
  SELECT r.loan_id, COUNT(*) AS n
  FROM repayment_schedule r
  WHERE r.status = 'OVERDUE'
  GROUP BY r.loan_id
  HAVING COUNT(*) >= 2
)
SELECT c.loan_id, c.n AS 逾期期数, ROUND(lbs.principal_balance, 2) AS 当前本金余额
FROM cnte c
JOIN loan_balance_snapshot lbs ON lbs.loan_id = c.loan_id
WHERE lbs.principal_balance <= 50000000
ORDER BY 当前本金余额 DESC, c.loan_id;"""),
    dict(
        id="BRB2-0309", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="集团内部分成员未纳入授信范围，集团风险识别不完整",
        question="统计各敞口集团中已在本行取得贷款的成员与未取得贷款的成员数量，输出集团编号、集团名称、已贷款成员数、未贷款成员数，按已贷款成员数降序排列。",
        sql="""SELECT eg.exposure_group_id AS 集团编号, eg.group_name AS 集团名称,
       COUNT(DISTINCT CASE WHEN lb.pid IS NOT NULL THEN lb.pid END) AS 已贷款成员数,
       COUNT(DISTINCT egm.party_id) - COUNT(DISTINCT CASE WHEN lb.pid IS NOT NULL THEN lb.pid END) AS 未贷款成员数
FROM exposure_group eg
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
LEFT JOIN (
  SELECT DISTINCT a.borrower_party_id AS pid FROM credit_agreement a
) lb ON lb.pid = egm.party_id
GROUP BY eg.exposure_group_id, eg.group_name
ORDER BY 已贷款成员数 DESC, eg.exposure_group_id;"""),
    dict(
        id="BRB2-0310", difficulty="hard", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="既是关联方又是集团成员的多重身份贷款，穿透识别不足、风险叠加",
        question="找出付款端为本行员工主控账户、收款端为对公客户主控账户的转账交易，输出交易流水号、业务日期、金额与机构名称，按金额降序排列，只取前两百条。",
        sql="""SELECT e.payment_id, e.business_date, e.amount, i.institution_name
FROM payment_event e
JOIN account ha ON ha.account_id=e.from_account_id
JOIN institution i ON i.institution_id=ha.institution_id
WHERE e.payment_type='TRANSFER'
  AND EXISTS (SELECT 1 FROM account_holder ah JOIN party p ON p.party_id=ah.party_id WHERE ah.account_id=e.from_account_id AND p.party_type='STAFF' AND ah.holder_role='PRIMARY')
  AND EXISTS (SELECT 1 FROM account_holder ah2 JOIN party p2 ON p2.party_id=ah2.party_id WHERE ah2.account_id=e.to_account_id AND p2.party_type='CORPORATE' AND ah2.holder_role='PRIMARY')
ORDER BY e.amount DESC, e.payment_id
LIMIT 200;"""),
    dict(
        id="BRB2-0311", difficulty="easy", features=[],
        penalty_law_zh="《严禁柜台违规行为防范案件风险的工作意见》、《中华人民共和国商业银行法》第五十二条",
        penalty_fact_zh="担保合同由本行员工单人集中管理，权责分离与岗位制衡失效，存在越权处置抵押担保风险",
        question="统计本行各员工作为担保合同管理人负责管理的担保合同笔数与担保金额合计，输出员工编号、员工姓名、管理担保合同笔数与管理担保金额合计，按管理担保金额合计降序排列。",
        sql="""SELECT sm.staff_id AS 员工编号, p.display_name AS 员工姓名,
       COUNT(DISTINCT sa.security_id) AS 管理担保合同笔数,
       ROUND(SUM(sa.secured_amount), 2) AS 管理担保金额合计
FROM security_agreement sa
JOIN staff_member sm ON sm.staff_id = sa.manager_staff_id
JOIN party p ON p.party_id = sm.person_party_id
WHERE sa.status = 'ACTIVE'
GROUP BY sm.staff_id, p.display_name
ORDER BY 管理担保金额合计 DESC, sm.staff_id;"""),
    dict(
        id="BRB2-0312", difficulty="hard", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》",
        penalty_fact_zh="部分机构关联交易集中度高，关联授信审查流于形式",
        question="按机构对比授信额度合计、借据累计发放金额与资本净额，计算发放金额对资本净额的占比，输出机构名称、授信额度合计、发放金额合计、资本净额与发放对资本净额占比，只保留累计发放金额超过资本净额的机构，按发放对资本占比降序排列（占比保留四位小数）。",
        sql="""WITH fac AS (SELECT cf.institution_id, SUM(cf.limit_amount) AS tl, COUNT(cf.facility_id) AS n FROM credit_facility cf GROUP BY cf.institution_id),
drawn AS (SELECT a.institution_id, SUM(ld.disbursed_amount) AS td FROM loan_drawdown ld JOIN credit_agreement a ON a.agreement_id=ld.agreement_id GROUP BY a.institution_id),
cap AS (SELECT cs.institution_id, cs.net_capital AS nc FROM capital_snapshot cs)
SELECT i.institution_name, ROUND(f.tl,2) AS tl, ROUND(d.td,2) AS td, ROUND(c.nc,2) AS nc,
       ROUND(d.td*1.0/c.nc,4) AS ratio
FROM fac f JOIN drawn d ON d.institution_id=f.institution_id
JOIN cap c ON c.institution_id=f.institution_id
JOIN institution i ON i.institution_id=f.institution_id
WHERE d.td > c.nc
ORDER BY ratio DESC, i.institution_name;"""),
    dict(
        id="BRB2-0313", difficulty="hard", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》",
        penalty_fact_zh="保证担保金额缺口，担保充足率不足仍发放贷款",
        question="查出由保证人提供的担保金额合计低于担保合同设定担保金额的担保合同，输出担保合同编号、设定担保金额、保证人个数与保证金额合计，按保证金额合计降序排列（仅统计有效状态的保证承诺，且担保合同类型为保证担保）。",
        sql="""SELECT sa.security_id AS 担保合同编号,
       ROUND(sa.secured_amount, 2) AS 设定担保金额,
       COUNT(DISTINCT gc.commitment_id) AS 保证人个数,
       ROUND(SUM(gc.guaranteed_amount), 2) AS 保证金额合计
FROM security_agreement sa
JOIN guarantor_commitment gc ON gc.security_id = sa.security_id
WHERE gc.status = 'ACTIVE' AND sa.security_type = 'GUARANTEE'
GROUP BY sa.security_id, sa.secured_amount
HAVING SUM(gc.guaranteed_amount) < sa.secured_amount
ORDER BY 保证金额合计 DESC, sa.security_id;"""),
    dict(
        id="BRB2-0314", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="列出循环授信额度的授信额度记录，输出授信额度编号、授信限额与额度状态名称，按授信限额从高到低排列（额度状态名称取自状态码表中授信合同实体的状态名称）。",
        sql="""SELECT cf.facility_id, cf.limit_amount, sc.name_zh AS 额度状态名称
FROM credit_facility cf
JOIN status_catalog sc ON sc.status_code = cf.status AND sc.entity = 'credit_agreement'
WHERE cf.facility_type = 'REVOLVING'
ORDER BY cf.limit_amount DESC, cf.facility_id;"""),
    dict(
        id="BRB2-0315", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="按金融机构统计循环授信额度且授信限额超过五亿元的额度记录数与其授信限额合计，输出机构名称、记录数与限额合计，按限额合计降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS 记录数, ROUND(SUM(cf.limit_amount), 2) AS 限额合计
FROM credit_facility cf
JOIN institution i ON i.institution_id = cf.institution_id
WHERE cf.facility_type = 'REVOLVING' AND cf.limit_amount > 500000000
GROUP BY i.institution_id, i.institution_name
ORDER BY 限额合计 DESC, i.institution_name;"""),
    dict(
        id="BRB2-0316", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="统计每家机构名下的循环授信额度记录数及其授信限额合计，只保留循环授信额度超过十二笔的机构，输出机构名称、记录数与限额合计，按限额合计降序排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS 记录数, ROUND(SUM(cf.limit_amount), 2) AS 限额合计
FROM credit_facility cf
JOIN institution i ON i.institution_id = cf.institution_id
WHERE cf.facility_type = 'REVOLVING'
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(*) > 12
ORDER BY 限额合计 DESC, i.institution_name;"""),
    dict(
        id="BRB2-0317", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="针对授信额度已导致同一授信类型名下授信限额合计超过二十亿元的机构，统计其授信限额合计，输出机构名称、授信类型代码与授信限额合计，按授信限额合计降序排列。",
        sql="""SELECT i.institution_name, cf.facility_type, ROUND(SUM(cf.limit_amount), 2) AS 授信限额合计
FROM credit_facility cf
JOIN institution i ON i.institution_id = cf.institution_id
GROUP BY i.institution_id, i.institution_name, cf.facility_type
HAVING SUM(cf.limit_amount) > 2000000000
ORDER BY 授信限额合计 DESC, i.institution_name;"""),
    dict(
        id="BRB2-0318", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="按授信类型统计授信限额超过三亿元的授信额度记录数，输出授信类型与记录数，按记录数降序排列。",
        sql="""SELECT cf.facility_type, COUNT(*) AS 记录数
FROM credit_facility cf
WHERE cf.limit_amount > 300000000
GROUP BY cf.facility_type
ORDER BY 记录数 DESC, cf.facility_type;"""),
    dict(
        id="BRB2-0319", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="按授信协议开办机构统计已签署授信协议所关联的不重复授信额度记录数，输出机构名称与授信额度记录数，按授信额度记录数降序排列。",
        sql="""WITH per_org AS (
  SELECT ca.institution_id, COUNT(DISTINCT cf.facility_id) AS cnt
  FROM credit_facility cf
  JOIN credit_agreement ca ON ca.facility_id = cf.facility_id
  GROUP BY ca.institution_id
)
SELECT i.institution_name, p.cnt AS 授信额度记录数
FROM per_org p
JOIN institution i ON i.institution_id = p.institution_id
ORDER BY 授信额度记录数 DESC, i.institution_name;"""),
    dict(
        id="BRB2-0320", difficulty="extra", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="计算每家机构循环授信额度的授信限额合计，只保留总限额超过五十亿元的机构，输出机构名称与总限额，按总限额降序排列。",
        sql="""SELECT i.institution_name, ROUND(SUM(cf.limit_amount), 2) AS 总限额
FROM credit_facility cf
JOIN institution i ON i.institution_id = cf.institution_id
WHERE cf.facility_type = 'REVOLVING'
GROUP BY i.institution_id, i.institution_name
HAVING SUM(cf.limit_amount) > 5000000000
ORDER BY 总限额 DESC, i.institution_name;"""),
    dict(
        id="BRB2-0321", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="找出每位借款人名下授信限额最高的那笔授信额度记录（并列时取额度编号最小者），输出借款人编号、最大授信限额与对应授信额度类型，按最大授信限额降序排列，只取前两百条。",
        sql="""WITH ranked AS (
    SELECT cf.obligor_party_id, ROUND(cf.limit_amount, 2) AS max_limit, cf.facility_type,
           ROW_NUMBER() OVER (PARTITION BY cf.obligor_party_id ORDER BY cf.limit_amount DESC, cf.facility_id ASC) AS rn
    FROM credit_facility cf
)
SELECT obligor_party_id, max_limit, facility_type
FROM ranked
WHERE rn = 1
ORDER BY max_limit DESC, obligor_party_id
LIMIT 200;"""),
    dict(
        id="BRB2-0322", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="统计各机构定期存款开户本金合计并给出名次，连同平均单笔本金一起输出，输出名次、机构名称、本金合计与平均单笔本金，按名次升序排列。",
        sql="""SELECT RANK() OVER (ORDER BY tsum DESC) AS rk, i.institution_name, tsum, avg_amt FROM (
  SELECT a.institution_id, ROUND(SUM(td.opening_principal),2) AS tsum, ROUND(AVG(td.opening_principal),2) AS avg_amt
  FROM term_deposit td JOIN account a ON a.account_id=td.account_id
  GROUP BY a.institution_id
) t JOIN institution i ON i.institution_id=t.institution_id
ORDER BY rk, i.institution_name;"""),
    dict(
        id="BRB2-0323", difficulty="easy", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="贷款受托支付与自主支付方式管控失当、化整为零规避受托支付",
        question="统计每类支付方式对应的贷款借据发放记录数，输出支付方式中文名称与记录数，按记录数降序排列。",
        sql="""SELECT pm.payment_mode_name_zh AS 支付方式, COUNT(*) AS 记录数
FROM loan_drawdown ld
JOIN payment_mode_catalog pm ON pm.payment_mode = ld.payment_mode
GROUP BY pm.payment_mode_name_zh
ORDER BY 记录数 DESC, pm.payment_mode_name_zh;"""),
    dict(
        id="BRB2-0324", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="贷款受托支付与自主支付方式管控失当、化整为零规避受托支付",
        question="统计受托支付及自主支付方式下贷款本金余额合计，输出支付方式中文名称与本金余额合计，按本金余额合计降序排列。",
        sql="""SELECT pm.payment_mode_name_zh AS 支付方式, ROUND(SUM(lbs.principal_balance), 2) AS 本金余额合计
FROM loan_drawdown ld
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
JOIN payment_mode_catalog pm ON pm.payment_mode = ld.payment_mode
GROUP BY pm.payment_mode_name_zh
ORDER BY 本金余额合计 DESC, pm.payment_mode_name_zh;"""),
    dict(
        id="BRB2-0325", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="贷款受托支付与自主支付方式管控失当、化整为零规避受托支付",
        question="按支付方式统计贷款发放金额合计及发放笔数，只保留发放笔数超过一千一百笔的支付方式，输出支付方式中文名称、发放笔数与发放金额合计，按发放金额合计降序排列。",
        sql="""SELECT pm.payment_mode_name_zh AS 支付方式, COUNT(*) AS 发放笔数, ROUND(SUM(ld.disbursed_amount), 2) AS 发放金额合计
FROM loan_drawdown ld
JOIN payment_mode_catalog pm ON pm.payment_mode = ld.payment_mode
GROUP BY pm.payment_mode_name_zh
HAVING COUNT(*) > 1100
ORDER BY 发放金额合计 DESC, pm.payment_mode_name_zh;"""),
    dict(
        id="BRB2-0326", difficulty="extra", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="贷款受托支付与自主支付方式管控失当、化整为零规避受托支付",
        question="按支付方式汇总计价划转指令的指令金额合计，只保留指令金额合计低于一兆元的支付方式，输出支付方式中文名称、指令笔数与指令金额合计，按指令金额合计降序排列。",
        sql="""SELECT pm.payment_mode_name_zh AS 支付方式, COUNT(*) AS 指令笔数, ROUND(SUM(pi.instruction_amount), 2) AS 指令金额合计
FROM payment_instruction pi
JOIN payment_mode_catalog pm ON pm.payment_mode = pi.payment_mode
GROUP BY pm.payment_mode_name_zh
HAVING SUM(pi.instruction_amount) < 1000000000000
ORDER BY 指令金额合计 DESC, pm.payment_mode_name_zh;"""),
    dict(
        id="BRB2-0327", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="贷款受托支付与自主支付方式管控失当、化整为零规避受托支付",
        question="列出计价指令中指令金额超过两亿两千万元的指令，输出支付方式中文名称、指令金额与指令状态，按指令金额降序排列。",
        sql="""SELECT pm.payment_mode_name_zh AS 支付方式, pi.instruction_amount, pi.status
FROM payment_instruction pi
JOIN payment_mode_catalog pm ON pm.payment_mode = pi.payment_mode
WHERE pi.instruction_amount > 220000000
ORDER BY pi.instruction_amount DESC, pi.instruction_id;"""),
    dict(
        id="BRB2-0328", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="贷款受托支付与自主支付方式管控失当、化整为零规避受托支付",
        question="统计属于个人客户且未在任何名下账户中担任主要持有人的客户，按客户分群汇总客户数量，仅保留数量少于五十的分群，输出客户分群与客户数量，按客户数量降序、客户分群升序排列。",
        sql="""SELECT p.customer_segment,
       COUNT(*) AS cnt
FROM party p
WHERE p.party_type = 'INDIVIDUAL'
  AND NOT EXISTS (
    SELECT 1 FROM account_holder ah
    WHERE ah.party_id = p.party_id AND ah.holder_role = 'PRIMARY'
  )
GROUP BY p.customer_segment
HAVING COUNT(*) < 50
ORDER BY cnt DESC, p.customer_segment;"""),
    dict(
        id="BRB2-0329", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="贷款受托支付与自主支付方式管控失当、化整为零规避受托支付",
        question="按开户营业单元统计开立账户数与本单元账户对应的持有人记录数，输出营业单元名称、账户数与持有人记录数，按持有人记录数降序排列，只取前两百条。",
        sql="""SELECT o.unit_name, COUNT(DISTINCT a.account_id) AS acct_cnt, COUNT(ah.account_holder_id) AS holder_cnt
FROM organization_unit o
JOIN account a ON a.org_unit_id=o.org_unit_id
LEFT JOIN account_holder ah ON ah.account_id=a.account_id
GROUP BY o.org_unit_id, o.unit_name
ORDER BY holder_cnt DESC, o.unit_name
LIMIT 200;"""),
    dict(
        id="BRB2-0330", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="先将处于在售状态的理财产品依据实际募集金额从高到低划分为四个等份组，再统计其中最低持有期大于零的产品数量，仅保留产品数量介于三十一至三十三之间的分组，输出分组序号与产品数量，按分组序号升序排列。",
        sql="""WITH wp AS (
  SELECT product_id, minimum_holding_days,
         NTILE(4) OVER (ORDER BY actual_raise_amount DESC) AS quartile
  FROM wealth_product WHERE status = 'ON_SALE'
)
SELECT q.quartile,
       COUNT(*) AS cnt
FROM wp q
WHERE q.minimum_holding_days > 0
GROUP BY q.quartile
HAVING COUNT(*) BETWEEN 31 AND 33
ORDER BY q.quartile;"""),
    dict(
        id="BRB2-0331", difficulty="extra", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="对于授信额度类型为循环授信且支付方式为受托支付的贷款，统计循环授信限额合计，输出循环授信限额合计、发放笔数，按循环授信限额合计降序排列。",
        sql="""SELECT ROUND(SUM(cf.limit_amount), 2) AS 循环授信限额合计, COUNT(DISTINCT ld.loan_id) AS 发放笔数
FROM credit_facility cf
JOIN credit_agreement ca ON ca.facility_id = cf.facility_id
JOIN loan_drawdown ld ON ld.agreement_id = ca.agreement_id
JOIN payment_mode_catalog pm ON pm.payment_mode = ld.payment_mode
WHERE cf.facility_type = 'REVOLVING' AND pm.payment_mode_name_zh = '受托支付'
ORDER BY 循环授信限额合计 DESC;"""),
    dict(
        id="BRB2-0332", difficulty="medium", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="贷款受托支付与自主支付方式管控失当、化整为零规避受托支付",
        question="统计每一支付方式下处于待执行状态的计价指令数量，输出支付方式中文名称与待执行指令数量，按待执行指令数量降序排列。",
        sql="""SELECT pm.payment_mode_name_zh AS 支付方式, COUNT(*) AS 待执行指令数量
FROM payment_instruction pi
JOIN payment_mode_catalog pm ON pm.payment_mode = pi.payment_mode
WHERE pi.status = 'PENDING'
GROUP BY pm.payment_mode_name_zh
ORDER BY 待执行指令数量 DESC, pm.payment_mode_name_zh;"""),
    dict(
        id="BRB2-0333", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国票据法》第十条、《商业汇票承兑、贴现与再贴现管理暂行办法》第十九条",
        penalty_fact_zh="票据业务贸易背景真实性审核不严、银行承兑汇票出票资质核查缺失",
        question="列出融资工具类型码表中的全部融资工具类型代码及其中文名称，输出融资工具类型代码与中文名称，按中文名称排列。",
        sql="""SELECT it.instrument_type, it.name_zh
FROM instrument_type_catalog it
ORDER BY it.name_zh;"""),
    dict(
        id="BRB2-0334", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="列出实体状态码表中隶属于贷款借据实体的全部状态代码及其中文名称，输出状态代码与中文名称，按状态代码排列。",
        sql="""SELECT sc.status_code, sc.name_zh
FROM status_catalog sc
WHERE sc.entity = 'loan_drawdown'
ORDER BY sc.status_code;"""),
    dict(
        id="BRB2-0335", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="统计贷款借据在实体状态码表中的每一状态对应的不同借据数量，输出状态中文名称与借据数量，按借据数量降序排列。",
        sql="""SELECT sc.name_zh AS 状态中文名称, COUNT(DISTINCT ld.loan_id) AS 借据数量
FROM loan_drawdown ld
JOIN status_catalog sc ON sc.status_code = ld.status AND sc.entity = 'loan_drawdown'
GROUP BY sc.name_zh
ORDER BY 借据数量 DESC, sc.name_zh;"""),
    dict(
        id="BRB2-0336", difficulty="extra", features=[],
        penalty_law_zh="《中华人民共和国票据法》第十条、《商业汇票承兑、贴现与再贴现管理暂行办法》第十九条",
        penalty_fact_zh="票据业务贸易背景真实性审核不严、银行承兑汇票出票资质核查缺失",
        question="将融资工具类型码表与实体状态码表交叉关联，输出融资工具中文名称与实体状态中文名称的每种组合，按融资工具中文名称、再按状态中文名称排列（实体状态仅取借据实体的状态码）。",
        sql="""SELECT it.name_zh AS 融资工具中文名称, sc.name_zh AS 实体状态中文名称
FROM instrument_type_catalog it
CROSS JOIN status_catalog sc
WHERE sc.entity = 'loan_drawdown'
ORDER BY it.name_zh, sc.name_zh;"""),
    dict(
        id="BRB2-0337", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="分期还款计划连续逾期、还款能力评估失准导致贷款进入不良",
        question="统计贷款借据在实体状态码表中的状态分布笔数，只保留已核销状态的借贷据笔数，输出当前状态中文名称与借据笔数，按借据笔数降序排列。",
        sql="""SELECT sc.name_zh AS 状态中文名称, COUNT(*) AS 借据笔数
FROM loan_drawdown ld
JOIN status_catalog sc ON sc.status_code = ld.status AND sc.entity = 'loan_drawdown'
WHERE sc.name_zh = '已核销'
GROUP BY sc.name_zh
ORDER BY 借据笔数 DESC, sc.name_zh;"""),
    dict(
        id="BRB2-0338", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="统计单笔金额不低于三千万的大额支付交易在不同受理渠道的发生次数，仅保留发生次数少于一千二百次的渠道，输出交易渠道与发生次数，按发生次数降序、交易渠道升序排列。",
        sql="""SELECT pe.channel,
       COUNT(*) AS n
FROM payment_event pe
WHERE pe.amount >= 30000000
GROUP BY pe.channel
HAVING COUNT(*) < 1200
ORDER BY n DESC, pe.channel;"""),
    dict(
        id="BRB2-0339", difficulty="extra", features=[],
        penalty_law_zh="《流动资金贷款管理暂行办法》第九条、《固定资产贷款管理暂行办法》第二十六条、《个人贷款管理暂行办法》",
        penalty_fact_zh="贷款受托支付与自主支付方式管控失当、化整为零规避受托支付",
        question="针对以受托支付方式发放且状态已结清的贷款借据，统计其发放金额合计与平均发放金额，输出支付方式中文名称、发放金额合计与平均金额，按发放金额合计降序排列。",
        sql="""SELECT pm.payment_mode_name_zh AS 支付方式, ROUND(SUM(ld.disbursed_amount), 2) AS 发放金额合计, ROUND(AVG(ld.disbursed_amount), 2) AS 平均金额
FROM loan_drawdown ld
JOIN payment_mode_catalog pm ON pm.payment_mode = ld.payment_mode
JOIN status_catalog sc ON sc.status_code = ld.status AND sc.entity = 'loan_drawdown'
WHERE pm.payment_mode_name_zh = '受托支付' AND sc.name_zh = '已结清'
GROUP BY pm.payment_mode_name_zh
ORDER BY 发放金额合计 DESC, pm.payment_mode_name_zh;"""),
    dict(
        id="BRB2-0340", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条、《商业银行集团客户授信业务风险管理指引》第十二条",
        penalty_fact_zh="授信额度测算超限、循环授信额度管控失效致集团授信集中度超标",
        question="统计每名借款主体名下的授信额度记录数与其授信限额合计，只保留授信额度记录数超过三笔的借款主体，输出借款主体编号、授信记录数与授信限额合计，按授信限额合计降序排列。",
        sql="""SELECT cf.obligor_party_id, COUNT(*) AS 授信记录数, ROUND(SUM(cf.limit_amount), 2) AS 授信限额合计
FROM credit_facility cf
GROUP BY cf.obligor_party_id
HAVING COUNT(*) > 3
ORDER BY 授信限额合计 DESC, cf.obligor_party_id;"""),
    dict(
        id="BRB2-0341", difficulty="easy", features=[],
        penalty_law_zh="《严禁柜台违规行为防范案件风险的工作意见》",
        penalty_fact_zh="分支机构柜面操作权限配置不合理，高级授权过度集中",
        question="统计各营业机构单元配置的运行操作员数量，输出营业单元编号、营业单元名称、操作员数量与其中高级权限人数，按高级权限人数降序排列。",
        sql="""SELECT ou.org_unit_id AS 营业单元编号, ou.unit_name AS 营业单元名称,
       COUNT(DISTINCT so.operator_id) AS 操作员数量,
       COUNT(DISTINCT CASE WHEN so.authority_level = 'L3' THEN so.operator_id END) AS 高级权限人数
FROM service_operator so
JOIN organization_unit ou ON ou.org_unit_id = so.org_unit_id
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY 高级权限人数 DESC, ou.org_unit_id;"""),
    dict(
        id="BRB2-0342", difficulty="easy", features=[],
        penalty_law_zh="《严禁柜台违规行为防范案件风险的工作意见》",
        penalty_fact_zh="信贷客户经理配置不足或过度集中于个别分支机构，内控失衡",
        question="统计各营业机构单元任职的信贷客户经理人数，输出营业单元编号、营业单元名称与信贷客户经理人数，按信贷客户经理人数降序排列。",
        sql="""SELECT ou.org_unit_id AS 营业单元编号, ou.unit_name AS 营业单元名称,
       COUNT(DISTINCT sa.staff_id) AS 信贷客户经理人数
FROM staff_assignment sa
JOIN organization_unit ou ON ou.org_unit_id = sa.org_unit_id
WHERE sa.role_code = 'CREDIT_OFFICER'
GROUP BY ou.org_unit_id, ou.unit_name
ORDER BY 信贷客户经理人数 DESC, ou.org_unit_id;"""),
    dict(
        id="BRB2-0343", difficulty="hard", features=[],
        penalty_law_zh="《商业银行金融资产风险分类办法》（银保监会令〔2023〕第1号）第十条、第二十四条：债务人对任何金融债务发生实质违约或风险显著恶化时，监管机构应依据“交叉违约”与债务人综合偿债能力原则，对其全部相关债务同步下调分类；严禁通过拆分借据、选择性分类掩盖不良资产真实水平。",
        penalty_fact_zh="同一债务人在本行名下同时持有已划分为不良类与其他仍划为正常/关注的借据，存在未依“交叉违约”原则整体下调的分类失真，涉嫌压低五级分类、虚减不良率并少计提损失准备。",
        question="监管检查要求核查同一借款人在本行名下既存在已纳入不良类（次级、可疑、损失）的借据、同时又存在仍处非不良的其他借据，从而判断是否存在利用“交叉违约”未整体下调来掩盖不良的情况。输出债务人编号、债务人名称、其名下全部借据数与其中不良类借据数，按全部借据数由多到少排列，笔数相同再按债务人编号从小到大排列。",
        sql="""with cl as (
  select a.borrower_party_id, g.is_nonperforming, ld.loan_id
  from risk_classification rc
  join classification_grade g on g.grade_code = rc.grade_code
  join loan_drawdown ld on ld.loan_id = rc.loan_id
  join credit_agreement a on a.agreement_id = ld.agreement_id
)
select cl.borrower_party_id, p.display_name, count(*) as 借据数,
  sum(case when cl.is_nonperforming = 1 then 1 else 0 end) as 不良借据数
from cl
join party p on p.party_id = cl.borrower_party_id
group by cl.borrower_party_id, p.display_name
having count(*) > sum(case when cl.is_nonperforming = 1 then 1 else 0 end)
   and sum(case when cl.is_nonperforming = 1 then 1 else 0 end) > 0
order by 借据数 desc, cl.borrower_party_id"""),
    dict(
        id="BRB2-0344", difficulty="hard", features=[],
        penalty_law_zh="《商业银行金融资产风险分类办法》第十三条、第十四条：本金、利息逾期超过90天或虽未逾期但信用状况明显恶化的债权，至少应划分为次级类（纳入不良）；分类调整应随风险变化及时完成，不得以账务处理变通拖延下迁。",
        penalty_fact_zh="存在本金逾期天数超过90天却仍被划分为正常或关注类的借据，分类明显滞后于实际风险，未及时确认为不良并计提相应损失准备，导致不良率与减值水平被低估。",
        question="监管核查要求排查本金逾期已超过90天、但五级业务分类仍未被划分至不良类的借据，此类借据属于风险分类延迟调整、掩盖实质不良。输出借据编号、发放金额、本金逾期天数与五级分类名称，按本金逾期天数由多到少排列，逾期天数相同再按借据编号从小到大排列。",
        sql="""select rc.loan_id, ld.disbursed_amount, d.principal_overdue_days, g.grade_name_zh
from risk_classification rc
join classification_grade g on g.grade_code = rc.grade_code
join delinquency_snapshot d on d.loan_id = rc.loan_id
join loan_drawdown ld on ld.loan_id = rc.loan_id
where d.principal_overdue_days > 90 and g.is_nonperforming = 0
order by d.principal_overdue_days desc, rc.loan_id"""),
    dict(
        id="BRB2-0345", difficulty="medium", features=[],
        penalty_law_zh="《商业银行金融资产风险分类办法》第十二条：金融资产已发生本金或利息逾期即应审慎下调分类；正常类债权不得出现本金逾期，逾期风险信号一经出现必须及时复核并下调。",
        penalty_fact_zh="存在本金逾期超过30天仍被划分为正常类的借据，分类口径未严格把关，反映贷后风险监测与五级分类管理存在疏漏。",
        question="监管核查要求排查本金已发生逾期超过30天、却仍被划分为正常类的借据，此类借据的清分未反映风险恶化。输出借据编号、五级分类名称、本金逾期天数与逾期本金，按本金逾期天数由多到少排列，逾期天数相同再按借据编号从小到大排列。",
        sql="""select rc.loan_id, g.grade_name_zh, d.principal_overdue_days, d.overdue_principal
from risk_classification rc
join classification_grade g on g.grade_code = rc.grade_code
join delinquency_snapshot d on d.loan_id = rc.loan_id
where g.grade_name_zh = '正常' and d.principal_overdue_days > 30
order by d.principal_overdue_days desc, rc.loan_id"""),
    dict(
        id="BRB2-0346", difficulty="extra", features=[],
        penalty_law_zh="《商业银行金融资产风险分类办法》第二十四条及《商业银行监管评级办法》对资产质量真实性要求：集团客户或同一债务人存在交叉违约、多笔债务互负连带还款义务时，应将其名下全部债务一并下调；机构不得利用多头分类规避不良认定与拨备计提监管要求。",
        penalty_fact_zh="已统计出各机构存在“不良与正常/关注并存”的交叉违约客户规模，此类客户若按客户维度统一分类将显著扩大不良与拨备计提，现行做法涉嫌压降不良率与少提减值准备。",
        question="监管核查要求按机构口径统计“同一债务人名下既有不良借据又有非不良借据”的交叉违约客户数量，用于识别各机构通过选择性分类掩盖不良的规模。输出机构名称与该机构交叉违约客户数，按客户数由多到少排列，客户数相同再按机构名称从小到大排列。",
        sql="""with mix as (
  select a.borrower_party_id, a.institution_id,
    max(g.is_nonperforming) as mx, min(g.is_nonperforming) as mn
  from risk_classification rc
  join classification_grade g on g.grade_code = rc.grade_code
  join loan_drawdown ld on ld.loan_id = rc.loan_id
  join credit_agreement a on a.agreement_id = ld.agreement_id
  group by a.borrower_party_id, a.institution_id
  having max(g.is_nonperforming) = 1 and min(g.is_nonperforming) = 0
)
select i.institution_name, count(*) as 交叉违约客户数
from mix
join institution i on i.institution_id = mix.institution_id
group by i.institution_name
order by 交叉违约客户数 desc, i.institution_name"""),
    dict(
        id="BRB2-0347", difficulty="medium", features=[],
        penalty_law_zh="《商业银行预期信用损失法实施管理办法》及《银保监会关于商业银行不良资产拨备覆盖率的监管要求》：对已纳入不良的债权（次级、可疑、损失）必须足额计提预期信用损失准备；已计提拨备不得明显低于应计提拨备，监管要求拨备覆盖率不低于150%。",
        penalty_fact_zh="已识别出不良类借据中拨备覆盖率由低到高排列的前列记录，部分借据用于覆盖风险的损失准备明显不足，存在少计提拨备、虚增当期利润与资本充足水平的嫌疑。",
        question="监管核查要求对已划分为次级、可疑、损失等不良类的借据，逐笔测算其损失准备拨备覆盖率（已计提除以应计提），找出覆盖率最低、拨备明显不足的借据。输出借据编号与拨备覆盖率，按拨备覆盖率由低到高排列，覆盖率相同再按借据编号从小到大排列。",
        sql="""with np as (
  select rc.loan_id,
    max(case when g.is_nonperforming = 1 then 1 else 0 end) as nonp
  from risk_classification rc
  join classification_grade g on g.grade_code = rc.grade_code
  group by rc.loan_id
)
select ps.loan_id, round(ps.recognized_amount / ps.required_amount, 4) as 拨备覆盖率
from provision_snapshot ps
join np on np.loan_id = ps.loan_id
where np.nonp = 1
order by 拨备覆盖率 asc, ps.loan_id"""),
    dict(
        id="BRB2-0348", difficulty="medium", features=[],
        penalty_law_zh="《商业银行预期信用损失法实施管理办法》（银保监规〔2020〕4号）：风险自初始确认后已显著增加的金融资产应至少划分为第二阶段并计提相应损失准备；二阶段资产拨备覆盖率显著偏低的，监管将责令补提并视为风险准备不足。",
        penalty_fact_zh="部分机构的二阶段资产拨备覆盖率低于0.5的借据占比较高，说明对已发生信用风险显著增加的资产未足额计提损失准备，减值计提充分性存疑。",
        question="监管核查要求按机构统计：处于预期信用损失二阶段（风险显著增加）且损失准备拨备覆盖率（已计提除以应计提）低于0.5的借据笔数，识别对二阶段资产拨备计提偏弱的机构。输出机构名称与覆盖不足的借据笔数，按笔数由多到少排列，笔数相同再按机构名称从小到大排列。",
        sql="""select i.institution_name, count(*) as 覆盖不足笔数
from provision_snapshot ps
join loan_drawdown ld on ld.loan_id = ps.loan_id
join credit_agreement a on a.agreement_id = ld.agreement_id
join institution i on i.institution_id = a.institution_id
where ps.provision_stage = 'STAGE_2'
  and ps.recognized_amount / ps.required_amount < 0.5
group by i.institution_name
order by 覆盖不足笔数 desc, i.institution_name"""),
    dict(
        id="BRB2-0349", difficulty="hard", features=[],
        penalty_law_zh="《商业银行预期信用损失法实施管理办法》及财务报表损失准备充足性监管要求：对已发生信用减值的第三阶段资产必须按违约敞口足额计提损失准备，应计提与已计提之间不得存在缺口，缺口部分将被责令追补并影响监管评级。",
        penalty_fact_zh="已识别处于损失阶段且已计提准备低于应计提准备的借据，逐笔缺口经累计后构成损失准备不足的敞口，直接影响拨备覆盖率与不良资产覆险能力。",
        question="监管核查要求逐笔排查处于损失阶段（三阶段）的借据中，应计提与已计提损失准备之间的缺口，识别准备计提存在缺口的借据。输出借据编号、拨备所处阶段名称与拨备缺口金额，按拨备缺口由大到小排列，缺口相同再按借据编号从小到大排列。",
        sql="""select ps.loan_id, ps.provision_stage, round(ps.required_amount - ps.recognized_amount, 2) as 拨备缺口
from provision_snapshot ps
where ps.provision_stage = 'STAGE_3' and ps.required_amount > ps.recognized_amount
order by 拨备缺口 desc, ps.loan_id"""),
    dict(
        id="BRB2-0350", difficulty="medium", features=[],
        penalty_law_zh="《商业银行预期信用损失法实施管理办法》与拨备计提监管要求：商业银行应足额计提损失准备，任何“已计提低于应计提”的缺口均属风险准备不足，监管将责令限期补提并扣分处理。",
        penalty_fact_zh="各机构普遍存在损失准备“已计提小于应计提”的缺口，缺口的机构分布与规模已量化，反映拨备计提审慎性不足、可能虚增利润。",
        question="监管核查要求按机构统计损失准备“已计提低于应计提”的拨备缺口总额，评估各机构拨备计提的总体充分性。输出机构名称与拨备缺口合计金额，按缺口合计由大到小排列，缺口相同再按机构名称从小到大排列。",
        sql="""select i.institution_name, round(sum(ps.required_amount - ps.recognized_amount), 2) as 拨备缺口合计
from provision_snapshot ps
join loan_drawdown ld on ld.loan_id = ps.loan_id
join credit_agreement a on a.agreement_id = ld.agreement_id
join institution i on i.institution_id = a.institution_id
where ps.required_amount > ps.recognized_amount
group by i.institution_name
order by 拨备缺口合计 desc, i.institution_name"""),
    dict(
        id="BRB2-0351", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="客户主体类型要素缺失、分类错误导致穿透识别失真",
        question="列出处于久悬状态、属于储蓄类且未登记任何次要持有人的账户，输出账户编号、账户子类型与账面余额，按账面余额降序排列。",
        sql="""SELECT a.account_id,
       a.account_subtype,
       ab.ledger_balance
FROM account a
JOIN account_balance_snapshot ab ON ab.account_id = a.account_id
WHERE a.account_kind = 'SAVINGS'
  AND a.status = 'DORMANT'
  AND NOT EXISTS (
    SELECT 1 FROM account_holder h2
    WHERE h2.account_id = a.account_id AND h2.holder_role = 'SECONDARY'
  )
ORDER BY ab.ledger_balance DESC;"""),
    dict(
        id="BRB2-0352", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="个人客户职业画像缺失导致收入与风险承受能力评估失真",
        question="统计在职的固定雇佣员工在不同岗位角色上的任职数量，仅保留数量不少于二且非客户经理岗位，输出岗位角色与任职数量，按任职数量降序、岗位角色升序排列。",
        sql="""SELECT sga.role_code,
       COUNT(*) AS cnt
FROM staff_assignment sga
JOIN staff_member sm ON sm.staff_id = sga.staff_id
WHERE sm.employment_type = 'PERMANENT'
  AND sga.role_code <> 'RELATIONSHIP_MANAGER'
GROUP BY sga.role_code
HAVING COUNT(*) >= 2
ORDER BY cnt DESC, sga.role_code;"""),
    dict(
        id="BRB2-0353", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="高收入客户未纳入理财与高风险产品适当性管理名单",
        question="请统计年收入超过一百万元的个人画像客户按客户分层分布的数量，输出客户分层、客户数量，按客户数量降序排列；数量相同时按客户分层升序排列。",
        sql="""SELECT p.customer_segment AS seg, COUNT(*) AS cnt
FROM person_profile pp
JOIN party p ON p.party_id = pp.party_id
WHERE pp.annual_income > 1000000
GROUP BY p.customer_segment
ORDER BY cnt DESC, p.customer_segment;"""),
    dict(
        id="BRB2-0354", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="个人客户就业与收入信息未及时更新影响偿债能力评估",
        question="对投向受限行业的受托管理资产，按主要资产类别汇总资产数量，仅保留数量少于三十三的类别，输出主要资产类别与资产数量，按资产数量降序、主要资产类别升序排列。",
        sql="""SELECT ma.asset_category_primary,
       COUNT(*) AS cnt
FROM managed_asset ma
JOIN industry_sector isec ON isec.sector_code = ma.industry_code
WHERE isec.risk_category = 'RESTRICTED'
GROUP BY ma.asset_category_primary
HAVING COUNT(*) < 33
ORDER BY cnt DESC, ma.asset_category_primary;"""),
    dict(
        id="BRB2-0355", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="收入偿债比失控、多头授信未收敛导致过度借贷风险",
        question="对于拥有授信额度的个人客户，计算其授信额度合计与年收入之比（即偿债比），筛选偿债比大于三倍的客户，输出客户编号、年收入、授信额度合计、偿债比，按偿债比降序排列；比值相同时按客户编号升序排列，并仅取前十条记录（偿债比保留两位小数）。",
        sql="""SELECT pp.party_id, pp.annual_income,
       ROUND(SUM(f.limit_amount), 2) AS tot_credit,
       ROUND(SUM(f.limit_amount) / pp.annual_income, 2) AS ratio
FROM person_profile pp
JOIN credit_facility f ON f.obligor_party_id = pp.party_id
GROUP BY pp.party_id, pp.annual_income
HAVING SUM(f.limit_amount) / pp.annual_income > 3
ORDER BY ratio DESC, pp.party_id
LIMIT 10;"""),
    dict(
        id="BRB2-0356", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="政治公众人物未纳入强化尽职调查与名单监测清单",
        question="请统计公职人员（政治公众人物标识为是）客户按就业板块分布的数量，输出就业板块、客户数量，按客户数量降序排列；数量相同时按就业板块升序排列。",
        sql="""SELECT pp.employment_sector AS sector, COUNT(*) AS cnt
FROM person_profile pp
WHERE pp.is_public_official = 1
GROUP BY pp.employment_sector
ORDER BY cnt DESC, pp.employment_sector;"""),
    dict(
        id="BRB2-0357", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="客户分层与财富管理产品适配管理不到位",
        question="找出名下所有分期还款计划均无任何已结清期次的借据（借款人疑似从未正常还款），输出借据编号，按借据编号升序排列，只取前两百条。",
        sql="""SELECT ld.loan_id FROM loan_drawdown ld
WHERE NOT EXISTS (SELECT 1 FROM repayment_schedule rs WHERE rs.loan_id=ld.loan_id AND rs.status='PAID')
ORDER BY ld.loan_id
LIMIT 200;"""),
    dict(
        id="BRB2-0358", difficulty="extra", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="个人信贷过度集中、负债收入比畸高未压降",
        question="请对拥有信贷合同的个人客户，计算其信贷合同金额合计与年收入之比，筛选合同金额合计超过年收入五倍的客户，输出客户编号、合同金额合计、年收入、偿债比，按偿债比降序排列；相同时按客户编号升序排列，并仅取前十条记录。",
        sql="""SELECT pp.party_id,
       ROUND(SUM(a.contract_amount), 2) AS tot_contract,
       pp.annual_income,
       ROUND(SUM(a.contract_amount) / pp.annual_income, 2) AS ratio
FROM person_profile pp
JOIN credit_agreement a ON a.borrower_party_id = pp.party_id
GROUP BY pp.party_id, pp.annual_income
HAVING SUM(a.contract_amount) > 5 * pp.annual_income
ORDER BY ratio DESC, pp.party_id
LIMIT 10;"""),
    dict(
        id="BRB2-0359", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="职业与行业信息组合画像缺失导致准入评估不全面",
        question="请统计职业与就业板块组合下的个人客户数量，输出职业代号、就业板块、客户数量，按客户数量降序排列；数量相同时按职业代号升序排列后再按就业板块升序排列。",
        sql="""SELECT pp.occupation_code AS occ, pp.employment_sector AS sector, COUNT(*) AS cnt
FROM person_profile pp
GROUP BY pp.occupation_code, pp.employment_sector
ORDER BY cnt DESC, pp.occupation_code, pp.employment_sector;"""),
    dict(
        id="BRB2-0360", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="低收入客户准入与授信额度匹配审核不严",
        question="请统计年收入低于十五万元的个人客户数量，按客户所属营业单元统计，输出营业单元编号、营业单元名称、客户数量，按客户数量降序排列；数量相同时按营业单元名称升序排列。",
        sql="""SELECT o.org_unit_id, o.unit_name, COUNT(*) AS cnt
FROM person_profile pp
JOIN party p ON p.party_id = pp.party_id
JOIN party_type_catalog t ON t.party_type = p.party_type
JOIN organization_unit o ON o.org_unit_id = p.home_org_unit_id
WHERE t.name_zh = '个人客户' AND pp.annual_income < 150000
GROUP BY o.org_unit_id, o.unit_name
ORDER BY cnt DESC, o.unit_name;"""),
    dict(
        id="BRB2-0361", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="授信集中度风险未及时预警与限额管控",
        question="请对每位拥有授信额度的个人客户，按授信额度合计从高到低排名，计算其授信额度合计与年收入的比值，输出排名、客户编号、授信额度合计、偿债比，仅选取排名前五位客户并按其授信额度合计降序排列。",
        sql="""SELECT RANK() OVER (ORDER BY SUM(f.limit_amount) DESC) AS rnk,
       pp.party_id,
       ROUND(SUM(f.limit_amount), 2) AS tot_credit,
       ROUND(SUM(f.limit_amount) / pp.annual_income, 2) AS ratio
FROM person_profile pp
JOIN credit_facility f ON f.obligor_party_id = pp.party_id
GROUP BY pp.party_id, pp.annual_income
ORDER BY tot_credit DESC
LIMIT 5;"""),
    dict(
        id="BRB2-0362", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="金融从业等强相关行业客户交叉任职与关联风险识别不到位",
        question="请统计就业板块为金融机构或证券业的个人客户数量与平均年收入，分别输出就业板块、客户数量、平均年收入，按平均年收入降序排列；收入相同时按就业板块升序排列。",
        sql="""SELECT pp.employment_sector AS sector, COUNT(*) AS cnt, ROUND(AVG(pp.annual_income), 0) AS avg_income
FROM person_profile pp
WHERE pp.employment_sector IN ('FINANCE', 'SECURITIES')
GROUP BY pp.employment_sector
ORDER BY avg_income DESC, pp.employment_sector;"""),
    dict(
        id="BRB2-0363", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="银行卡品类统计口径不清、码表映射错误",
        question="按机构类型统计各类型纳入监管报告的机构数量及其最高一级资本，仅保留最高一级资本超过二百亿元的机构类型，输出机构类型、机构数量与最高一级资本，按机构数量降序、机构类型升序排列。",
        sql="""SELECT i.institution_type,
       COUNT(*) AS inst_cnt,
       MAX(cs.total_capital) AS max_cap
FROM institution i
LEFT JOIN capital_snapshot cs ON cs.institution_id = i.institution_id
GROUP BY i.institution_type
HAVING MAX(cs.total_capital) > 20000000000
ORDER BY inst_cnt DESC, i.institution_type;"""),
    dict(
        id="BRB2-0364", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="借记卡长期不动户与久悬账户清理不及时",
        question="请统计借记卡在各类卡状态下的发卡数量，输出卡状态、发卡数量，按发卡数量降序排列；数量相同时按卡状态升序排列。",
        sql="""SELECT c.status AS card_status, COUNT(*) AS cnt
FROM payment_card c
JOIN card_type_catalog t ON t.card_type = c.card_type
WHERE t.name_zh = '借记卡'
GROUP BY c.status
ORDER BY cnt DESC, c.status;"""),
    dict(
        id="BRB2-0365", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="信用卡套现与商户异常交易监测模型漏报",
        question="统计贷记卡结算账户作为付款转出账户发生的现金交易笔数与金额合计，按持卡人所属营业单元汇总，输出营业单元编号、营业单元名称、交易笔数与金额合计（保留两位小数），按金额合计降序、营业单元名称升序排列。",
        sql="""SELECT o.org_unit_id, o.unit_name, COUNT(*) AS n,
       ROUND(SUM(e.amount), 2) AS tot
FROM payment_event e
JOIN account a ON a.account_id = e.from_account_id
JOIN payment_card c ON c.settlement_account_id = a.account_id
JOIN card_type_catalog t ON t.card_type = c.card_type
JOIN party h ON h.party_id = c.holder_party_id
JOIN organization_unit o ON o.org_unit_id = h.home_org_unit_id
WHERE t.name_zh = '贷记卡' AND e.is_cash = 1
GROUP BY o.org_unit_id, o.unit_name
ORDER BY tot DESC, o.unit_name;"""),
    dict(
        id="BRB2-0366", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="套现交易未触发可疑交易报告与止付控制",
        question="检索贷记卡结算账户作为付款转出账户发生的现金交易与对应贷记卡记录，输出交易编号、银行卡编号、持卡人编号、交易日期与交易金额，按交易金额降序、交易编号升序、银行卡编号升序排列，并仅取前十条记录。",
        sql="""SELECT e.payment_id, c.card_id, h.party_id, e.business_date, e.amount
FROM payment_event e
JOIN account a ON a.account_id = e.from_account_id
JOIN payment_card c ON c.settlement_account_id = a.account_id
JOIN card_type_catalog t ON t.card_type = c.card_type
JOIN party h ON h.party_id = c.holder_party_id
WHERE t.name_zh = '贷记卡' AND e.is_cash = 1
ORDER BY e.amount DESC, e.payment_id, c.card_id
LIMIT 10;"""),
    dict(
        id="BRB2-0367", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="大额现金支取未执行预约与身份识别制度",
        question="对逾期天数介于一百五十至二百五十天且已计提第三阶段拨备的借据，统计其最长逾期天数与最高逾期本金，仅保留平均逾期本金超过二百万元的借据，输出借据编号、最长逾期天数与最高逾期本金，按最长逾期天数降序排列。",
        sql="""SELECT ds.loan_id,
       MAX(ds.principal_overdue_days) AS max_days,
       MAX(ds.overdue_principal) AS overdue_amt
FROM delinquency_snapshot ds
JOIN provision_snapshot ps ON ps.loan_id = ds.loan_id
WHERE ds.principal_overdue_days BETWEEN 150 AND 250
  AND ps.provision_stage = 'STAGE_3'
GROUP BY ds.loan_id
HAVING AVG(ds.overdue_principal) > 2000000
ORDER BY max_days DESC;"""),
    dict(
        id="BRB2-0368", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="高频套现客户未被纳入反欺诈与限额黑名单监控",
        question="请统计每位贷记卡持卡人发生的现金交易（疑似套现）笔数与金额合计，筛选现金交易笔数大于五笔的持卡人，输出持卡人编号、现金交易笔数、金额合计，按现金交易笔数降序排列；笔数相同时按金额合计降序排列，金额保留两位小数。",
        sql="""SELECT h.party_id, COUNT(*) AS n, ROUND(SUM(e.amount), 2) AS tot
FROM payment_event e
JOIN account a ON a.account_id = e.from_account_id
JOIN payment_card c ON c.settlement_account_id = a.account_id
JOIN card_type_catalog t ON t.card_type = c.card_type
JOIN party h ON h.party_id = c.holder_party_id
WHERE t.name_zh = '贷记卡' AND e.is_cash = 1
GROUP BY h.party_id
HAVING COUNT(*) > 5
ORDER BY n DESC, tot DESC;"""),
    dict(
        id="BRB2-0369", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="授信类银行卡准入与额度共债评估不严",
        question="按客户分层汇总该层次客户名下主控账户的账面余额合计，并给出各层次的余额名次，输出客户分层、账面余额合计与名次，按名次升序排列。",
        sql="""SELECT p.customer_segment, ROUND(SUM(abb.ledger_balance),2) AS tot,
       DENSE_RANK() OVER (ORDER BY SUM(abb.ledger_balance) DESC) AS rk
FROM account_balance_snapshot abb
JOIN account a ON a.account_id=abb.account_id
JOIN account_holder ah ON ah.account_id=a.account_id AND ah.holder_role='PRIMARY'
JOIN party p ON p.party_id=ah.party_id
GROUP BY p.customer_segment
ORDER BY rk;"""),
    dict(
        id="BRB2-0370", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="银行卡现金交易监测未覆盖平均金额异常形态",
        question="对于以保证方式登记的授信担保，统计各担保合同在全部保证承诺项下的保证金额合计，仅保留保证金额合计仍不足其担保金额的担保，输出担保合同编号、担保金额与保证金额合计，按保证金额合计升序排列。",
        sql="""SELECT sa.security_id,
       sa.secured_amount,
       SUM(COALESCE(gc.guaranteed_amount, 0)) AS guaranteed_total
FROM security_agreement sa
LEFT JOIN guarantor_commitment gc ON gc.security_id = sa.security_id
WHERE sa.security_type = 'GUARANTEE'
GROUP BY sa.security_id, sa.secured_amount
HAVING SUM(COALESCE(gc.guaranteed_amount, 0)) < sa.secured_amount
ORDER BY guaranteed_total ASC;"""),
    dict(
        id="BRB2-0371", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="一人多卡、拆分交易规避监管限额",
        question="请统计每位银行卡持卡人名下的发卡数量，筛选持卡数量大于三张的持卡人，输出持卡人编号、发卡数量，按发卡数量降序排列；数量相同时按持卡人编号升序排列。",
        sql="""SELECT c.holder_party_id, COUNT(*) AS cnt
FROM payment_card c
GROUP BY c.holder_party_id
HAVING COUNT(*) > 3
ORDER BY cnt DESC, c.holder_party_id;"""),
    dict(
        id="BRB2-0372", difficulty="extra", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="贷记卡套现与借记卡存取现金形态未做差异化监测",
        question="请比较贷记卡与借记卡两类银行卡的现金交易平均单笔金额，输出银行卡类型名称、交易笔数、平均单笔金额，按平均单笔金额降序排列；金额相同时按类型名称升序排列，金额保留两位小数。",
        sql="""SELECT t.name_zh AS card_type_name, COUNT(*) AS n,
       ROUND(AVG(e.amount), 2) AS avg_amt
FROM payment_event e
JOIN account a ON a.account_id = e.from_account_id
JOIN payment_card c ON c.settlement_account_id = a.account_id
JOIN card_type_catalog t ON t.card_type = c.card_type
WHERE t.name_zh IN ('贷记卡', '借记卡') AND e.is_cash = 1
GROUP BY t.card_type, t.name_zh
ORDER BY avg_amt DESC, t.name_zh;"""),
    dict(
        id="BRB2-0373", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="柜面柜员岗位配置与交接班管理不严",
        question="统计已结算且为非现金的支付交易在不同渠道的数量与平均金额，仅保留平均金额高于一千一百七十八万元的渠道，输出交易渠道、交易数量与平均金额，按平均金额降序、交易渠道升序排列。",
        sql="""SELECT pe.channel,
       COUNT(*) AS n,
       ROUND(AVG(pe.amount), 2) AS avg_amt
FROM payment_event pe
WHERE pe.is_cash = 0
  AND pe.status = 'SETTLED'
GROUP BY pe.channel
HAVING AVG(pe.amount) > 11780000
ORDER BY avg_amt DESC, pe.channel;"""),
    dict(
        id="BRB2-0374", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="柜面系统操作权限分级授信与复核机制落实不到位",
        question="找出账面余额超过其开户机构平均账面余额三倍的账户，疑似异常资金归集，输出机构名称、账户编号、账面余额、机构平均余额与超出金额，按超出金额降序排列。",
        sql="""WITH iavg AS (SELECT a.institution_id, AVG(abb.ledger_balance) AS av FROM account_balance_snapshot abb JOIN account a ON a.account_id=abb.account_id GROUP BY a.institution_id)
SELECT i.institution_name, a.account_id, ROUND(abb.ledger_balance,2) AS bal, ROUND(ia.av,2) AS avgbal, ROUND(abb.ledger_balance-ia.av,2) AS gap
FROM account_balance_snapshot abb JOIN account a ON a.account_id=abb.account_id
JOIN iavg ia ON ia.institution_id=a.institution_id
JOIN institution i ON i.institution_id=a.institution_id
WHERE abb.ledger_balance > 3*ia.av
ORDER BY gap DESC, a.account_id;"""),
    dict(
        id="BRB2-0375", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="柜面系统岗位与权限矩阵映射不完整",
        question="列出存款已到期但仍处于正常状态的定期存款及对应账户状态，疑似到期未兑付或未销户，输出账户编号、到期日期与账户状态，按到期日期降序排列，只取前两百条。",
        sql="""SELECT td.account_id, td.maturity_on, a.status
FROM term_deposit td JOIN account a ON a.account_id=td.account_id
WHERE julianday(td.maturity_on)<julianday('2026-06-30') AND a.status='ACTIVE'
ORDER BY td.maturity_on DESC, td.account_id
LIMIT 200;"""),
    dict(
        id="BRB2-0376", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="柜面操作员与员工编制岗位脱节、人员交叉任职",
        question="找出存期为三十天至一年之间且账户仍正常的定期存款，输出账户编号、开户本金、开立日期、到期日期与存期天数，按存期天数降序排列，只取前两百条。",
        sql="""SELECT td.account_id, td.opening_principal, td.booked_on, td.maturity_on,
       CAST(julianday(td.maturity_on)-julianday(td.booked_on) AS INTEGER) AS days
FROM term_deposit td
JOIN account a ON a.account_id=td.account_id
WHERE a.status='ACTIVE' AND CAST(julianday(td.maturity_on)-julianday(td.booked_on) AS INTEGER) BETWEEN 30 AND 366
ORDER BY days DESC, td.account_id
LIMIT 200;"""),
    dict(
        id="BRB2-0377", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="通过劳务派遣与借调规避重要岗位任职与轮岗要求",
        question="对每个抵质押物取其历次评估中价值最高的一次，但只统计进行过两次及以上评估的抵质押物，输出抵质押物编号、名称与最高评估价值，按最高评估价值降序排列。",
        sql="""WITH ranked AS (
  SELECT cv.collateral_id, cv.valuation_amount,
         ROW_NUMBER() OVER (PARTITION BY cv.collateral_id ORDER BY cv.valuation_amount DESC) AS rn,
         COUNT(*) OVER (PARTITION BY cv.collateral_id) AS n
  FROM collateral_valuation cv
)
SELECT ca.collateral_id, ca.asset_label, ROUND(r.valuation_amount,2) AS val
FROM ranked r JOIN collateral_asset ca ON ca.collateral_id=r.collateral_id
WHERE r.rn=1 AND r.n>=2
ORDER BY val DESC, ca.collateral_id;"""),
    dict(
        id="BRB2-0378", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="系统操作员账号管理与营业网点配置不匹配",
        question="列出在售状态且实际募集金额不足计划募集金额一半的理财产品，输出产品名称、实际募集金额与计划募集金额，按实际募集金额降序、产品名称升序排列。",
        sql="""SELECT wp.product_name,
       ROUND(wp.actual_raise_amount, 2) AS actual_amt,
       ROUND(wp.planned_raise_amount, 2) AS planned_amt
FROM wealth_product wp
WHERE wp.actual_raise_amount < wp.planned_raise_amount * 0.5
  AND wp.status = 'ON_SALE'
ORDER BY wp.actual_raise_amount DESC, wp.product_name;"""),
    dict(
        id="BRB2-0379", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="柜面系统最高权限账号过多、存在越权操作风险",
        question="找出持有两个及以上久悬账户的个人客户，输出客户编号与久悬账户数量，按久悬账户数量降序排列，只取前两百条。",
        sql="""SELECT p.party_id, COUNT(DISTINCT a.account_id) AS dormant_cnt
FROM party p
JOIN account_holder ah ON ah.party_id=p.party_id
JOIN account a ON a.account_id=ah.account_id AND a.status='DORMANT'
WHERE p.party_type='INDIVIDUAL'
GROUP BY p.party_id
HAVING COUNT(DISTINCT a.account_id)>=2
ORDER BY dormant_cnt DESC, p.party_id
LIMIT 200;"""),
    dict(
        id="BRB2-0380", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条、第四十八条",
        penalty_fact_zh="离职或调岗员工系统操作权限未及时注销",
        question="按授权等级统计柜面系统操作员的总数，并拆分其在高管监督与授信审核两类岗位上所登记的人数，输出授权等级、操作员总数、授信审核岗人数与高管监督岗人数，仅保留操作员总数不少于 2 名的等级，按总数降序、授权等级升序排列。",
        sql="""SELECT so.authority_level AS auth_level,
       COUNT(*) AS total_ops,
       SUM(CASE WHEN so.operator_kind = 'CREDIT_OFFICER' THEN 1 ELSE 0 END) AS credit_ops,
       SUM(CASE WHEN so.operator_kind = 'SUPERVISOR' THEN 1 ELSE 0 END) AS supervisor_ops
FROM service_operator so
GROUP BY so.authority_level
HAVING COUNT(*) >= 2
ORDER BY total_ops DESC, so.authority_level;"""),
    dict(
        id="BRB2-0381", difficulty="hard", features=[],
        penalty_law_zh="《储蓄管理条例》第三条、《商业银行法》第三十五条及《流动资金贷款管理办法》（2024）关于贷款“三查”与用途真实性的规定：严禁以存款作为发放贷款的条件，严禁要求借款人将贷款资金转存本行以满足存款考核（以贷转存）。",
        penalty_fact_zh="发现存在同时持有本行未结清贷款与定期存款的借款人，其存款与贷款之比被量化排序，反映出以贷转存、存贷挂钩、虚增存款规模的违规操作嫌疑。",
        question="穿透识别大额存贷挂钩型客户：既作为主账户持有人在本行开立定期存款且定期存款开户本金合计不少于一千万元、又在本行存在未结清贷款本金余额的借款人，输出借款人编号、借款人名称、未结清贷款余额、定期存款本金合计与存贷覆盖倍数（定期存款本金合计除以未结清贷款余额，保留两位小数），按覆盖倍数降序、借款人编号升序排列。",
        sql="""WITH dep AS (
    SELECT ah.party_id AS party_id,
           ROUND(SUM(td.opening_principal), 2) AS deposit_principal,
           COUNT(*) AS deposit_count
    FROM term_deposit td
    JOIN account ac ON ac.account_id = td.account_id
    JOIN account_holder ah ON ah.account_id = ac.account_id AND ah.holder_role = 'PRIMARY'
    GROUP BY ah.party_id
)
SELECT a.borrower_party_id AS party_id, p.display_name,
       ROUND(SUM(lbs.principal_balance), 2) AS loan_balance,
       d.deposit_principal,
       ROUND(d.deposit_principal * 1.0 / NULLIF(SUM(lbs.principal_balance), 0), 2) AS coverage
FROM credit_agreement a
JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
JOIN party p ON p.party_id = a.borrower_party_id
JOIN dep d ON d.party_id = a.borrower_party_id
WHERE d.deposit_principal >= 10000000
GROUP BY a.borrower_party_id, p.display_name, d.deposit_principal
ORDER BY coverage DESC, a.borrower_party_id;"""),
    dict(
        id="BRB2-0382", difficulty="medium", features=[],
        penalty_law_zh="《商业银行法》第四十七条及整治“以贷转存、存贷挂钩”监管要求：严禁银行贷款与存款业务捆绑，贷款客户在本行存款余额显著超过其贷款敞口的，属于变相搭配存款，将受到监管处罚。",
        penalty_fact_zh="已识别存款余额超过其本行未结清贷款余额的借款人，此类存贷倒挂客户涉嫌以贷款资金或关联资金沉淀为本行存款，虚增负债规模并扭曲流动性指标。",
        question="排查存款规模倒挂型异常客户：将对公客户在结算与储蓄账户上的账面存款余额合计，与其在本行的未结清贷款本金余额合计进行比较，仅保留存款余额超过贷款余额、且放款余额大于零的客户，输出客户编号、客户名称、存款余额与贷款余额，按存款余额降序、客户编号升序排列。",
        sql="""WITH loan_tot AS (
    SELECT a.borrower_party_id AS party_id,
           ROUND(SUM(lbs.principal_balance), 2) AS loan_balance,
           COUNT(DISTINCT ld.loan_id) AS loan_cnt
    FROM credit_agreement a
    JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
    JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
    GROUP BY a.borrower_party_id
)
SELECT p.party_id, p.display_name,
       ROUND(SUM(ab.ledger_balance), 2) AS deposit_balance,
       lt.loan_balance
FROM party p
JOIN account_holder ah ON ah.party_id = p.party_id AND ah.holder_role = 'PRIMARY'
JOIN account ac ON ac.account_id = ah.account_id
JOIN account_balance_snapshot ab ON ab.account_id = ac.account_id
JOIN loan_tot lt ON lt.party_id = p.party_id
WHERE p.party_type = 'CORPORATE'
  AND ac.account_kind IN ('CURRENT', 'SAVINGS')
GROUP BY p.party_id, p.display_name, lt.loan_balance
HAVING SUM(ab.ledger_balance) > lt.loan_balance
   AND lt.loan_balance > 0
ORDER BY deposit_balance DESC, p.party_id;"""),
    dict(
        id="BRB2-0383", difficulty="medium", features=[],
        penalty_law_zh="《商业银行法》与《流动资金贷款管理办法》关于贷款资金流向与用途真实性规定：借款人贷款已逾期却仍持有大额定期存单，涉嫌以存单抵质押套取贷款或以贷转存，构成贷后资金用途失实与存款虚增违规。",
        penalty_fact_zh="已识别贷款存在本金逾期却仍在本行持有大额定期存单的借款人，其存款沉淀反映贷款资金并非全部真实使用，存在借新还旧、以存抵贷的资金空转风险。",
        question="监管核查要求识别“贷款已发生本金逾期、却在同一机构仍持有大额定期存单”的借款人，此类情形反映以存抵贷、贷款资金回流的异常资金安排。输出债务人编号、债务人名称、其名下定期存单金额合计与存单笔数，按定期存单金额由大到小排列，金额相同再按债务人编号从小到大排列。",
        sql="""with od as (
  select distinct a.borrower_party_id
  from credit_agreement a
  join loan_drawdown ld on ld.agreement_id = a.agreement_id
  join delinquency_snapshot d on d.loan_id = ld.loan_id and d.principal_overdue_days > 0
)
select od.borrower_party_id, p.display_name,
  round(sum(td.opening_principal), 2) as 定期存单金额, count(*) as 存单笔数
from od
join party p on p.party_id = od.borrower_party_id
join account_holder ah on ah.party_id = od.borrower_party_id and ah.holder_role = 'PRIMARY'
join account ac on ac.account_id = ah.account_id
join term_deposit td on td.account_id = ac.account_id
group by od.borrower_party_id, p.display_name
order by 定期存单金额 desc, od.borrower_party_id"""),
    dict(
        id="BRB2-0384", difficulty="medium", features=[],
        penalty_law_zh="《商业银行法》第四十七条及监管“以贷转存”专项治理要求：银行不得将存款指标与贷款发放挂钩，各机构以此类方式虚增存款余额与贷款规模的，将被责令整改并给予处罚。",
        penalty_fact_zh="已从机构层面量化与存款挂钩的贷款规模与客户数，相关机构存在以贷吸存、存贷绑定的业务结构，需按监管要求整改业务考核与授信流程。",
        question="监管核查要求从机构层面统计“存贷挂钩”业务的总体规模：各机构向同时在本行持有定期存款的借款人发放的贷款余额合计与涉及的挂钩客户数。输出机构名称、挂钩客户数与挂钩贷款余额合计，按挂钩贷款余额合计由大到小排列，余额相同再按机构名称从小到大排列。",
        sql="""with dep as (
  select ah.party_id, sum(td.opening_principal) as dep_total
  from term_deposit td
  join account ac on ac.account_id = td.account_id
  join account_holder ah on ah.account_id = ac.account_id and ah.holder_role = 'PRIMARY'
  group by ah.party_id
),
lob as (
  select a.borrower_party_id, a.institution_id, sum(lbs.principal_balance) as loan_bal
  from credit_agreement a
  join loan_drawdown ld on ld.agreement_id = a.agreement_id
  join loan_balance_snapshot lbs on lbs.loan_id = ld.loan_id
  group by a.borrower_party_id, a.institution_id
)
select i.institution_name, count(distinct lob.borrower_party_id) as 挂钩客户数,
  round(sum(lob.loan_bal), 2) as 挂钩贷款余额合计
from lob
join dep on dep.party_id = lob.borrower_party_id
join institution i on i.institution_id = lob.institution_id
group by i.institution_name
order by 挂钩贷款余额合计 desc, i.institution_name"""),
    dict(
        id="BRB2-0385", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》（银监发〔2017〕16号）第二十条、第二十三条：押品担保期限应覆盖授信存续期限，押品担保期限届满时银行应及时要求展期或补充担保；担保脱保致债权悬空、第二还款来源落空的，监管将责令限期整改。",
        penalty_fact_zh="已识别担保合同有效期早于授信合同到期日的错配记录，生效授信对应的担保已届期或提前失效，第二还款来源落空，存在实质性脱保风险。",
        question="穿透识别处于有效状态的授信合同中的“担保期限悬空”风险：通过被担保主债权桥接表关联担保合同与有效授信合同，找出担保合同有效期届满日早于所担保授信合同到期日的桥接记录，输出被担保主债权桥接编号、授信合同编号、担保合同编号、担保合同有效期届满日与授信合同到期日，按授信合同到期日由早到晚、被担保主债权桥接编号从小到大排列。",
        sql="""select so.secured_obligation_id, a.agreement_id, sa.security_id,
  sa.effective_to, a.maturity_on
from secured_obligation so
join security_agreement sa on sa.security_id = so.security_id
join credit_agreement a on a.agreement_id = so.agreement_id
where sa.effective_to < a.maturity_on and a.status = 'ACTIVE'
order by a.maturity_on asc, so.secured_obligation_id"""),
    dict(
        id="BRB2-0386", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》及《商业银行与内部人和股东关联交易管理办法》关于担保有效性的要求：担保履行期限应与主债权存续期相匹配，担保期限不足构成担保瑕疵，监管要求纠正并按担保有效性下迁资产分类。",
        penalty_fact_zh="已按机构与担保方式汇总期限错配的合同数量，部分机构特定担保方式下脱保高发，反映担保管理未建立续保监测机制。",
        question="监管核查要求按机构与担保方式两个维度统计“担保合同到期日早于授信合同到期日”的期限错配合同数量，定位脱保风险高发的机构与担保方式。输出机构名称、担保方式与错配合同数，按错配合同数由多到少排列，再依次按机构名称、担保方式从小到大排列。",
        sql="""select i.institution_name, sa.security_type, count(*) as 错配合同数
from secured_obligation so
join security_agreement sa on sa.security_id = so.security_id
join credit_agreement a on a.agreement_id = so.agreement_id
join institution i on i.institution_id = a.institution_id
where sa.effective_to < a.maturity_on
group by i.institution_name, sa.security_type
order by 错配合同数 desc, i.institution_name, sa.security_type"""),
    dict(
        id="BRB2-0387", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》第三十三条、第四十五条：同一押品被用于多笔担保的，各笔债权合计不得显著超出押品价值；银行应评估重复担保对押品覆盖能力的稀释，超值担保将弱化第二还款来源并影响风险缓释有效性。",
        penalty_fact_zh="已识别同一押品多项质押金额合计超过其最新评估价值的押品，重复押抵导致债权保障不足，押品变现价值无法覆盖合计债务。",
        question="监管核查要求识别“一物多押、超值押抵”：同一押品在多个担保合同中被重复质押，其最新评估价值低于各项质押金额合计，构成押品价值超质押。输出押品编号、押品标识、最新评估价值、质押金额合计与超押金额，按超押金额由大到小排列，超押金额相同再按押品编号从小到大排列。",
        sql="""with latest_val as (
  select collateral_id, valuation_amount,
    row_number() over (partition by collateral_id order by valued_on desc, valuation_id desc) as rn
  from collateral_valuation
),
pt as (
  select collateral_id, round(sum(pledged_amount), 2) as total_pledged
  from collateral_link where status = 'ACTIVE'
  group by collateral_id
)
select ca.collateral_id, ca.asset_label, lv.valuation_amount as 最新评估值,
  pt.total_pledged as 质押合计, round(pt.total_pledged - lv.valuation_amount, 2) as 超押金额
from collateral_asset ca
join latest_val lv on lv.collateral_id = ca.collateral_id and lv.rn = 1
join pt on pt.collateral_id = ca.collateral_id
where lv.valuation_amount < pt.total_pledged
order by 超押金额 desc, ca.collateral_id"""),
    dict(
        id="BRB2-0388", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》第四十四条：银行应按押品评估价值审慎核定担保金额，同一押品支持的担保总额不得超过其评估价值；违反超值担保的，监管将认定抵质押缓释效力不足。",
        penalty_fact_zh="已识别质押合计金额超过押品最低评估价值的押品，重复质押导致押品风险缓释能力被高估。",
        question="监管核查要求识别同一押品在多笔担保中被质押、且质押金额合计超过其最低一次评估价值的押品，以判断押品价值对债务覆盖的充分性。输出押品编号、质押金额合计、最低评估价值与超押金额，按超押金额由大到小排列，超押金额相同再按押品编号从小到大排列。",
        sql="""with mv as (
  select collateral_id, min(valuation_amount) as min_val, max(valuation_amount) as max_val
  from collateral_valuation group by collateral_id
)
select cl.collateral_id, round(sum(cl.pledged_amount), 2) as 质押合计, mv.min_val as 最低评估值,
  round(sum(cl.pledged_amount) - mv.min_val, 2) as 超押
from collateral_link cl
join mv on mv.collateral_id = cl.collateral_id
where cl.status = 'ACTIVE'
group by cl.collateral_id, mv.min_val
having sum(cl.pledged_amount) > mv.min_val
order by 超押 desc, cl.collateral_id"""),
    dict(
        id="BRB2-0389", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》第二十九条：银行应对押品及其担保关系进行持续监测，掌握同一押品被多笔担保使用的情况，防范押品重复登记导致的担保悬空与覆盖虚增。",
        penalty_fact_zh="已识别被多笔担保反复引用的押品，其担保链撕裂任一笔将牵连多笔债权，押品集中使用放大风险缓释的不确定性。",
        question="监管核查要求识别被反复用于多笔担保的同一押品，评估“一物多押”对押品集中度的放大。输出押品编号、押品标识、押品被引用的次数与关联的不同担保合同数，按押品被引用次数由多到少排列，次数相同再按押品编号从小到大排列（仅统计有效状态的押品关联记录，引用次数不少于两次）。",
        sql="""select cl.collateral_id, ca.asset_label, count(*) as 押品使用次数,
  count(distinct cl.security_id) as 关联担保数
from collateral_link cl
join collateral_asset ca on ca.collateral_id = cl.collateral_id
where cl.status = 'ACTIVE'
group by cl.collateral_id, ca.asset_label
having count(*) >= 2
order by 押品使用次数 desc, cl.collateral_id"""),
    dict(
        id="BRB2-0390", difficulty="medium", features=[],
        penalty_law_zh="《担保法》与《商业银行担保业务管理》要求保证担保额度应与实际债权敞口一致；担保金额显著超过对应授信敞口且无对应债权基础的，反映担保管理记录不实或超额担保，监管将要求核实并规范。",
        penalty_fact_zh="存在担保人保证金额大于对应贷款发放金额的不匹配记录，担保余额虚高造成风险缓释额被重复计算或高估。",
        question="识别保证人单笔有效保证承诺金额超过其所担保授信合同项下实际放款总金额的异常担保记录：先按授信合同汇总放款借据的实际放款总金额，再通过被担保主债权桥接表关联担保合同与有效保证人承诺，找出单笔保证承诺金额大于对应授信合同实际放款总金额的记录，输出保证人客户编号、保证人名称、授信合同编号、保证承诺金额与该合同实际放款总金额（保留两位小数），按保证承诺金额降序、保证人客户编号升序、授信合同编号升序排列。",
        sql="""WITH agr_loan AS (
  SELECT agreement_id, ROUND(SUM(disbursed_amount), 2) AS total_disbursed
  FROM loan_drawdown
  GROUP BY agreement_id
)
SELECT gmt.guarantor_party_id, p.display_name, so.agreement_id,
       gmt.guaranteed_amount, al.total_disbursed
FROM guarantor_commitment gmt
JOIN party p ON p.party_id = gmt.guarantor_party_id
JOIN security_agreement sa ON sa.security_id = gmt.security_id
JOIN secured_obligation so ON so.security_id = sa.security_id
JOIN agr_loan al ON al.agreement_id = so.agreement_id
WHERE gmt.status = 'ACTIVE' AND gmt.guaranteed_amount > al.total_disbursed
ORDER BY gmt.guaranteed_amount DESC, gmt.guarantor_party_id, so.agreement_id;"""),
    dict(
        id="BRB2-0391", difficulty="hard", features=[],
        penalty_law_zh="中国人民银行《银行卡业务管理办法》及信用卡贷后管理要求：持卡人信用状况恶化或贷款出现重大逾期的，银行应及时采取降额、止付等措施控制风险；对风控失职、继续放任逾期客户用卡的，监管将按信用卡业务违规处罚。",
        penalty_fact_zh="已识别贷款本金逾期而名下有效贷记卡仍持续发生消费或现金交易的多条记录，反映信用卡止付与联动风控机制未有效触发，风险敞口继续扩大。",
        question="监管核查要求穿透识别“逾期借款人未止付信用卡”：贷款已发生本金逾期的借款人，名下仍持有效的贷记卡并继续发生卡消费或现金支取交易，反映未及时止付、风险敞口持续扩大的管控缺失。输出债务人编号、债务人名称、贷记卡卡号、交易流水号与交易金额，按交易金额由大到小排列，再依次按债务人编号、卡号、流水号从小到大排列，取交易金额最大的前100条。",
        sql="""select distinct a.borrower_party_id, p.display_name, pc.card_id, pe.payment_id, pe.amount
from credit_agreement a
join loan_drawdown ld on ld.agreement_id = a.agreement_id
join delinquency_snapshot d on d.loan_id = ld.loan_id and d.principal_overdue_days > 0
join party p on p.party_id = a.borrower_party_id
join payment_card pc on pc.holder_party_id = a.borrower_party_id and pc.status = 'ACTIVE' and pc.card_type = 'CREDIT'
join payment_event pe on pe.from_account_id = pc.settlement_account_id
  and pe.payment_type in ('CARD_PURCHASE','CASH_WITHDRAWAL')
order by pe.amount desc, a.borrower_party_id, pc.card_id, pe.payment_id
limit 100"""),
    dict(
        id="BRB2-0392", difficulty="medium", features=[],
        penalty_law_zh="《银行卡业务管理办法》及信用卡风险管控要求：对已出现本金逾期的借款人，其名下多张有效贷记卡应同步纳入监控并实施止付；未与贷款风险联动管控多卡的，构成信用卡授信过度与风控缺失。",
        penalty_fact_zh="已识别本金逾期借款人名下仍持有有效贷记卡的多卡记录，未依据其贷款风险状况集中止付，存在多通道继续透支的风险。",
        question="监管核查要求识别名下拥有有效贷记卡、且其在本行贷款已发生本金逾期的借款人及各人名下有效贷记卡数量。输出持卡人编号与有效贷记卡数量，按有效贷记卡数量由多到少排列，数量相同再按持卡人编号从小到大排列。",
        sql="""select pc.holder_party_id, count(*) as 有效贷记卡数
from payment_card pc
where pc.card_type = 'CREDIT' and pc.status = 'ACTIVE'
  and pc.holder_party_id in (
    select distinct a.borrower_party_id
    from credit_agreement a
    join loan_drawdown ld on ld.agreement_id = a.agreement_id
    join delinquency_snapshot d on d.loan_id = ld.loan_id
  )
group by pc.holder_party_id
order by 有效贷记卡数 desc, pc.holder_party_id"""),
    dict(
        id="BRB2-0393", difficulty="medium", features=[],
        penalty_law_zh="《银行卡业务管理办法》及《商业银行信用卡业务监督管理办法》：对已发生重大逾期或信用状况恶化的持卡人应实施止付、降额；机构放任逾期客户继续通过贷记卡透支的，构成风险管控不到位并被追责。",
        penalty_fact_zh="已按机构量化逾期借款人在未止付贷记卡上继续发生的消费与现金支取规模，反映信用卡与贷款业务的联动风险管控缺位。",
        question="监管核查要求从机构层面统计：向贷款已发生本金逾期的借款人发放的贷记卡，在其名下仍发生的卡消费或现金支取交易金额与笔数，评估逾期客户未止付卡的用卡规模。输出机构名称、逾期客户卡消费金额合计与交易笔数，按消费金额合计由大到小排列，金额相同再按机构名称从小到大排列。",
        sql="""with odl as (
  select distinct a.borrower_party_id, a.institution_id
  from credit_agreement a
  join loan_drawdown ld on ld.agreement_id = a.agreement_id
  join delinquency_snapshot d on d.loan_id = ld.loan_id and d.principal_overdue_days > 0
)
select i.institution_name,
  round(sum(pe.amount), 2) as 逾期客户卡消费金额, count(*) as 交易笔数
from odl
join institution i on i.institution_id = odl.institution_id
join payment_card pc on pc.holder_party_id = odl.borrower_party_id and pc.status = 'ACTIVE' and pc.card_type = 'CREDIT'
join payment_event pe on pe.from_account_id = pc.settlement_account_id
  and pe.payment_type in ('CARD_PURCHASE','CASH_WITHDRAWAL')
group by i.institution_name
order by 逾期客户卡消费金额 desc, i.institution_name"""),
    dict(
        id="BRB2-0394", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》与《贷款通则》关于第二还款来源的要求：抵质押、保证担保应充分覆盖授信风险敞口；担保覆盖金额不足授信金额的，属于担保不足额，银行应追加担保或相应下调资产分类与资本缓释。",
        penalty_fact_zh="已识别担保合同覆盖金额合计低于授信合同金额的合同，部分债权缺乏足额第二还款来源，风险缓释有效性不足。",
        question="监管核查要求识别“担保覆盖不足”：有效授信合同由有效担保合同覆盖，但各项担保覆盖金额合计低于授信合同金额，即债权存在未完全覆盖的部分。输出授信合同编号、债务人编号、授信合同金额、担保覆盖合计与保障缺口，按保障缺口由大到小排列，缺口相同再按授信合同编号从小到大排列，取缺口最大的前100条。",
        sql="""select a.agreement_id, a.borrower_party_id, a.contract_amount,
  round(sum(so.covered_amount), 2) as 担保覆盖合计,
  round(a.contract_amount - sum(so.covered_amount), 2) as 保障缺口
from credit_agreement a
join secured_obligation so on so.agreement_id = a.agreement_id
join security_agreement sa on sa.security_id = so.security_id
where a.status = 'ACTIVE' and sa.status = 'ACTIVE'
group by a.agreement_id, a.borrower_party_id, a.contract_amount
having sum(so.covered_amount) < a.contract_amount
order by 保障缺口 desc, a.agreement_id
limit 100"""),
    dict(
        id="BRB2-0395", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》《流动资金贷款管理办法》：除信用贷款外，授信应落实足值担保；已承诺担保却未实际落实有效担保（完全脱保）的授信，应视为担保违约并责成整改，监管将要求核查担保落实环节。",
        penalty_fact_zh="已识别处于有效状态却无任何有效担保覆盖的授信合同，债权处于完全无担保状态，一旦违约将无第二还款来源。",
        question="监管核查要求识别“完全脱保”的授信：处于有效存续状态、金额大于零的授信合同，却不存在任何一项处于有效状态的担保覆盖记录，即债权完全没有抵质押或保证支撑。输出授信合同编号、债务人编号与授信合同金额，按授信合同金额由大到小排列，金额相同再按授信合同编号从小到大排列，取金额最大的前100条。",
        sql="""select a.agreement_id, a.borrower_party_id, a.contract_amount
from credit_agreement a
where a.status = 'ACTIVE'
  and not exists (
    select 1 from secured_obligation so
    join security_agreement sa on sa.security_id = so.security_id
    where so.agreement_id = a.agreement_id and sa.status = 'ACTIVE'
  )
order by a.contract_amount desc, a.agreement_id
limit 100"""),
    dict(
        id="BRB2-0396", difficulty="medium", features=[],
        penalty_law_zh="《商业银行预期信用损失法实施管理办法》：次级类资产属不良资产，应足额计提损失准备；已计提低于应计提的次级借据反映减值计提不充分，监管将责令补提并影响资本与利润真实性。",
        penalty_fact_zh="已识别次级类借据中拨备计提不足的机构分布与笔数，次级资产减值准备缺口显著，存在少提拨备虚增利润问题。",
        question="监管核查要求按机构统计：已划分为次级类的不良借据中，损失准备“已计提低于应计提”的借据笔数，识别对次级资产拨备不足的机构。输出机构名称、五级分类名称与拨备不足的借据笔数，按借据笔数由多到少排列，笔数相同再按机构名称从小到大排列。",
        sql="""select i.institution_name, g.grade_name_zh, count(*) as 拨备不足借据数
from provision_snapshot ps
join risk_classification rc on rc.loan_id = ps.loan_id
join classification_grade g on g.grade_code = rc.grade_code
join loan_drawdown ld on ld.loan_id = ps.loan_id
join credit_agreement a on a.agreement_id = ld.agreement_id
join institution i on i.institution_id = a.institution_id
where g.grade_name_zh = '次级' and ps.required_amount > ps.recognized_amount
group by i.institution_name, g.grade_name_zh
order by 拨备不足借据数 desc, i.institution_name"""),
    dict(
        id="BRB2-0397", difficulty="hard", features=[],
        penalty_law_zh="《流动资金贷款管理办法》《固定资产贷款管理办法》：贷款发放不得超过授信额度与合同金额，超授信用信属违规放款，监管将责令收回超限部分并追究审查审批责任。",
        penalty_fact_zh="已识别贷款本金余额超过授信合同金额的借据，实际用信突破授信限额，反映授信额度管控失效或越权放款。",
        question="监管核查要求穿透识别“超授信额度放款”：借据当前贷款本金余额超过其所属授信合同授信金额至少4倍的借据，说明实际用信大幅突破合同限额。输出债务人编号、借据编号、贷款余额、授信金额与余额倍数，按余额倍数由大到小排列，倍数相同再按借据编号从小到大排列（至少四倍含恰为四倍，余额倍数保留两位小数）。",
        sql="""select a.borrower_party_id, l.loan_id, l.principal_balance as 贷款余额,
  a.contract_amount as 授信金额, round(l.principal_balance / a.contract_amount, 2) as 余额倍数
from loan_balance_snapshot l
join loan_drawdown ld on ld.loan_id = l.loan_id
join credit_agreement a on a.agreement_id = ld.agreement_id
where l.principal_balance >= 4.0 * a.contract_amount
order by 余额倍数 desc, l.loan_id"""),
    dict(
        id="BRB2-0398", difficulty="medium", features=[],
        penalty_law_zh="《商业银行金融资产风险分类办法》与《不良金融资产处置尽职指引》（银监发〔2010〕96号）：银行应真实、完整反映不良资产的规模与级别分布，据实计提相应损失准备并落实清收处置，不得人为调减不良级别。",
        penalty_fact_zh="已量化次级、可疑、损失各类不良的本金敞口与笔数，用于核对分类准确性与拨备计提、处置计划的真实性。",
        question="监管核查要求对不良类（次级、可疑、损失）五级分类逐级统计其当前贷款本金余额与借据笔数，评估各不良级别的敞口总量。输出五级分类名称、借据笔数与本金合计金额，按借据笔数由多到少排列，笔数相同再按五级分类名称从小到大排列。",
        sql="""select g.grade_name_zh, count(*) as 借据数, round(sum(lbs.principal_balance), 2) as 本金合计
from risk_classification rc
join classification_grade g on g.grade_code = rc.grade_code
join loan_balance_snapshot lbs on lbs.loan_id = rc.loan_id
where g.is_nonperforming = 1
group by g.grade_name_zh
order by 借据数 desc, g.grade_name_zh"""),
    dict(
        id="BRB2-0399", difficulty="medium", features=[],
        penalty_law_zh="《商业银行金融资产风险分类办法》第十四条：本金无意延期且逾期超过90天的债权，分类至少应下调至次级，不得保留在正常或关注类；机构逾期90天以上仍不下调的，属分类人为滞后，监管将予以纠正并处罚。",
        penalty_fact_zh="已按机构统计逾期超过90天仍被划分为非不良的借据数量，存在分类下迁迟滞，不良真实性受质疑。",
        question="监管核查要求按机构统计“本金逾期超过90天但未下调至不良类”的借据笔数，识别分类调整滞后的机构。输出机构名称与逾期未下调的借据笔数，按借据笔数由多到少排列，笔数相同再按机构名称从小到大排列。",
        sql="""with dd as (
  select ld.loan_id, a.institution_id
  from loan_drawdown ld
  join credit_agreement a on a.agreement_id = ld.agreement_id
  join (select loan_id from delinquency_snapshot where principal_overdue_days > 90) d on d.loan_id = ld.loan_id
)
select i.institution_name, count(*) as 逾期未下调借据数
from risk_classification rc
join classification_grade g on g.grade_code = rc.grade_code
join dd on dd.loan_id = rc.loan_id
join institution i on i.institution_id = dd.institution_id
where g.is_nonperforming = 0
group by i.institution_name
order by 逾期未下调借据数 desc, i.institution_name"""),
    dict(
        id="BRB2-0400", difficulty="medium", features=[],
        penalty_law_zh="《商业银行预期信用损失法实施管理办法》及财务审慎监管要求：损失准备应按统一模型与政策足额、审慎计提，不得为调节利润任意超额计提；对超额计提影响损益真实性的，监管将要求还原调整。",
        penalty_fact_zh="已识别不良类借据中已计提超过应计提的机构与级别分布，超额计提准备存在蓄意压低利润、隐藏利润的调节嫌疑。",
        question="监管核查要求按机构与五级分类两个维度统计“不良类借据已计提损失准备超过应计提金额”的笔数与多计提金额，识别损失准备计提不审慎（超额计提、利润调节）的机构。输出机构名称、五级分类名称、多计提笔数与多计提金额合计，按多计提金额合计由大到小排列，再依次按机构名称、五级分类名称从小到大排列。",
        sql="""select i.institution_name, g.grade_name_zh, count(*) as 多计提笔数,
  round(sum(ps.recognized_amount - ps.required_amount), 2) as 多计提金额
from provision_snapshot ps
join risk_classification rc on rc.loan_id = ps.loan_id
join classification_grade g on g.grade_code = rc.grade_code
join loan_drawdown ld on ld.loan_id = ps.loan_id
join credit_agreement a on a.agreement_id = ld.agreement_id
join institution i on i.institution_id = a.institution_id
where g.is_nonperforming = 1 and ps.recognized_amount > ps.required_amount
group by i.institution_name, g.grade_name_zh
order by 多计提金额 desc, i.institution_name, g.grade_name_zh"""),
    dict(
        id="BRB2-0401", difficulty="easy", features=[],
        penalty_law_zh="《商业银行押品管理指引》第二十六条；《商业银行授信工作尽职指引》第三十三条",
        penalty_fact_zh="担保债权金额低于授信合同金额，押品覆盖明显不足",
        question="通过被担保主债权桥接表关联担保合同与授信协议，找出被担保债权覆盖金额低于授信合同金额的记录，输出担保合同编号、授信协议编号、被担保债权覆盖金额、授信合同金额与缺口金额（合同金额减覆盖金额，保留两位小数），按缺口金额降序排列。",
        sql="""SELECT sa.security_id, so.agreement_id, so.covered_amount, a.contract_amount,
       ROUND(a.contract_amount - so.covered_amount, 2) AS gap
FROM secured_obligation so
JOIN security_agreement sa ON sa.security_id = so.security_id
JOIN credit_agreement a ON a.agreement_id = so.agreement_id
WHERE so.covered_amount < a.contract_amount
ORDER BY gap DESC, sa.security_id, so.agreement_id;"""),
    dict(
        id="BRB2-0402", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第十三条；《商业银行授信工作尽职指引》第七十四条",
        penalty_fact_zh="同一授信协议整体担保覆盖不足，抵质押与保证合计仍低于合同金额",
        question="汇总每笔授信协议通过被担保主债权桥接表关联的被担保债权金额合计，并与该协议合同金额比较，找出被担保金额合计仍低于合同金额的授信协议，输出协议编号、借款人编号、合同金额、被担保金额合计与缺口金额，按缺口金额降序排列，缺口金额按合同金额减被担保金额合计计算后四舍五入到两位小数。",
        sql="""SELECT a.agreement_id, a.borrower_party_id, a.contract_amount,
       ROUND(SUM(so.covered_amount), 2) AS covered_total,
       ROUND(a.contract_amount - SUM(so.covered_amount), 2) AS gap
FROM credit_agreement a
JOIN secured_obligation so ON so.agreement_id = a.agreement_id
JOIN security_agreement sa ON sa.security_id = so.security_id
WHERE sa.status = 'ACTIVE'
GROUP BY a.agreement_id, a.borrower_party_id, a.contract_amount
HAVING SUM(so.covered_amount) < a.contract_amount
ORDER BY a.contract_amount - SUM(so.covered_amount) DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0403", difficulty="medium", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》第五十六条；《商业银行集团客户授信业务风险管理指引》第六条",
        penalty_fact_zh="单户担保覆盖金额过高，逆担保集中度风险突出",
        question="按借款人汇总其名下所有授信通过被担保主债权桥接表取得的被担保债权金额合计，只保留合计超过四亿元的借款人，输出借款人编号、借款人名称与被担保金额合计，按合计金额降序排列，合计金额四舍五入到两位小数。",
        sql="""SELECT a.borrower_party_id, p.display_name,
       ROUND(SUM(so.covered_amount), 2) AS covered_total
FROM secured_obligation so
JOIN security_agreement sa ON sa.security_id = so.security_id
JOIN credit_agreement a ON a.agreement_id = so.agreement_id
JOIN party p ON p.party_id = a.borrower_party_id
WHERE sa.status = 'ACTIVE'
GROUP BY a.borrower_party_id, p.display_name
HAVING SUM(so.covered_amount) > 400000000
ORDER BY SUM(so.covered_amount) DESC, a.borrower_party_id;"""),
    dict(
        id="BRB2-0404", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》第十一条；《银行业金融机构案件防控要求》相关条款",
        penalty_fact_zh="机构层面担保覆盖总量统计失真，缺乏统一担保集中度监测",
        question="按机构汇总其授信协议经被担保主债权桥接表关联的有效担保合同的被担保债权金额合计与担保合同笔数，输出机构名称、担保合同笔数与被担保金额合计，按被担保金额合计降序排列，金额四舍五入到两位小数。",
        sql="""SELECT i.institution_name, COUNT(DISTINCT so.security_id) AS sec_count,
       ROUND(SUM(so.covered_amount), 2) AS covered_total
FROM secured_obligation so
JOIN credit_agreement a ON a.agreement_id = so.agreement_id
JOIN institution i ON i.institution_id = a.institution_id
JOIN security_agreement sa ON sa.security_id = so.security_id
WHERE sa.status = 'ACTIVE'
GROUP BY i.institution_id, i.institution_name
ORDER BY SUM(so.covered_amount) DESC, i.institution_name;"""),
    dict(
        id="BRB2-0405", difficulty="easy", features=[],
        penalty_law_zh="《商业银行押品管理指引》第十八条；《商业银行授信工作尽职指引》第二十九条",
        penalty_fact_zh="单笔授信由多份担保合同共同担保，权属与顺位管理复杂化",
        question="统计每笔授信协议被关联到多少份担保合同（通过被担保主债权桥接表统计），只保留被关联担保合同数不少于两笔的授信协议，输出协议编号、协议合同金额与被关联担保合同笔数，按被关联担保合同笔数降序排列，合同金额四舍五入到两位小数。",
        sql="""SELECT a.agreement_id, a.contract_amount, COUNT(so.security_id) AS sec_count
FROM credit_agreement a
JOIN secured_obligation so ON so.agreement_id = a.agreement_id
GROUP BY a.agreement_id, a.contract_amount
HAVING COUNT(so.security_id) >= 2
ORDER BY COUNT(so.security_id) DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0406", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》第二十一条；《中华人民共和国担保法》第四十一条",
        penalty_fact_zh="抵押物未与任何担保合同建立关联，押品管理悬空",
        question="列出从未关联到任何担保合同的悬空抵押物，即通过押品关联表无法关联到任何担保合同的抵押物，输出抵押物编号、抵押物名称与抵押物类型，按抵押物编号升序排列。",
        sql="""SELECT ca.collateral_id, ca.asset_label, ca.collateral_type
FROM collateral_asset ca
LEFT JOIN collateral_link cl ON cl.collateral_id = ca.collateral_id
WHERE cl.collateral_link_id IS NULL
ORDER BY ca.collateral_id;"""),
    dict(
        id="BRB2-0407", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》第四十四条；《商业银行贷款损失准备管理办法》相关条款",
        penalty_fact_zh="内外部评估价值显著背离，评估方法或价值时点不一致",
        question="对既存在内部评估又存在外部评估的抵质押物，取其内部评估记录中的最高评估价值与外部评估记录中的最低评估价值，计算外部最低评估价值减去内部最高评估价值的差额，输出抵质押物编号、抵质押物名称、内部最高评估价值、外部最低评估价值与差额（保留两位小数），按差额降序排列。",
        sql="""SELECT ca.collateral_id, ca.asset_label,
       MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END) AS internal_val,
       MIN(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END) AS external_val,
       ROUND(MIN(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END)
           - MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END), 2) AS diff
FROM collateral_asset ca
JOIN collateral_valuation cv ON cv.collateral_id = ca.collateral_id
WHERE cv.valuation_type IN ('INTERNAL', 'EXTERNAL')
GROUP BY ca.collateral_id, ca.asset_label
HAVING MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END) IS NOT NULL
   AND MIN(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END) IS NOT NULL
ORDER BY MIN(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END)
        - MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END) DESC, ca.collateral_id;"""),
    dict(
        id="BRB2-0408", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》第四十四条；《商业银行授信工作尽职指引》第二十二条",
        penalty_fact_zh="外部评估机构低估押品价值，影响押品覆盖率认定",
        question="对既存在内部评估又存在外部评估的抵押物，取其内部评估记录中的最高评估价值与外部评估记录中的最高评估价值，找出外部评估价值低于内部评估价值的抵押物，输出抵押物编号、抵押物名称、内部评估最高价值、外部评估最高价值与低估差额（内部减外部），只保留两类评估最高价值均存在的抵押物，按低估差额降序排列，金额四舍五入到两位小数。",
        sql="""SELECT ca.collateral_id, ca.asset_label,
       MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END) AS internal_val,
       MAX(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END) AS external_val,
       ROUND(MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END)
           - MAX(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END), 2) AS under_diff
FROM collateral_asset ca
JOIN collateral_valuation cv ON cv.collateral_id = ca.collateral_id
WHERE cv.valuation_type IN ('INTERNAL', 'EXTERNAL')
GROUP BY ca.collateral_id, ca.asset_label
HAVING MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END) IS NOT NULL
   AND MAX(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END) IS NOT NULL
   AND MAX(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END)
     < MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END)
ORDER BY MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END)
        - MAX(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END) DESC, ca.collateral_id;"""),
    dict(
        id="BRB2-0409", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》第三十五条；《商业银行实施统一授信制度指引》第二十条",
        penalty_fact_zh="不同类押品内外评估口径差异显著，价值认定标准不统一",
        question="按抵押物类型汇总内部评估与外部评估的平均价值，并计算外部平均价值与内部平均价值之比（外部除以内部，四舍五入到四位小数），只保留既有内部又有外部评估的抵押物类型，输出抵押物类型、内部评估平均价值、外部评估平均价值与内外价值比，按价值比降序排列，平均价值四舍五入到两位小数。",
        sql="""SELECT ca.collateral_type,
       ROUND(AVG(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END), 2) AS avg_int,
       ROUND(AVG(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END), 2) AS avg_ext,
       ROUND(AVG(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END)
           * 1.0 / AVG(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END), 4) AS ratio
FROM collateral_asset ca
JOIN collateral_valuation cv ON cv.collateral_id = ca.collateral_id
WHERE cv.valuation_type IN ('INTERNAL', 'EXTERNAL')
GROUP BY ca.collateral_type
HAVING AVG(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END) IS NOT NULL
   AND AVG(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END) IS NOT NULL
ORDER BY ratio DESC, ca.collateral_type;"""),
    dict(
        id="BRB2-0410", difficulty="easy", features=[],
        penalty_law_zh="《商业银行押品管理指引》第四十三条；《商业银行授信工作尽职指引》第六十一条",
        penalty_fact_zh="押品频繁重估，估值管理缺乏统一频率约束",
        question="对每件抵质押物统计其被评估的次数，并依据评估次数由高到低给出稠密名次，输出抵质押物编号、抵质押物名称、评估次数与名次，仅保留评估次数不少于 3 次的抵质押物，按评估次数降序、抵质押物编号升序排列。",
        sql="""WITH cnt AS (
    SELECT ca.collateral_id AS collateral_id, ca.asset_label AS label,
           COUNT(cv.valuation_id) AS val_count
    FROM collateral_asset ca
    JOIN collateral_valuation cv ON cv.collateral_id = ca.collateral_id
    GROUP BY ca.collateral_id, ca.asset_label
)
SELECT collateral_id, label, val_count,
       DENSE_RANK() OVER (ORDER BY val_count DESC) AS rank_by_freq
FROM cnt
WHERE val_count >= 3
ORDER BY val_count DESC, collateral_id;"""),
    dict(
        id="BRB2-0411", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》第十九条；《商业银行操作风险管理指引》相关条款",
        penalty_fact_zh="评估价值无法覆盖质押担保金额，担保缺口扩大",
        question="针对每一件抵质押物通取最近一次评估价，并与名下的累计质押担保金额作比对，识别存在担保覆盖缺口的抵质押物（即最新估价不足以覆盖累计质押额），输出抵质押物编号、资产名称、最新评估价、累计质押额与覆盖缺口（保留两位小数），按覆盖缺口降序排列（累计质押额只汇总状态为有效的质押关联，没有有效质押关联的抵质押物不输出）。",
        sql="""WITH pledged_tot AS (
    SELECT collateral_id AS collateral_id, ROUND(SUM(pledged_amount), 2) AS total_pledged,
           COUNT(*) AS links
    FROM collateral_link
    WHERE status = 'ACTIVE'
    GROUP BY collateral_id
)
SELECT ca.collateral_id AS collateral_id, ca.asset_label AS label,
       (SELECT cv.valuation_amount FROM collateral_valuation cv
         WHERE cv.collateral_id = ca.collateral_id
         ORDER BY cv.valued_on DESC, cv.valuation_id DESC LIMIT 1) AS latest_val,
       pt.total_pledged,
       ROUND(pt.total_pledged - (SELECT cv.valuation_amount FROM collateral_valuation cv
               WHERE cv.collateral_id = ca.collateral_id
               ORDER BY cv.valued_on DESC, cv.valuation_id DESC LIMIT 1), 2) AS gap
FROM collateral_asset ca
JOIN pledged_tot pt ON pt.collateral_id = ca.collateral_id
WHERE (SELECT cv.valuation_amount FROM collateral_valuation cv
         WHERE cv.collateral_id = ca.collateral_id
         ORDER BY cv.valued_on DESC, cv.valuation_id DESC LIMIT 1) < pt.total_pledged
ORDER BY gap DESC, ca.collateral_id;"""),
    dict(
        id="BRB2-0412", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》第四十一条；《银行业金融机构外部评估机构管理指引》相关条款",
        penalty_fact_zh="外部评估依赖度失衡，内部评估能力建设不足",
        question="按抵押物类型汇总外部评估记录笔数与外部评估价值合计，输出抵押物类型、外部评估笔数与外部评估价值合计，按外部评估价值合计降序排列，金额四舍五入到两位小数。",
        sql="""SELECT ca.collateral_type, COUNT(cv.valuation_id) AS ext_count,
       ROUND(SUM(cv.valuation_amount), 2) AS ext_total
FROM collateral_asset ca
JOIN collateral_valuation cv ON cv.collateral_id = ca.collateral_id
WHERE cv.valuation_type = 'EXTERNAL'
GROUP BY ca.collateral_type
ORDER BY SUM(cv.valuation_amount) DESC, ca.collateral_type;"""),
    dict(
        id="BRB2-0413", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国担保法》第六条、第十八条；《商业银行授信工作尽职指引》第三十五条",
        penalty_fact_zh="保证人担保能力未能与其对外保证总额相匹配",
        question="统计各担保人当前有效（状态为有效）的保证承诺金额合计，取名次靠前的十位担保人，输出担保人编号、担保人名称与保证承诺金额合计，按金额合计降序排列，金额四舍五入到两位小数。",
        sql="""SELECT gc.guarantor_party_id, p.display_name,
       ROUND(SUM(gc.guaranteed_amount), 2) AS total_guaranteed
FROM guarantor_commitment gc
JOIN party p ON p.party_id = gc.guarantor_party_id
WHERE gc.status = 'ACTIVE'
GROUP BY gc.guarantor_party_id, p.display_name
ORDER BY SUM(gc.guaranteed_amount) DESC, gc.guarantor_party_id
LIMIT 10;"""),
    dict(
        id="BRB2-0414", difficulty="hard", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第十一条；《中华人民共和国担保法》第十二条",
        penalty_fact_zh="保证人既借款又互保，对外保证总额超过自身还款能力",
        question="找出自身在本行有授信借款、同时对外提供担保的互保保证人，比较其对外有效保证承诺金额合计与自身借款合同金额合计，只保留对外保证金额合计大于自身借款金额合计的保证人，输出保证人编号、保证人名称、自身借款金额合计与对外保证金额合计，按对外保证金额合计降序排列，金额四舍五入到两位小数。",
        sql="""SELECT gmt.guarantor_party_id, p.display_name,
       ROUND((SELECT SUM(a.contract_amount) FROM credit_agreement a
              WHERE a.borrower_party_id = gmt.guarantor_party_id), 2) AS own_borrow,
       ROUND(SUM(gmt.guaranteed_amount), 2) AS total_guaranteed
FROM guarantor_commitment gmt
JOIN party p ON p.party_id = gmt.guarantor_party_id
WHERE gmt.status = 'ACTIVE'
  AND EXISTS (SELECT 1 FROM credit_agreement ca
              WHERE ca.borrower_party_id = gmt.guarantor_party_id)
GROUP BY gmt.guarantor_party_id, p.display_name
HAVING SUM(gmt.guaranteed_amount) > (SELECT SUM(a.contract_amount) FROM credit_agreement a
                                     WHERE a.borrower_party_id = gmt.guarantor_party_id)
ORDER BY SUM(gmt.guaranteed_amount) DESC, gmt.guarantor_party_id;"""),
    dict(
        id="BRB2-0415", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国担保法》第十二条；《商业银行授信工作尽职指引》第三十六条",
        penalty_fact_zh="保证承诺合计低于担保债权金额，保证覆盖不足",
        question="汇总每份担保合同下各保证人保证承诺金额合计，并与该担保合同的担保债权金额比较，找出保证承诺金额合计低于担保债权金额的担保合同，输出担保合同编号、担保债权金额、保证人数量与保证承诺金额合计，按保证承诺金额合计降序排列，金额四舍五入到两位小数（仅统计有效状态的保证承诺）。",
        sql="""SELECT sa.security_id, sa.secured_amount, COUNT(gc.commitment_id) AS guarantor_count,
       ROUND(SUM(gc.guaranteed_amount), 2) AS total_guaranteed
FROM security_agreement sa
JOIN guarantor_commitment gc ON gc.security_id = sa.security_id
WHERE gc.status = 'ACTIVE'
GROUP BY sa.security_id, sa.secured_amount
HAVING SUM(gc.guaranteed_amount) < sa.secured_amount
ORDER BY SUM(gc.guaranteed_amount) DESC, sa.security_id;"""),
    dict(
        id="BRB2-0416", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国担保法》第十四条；《商业银行授信工作尽职指引》第三十五条",
        penalty_fact_zh="保证承诺金额超过担保债权金额，保证责任设置不审慎",
        question="找出保证承诺金额高于其所在担保合同担保债权金额的过度保证情形，输出担保合同编号、担保债权金额、保证人编号与保证承诺金额，按保证承诺金额与担保债权金额的差额降序排列，金额四舍五入到两位小数。",
        sql="""SELECT gc.security_id, sa.secured_amount, gc.guarantor_party_id, gc.guaranteed_amount,
       ROUND(gc.guaranteed_amount - sa.secured_amount, 2) AS excess
FROM guarantor_commitment gc
JOIN security_agreement sa ON sa.security_id = gc.security_id
WHERE gc.status = 'ACTIVE'
  AND gc.guaranteed_amount > sa.secured_amount
ORDER BY gc.guaranteed_amount - sa.secured_amount DESC, gc.security_id;"""),
    dict(
        id="BRB2-0417", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国担保法》第二十五条；《商业银行授信工作尽职指引》第七十一条",
        penalty_fact_zh="保证期间届满或承诺失效后担保合同仍视为有效，风险敞口失真",
        question="统计属于公务人员且年收入不低于三十万元的个人客户，按客户分群汇总客户数量，输出客户分群与客户数量，按客户数量降序、客户分群升序排列。",
        sql="""SELECT p.customer_segment,
       COUNT(*) AS cnt
FROM person_profile pp
JOIN party p ON p.party_id = pp.party_id
WHERE pp.is_public_official = 1
  AND pp.annual_income >= 300000
GROUP BY p.customer_segment
ORDER BY cnt DESC, p.customer_segment;"""),
    dict(
        id="BRB2-0418", difficulty="easy", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第十三条；《商业银行实施统一授信制度指引》第十六条",
        penalty_fact_zh="集团敞口识别与分组类型登记不规范",
        question="列出所有敞口集团并关联敞口组类型码表，输出集团编号、集团名称、中文敞口组类型名称与集团成员数量，按集团成员数量降序排列，成员数量相同按集团编号升序排列。",
        sql="""SELECT eg.exposure_group_id, eg.group_name, egt.name_zh,
       COUNT(DISTINCT egm.party_id) AS member_count
FROM exposure_group eg
JOIN exposure_group_type_catalog egt ON egt.group_type = eg.group_type
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
GROUP BY eg.exposure_group_id, eg.group_name, egt.name_zh
ORDER BY COUNT(DISTINCT egm.party_id) DESC, eg.exposure_group_id;"""),
    dict(
        id="BRB2-0419", difficulty="easy", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第五条；《商业银行授权、授信管理暂行办法》第十七条",
        penalty_fact_zh="集团客户识别不足，统一授信范围受限",
        question="按敞口组类型码表汇总各中文敞口组类型下的集团个数与成员去重数量，输出中文敞口组类型名称、集团个数与成员去重数量，按成员去重数量降序排列。",
        sql="""SELECT egt.name_zh,
       COUNT(DISTINCT eg.exposure_group_id) AS group_count,
       COUNT(DISTINCT egm.party_id) AS member_count
FROM exposure_group eg
JOIN exposure_group_type_catalog egt ON egt.group_type = eg.group_type
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
GROUP BY egt.name_zh
ORDER BY COUNT(DISTINCT egm.party_id) DESC, egt.name_zh;"""),
    dict(
        id="BRB2-0420", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第十四条；《商业银行并表管理与监管指引》第二十八条",
        penalty_fact_zh="集团成员与机构权属对应关系混乱，并表管理不严",
        question="按机构及敞口组类型码表的中文敞口组类型名称统计集团成员去重数量，只保留成员去重数量不少于六名的机构类型组合，输出机构名称、中文敞口组类型名称与成员去重数量，按成员去重数量降序排列。",
        sql="""SELECT i.institution_name, egt.name_zh, COUNT(DISTINCT egm.party_id) AS member_count
FROM exposure_group eg
JOIN exposure_group_type_catalog egt ON egt.group_type = eg.group_type
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
JOIN institution i ON i.institution_id = eg.institution_id
GROUP BY i.institution_name, egt.name_zh
HAVING COUNT(DISTINCT egm.party_id) >= 6
ORDER BY COUNT(DISTINCT egm.party_id) DESC, i.institution_name;"""),
    dict(
        id="BRB2-0421", difficulty="hard", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第三条、第十六条",
        penalty_fact_zh="集团客户授信集中度占比失真，超越法定大额风险暴露比例",
        question="按集团敞口组类型中文名称与主办机构汇总集团成员在本行的贷款本金余额合计，并与该主办机构的资本净额比较计算敞口占资本净额比例，输出机构名称、敞口组类型中文名称、成员贷款余额合计、机构资本净额与敞口占比（金额保留两位小数、占比保留六位小数），按敞口占比降序排列。",
        sql="""WITH grp_bal AS (
    SELECT eg.institution_id, egt.name_zh,
           SUM(lbs.principal_balance) AS bal_total
    FROM exposure_group eg
    JOIN exposure_group_type_catalog egt ON egt.group_type = eg.group_type
    JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
    JOIN credit_agreement a ON a.borrower_party_id = egm.party_id AND a.institution_id = eg.institution_id
    JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
    JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
    GROUP BY eg.institution_id, egt.name_zh
)
SELECT i.institution_name, gb.name_zh,
       ROUND(gb.bal_total, 2) AS bal_total,
       ROUND(cs.net_capital, 2) AS net_capital,
       ROUND(gb.bal_total * 1.0 / cs.net_capital, 6) AS ratio
FROM grp_bal gb
JOIN institution i ON i.institution_id = gb.institution_id
JOIN capital_snapshot cs ON cs.institution_id = gb.institution_id
ORDER BY ratio DESC, i.institution_name, gb.name_zh;"""),
    dict(
        id="BRB2-0422", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第九条；《商业银行与内部人和股东关联交易管理办法》第二十五条",
        penalty_fact_zh="成员客户交叉归属多个集团，关联关系穿透识别不到位",
        question="找出同时属于两个及以上不同敞口集团的成员客户，输出成员客户编号、客户名称与所属集团数量，按所属集团数量降序排列，数量相同按成员客户编号升序排列。",
        sql="""SELECT egm.party_id, p.display_name, COUNT(DISTINCT egm.exposure_group_id) AS group_count
FROM exposure_group_member egm
JOIN party p ON p.party_id = egm.party_id
GROUP BY egm.party_id, p.display_name
HAVING COUNT(DISTINCT egm.exposure_group_id) >= 2
ORDER BY COUNT(DISTINCT egm.exposure_group_id) DESC, egm.party_id;"""),
    dict(
        id="BRB2-0423", difficulty="easy", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》第八条；《商业银行公司治理指引》第八十五条",
        penalty_fact_zh="关联关系类型登记不完整，关联方识别口径不统一",
        question="按关联关系类型码表统计各中文关系名称下的关联关系记录条数，输出中文关系名称与记录条数，按记录条数降序排列，条数相同的按中文关系名称升序排列。",
        sql="""SELECT rc.relation_name_zh, COUNT(pr.relation_id) AS rel_count
FROM party_relation pr
JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
GROUP BY rc.relation_name_zh
ORDER BY COUNT(pr.relation_id) DESC, rc.relation_name_zh;"""),
    dict(
        id="BRB2-0424", difficulty="hard", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》第二十二条；《商业银行授信工作尽职指引》第三十条",
        penalty_fact_zh="关联方自我交易未经识别，关联授信集中风险被忽视",
        question="找出存在关联关系（排除非关联方）且自身又是本行借款客户的主体，统计其作为关系一方的关联关系条数与其借款合同笔数，输出主体编号、主体名称、关联关系条数与借款合同笔数，按关联关系条数降序排列。",
        sql="""SELECT p.party_id, p.display_name, rel.rel_count, ag.agreement_count
FROM party p
JOIN (SELECT source_party_id AS pid, COUNT(*) AS rel_count
      FROM party_relation JOIN relation_type_catalog rc ON rc.relation_type = party_relation.relation_type
      WHERE rc.relation_name_zh <> '非关联方'
      GROUP BY source_party_id) rel ON rel.pid = p.party_id
JOIN (SELECT borrower_party_id AS pid, COUNT(*) AS agreement_count
      FROM credit_agreement GROUP BY borrower_party_id) ag ON ag.pid = p.party_id
ORDER BY rel.rel_count DESC, p.party_id;"""),
    dict(
        id="BRB2-0425", difficulty="hard", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》第十七条；《商业银行股权管理暂行办法》第四十四条",
        penalty_fact_zh="影子股东通过集团成员隐匿关联身份，规避持股监管",
        question="找出属于影子股东关联关系的一方当事人且同时是敞口集团成员的客户，输出客户编号、客户名称与所属集团数量，按所属集团数量降序排列，数量相同按客户编号升序排列。",
        sql="""SELECT p.party_id, p.display_name, COUNT(DISTINCT egm.exposure_group_id) AS group_count
FROM party_relation pr
JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
JOIN party p ON p.party_id = pr.source_party_id
JOIN exposure_group_member egm ON egm.party_id = p.party_id
WHERE rc.relation_name_zh = '影子股东'
GROUP BY p.party_id, p.display_name
ORDER BY COUNT(DISTINCT egm.exposure_group_id) DESC, p.party_id;"""),
    dict(
        id="BRB2-0426", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第十二条；《商业银行内部人和股东关联交易管理办法》第三十四条",
        penalty_fact_zh="实际控制人控制多家企业形成隐性集团，风险控制失效",
        question="列出实际控制人关联关系中作为控制一方的各主体及其关联另一方的去重数量，输出主体编号、主体名称与关联另一方去重数量，按关联另一方去重数量降序排列，数量相同按主体编号升序排列。",
        sql="""SELECT pr.source_party_id, p.display_name,
       COUNT(DISTINCT pr.target_party_id) AS target_count
FROM party_relation pr
JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
JOIN party p ON p.party_id = pr.source_party_id
WHERE rc.relation_name_zh = '实际控制人'
GROUP BY pr.source_party_id, p.display_name
ORDER BY COUNT(DISTINCT pr.target_party_id) DESC, pr.source_party_id;"""),
    dict(
        id="BRB2-0427", difficulty="medium", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》第十九条；《商业银行集团客户授信业务风险管理指引》第十条",
        penalty_fact_zh="关联双方同时获得授信形成集团套取信贷，关联授信未合并计算",
        question="找出关联交易关系双方（排除非关联方）均在本行有借款合同的情形，输出关系编号、关系一方主体编号、关系另一方主体编号、一主体现有借款合同数与另一主体现有借款合同数，按两边借款合同数之和降序排列。",
        sql="""SELECT pr.relation_id, pr.source_party_id, pr.target_party_id,
       CASE WHEN sb.agreement_count IS NULL THEN 0 ELSE sb.agreement_count END AS src_agr,
       CASE WHEN tb.agreement_count IS NULL THEN 0 ELSE tb.agreement_count END AS tgt_agr
FROM party_relation pr
JOIN relation_type_catalog rc ON rc.relation_type = pr.relation_type
LEFT JOIN (SELECT borrower_party_id AS pid, COUNT(*) AS agreement_count
           FROM credit_agreement GROUP BY borrower_party_id) sb ON sb.pid = pr.source_party_id
LEFT JOIN (SELECT borrower_party_id AS pid, COUNT(*) AS agreement_count
           FROM credit_agreement GROUP BY borrower_party_id) tb ON tb.pid = pr.target_party_id
WHERE rc.relation_name_zh <> '非关联方'
  AND sb.agreement_count IS NOT NULL AND tb.agreement_count IS NOT NULL
ORDER BY COALESCE(sb.agreement_count, 0) + COALESCE(tb.agreement_count, 0) DESC, pr.relation_id;"""),
    dict(
        id="BRB2-0428", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》（银监发〔2017〕16号）第二十五条：担保期限应与主债权期限相匹配，对担保届满先于授信到期的，应重新评估并补充担保，防范授信存续期发生担保虚空而监管不到位。",
        penalty_fact_zh="已按授信合同量化最早担保届满日早于授信到期日的天数，脱保天数越长的债权其在授信期内长期无有效担保。",
        question="监管核查要求穿透测算授信的“脱保悬空天数”：对同一授信合同的所有担保，取其担保有效期届满日最早的担保，比较其该担保届满日与授信到期日之间间隔天数，识别担保先于授信到期而失效的合同。输出授信合同编号、债务人编号、授信到期日、最早担保届满日与脱保天数，按授信到期日由早到晚排列，到期日相同再按授信合同编号从小到大排列。",
        sql="""with earliest as (
  select a.agreement_id, min(sa.effective_to) as earliest_expiry
  from credit_agreement a
  join secured_obligation so on so.agreement_id = a.agreement_id
  join security_agreement sa on sa.security_id = so.security_id
  group by a.agreement_id
)
select e.agreement_id, a.borrower_party_id, a.maturity_on, e.earliest_expiry,
  round(julianday(a.maturity_on) - julianday(e.earliest_expiry), 0) as 脱保天数
from earliest e
join credit_agreement a on a.agreement_id = e.agreement_id
where e.earliest_expiry < a.maturity_on
order by a.maturity_on asc, e.agreement_id"""),
    dict(
        id="BRB2-0429", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》第二十七条、第二十八条：银行应根据独立、审慎原则对押品开展评估，内外部评估差异若反映内部评估虚高，将导致抵押价值与担保额度虚增，监管要求重估并核减。",
        penalty_fact_zh="已识别外部评估价值低于内部评估价值的押品，内部评估存在乐观偏差，按内部评估核定的担保额度可能高估押品缓释能力。",
        question="监管核查要求识别“外部评估明显低于内部评估”的押品：同一押品经内外部两种口径评估且外部评估价值低于内部评估价值的，反映内部评估偏乐观、抵押价值可能虚高。输出押品编号、押品标识、外部评估价值、内部评估价值与外部评估占内部评估的百分比，按外部占比由低到高排列，占比相同再按押品编号从小到大排列。",
        sql="""select ca.collateral_id, ca.asset_label,
  max(case when cv.valuation_type = 'EXTERNAL' then cv.valuation_amount end) as 外部评估,
  max(case when cv.valuation_type = 'INTERNAL' then cv.valuation_amount end) as 内部评估,
  round(max(case when cv.valuation_type = 'EXTERNAL' then cv.valuation_amount end) * 100.0 /
    max(case when cv.valuation_type = 'INTERNAL' then cv.valuation_amount end), 2) as 外部占比
from collateral_asset ca
join collateral_valuation cv on cv.collateral_id = ca.collateral_id
where cv.valuation_type in ('EXTERNAL','INTERNAL')
group by ca.collateral_id, ca.asset_label
having max(case when cv.valuation_type = 'EXTERNAL' then cv.valuation_amount end) <
       max(case when cv.valuation_type = 'INTERNAL' then cv.valuation_amount end)
order by 外部占比 asc, ca.collateral_id"""),
    dict(
        id="BRB2-0430", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》及贷款“担保落实”审查要求：押品应在授信发放前后完成评估、登记与担保设立；押品状态有效却无有效担保关联，属于担保未落实、押品空转，监管将责令限时完善抵押手续。",
        penalty_fact_zh="已识别状态有效、但未实际用于任何有效担保关联的押品资产，存在押品登记滞后或未办理抵押手续的担保落实缺口。",
        question="监管核查要求识别“已入账但未实际落实抵押”的押品：状态为有效的押品资产，却不存在任何一条处于有效状态的押品担保关联记录，反映抵押登记或担保设立尚未真正落实。输出押品编号、押品标识与押品类型，按押品编号从小到大排列。",
        sql="""select ca.collateral_id, ca.asset_label, ca.collateral_type
from collateral_asset ca
where ca.status = 'ACTIVE'
  and not exists (
    select 1 from collateral_link cl
    where cl.collateral_id = ca.collateral_id and cl.status = 'ACTIVE'
  )
order by ca.collateral_id"""),
    dict(
        id="BRB2-0431", difficulty="hard", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》及《流动资金贷款管理办法》关于担保人资信审查：保证人担保责任应与其偿债能力相匹配，小额资本金的担保人承担远超其自身贷款敞口的或有负债，属过度担保，监管将要求核减并强化代偿能力评估。",
        penalty_fact_zh="已识别对外保证责任合计超过自身贷款敞口的担保人，其或有负债远超自有资本消化能力，代偿风险高度集中。",
        question="识别担保责任超出自身偿债能力的担保人：统计其名下仍处于有效状态的保证承诺金额合计，与本人在本行的贷款敞口进行比较，仅保留对外有效保证金额超过自身贷款敞口的保证人，输出保证人编号、保证人名称、有效保证责任合计、自身贷款金额与超额担保金额（保留两位小数），按超额担保金额降序排列（自身贷款敞口取其作为借款人名下借据的当前本金余额合计）。",
        sql="""WITH own AS (
    SELECT a.borrower_party_id AS party_id, ROUND(SUM(lbs.principal_balance), 2) AS own_loan
    FROM credit_agreement a
    JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
    JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
    GROUP BY a.borrower_party_id
)
SELECT gc.guarantor_party_id AS party_id, p.display_name,
       ROUND(SUM(gc.guaranteed_amount), 2) AS guaranteed_total,
       COALESCE(o.own_loan, 0) AS own_loan_bal,
       ROUND(SUM(gc.guaranteed_amount) - COALESCE(o.own_loan, 0), 2) AS excess
FROM guarantor_commitment gc
JOIN party p ON p.party_id = gc.guarantor_party_id
LEFT JOIN own o ON o.party_id = gc.guarantor_party_id
WHERE gc.status = 'ACTIVE'
GROUP BY gc.guarantor_party_id, p.display_name, o.own_loan
HAVING SUM(gc.guaranteed_amount) > COALESCE(o.own_loan, 0)
ORDER BY excess DESC, gc.guarantor_party_id;"""),
    dict(
        id="BRB2-0432", difficulty="medium", features=[],
        penalty_law_zh="《商业银行信用卡业务监督管理办法》（银监发〔2011〕2号）第四十四条、第五十一条：发卡银行应对持卡人信用风险持续监测，持卡人贷款或信用卡发生重大违约的应实施止付、销户等管控；我行贷款逾期超90天仍保留有效贷记卡的，属风险管控不力。",
        penalty_fact_zh="已识别贷款逾期超90天的借款人名下仍处于有效状态的贷记卡，截至其卡片到期日均未联动止付，多笔风险敞口持续并存。",
        question="监管核查要求识别“分期兜底型长期风险”：贷款已发生本金逾期超90天的借款人，名下仍持有生效中的贷记卡，反映信用卡长期未联动止付。输出持卡人编号、持卡人名称、贷记卡卡号与卡片到期日，按卡片到期日由早到晚排列，到期日相同再按卡号从小到大排列。",
        sql="""select pc.holder_party_id, p.display_name, pc.card_id, pc.expires_on
from payment_card pc
join party p on p.party_id = pc.holder_party_id
where pc.card_type = 'CREDIT' and pc.status = 'ACTIVE'
  and exists (
    select 1 from credit_agreement a
    join loan_drawdown ld on ld.agreement_id = a.agreement_id
    join delinquency_snapshot d on d.loan_id = ld.loan_id
    where a.borrower_party_id = pc.holder_party_id and d.principal_overdue_days > 90
  )
order by pc.expires_on asc, pc.card_id"""),
    dict(
        id="BRB2-0433", difficulty="medium", features=[],
        penalty_law_zh="《商业银行法》第三十五条及《流动资金贷款管理办法》关于贷款用途真实性的规定：严禁以贷还贷、以贷吸存，严禁贷款资金回流后用于归还本行贷款；资金闭环空转将导致贷款实际未形成真实生产经营用途，监管将按挪用贷款处理。",
        penalty_fact_zh="已识别来自贷款发放账户的还款交易，反映贷款资金发放后回流用于偿还本行贷款，存在借新还旧、资金空转的以贷还贷特征。",
        question="监管核查要求穿透识别“贷款资金回流/以贷还贷”：账户在贷款发放后又被用于向本行偿还贷款本金，若同一账户既接收贷款发放又发生还款资金划转，存在资金循环空转。输出交易流水号、付款账户、收款账户、交易金额与业务日期，按交易金额由大到小排列，金额相同再按交易流水号从小到大排列，取金额最大的前100条。",
        sql="""select pe.payment_id, pe.from_account_id, pe.to_account_id, pe.amount, pe.business_date
from payment_event pe
where pe.payment_type = 'LOAN_REPAYMENT'
  and pe.from_account_id in (
    select ld.disbursement_account_id
    from loan_drawdown ld
  )
order by pe.amount desc, pe.payment_id
limit 100"""),
    dict(
        id="BRB2-0434", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》及担保人资信审查要求：对已发生贷款逾期的借款主体，应审慎评估其对外担保的连带责任风险，防止其或有负债与经营风险交叉传染，必要时不得再接受其增信。",
        penalty_fact_zh="已识别贷款逾期借款人仍对外承担保证责任的记录，其资信恶化下或有负债持续累积，风险交叉传染渠道未予切断。",
        question="排查贷款已发生本金逾期、同时仍对外提供有效保证的借款人：通过担保承诺记录关联，找出存在逾期借据的保证人，输出保证人编号、保证人名称、保证金额与保证状态，按保证金额降序、保证人编号升序排列（逾期指保证人自己作为借款人名下的借据存在本金逾期）。",
        sql="""SELECT gc.guarantor_party_id AS party_id, p.display_name,
       gc.guaranteed_amount AS guaranteed_amount,
       gc.status AS guarantor_status
FROM guarantor_commitment gc
JOIN party p ON p.party_id = gc.guarantor_party_id
WHERE gc.status = 'ACTIVE'
  AND EXISTS (
    SELECT 1
    FROM credit_agreement a
    JOIN loan_drawdown ld ON ld.agreement_id = a.agreement_id
    JOIN delinquency_snapshot d ON d.loan_id = ld.loan_id AND d.principal_overdue_days > 0
    WHERE a.borrower_party_id = gc.guarantor_party_id
  )
ORDER BY gc.guaranteed_amount DESC, gc.guarantor_party_id;"""),
    dict(
        id="BRB2-0435", difficulty="medium", features=[],
        penalty_law_zh="《商业银行预期信用损失法实施管理办法》：第三阶段即已发生信用减值资产必须足额计提损失准备，三阶段拨备缺口按不良级别汇总后如长期存在，监管将责令补提并视其影响资本充足与利润真实性。",
        penalty_fact_zh="已按五级分类级别汇总损失阶段拨备计提缺口，反映各不良级别的减值准备覆盖不均，个别级别的缺额集中。",
        question="监管核查要求按五级分类级别汇总损失阶段（三阶段）准备计提存在缺口的借据，识别各不良级别的拨备不足集中度。输出五级分类名称、存在缺口的借据笔数与缺口金额合计，按缺口金额合计由大到小排列，金额相同再按五级分类名称从小到大排列。",
        sql="""with su as (
  select ps.loan_id, ps.recognized_amount, ps.required_amount
  from provision_snapshot ps
  where ps.provision_stage = 'STAGE_3' and ps.required_amount > ps.recognized_amount
)
select g.grade_name_zh, count(*) as 缺口借据数,
  round(sum(su.required_amount - su.recognized_amount), 2) as 缺口合计
from su
join risk_classification rc on rc.loan_id = su.loan_id
join classification_grade g on g.grade_code = rc.grade_code
group by g.grade_name_zh
order by 缺口合计 desc, g.grade_name_zh"""),
    dict(
        id="BRB2-0436", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》及不良资产处置监管要求：分支机构应对逾期客户集中度与继续新增敞口进行控制，对已逾期的借款人不得放任授信积聚；监管将按机构问责风险管控不力的前台部门。",
        penalty_fact_zh="已按分支机构量化对逾期借款人的敞口余额与户数，个别机构逾期敞口高度集中，反映其贷后催收与新增授信管控薄弱。",
        question="从授信合同管理营业单元维度统计已发生逾期借据的风险敞口：关联逾期快照、放款借据、授信合同与贷款余额快照，按授信合同管理营业单元汇总存在逾期记录的借款人去重户数及这些逾期借据的本金余额合计（保留两位小数），输出营业单元编号、营业单元名称、逾期借款人户数与逾期借据本金余额合计，按逾期借据本金余额合计降序、营业单元编号升序排列。",
        sql="""SELECT o.org_unit_id, o.unit_name,
       COUNT(DISTINCT a.borrower_party_id) AS 逾期借款人户数,
       ROUND(SUM(lbs.principal_balance), 2) AS 逾期借据本金余额合计
FROM delinquency_snapshot d
JOIN loan_drawdown ld ON ld.loan_id = d.loan_id
JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
JOIN loan_balance_snapshot lbs ON lbs.loan_id = ld.loan_id
JOIN organization_unit o ON o.org_unit_id = a.managing_org_unit_id
GROUP BY o.org_unit_id, o.unit_name
ORDER BY 逾期借据本金余额合计 DESC, o.org_unit_id;"""),
    dict(
        id="BRB2-0437", difficulty="hard", features=[],
        penalty_law_zh="《不良金融资产处置尽职指引》（银监发〔2010〕96号）及《商业银行贷款损失准备计提指引》：贷款本金核算应真实反映逾期与余额关系，逾期本金异常大于当前余额反映账务冲减、核销或余额调整不合规，监管将责令核实账务。",
        penalty_fact_zh="已识别逾期本金大于当前贷款余额的借据，逾期与余额的核算关系异常，背后存在账务冲销或本息重组不规范的情况。",
        question="监管核查要求识别“逾期本金核算异常”的借据：借据当前本金余额大于零，而其累计逾期本金超过当前本金余额，即负债已被动性交叉核销或逾期金额与余额失当。输出借据编号、本金逾期天数、逾期本金、当前本金余额与逾期本金占当前余额的比例，按该比例由大到小排列，比例相同再按借据编号从小到大排列。",
        sql="""select d.loan_id, d.principal_overdue_days,
  round(d.overdue_principal, 2) as 逾期本金,
  round(lbs.principal_balance, 2) as 本金余额,
  round(d.overdue_principal / lbs.principal_balance, 2) as 逾期占比
from delinquency_snapshot d
join loan_balance_snapshot lbs on lbs.loan_id = d.loan_id
where lbs.principal_balance > 0
  and d.overdue_principal > lbs.principal_balance
order by 逾期占比 desc, d.loan_id"""),
    dict(
        id="BRB2-0438", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》及《不良金融资产处置尽职指引》：银行应对担保合同与所担保授信的覆盖关系持续校验，担保合同标的金额过大而实际覆盖授信不足或空置的，属于担保资源配置低效，监管将要求优化担保结构。",
        penalty_fact_zh="已按机构测算担保合同金额与其实际覆盖授信的利用率，部分机构担保合同未充分对应有效授信，担保资源空转。",
        question="测算各机构有效担保合同对被担保主债权实现的平均覆盖利用率：汇总担保合同担保金额与经桥接表关联的覆盖授信金额，输出机构名称、担保合同金额、覆盖授信合计与覆盖率百分比，按覆盖利用率升序排列。",
        sql="""WITH sec AS (
    SELECT institution_id AS institution_id, ROUND(SUM(secured_amount), 2) AS secured_total,
           COUNT(DISTINCT security_id) AS n_agreements
    FROM security_agreement
    WHERE status = 'ACTIVE'
    GROUP BY institution_id
),
cov AS (
    SELECT sa.institution_id AS institution_id, ROUND(SUM(so.covered_amount), 2) AS covered_total
    FROM secured_obligation so
    JOIN security_agreement sa ON sa.security_id = so.security_id
    GROUP BY sa.institution_id
)
SELECT i.institution_name, sc.secured_total, cv.covered_total,
       ROUND(cv.covered_total * 100.0 / sc.secured_total, 2) AS utilization_pct
FROM sec sc
JOIN cov cv ON cv.institution_id = sc.institution_id
JOIN institution i ON i.institution_id = sc.institution_id
ORDER BY utilization_pct, i.institution_name;"""),
    dict(
        id="BRB2-0439", difficulty="hard", features=[],
        penalty_law_zh="《商业银行预期信用损失法实施管理办法》及不良资产拨备监管要求：各经营单位对不良资产的损失准备覆盖应充分、均衡；分支机构拨备覆盖率显著低下的，反映其在不良认定与减值计提上不审慎，监管将责令足额补提。",
        penalty_fact_zh="已按分支机构测算不良借据的拨备覆盖率，低覆盖率的机构对不良资产的损失准备明显不足，需补提并核实其不良认定口径。",
        question="监管核查要求从分支机构维度测算其对不良借据的损失准备拨备覆盖率：各分支机构的次级、可疑、损失类不良借据中，已计提损失准备合计占应计提合计的比例，识别拨备覆盖不足的分支机构。输出分支机构（营业机构单元）编号、名称、不良借据笔数与拨备覆盖率，按拨备覆盖率由低到高排列，覆盖率相同再按营业机构名称从小到大排列。",
        sql="""with cov as (
  select rc.loan_id, g.is_nonperforming
  from risk_classification rc
  join classification_grade g on g.grade_code = rc.grade_code
)
select o.org_unit_id, o.unit_name,
  count(*) as 不良借据数,
  round(sum(ps.recognized_amount) / nullif(sum(ps.required_amount), 0), 4) as 拨备覆盖率
from cov
join loan_drawdown ld on ld.loan_id = cov.loan_id
join credit_agreement a on a.agreement_id = ld.agreement_id
join organization_unit o on o.org_unit_id = a.managing_org_unit_id
join provision_snapshot ps on ps.loan_id = cov.loan_id
where cov.is_nonperforming = 1
group by o.org_unit_id, o.unit_name
order by 拨备覆盖率 asc, o.unit_name"""),
    dict(
        id="BRB2-0440", difficulty="easy", features=[],
        penalty_law_zh="《商业银行理财业务监督管理办法》及《关于规范金融机构资产管理业务的指导意见》（资管新规）关于严禁理财资金违规投向本行表内信贷客户、严禁为表内不良资产输送资金的展业要求。",
        penalty_fact_zh="经穿透识别，多只理财产品通过嵌套结构持有的底层资产最终债务人与本行存在本金逾期借据的借款人高度重合，涉嫌以理财资金变相承接本行逾期信贷客户资产、规避表内风险管控。",
        question="请找出理财产品通过多层嵌套最终持有的底层资产，其最终债务人同时又是理财产品发行机构本行存在逾期借据的对公借款人（即以理财资金变相承接本行逾期信贷客户资产），输出产品名称、底层资产名称、最终债务人编号、该债务人在本行的逾期本金合计，按产品名称升序、逾期本金合计降序排列。",
        sql="""WITH dlq AS (SELECT ca.borrower_party_id AS party, ca.institution_id AS inst, SUM(d.overdue_principal) AS overdue FROM delinquency_snapshot d JOIN loan_drawdown ld ON ld.loan_id=d.loan_id JOIN credit_agreement ca ON ca.agreement_id=ld.agreement_id GROUP BY ca.borrower_party_id, ca.institution_id)
SELECT wp.product_name, ma.asset_name, ma.obligor_party_id, ROUND(dlq.overdue,2) AS sum_overdue
FROM product_holding_snapshot ph
JOIN wealth_product wp ON wp.product_id=ph.product_id
JOIN managed_asset ma ON ma.asset_id=ph.asset_id
JOIN dlq ON dlq.party=ma.obligor_party_id AND dlq.overdue>0 AND dlq.inst=wp.issuer_institution_id
JOIN party pc ON pc.party_id=ma.obligor_party_id AND pc.party_type='CORPORATE'
WHERE ph.lookthrough_depth>=2
ORDER BY wp.product_name, sum_overdue DESC;"""),
    dict(
        id="BRB2-0441", difficulty="hard", features=[],
        penalty_law_zh="《商业银行法》及监管机构关于信贷与理财资金投向限制类、退出类行业（两高一剩、淘汰落后产能）的调控监管要求。",
        penalty_fact_zh="部分理财产品底层资产最终债务人所属行业属于监管限制类行业，理财资金穿透后又回流至限制行业借款人，涉嫌规避信贷投向限制。",
        question="对属于负债类别的受托管理资产按内部评级汇总资产数量，仅保留数量介于二十五至三十之间的评级，输出内部评级与资产数量，按资产数量降序、内部评级升序排列。",
        sql="""SELECT ma.internal_rating,
       COUNT(*) AS cnt
FROM managed_asset ma
WHERE ma.is_liability = 1
GROUP BY ma.internal_rating
HAVING COUNT(*) BETWEEN 25 AND 30
ORDER BY cnt DESC, ma.internal_rating;"""),
    dict(
        id="BRB2-0442", difficulty="easy", features=[],
        penalty_law_zh="资管新规及《商业银行理财业务监督管理办法》关于非标准化债权类资产不得采取摊余成本法计量、估值方法应与资产信用风险相匹配的规定。",
        penalty_fact_zh="存在多笔非标准化债权底层资产采用摊余成本法估值且内部评级低于外部评级，估值方法选择与资产信用状况不匹配，涉嫌低估风险、虚增理财净值。",
        question="找出采用摊余成本法估值的非标准化债权类底层资管资产中，外部评级为未评级或内部评级与外部评级不一致的记录，按自定义评级风险分值（AAA=1、AA+=2、AA=3、A+=4、A=5、BBB=6、未评级=7）筛选出外部评级风险分值高于内部评级风险分值（即外部评级比内部评级更差或无外部评级）的资产，输出资产编号、资产名称、内部评级与外部评级，按资产编号升序排列。",
        sql="""WITH rated AS (
  SELECT ma.asset_id, ma.asset_name, ma.internal_rating, ma.external_rating,
         CASE ma.internal_rating WHEN 'AAA' THEN 1 WHEN 'AA+' THEN 2 WHEN 'AA' THEN 3 WHEN 'A+' THEN 4 WHEN 'A' THEN 5 WHEN 'BBB' THEN 6 ELSE 7 END AS in_score,
         CASE ma.external_rating WHEN 'AAA' THEN 1 WHEN 'AA+' THEN 2 WHEN 'AA' THEN 3 WHEN 'A+' THEN 4 WHEN 'A' THEN 5 WHEN 'BBB' THEN 6 ELSE 7 END AS ex_score
  FROM managed_asset ma
  WHERE ma.asset_scope = 'NON_STANDARDIZED' AND ma.valuation_method = 'AMORTIZED_COST'
)
SELECT asset_id, asset_name, internal_rating, external_rating
FROM rated
WHERE ex_score > in_score
ORDER BY asset_id;"""),
    dict(
        id="BRB2-0443", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》第二十四条；《商业银行授信工作尽职指引》第五十五条",
        penalty_fact_zh="不同担保方式担保覆盖结构失衡，增信工具组合不审慎",
        question="按担保方式汇总经被担保主债权桥接表关联到有效授信协议的担保合同笔数与被担保金额合计，输出担保方式与担保合同笔数、被担保金额合计，按被担保金额合计降序排列，金额四舍五入到两位小数。",
        sql="""SELECT sa.security_type, COUNT(DISTINCT sa.security_id) AS sec_count,
       ROUND(SUM(so.covered_amount), 2) AS covered_total
FROM secured_obligation so
JOIN security_agreement sa ON sa.security_id = so.security_id
JOIN credit_agreement a ON a.agreement_id = so.agreement_id
WHERE a.status = 'ACTIVE'
GROUP BY sa.security_type
ORDER BY SUM(so.covered_amount) DESC, sa.security_type;"""),
    dict(
        id="BRB2-0444", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》第三十条；《商业银行授信工作尽职指引》第三十三条",
        penalty_fact_zh="押品过度估价形成担保虚增，缓释计量失真",
        question="围绕押品价值是否被充分运用展开核查：按抵质押物归集最新评估价及其名下被质押担保金额之和，筛选出最新评估价达到被质押累计金额二倍之上的抵质押物，输出抵质押物编号、资产名称、最新评估价、被质押金额合计与剩余价值空间（最新评估价减去被质押合计，保留两位小数），按剩余价值空间降序排列。",
        sql="""WITH latest AS (
    SELECT collateral_id AS collateral_id, valuation_amount AS valuation_amount,
           ROW_NUMBER() OVER (PARTITION BY collateral_id ORDER BY valued_on DESC, valuation_id DESC) AS rn
    FROM collateral_valuation
),
pledged_tot AS (
    SELECT collateral_id AS collateral_id, ROUND(SUM(pledged_amount), 2) AS total_pledged
    FROM collateral_link
    WHERE status = 'ACTIVE'
    GROUP BY collateral_id
)
SELECT ca.collateral_id AS collateral_id, ca.asset_label AS label,
       lv.valuation_amount AS latest_val, pt.total_pledged AS total_pledged,
       ROUND(lv.valuation_amount - pt.total_pledged, 2) AS excess
FROM collateral_asset ca
JOIN latest lv ON lv.collateral_id = ca.collateral_id AND lv.rn = 1
JOIN pledged_tot pt ON pt.collateral_id = ca.collateral_id
WHERE lv.valuation_amount > pt.total_pledged * 2
ORDER BY excess DESC, ca.collateral_id;"""),
    dict(
        id="BRB2-0445", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国担保法》第二十八条；《商业银行授信工作尽职指引》第三十八条",
        penalty_fact_zh="抵押与保证并用增加保证担保但未明晰清偿次序",
        question="找出同时以抵押物担保并取得第三方保证承诺的授信协议（经被担保主债权桥接表关联），输出协议编号、借款人名称、合同金额、关联抵押物笔数与保证人笔数，按合同金额降序排列，金额四舍五入到两位小数（仅统计有效状态的担保协议）。",
        sql="""SELECT a.agreement_id, p.display_name, a.contract_amount,
       COUNT(DISTINCT cl.collateral_id) AS collateral_count,
       COUNT(DISTINCT gc.guarantor_party_id) AS guarantor_count
FROM credit_agreement a
JOIN party p ON p.party_id = a.borrower_party_id
JOIN secured_obligation so ON so.agreement_id = a.agreement_id
JOIN security_agreement sa ON sa.security_id = so.security_id
JOIN collateral_link cl ON cl.security_id = sa.security_id
JOIN guarantor_commitment gc ON gc.security_id = sa.security_id
WHERE sa.status = 'ACTIVE'
GROUP BY a.agreement_id, p.display_name, a.contract_amount
ORDER BY a.contract_amount DESC, a.agreement_id;"""),
    dict(
        id="BRB2-0446", difficulty="medium", features=[],
        penalty_law_zh="《商业银行集团客户授信业务风险管理指引》第十四条；《商业银行内部人和股东关联交易管理办法》第三十二条",
        penalty_fact_zh="关联客户群授信集中度高企，并表计量不完整",
        question="按机构汇总其名下关联客户型敞口集团的成员去重数量与这些成员在本行的合同金额合计，只保留成员去重数量不少于五名的机构，输出机构名称、成员去重数量与合同金额合计，按合同金额合计降序排列，金额四舍五入到两位小数。",
        sql="""SELECT i.institution_name, COUNT(DISTINCT egm.party_id) AS member_count,
       ROUND(SUM(a.contract_amount), 2) AS total_amount
FROM exposure_group eg
JOIN exposure_group_type_catalog egt ON egt.group_type = eg.group_type
JOIN exposure_group_member egm ON egm.exposure_group_id = eg.exposure_group_id
JOIN credit_agreement a ON a.borrower_party_id = egm.party_id AND a.institution_id = eg.institution_id
JOIN institution i ON i.institution_id = eg.institution_id
WHERE egt.name_zh = '关联客户群'
GROUP BY i.institution_id, i.institution_name
HAVING COUNT(DISTINCT egm.party_id) >= 5
ORDER BY SUM(a.contract_amount) DESC, i.institution_name;"""),
    dict(
        id="BRB2-0447", difficulty="medium", features=[],
        penalty_law_zh="《关于规范金融机构资产管理业务的指导意见》关于金融资产公允价值计量、净值化管理的合规要求，账面价值与公允价值严重倒挂涉嫌估值不审慎。",
        penalty_fact_zh="多家理财机构存在持仓账面价值高于公允价值的情形，账面与公允价值倒挂涉嫌估值不审慎、未按公允价值真实反映理财资产状况。",
        question="请找出理财持仓中账面价值高于公允价值（即持仓账面价值与公允价值倒挂）的持仓，按理财产品输出产品编号、产品名称、倒挂金额合计、构成倒挂的持仓笔数，仅保留倒挂金额合计大于零的理财产品，按倒挂金额合计降序、产品编号升序排列。",
        sql="""SELECT wp.product_id, wp.product_name, SUM(ph.carrying_amount-ph.fair_value) AS inv_diff, COUNT(*) AS cnt
FROM product_holding_snapshot ph
JOIN wealth_product wp ON wp.product_id=ph.product_id
WHERE ph.carrying_amount > ph.fair_value
GROUP BY wp.product_id, wp.product_name
HAVING SUM(ph.carrying_amount-ph.fair_value)>0
ORDER BY inv_diff DESC, wp.product_id;"""),
    dict(
        id="BRB2-0448", difficulty="hard", features=[],
        penalty_law_zh="资管新规关于资管产品多层嵌套不得超过一层、不得嵌套通道规避监管的穿透式监管要求。",
        penalty_fact_zh="嵌套深度达三层及以上的理财持仓，穿透后底层资产发行人为本行逾期借款人，涉嫌通过多层嵌套规避监管、向高风险客户输送资金。",
        question="请找出嵌套深度不低于三层的理财产品持仓，其穿透后的底层资产发行人为本行存在逾期借据的借款人，输出产品名称、底层资产名称、嵌套深度、持仓账面价值、该发行人的逾期本金合计，按嵌套深度降序、持仓编号升序排列（逾期借据限于该理财产品发行机构本行）。",
        sql="""WITH dlq AS (SELECT ca.borrower_party_id AS party, ca.institution_id AS inst, SUM(d.overdue_principal) AS overdue, COUNT(DISTINCT ld.loan_id) AS nln FROM delinquency_snapshot d JOIN loan_drawdown ld ON ld.loan_id=d.loan_id JOIN credit_agreement ca ON ca.agreement_id=ld.agreement_id GROUP BY ca.borrower_party_id, ca.institution_id) SELECT wp.product_name, ma.asset_name, ph.lookthrough_depth, ROUND(ph.carrying_amount,2) AS carry, ROUND(dlq.overdue,2) AS overdue
FROM product_holding_snapshot ph
JOIN wealth_product wp ON wp.product_id=ph.product_id
JOIN managed_asset ma ON ma.asset_id=ph.asset_id
JOIN dlq ON dlq.party=ma.issuer_party_id AND dlq.overdue>0 AND dlq.inst=wp.issuer_institution_id
WHERE ph.lookthrough_depth>=3
ORDER BY ph.lookthrough_depth DESC, ph.holding_id;"""),
    dict(
        id="BRB2-0449", difficulty="medium", features=[],
        penalty_law_zh="《商业银行押品管理指引》第三十一条；《商业银行授信工作尽职指引》第六十条",
        penalty_fact_zh="第一顺位押品质押率过高，缓释能力不足",
        question="统计各抵押物被登记为第一顺位的有效押品关联记录中，质押率超过百分之六十的条数，只保留条数不少于两条的抵押物，输出抵押物编号、第一顺位有效记录数与超过百分之六十的记录数，按超过记录数降序排列。",
        sql="""SELECT cl.collateral_id,
       SUM(CASE WHEN cl.lien_priority = 1 AND cl.status = 'ACTIVE' THEN 1 ELSE 0 END) AS first_lien_count,
       SUM(CASE WHEN cl.lien_priority = 1 AND cl.status = 'ACTIVE' AND cl.pledge_ratio > 0.6 THEN 1 ELSE 0 END) AS high_ratio_count
FROM collateral_link cl
GROUP BY cl.collateral_id
HAVING SUM(CASE WHEN cl.lien_priority = 1 AND cl.status = 'ACTIVE' AND cl.pledge_ratio > 0.6 THEN 1 ELSE 0 END) >= 2
ORDER BY SUM(CASE WHEN cl.lien_priority = 1 AND cl.status = 'ACTIVE' AND cl.pledge_ratio > 0.6 THEN 1 ELSE 0 END) DESC, cl.collateral_id;"""),
    dict(
        id="BRB2-0450", difficulty="hard", features=[],
        penalty_law_zh="《商业银行押品管理指引》第四十二条；《商业银行贷款分类指引》相关条款",
        penalty_fact_zh="内外评估口径差异显著，价值比对失真影响缓释计量",
        question="对同时拥有内部评估与外部评估的抵质押物，比较两类评估的最高价值，找出外部最高价值高于内部最高价值的抵质押物，输出抵质押物编号、名称、内部最高价值、外部最高价值与内外价值比（保留四位小数），按价值比降序排列。",
        sql="""SELECT ca.collateral_id AS collateral_id, ca.asset_label AS label,
       MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END) AS internal_max,
       MAX(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END) AS external_max,
       ROUND(MAX(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END) * 1.0
             / MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END), 4) AS ratio_val
FROM collateral_asset ca
JOIN collateral_valuation cv ON cv.collateral_id = ca.collateral_id
GROUP BY ca.collateral_id, ca.asset_label
HAVING MAX(CASE WHEN cv.valuation_type = 'EXTERNAL' THEN cv.valuation_amount END)
     > MAX(CASE WHEN cv.valuation_type = 'INTERNAL' THEN cv.valuation_amount END)
ORDER BY ratio_val DESC, ca.collateral_id;"""),
    dict(
        id="BRB2-0451", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第三十四条、第四十六条：监管机构有权对金融机构报送的财务报表真实性进行核查，财务与资本数据失实或严重偏离审慎指标，可依法责令整改并处以罚款。",
        penalty_fact_zh="华东银行向监管报送的资产负债表与企业所得税汇算口径明显背离，营业收入与净资产的审慎核算标准执行不一，被认定信息披露不实。",
        question="输出各银行机构的名称、总资产、总负债、净资产与营业收入，按营业收入从高到低排列（机构财务数据存放在财务快照表中，其主体编号为 PTY- 加机构编号）。",
        sql="""SELECT i.institution_name, f.total_assets, f.total_liabilities, f.net_assets, f.annual_revenue FROM institution i JOIN financial_snapshot f ON f.party_id = 'PTY-'||i.institution_id ORDER BY f.annual_revenue DESC;"""),
    dict(
        id="BRB2-0452", difficulty="easy", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第三十四条、第四十六条：监管机构有权对金融机构报送的财务报表真实性进行核查，财务与资本数据失实或严重偏离审慎指标，可依法责令整改并处以罚款。",
        penalty_fact_zh="西部城市商业银行杠杆水平远超同业，总负债对总资产占比畸高，反映出负债扩张激进、偿债压力向监管红线上探，被要求补充资本。",
        question="计算并输出各银行机构的资产负债率（总负债除以总资产，保留四位小数），按资产负债率从高到低排列（机构财务数据存放在财务快照表中，其主体编号为 PTY- 加机构编号）。",
        sql="""SELECT i.institution_name, ROUND(f.total_liabilities/f.total_assets,4) AS ratio_val FROM institution i JOIN financial_snapshot f ON f.party_id='PTY-'||i.institution_id ORDER BY ratio_val DESC;"""),
    dict(
        id="BRB2-0453", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条及《商业银行资本管理办法》就资本充足率、杠杆与偿债能力设定的监管指标，是判断机构稳健经营与可能触及监管红线的法定依据。",
        penalty_fact_zh="北方农村商业银行核心一级资本相对风险加权资产明显偏低，逼近监管最低要求，反映出资本内生补充能力不足、风险加权扩张过快。",
        question="计算并输出各银行机构的核心一级资本占风险加权资产的比例（核心一级资本除以风险加权资产，保留四位小数），按该比例从高到低排列。",
        sql="""SELECT i.institution_name, ROUND(c.tier1_capital/c.risk_weighted_assets,4) AS ratio_val FROM capital_snapshot c JOIN institution i ON i.institution_id=c.institution_id ORDER BY ratio_val DESC;"""),
    dict(
        id="BRB2-0454", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第四十六条及《商业银行资本管理办法》就资本充足率、杠杆与偿债能力设定的监管指标，是判断机构稳健经营与可能触及监管红线的法定依据。",
        penalty_fact_zh="东海村镇银行净资本相对总资产的比例显著偏低，抗风险与吸收损失能力不足，监管部门据此下调其监管评级并责令补充资本。",
        question="输出各银行机构的名称、净资本与总资产之比（保留六位小数），按该比值从高到低排列（机构财务数据存放在财务快照表中，其主体编号为 PTY- 加机构编号）。",
        sql="""SELECT i.institution_name, ROUND(c.net_capital/f.total_assets,6) AS leverage_val FROM institution i JOIN capital_snapshot c ON c.institution_id=i.institution_id JOIN financial_snapshot f ON f.party_id='PTY-'||i.institution_id ORDER BY leverage_val DESC;"""),
    dict(
        id="BRB2-0455", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第三十四条、第四十六条：监管机构有权对金融机构报送的财务报表真实性进行核查，财务与资本数据失实或严重偏离审慎指标，可依法责令整改并处以罚款。",
        penalty_fact_zh="华南银行净利润率长期为正但略低于同业均值，监管核查其收入确认口径后认定财务列报存在口径不一致问题。",
        question="输出净利润率（净资产除以营业收入，保留四位小数）低于0.85的各机构名称与净利润率，按净利润率从低到高排列。",
        sql="""SELECT i.institution_name, ROUND(f.net_assets/f.annual_revenue,4) AS margin FROM institution i JOIN financial_snapshot f ON f.party_id='PTY-'||i.institution_id WHERE f.net_assets/f.annual_revenue < 0.85 ORDER BY margin;"""),
    dict(
        id="BRB2-0456", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第三十四条、第四十六条：监管机构有权对金融机构报送的财务报表真实性进行核查，财务与资本数据失实或严重偏离审慎指标，可依法责令整改并处以罚款。",
        penalty_fact_zh="中原民营银行以窗口函数对其未来评级排序，监管发现其按总资产排序的位次与监管评级明显背离，数据自洽性存疑。",
        question="按银行机构总资产从高到低使用排名函数给出名次，输出机构名称、总资产与名次，按名次从高到低排列。",
        sql="""SELECT i.institution_name, f.total_assets, RANK() OVER (ORDER BY f.total_assets DESC) AS rank_val FROM institution i JOIN financial_snapshot f ON f.party_id='PTY-'||i.institution_id ORDER BY rank_val;"""),
    dict(
        id="BRB2-0457", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国银行业监督管理法》第三十四条、第四十六条：监管机构有权对金融机构报送的财务报表真实性进行核查，财务与资本数据失实或严重偏离审慎指标，可依法责令整改并处以罚款。",
        penalty_fact_zh="华东银行、华南银行合计营业收入占全部银行机构营业收入比重明显超过四分之一，监管认定其收入集中于头部，风险抵御集中度偏高。",
        question="输出营业收入占全部银行机构营业收入合计的比例超过15%的机构名称、营业收入与占比（保留两位小数），按占比从高到低排列（机构财务数据存放在财务快照表中，其主体编号为 PTY- 加机构编号）。",
        sql="""SELECT i.institution_name, f.annual_revenue, ROUND(f.annual_revenue*100.0/t.agg_rev,2) AS share FROM institution i JOIN financial_snapshot f ON f.party_id='PTY-'||i.institution_id CROSS JOIN (SELECT SUM(annual_revenue) AS agg_rev FROM financial_snapshot) t WHERE f.annual_revenue*100.0/t.agg_rev > 15 ORDER BY share DESC;"""),
    dict(
        id="BRB2-0458", difficulty="easy", features=[],
        penalty_law_zh="《商业银行理财业务监督管理办法》及《关于规范金融机构资产管理业务的指导意见》（资管新规）要求对资管产品底层资产进行穿透、公允估值与风险评级，禁止通过表内外嵌套规避监管。",
        penalty_fact_zh="多家银行理财持仓底层资产采用不同估值方法，监管要求对公允价值计量科目实行穿透核对，防止估值方法不一致导致净值虚增。",
        question="按底层资产的估值方法进行分组，输出每种估值方法对应的底层资产数量，按数量从多到少排列。",
        sql="""SELECT valuation_method, COUNT(*) AS asset_cnt FROM managed_asset GROUP BY valuation_method ORDER BY asset_cnt DESC;"""),
    dict(
        id="BRB2-0459", difficulty="hard", features=[],
        penalty_law_zh="《商业银行理财业务监督管理办法》及《关于规范金融机构资产管理业务的指导意见》（资管新规）要求对资管产品底层资产进行穿透、公允估值与风险评级，禁止通过表内外嵌套规避监管。",
        penalty_fact_zh="监管抽查底层资产内部评级为AAA的债券类资产，发现其发行金额与外部评级存在明显偏离，要求机构重新核验评级依据。",
        question="逐类计算保证合同中保证金额低于其担保金额的保证份额占比，仅保留该占比高于百分之八十的担保类型，输出担保类型与该占比，按该占比降序、担保类型升序排列。",
        sql="""SELECT sa.security_type,
       ROUND(AVG(CASE WHEN gc.guaranteed_amount < sa.secured_amount THEN 1.0 ELSE 0.0 END), 4) AS short_ratio
FROM security_agreement sa
JOIN guarantor_commitment gc ON gc.security_id = sa.security_id
GROUP BY sa.security_type
HAVING AVG(CASE WHEN gc.guaranteed_amount < sa.secured_amount THEN 1.0 ELSE 0.0 END) > 0.8
ORDER BY short_ratio DESC, sa.security_type;"""),
    dict(
        id="BRB2-0460", difficulty="medium", features=[],
        penalty_law_zh="《商业银行理财业务监督管理办法》及《关于规范金融机构资产管理业务的指导意见》（资管新规）要求对资管产品底层资产进行穿透、公允估值与风险评级，禁止通过表内外嵌套规避监管。",
        penalty_fact_zh="监管穿透比对发现相当数量的底层资产内部评级与外部评级不一致，机构在风险分类与资本占用上可能存在高估情形。",
        question="按银行机构分组，输出各机构内部评级与外部评级不一致的底层资产数量，按数量从多到少排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS mismatch_cnt FROM managed_asset m JOIN institution i ON i.institution_id=m.originator_institution_id WHERE m.internal_rating<>m.external_rating GROUP BY i.institution_name ORDER BY mismatch_cnt DESC;"""),
    dict(
        id="BRB2-0461", difficulty="medium", features=[],
        penalty_law_zh="《商业银行理财业务监督管理办法》及《关于规范金融机构资产管理业务的指导意见》（资管新规）要求对资管产品底层资产进行穿透、公允估值与风险评级，禁止通过表内外嵌套规避监管。",
        penalty_fact_zh="监管要求对理财产品持仓进行穿透核查，按底层资产估值方法汇总持仓账面价值，识别是否存在重复计量与错配。",
        question="按底层资产的估值方法分组，输出各方法下经理财产品持仓穿透核实的账面价值合计（保留两位小数），按合计从高到低排列。",
        sql="""SELECT m.valuation_method, ROUND(SUM(h.carrying_amount),2) AS carrying_total FROM product_holding_snapshot h JOIN managed_asset m ON m.asset_id=h.asset_id GROUP BY m.valuation_method ORDER BY carrying_total DESC;"""),
    dict(
        id="BRB2-0462", difficulty="hard", features=[],
        penalty_law_zh="《商业银行理财业务监督管理办法》及《关于规范金融机构资产管理业务的指导意见》（资管新规）要求对资管产品底层资产进行穿透、公允估值与风险评级，禁止通过表内外嵌套规避监管。",
        penalty_fact_zh="部分底层资产以负债性质入表且内部评级为BBB，监管质疑其出表与估值真实性，要求逐笔说明会计处理依据。",
        question="对剩余期限超过二百天的产品持仓按投资路径汇总持仓数量，仅保留数量少于三百五十二条的路径，输出投资路径与持仓数量，按持仓数量降序、投资路径升序排列。",
        sql="""SELECT ph.investment_path,
       COUNT(*) AS cnt
FROM product_holding_snapshot ph
WHERE ph.remaining_term_days > 200
GROUP BY ph.investment_path
HAVING COUNT(*) < 352
ORDER BY cnt DESC, ph.investment_path;"""),
    dict(
        id="BRB2-0463", difficulty="hard", features=[],
        penalty_law_zh="《商业银行理财业务监督管理办法》及《关于规范金融机构资产管理业务的指导意见》（资管新规）要求对资管产品底层资产进行穿透、公允估值与风险评级，禁止通过表内外嵌套规避监管。",
        penalty_fact_zh="监管对公允价值计量且外部评级为无评级的底层资产进行专项核查，要求机构就收益率偏离与估值参数作出说明。",
        question="按发行机构统计采用公允价值计量、且外部评级为无评级的底层资产的数量、平均年化收益率与发行金额合计，输出机构名称、资产数、平均年化收益率与发行金额合计，仅保留资产数不少于 10 只的机构，按发行金额合计降序排列。",
        sql="""SELECT i.institution_name,
       COUNT(*) AS asset_count,
       ROUND(AVG(m.annual_yield_rate), 4) AS avg_yield,
       ROUND(SUM(m.issued_amount), 2) AS issued_total
FROM managed_asset m
JOIN institution i ON i.institution_id = m.originator_institution_id
WHERE m.external_rating = 'NR'
  AND m.valuation_method = 'FVTPL'
GROUP BY i.institution_name
HAVING COUNT(*) >= 10
ORDER BY issued_total DESC, i.institution_name;"""),
    dict(
        id="BRB2-0464", difficulty="easy", features=[],
        penalty_law_zh="《储蓄管理条例》《商业银行大额风险管理指引》就存款真实性、质押止付、扣划合法性与存款人权益保护作出规定，违规操作予以行政处罚。",
        penalty_fact_zh="监管核查机构定期存款台账，要求按机构汇总本金与笔数以评估负债结构与稳定性。",
        question="统计各银行机构定期存款的开户笔数与本金合计（保留两位小数），输出机构名称、笔数、本金合计，按本金合计从高到低排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS deposit_cnt, ROUND(SUM(td.opening_principal),2) AS principal_total FROM term_deposit td JOIN account a ON a.account_id=td.account_id JOIN institution i ON i.institution_id=a.institution_id GROUP BY i.institution_name ORDER BY principal_total DESC;"""),
    dict(
        id="BRB2-0465", difficulty="medium", features=[],
        penalty_law_zh="《储蓄管理条例》《商业银行大额风险管理指引》就存款真实性、质押止付、扣划合法性与存款人权益保护作出规定，违规操作予以行政处罚。",
        penalty_fact_zh="部分机构以高利率吸收定期存款，监管视作变相抬高负债成本，要求查明资金用途与合规性。",
        question="输出各银行机构定期存款年化利率高于3%的存单数量，按数量从多到少排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS high_rate_cnt FROM term_deposit td JOIN account a ON a.account_id=td.account_id JOIN institution i ON i.institution_id=a.institution_id WHERE td.annual_interest_rate>3.0 GROUP BY i.institution_name ORDER BY high_rate_cnt DESC;"""),
    dict(
        id="BRB2-0466", difficulty="hard", features=[],
        penalty_law_zh="《储蓄管理条例》《商业银行大额风险管理指引》就存款真实性、质押止付、扣划合法性与存款人权益保护作出规定，违规操作予以行政处罚。",
        penalty_fact_zh="机构存在为拉客户而大幅抬高定期存款利率的情形，监管要求对利率过高产品说明定价依据。",
        question="统计固定雇佣员工在不同授权等级下的柜面操作员人数与其对应的员工人数，仅保留员工人数不少于十人的等级，输出授权等级、操作员人数与员工人数，按操作员人数降序、授权等级升序排列。",
        sql="""SELECT so.authority_level,
       COUNT(DISTINCT so.operator_id) AS ops,
       COUNT(DISTINCT so.staff_id) AS staffs
FROM service_operator so
JOIN staff_member sm ON sm.staff_id = so.staff_id
WHERE sm.employment_type = 'PERMANENT'
GROUP BY so.authority_level
HAVING COUNT(DISTINCT so.staff_id) >= 10
ORDER BY ops DESC, so.authority_level;"""),
    dict(
        id="BRB2-0467", difficulty="hard", features=[],
        penalty_law_zh="《储蓄管理条例》《商业银行大额风险管理指引》就存款真实性、质押止付、扣划合法性与存款人权益保护作出规定，违规操作予以行政处罚。",
        penalty_fact_zh="基准日后三十天内到期的定期存单面临集中转存，监管提示机构防范到期资金挪用与流动性错配风险。",
        question="统计在审计基准日（2026-06-30）当天及之后三十天内（即到期日距基准日天数在 0 至 30 天之间）到期的定期存款笔数，按开户机构分组输出机构名称与笔数，按笔数从多到少排列。",
        sql="""SELECT i.institution_name, COUNT(*) AS due_cnt
FROM term_deposit td
JOIN account a ON a.account_id = td.account_id
JOIN institution i ON i.institution_id = a.institution_id
WHERE julianday(td.maturity_on) - julianday('2026-06-30') BETWEEN 0 AND 30
GROUP BY i.institution_id, i.institution_name
ORDER BY due_cnt DESC, i.institution_name;"""),
    dict(
        id="BRB2-0468", difficulty="hard", features=[],
        penalty_law_zh="《储蓄管理条例》《商业银行大额风险管理指引》就存款真实性、质押止付、扣划合法性与存款人权益保护作出规定，违规操作予以行政处罚。",
        penalty_fact_zh="监管以窗口函数对机构定期存款本金规模进行排序，识别负债来源集中度风险。",
        question="按开户机构汇总定期存款的累计开户本金与开户笔数，并使用行号函数按本金从高到低给出名次，输出机构名称、本金合计、开户笔数与名次，仅保留开户笔数不少于 15 笔的机构，按名次升序排列。",
        sql="""SELECT i.institution_name,
       ROUND(SUM(td.opening_principal), 2) AS principal_total,
       COUNT(*) AS deposit_count,
       ROW_NUMBER() OVER (ORDER BY SUM(td.opening_principal) DESC) AS rnk
FROM term_deposit td
JOIN account a ON a.account_id = td.account_id
JOIN institution i ON i.institution_id = a.institution_id
GROUP BY i.institution_name, i.institution_id
HAVING COUNT(*) >= 15
ORDER BY rnk, i.institution_name;"""),
    dict(
        id="BRB2-0469", difficulty="hard", features=[],
        penalty_law_zh="《商业银行大额风险暴露管理办法》关于资产管理产品穿透至基础资产并计算单一客户集中度风险暴露的监管要求。",
        penalty_fact_zh="部分理财产品对单一底层债务人的持仓集中度占比过高，超过监管对大额风险暴露的审慎比例要求。",
        question="评估各理财产品对单一底层资产最终债务人的持仓集中度：统计理财产品对各最终债务人的持仓市值，并测算其占该产品持仓总市值的比重，仅保留占比超过三成的记录，输出产品名称、最终债务人编号、对该债务人的持仓市值与集中度占比（百分比，保留两位小数），按占比降序、产品名称升序排列。",
        sql="""WITH tot AS (
    SELECT product_id AS product_id, SUM(converted_amount) AS gross, COUNT(*) AS n
    FROM product_holding_snapshot
    GROUP BY product_id
)
SELECT wp.product_name,
       ma.obligor_party_id AS obligor_party_id,
       ROUND(SUM(ph.converted_amount), 2) AS exposed_amount,
       ROUND(SUM(ph.converted_amount) * 100.0 / tot.gross, 2) AS conc_pct
FROM product_holding_snapshot ph
JOIN wealth_product wp ON wp.product_id = ph.product_id
JOIN managed_asset ma ON ma.asset_id = ph.asset_id
JOIN tot ON tot.product_id = ph.product_id
GROUP BY wp.product_id, wp.product_name, ma.obligor_party_id, tot.gross
HAVING SUM(ph.converted_amount) * 100.0 / tot.gross > 30
ORDER BY conc_pct DESC, wp.product_name;"""),
    dict(
        id="BRB2-0470", difficulty="medium", features=[],
        penalty_law_zh="《商业银行法》《贷款损失准备计提管理办法》关于按监管要求足额计提贷款减值准备、不得少计提准备虚增利润与财务指标的监管规定。",
        penalty_fact_zh="多家机构贷款减值准备少计提总额占年度营业收入比重偏高，涉嫌通过少计提拨备虚增当年度经营利润。",
        question="请计算各机构贷款减值准备少计提总额（应计提额减已计提额合计）占该机构年度营业收入的比重，输出机构编号、少计提总额、少计提总额占营业收入的百分比，仅保留占比超过百分之五的机构，按少计提总额占营业收入百分比降序排列。",
        sql="""WITH ps AS (SELECT ca.institution_id AS institution_id, SUM(pv.required_amount-pv.recognized_amount) AS shortage FROM provision_snapshot pv JOIN loan_drawdown ld ON ld.loan_id=pv.loan_id JOIN credit_agreement ca ON ca.agreement_id=ld.agreement_id GROUP BY ca.institution_id)
SELECT ps.institution_id, ROUND(ps.shortage,2) AS shortage, ROUND(ps.shortage/f.annual_revenue*100,2) AS ratio
FROM ps JOIN financial_snapshot f ON f.party_id='PTY-'||ps.institution_id
WHERE ps.shortage/f.annual_revenue>0.05
ORDER BY ratio DESC;"""),
    dict(
        id="BRB2-0471", difficulty="medium", features=[],
        penalty_law_zh="《商业银行法》第五十五条、第五十六条及拨备监管规定关于足额计提拨备、真实反映盈利与净资产的财务真实性与审慎性要求。",
        penalty_fact_zh="部分机构贷款减值准备少计提总额占净资产比重过高，涉嫌利用少提拨备虚增净资产、粉饰财务指标。",
        question="测算各机构贷款减值准备少计提总额占其净资产的比重：仅统计已计提低于应计提的借据，输出机构编号、机构名称、少计提总额、净资产与少计提占净资产的百分比（保留两位小数），仅保留存在少计提的机构，按占比降序、机构编号升序排列（机构财务数据存放在财务快照表中，其主体编号为 PTY- 加机构编号）。",
        sql="""WITH short AS (
    SELECT ca.institution_id AS institution_id,
           ROUND(SUM(ps.required_amount - ps.recognized_amount), 2) AS shortage
    FROM provision_snapshot ps
    JOIN loan_drawdown ld ON ld.loan_id = ps.loan_id
    JOIN credit_agreement ca ON ca.agreement_id = ld.agreement_id
    WHERE ps.recognized_amount < ps.required_amount
    GROUP BY ca.institution_id
)
SELECT s.institution_id AS institution_id,
       i.institution_name,
       s.shortage AS shortage,
       f.net_assets AS net_assets,
       ROUND(s.shortage * 100.0 / f.net_assets, 2) AS pct_net_assets
FROM short s
JOIN institution i ON i.institution_id = s.institution_id
JOIN financial_snapshot f ON f.party_id = 'PTY-' || s.institution_id
ORDER BY pct_net_assets DESC, s.institution_id;"""),
    dict(
        id="BRB2-0472", difficulty="medium", features=[],
        penalty_law_zh="《商业银行资本管理办法》及风险监管核心指标关于风险加权资产计量准确性、资本与资产密度应审慎反映业务风险的要求。",
        penalty_fact_zh="各机构风险加权资产占总资产密度与其不良贷款余额情况经联动核验，存在资本计量与风险暴露不匹配的迹象。",
        question="请计算各机构风险加权资产占总资产的密度，并与不良贷款余额（即逾期本金合计）联动输出，输出机构编号、风险加权资产占总资产百分比、不良贷款余额（单位亿元），按风险加权资产占总资产百分比降序排列。",
        sql="""WITH bad AS (SELECT ca.institution_id AS institution_id, SUM(d.overdue_principal) AS bad_bal FROM delinquency_snapshot d JOIN loan_drawdown ld ON ld.loan_id=d.loan_id JOIN credit_agreement ca ON ca.agreement_id=ld.agreement_id GROUP BY ca.institution_id)
SELECT cs.institution_id, ROUND(cs.risk_weighted_assets/f.total_assets*100,2) AS rwa_density, ROUND(bad.bad_bal/100000000.0,2) AS bad_yi
FROM capital_snapshot cs
JOIN financial_snapshot f ON f.party_id='PTY-'||cs.institution_id
JOIN bad ON bad.institution_id=cs.institution_id
ORDER BY rwa_density DESC;"""),
    dict(
        id="BRB2-0473", difficulty="hard", features=[],
        penalty_law_zh="《商业银行资本管理办法》关于净资本充足率、风险资产覆盖率的最低监管要求及资本不得低于法定比例的处罚规定。",
        penalty_fact_zh="个别机构净资本充足率明显偏低，触及资本监管红线，需立即补充资本并整改。",
        question="对人工认定且属于不良分类的借据，按风险分类名称汇总借据数量，仅保留数量介于六十至一百零五之间的名称，输出风险分类名称与借据数量，按借据数量降序、风险分类名称升序排列。",
        sql="""SELECT g.grade_name_zh,
       COUNT(*) AS cnt
FROM risk_classification rc
JOIN classification_grade g ON g.grade_code = rc.grade_code
WHERE rc.classification_basis = 'MANUAL_REVIEW'
GROUP BY g.grade_name_zh
HAVING COUNT(*) BETWEEN 60 AND 105
ORDER BY cnt DESC, g.grade_name_zh;"""),
    dict(
        id="BRB2-0474", difficulty="easy", features=[],
        penalty_law_zh="监管部门关于禁止理财及信贷资金投向退出类（淘汰落后产能）行业、严禁通过通道违规投融两高一剩项目的合规要求。",
        penalty_fact_zh="存在底层资产最终债务人行业为监管退出类行业的持仓，涉嫌资金违规投向淘汰落后产能领域。",
        question="按落地行业分组统计外部评级退出类行业底层资产的规模：汇总资产数量与平均年化收益率，输出行业中文名称、资产数量与平均年化收益率，仅保留资产不少于 5 只的行业，按资产数量降序排列。",
        sql="""SELECT s.sector_name_zh AS sector_name,
       COUNT(*) AS asset_count,
       ROUND(AVG(m.annual_yield_rate), 4) AS avg_yield
FROM managed_asset m
JOIN industry_sector s ON s.sector_code = m.industry_code
WHERE s.risk_category = 'EXIT'
GROUP BY s.sector_code, s.sector_name_zh
HAVING COUNT(*) >= 5
ORDER BY asset_count DESC, sector_name;"""),
    dict(
        id="BRB2-0475", difficulty="extra", features=[],
        penalty_law_zh="《商业银行法》及不良贷款监管统计办法关于不良贷款认定准确性、逾期九十天以上贷款应如实记入不良并足额计提的监管要求。",
        penalty_fact_zh="存在逾期九十天以上不良贷款余额较重、占用机构营业收入比例明显偏高的机构，不良资产化解与准备计提压力突出。",
        question="请找出逾期本金天数达到九十天及以上的不良贷款，计算各机构不良贷款借据笔数合计与逾期本金合计，并输出逾期本金合计占该机构营业收入的比重是否偏高，输出机构编号、不良借据笔数、逾期本金合计，仅保留逾期本金合计占营业收入超过五成的机构，按逾期本金合计降序排列（机构财务数据存放在财务快照表中，其主体编号为 PTY- 加机构编号）。",
        sql="""WITH sh AS (SELECT ca.institution_id AS institution_id, COUNT(DISTINCT ld.loan_id) AS npl_loan, SUM(d.overdue_principal) AS tot_od FROM delinquency_snapshot d JOIN loan_drawdown ld ON ld.loan_id=d.loan_id JOIN credit_agreement ca ON ca.agreement_id=ld.agreement_id WHERE d.principal_overdue_days>=90 GROUP BY ca.institution_id)
SELECT cs.institution_id, sh.npl_loan, ROUND(sh.tot_od,2) AS tot_od
FROM capital_snapshot cs
JOIN sh ON sh.institution_id=cs.institution_id
JOIN financial_snapshot f ON f.party_id='PTY-'||cs.institution_id
WHERE sh.tot_od/f.annual_revenue>0.5
ORDER BY tot_od DESC;"""),
    dict(
        id="BRB2-0476", difficulty="medium", features=[],
        penalty_law_zh="资管新规关于理财产品实行公允价值计量与净值化管理、持仓估值应公允审慎的合规要求。",
        penalty_fact_zh="多只理财产品存在持仓账面价值高于公允价值情形，平均倒挂金额较大，涉嫌估值不审慎。",
        question="请计算各理财产品持仓账面价值高于公允价值（倒挂）的持仓，输出产品名称、平均倒挂金额、倒挂持仓笔数，按平均倒挂金额降序、倒挂持仓笔数降序排列。",
        sql="""SELECT wp.product_name, ROUND(AVG(ph.carrying_amount-ph.fair_value),2) AS avg_diff, COUNT(*) AS holdings
FROM product_holding_snapshot ph
JOIN wealth_product wp ON wp.product_id=ph.product_id
WHERE ph.carrying_amount>ph.fair_value
GROUP BY wp.product_name
ORDER BY avg_diff DESC, holdings DESC;"""),
    dict(
        id="BRB2-0477", difficulty="hard", features=[],
        penalty_law_zh="资管新规关于公募与私募理财产品投资非标准化债权类资产的比例上限（不得超过理财产品净值的百分之三十五）及穿透计量的监管要求。",
        penalty_fact_zh="多只理财产品持有非标准化债权类底层资产，需核查其占比是否超过监管百分比上限并经穿透计量。",
        question="列出仍处于有效状态、账户子类型为专用且可用余额不低于全行平均可用余额的银行账户，输出账户编号、账户子类型与可用余额，按可用余额降序排列。",
        sql="""SELECT a.account_id,
       a.account_subtype,
       ab.available_balance
FROM account a
JOIN account_balance_snapshot ab ON ab.account_id = a.account_id
WHERE a.status = 'ACTIVE'
  AND ab.available_balance >= (SELECT AVG(available_balance) FROM account_balance_snapshot)
  AND a.account_subtype = 'SPECIAL'
ORDER BY ab.available_balance DESC;"""),
    dict(
        id="BRB2-0478", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》及不良贷款追偿监管要求，理财资金不得承接该行已发生多笔逾期的借款人资产。",
        penalty_fact_zh="识别出部分借款人名下逾九十天不良借据达两笔及以上，其资产仍被某理财产品作为底层资产持有，涉嫌以理财资金承接高风险客户资产。",
        question="请找出名下逾期本金天数超过九十天的不良借据达两笔及以上的借款人，其同时是某理财产品底层资产的最终债务人，输出产品名称、底层资产名称、该借款人单笔最大逾期本金，按最大逾期本金降序、产品名称升序排列。",
        sql="""WITH dq AS (SELECT ca.borrower_party_id AS party, COUNT(DISTINCT ld.loan_id) AS cnt, MAX(d.overdue_principal) AS mx FROM delinquency_snapshot d JOIN loan_drawdown ld ON ld.loan_id=d.loan_id JOIN credit_agreement ca ON ca.agreement_id=ld.agreement_id WHERE d.principal_overdue_days>90 GROUP BY ca.borrower_party_id)
SELECT wp.product_name, ma.asset_name, dq.mx AS max_od
FROM product_holding_snapshot ph
JOIN wealth_product wp ON wp.product_id=ph.product_id
JOIN managed_asset ma ON ma.asset_id=ph.asset_id
JOIN dq ON dq.party=ma.obligor_party_id
WHERE dq.cnt>=2
ORDER BY max_od DESC, wp.product_name;"""),
    dict(
        id="BRB2-0479", difficulty="easy", features=[],
        penalty_law_zh="《商业银行资本管理办法》关于系统重要性银行一级资本充足率不得低于百分之九的资本监管最低要求。",
        penalty_fact_zh="个别机构一级资本充足率低于百分之九的法定最低要求，资本补充严重不足。",
        question="请计算各机构一级资本与风险加权资产的比率（一级资本充足率），输出机构名称、一级资本充足率，仅保留一级资本充足率低于百分之九的机构，按一级资本充足率升序排列。",
        sql="""SELECT i.institution_name, ROUND(cs.tier1_capital/cs.risk_weighted_assets*100,2) AS t1_car
FROM capital_snapshot cs
JOIN institution i ON i.institution_id=cs.institution_id
WHERE cs.tier1_capital/cs.risk_weighted_assets<0.09
ORDER BY t1_car;"""),
    dict(
        id="BRB2-0480", difficulty="medium", features=[],
        penalty_law_zh="资管新规关于资产管理产品多层嵌套不得超过一层的穿透式监管要求及嵌套结构的信息披露义务。",
        penalty_fact_zh="多只理财产品存在三层及以上多层嵌套持仓，涉嫌违反资管新规关于嵌套层数不得超过一层的限制。",
        question="统计各理财产品中嵌套深度达到三层及以上的穿透持仓笔数，并依据笔数由高到低给出名次，输出产品名称、深度持仓笔数与名次，按名次升序、产品名称升序排列。",
        sql="""WITH d AS (
    SELECT ph.product_id AS product_id, COUNT(*) AS deep_cnt
    FROM product_holding_snapshot ph
    WHERE ph.lookthrough_depth >= 3
    GROUP BY ph.product_id
)
SELECT wp.product_name AS product_name, d.deep_cnt AS deep_cnt,
       RANK() OVER (ORDER BY d.deep_cnt DESC) AS depth_rank
FROM d
JOIN wealth_product wp ON wp.product_id = d.product_id
ORDER BY depth_rank, wp.product_name;"""),
    dict(
        id="BRB2-0481", difficulty="hard", features=[],
        penalty_law_zh="《商业银行资本管理办法》关于风险加权资产计量准确、与其实际表内外风险暴露相匹配的监管要求。",
        penalty_fact_zh="部分机构风险加权资产与其表内贷款余额之比偏离明显，资本计量与实际风险暴露匹配存疑。",
        question="测算各机构未结清贷款本金余额合计占其风险加权资产的比例，输出机构名称、本金余额合计、风险加权资产与贷款占风险加权资产百分比（保留两位小数），按百分比降序、机构名称升序排列。",
        sql="""WITH lb AS (
    SELECT ca.institution_id AS institution_id,
           ROUND(SUM(lbs.principal_balance), 2) AS gross_loan
    FROM loan_balance_snapshot lbs
    JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
    JOIN credit_agreement ca ON ca.agreement_id = ld.agreement_id
    WHERE ld.status = 'ACTIVE'
    GROUP BY ca.institution_id
)
SELECT i.institution_name AS institution_name,
       lb.gross_loan AS gross_loan,
       cs.risk_weighted_assets AS rwa,
       ROUND(lb.gross_loan * 100.0 / cs.risk_weighted_assets, 2) AS loan_pct_rwa
FROM lb
JOIN institution i ON i.institution_id = lb.institution_id
JOIN capital_snapshot cs ON cs.institution_id = lb.institution_id
ORDER BY loan_pct_rwa DESC, i.institution_name;"""),
    dict(
        id="BRB2-0482", difficulty="hard", features=[],
        penalty_law_zh="资管新规与《商业银行理财业务监督管理办法》关于非标债权投向穿透核查、禁止为表内高风险客户变相融资的监管要求。",
        penalty_fact_zh="识别出多笔非标债权底层资产发行人为本行逾期借款人，理财资金穿透后又回流本行高风险客户。",
        question="排查非标准化债权类底层资产：其发行主体在本行存在本金逾期借据，输出资产编号、资产名称、发行人编号与该发行人本金逾期金额合计（取逾期本金合计，保留两位小数），按逾期金额合计降序、资产编号升序排列。",
        sql="""SELECT ma.asset_id AS asset_id, ma.asset_name AS asset_name,
       ma.issuer_party_id AS issuer_party_id,
       (SELECT ROUND(SUM(d.overdue_principal), 2) FROM delinquency_snapshot d
         JOIN loan_drawdown ld ON ld.loan_id = d.loan_id
         JOIN credit_agreement ca ON ca.agreement_id = ld.agreement_id
         WHERE ca.borrower_party_id = ma.issuer_party_id) AS overdue_total
FROM managed_asset ma
WHERE ma.asset_scope = 'NON_STANDARDIZED'
  AND EXISTS (SELECT 1 FROM delinquency_snapshot d
               JOIN loan_drawdown ld ON ld.loan_id = d.loan_id
               JOIN credit_agreement ca ON ca.agreement_id = ld.agreement_id
               WHERE ca.borrower_party_id = ma.issuer_party_id)
ORDER BY overdue_total DESC, ma.asset_id;"""),
    dict(
        id="BRB2-0483", difficulty="medium", features=[],
        penalty_law_zh="监管部门关于理财及信贷资源禁止投向限制类、退出类行业的宏观调控与合规要求。",
        penalty_fact_zh="大量理财底层资产投向限制类与退出类行业，资金投向与宏观调控与合规要求不符。",
        question="请按所属行业汇总限制类与退出类行业的理财底层资产，输出行业代码、行业中文名称、资产笔数、资产总规模（单位亿元），按资产总规模降序、行业代码升序排列。",
        sql="""SELECT ma.industry_code, is_.sector_name_zh, COUNT(*) AS cnt, ROUND(SUM(ma.issued_amount/100000000.0),2) AS amt_yi
FROM managed_asset ma
JOIN industry_sector is_ ON is_.sector_code=ma.industry_code
WHERE is_.risk_category IN ('RESTRICTED','EXIT')
GROUP BY ma.industry_code, is_.sector_name_zh
ORDER BY amt_yi DESC, ma.industry_code;"""),
    dict(
        id="BRB2-0484", difficulty="hard", features=[],
        penalty_law_zh="《商业银行理财业务监督管理办法》关于理财资金投资范围负面清单、严禁投向风险过高限制类行业资产的合规要求。",
        penalty_fact_zh="部分发行机构发售多支持有限制类行业底层资产的理财产品，理财资金投向风险偏高。",
        question="对存在待执行支付指令且仍处于有效状态的借据，按支付结算方式汇总待执行指令数量，仅保留数量多于四十五条的结算方式，输出结算方式与待执行指令数量，按待执行指令数量降序、结算方式升序排列。",
        sql="""SELECT pi.payment_mode,
       COUNT(*) AS cnt
FROM payment_instruction pi
JOIN loan_drawdown dd ON dd.loan_id = pi.loan_id
WHERE pi.status = 'PENDING'
  AND dd.status = 'ACTIVE'
GROUP BY pi.payment_mode
HAVING COUNT(*) > 45
ORDER BY cnt DESC, pi.payment_mode;"""),
    dict(
        id="BRB2-0485", difficulty="hard", features=[],
        penalty_law_zh="《商业银行法》及资管新规关于禁止银行利用理财产品向本行不良或高风险客户变相输送资金、规避信用风险管控的处罚规定。",
        penalty_fact_zh="各发行机构以理财资金持有本行自身逾期借款人底层资产的金额可观，涉嫌变相向本行高风险客户输血。",
        question="汇总各发行机构透过理财产品持有的底层资产中，最终债务人为其自身逾期借据借款人的持仓情况，并按底层资产所属行业归组，输出发行机构编号、行业代码、持仓笔数、理财资金投入金额与该机构理财投入合计，仅保留穿透深度至少两层的持仓，按投入金额降序、行业代码升序排列。",
        sql="""WITH dlq AS (
    SELECT ca.borrower_party_id AS party_id, SUM(d.overdue_principal) AS overdue,
       SUM(d.overdue_interest) AS overdue_int
    FROM delinquency_snapshot d
    JOIN loan_drawdown ld ON ld.loan_id = d.loan_id
    JOIN credit_agreement ca ON ca.agreement_id = ld.agreement_id
    GROUP BY ca.borrower_party_id
)
SELECT wp.issuer_institution_id AS issuer_inst,
       ma.industry_code AS industry_code,
       COUNT(*) AS holding_count,
       ROUND(SUM(ph.converted_amount), 2) AS funded_amount,
       ROUND(SUM(ph.converted_amount) OVER (PARTITION BY wp.issuer_institution_id), 2) AS issuer_funded
FROM product_holding_snapshot ph
JOIN wealth_product wp ON wp.product_id = ph.product_id
JOIN managed_asset ma ON ma.asset_id = ph.asset_id
JOIN dlq ON dlq.party_id = ma.obligor_party_id AND dlq.overdue > 0
WHERE ph.lookthrough_depth >= 2
GROUP BY wp.issuer_institution_id, ma.industry_code
ORDER BY funded_amount DESC, ma.industry_code;"""),
    dict(
        id="BRB2-0486", difficulty="medium", features=[],
        penalty_law_zh="《商业银行法》关于审慎经营、真实准确报送监管指标数据的义务及监管统计数据质量管理办法。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其审慎监管指标台账核查尚未完成，风险监测存在盲区与漏报。",
        question="按机构测算审慎监管指标台账中带异常标记的指标记录金额占该机构净资本的比重，并与总资产比对，输出机构名称、异常记录数、异常指标金额、净资本、总资产与占净资本比重（百分比，保留四位小数），仅保留异常记录数不少于 8 条的机构，按比重降序排列（机构财务数据存放在财务快照表中，其主体编号为 PTY- 加机构编号）。",
        sql="""SELECT i.institution_name,
       COUNT(*) AS exception_cnt,
       ROUND(SUM(q.amount_value), 2) AS exception_amount,
       cs.net_capital,
       f.total_assets,
       ROUND(SUM(q.amount_value) * 100.0 / cs.net_capital, 4) AS pct_of_capital
FROM prudential_metric_snapshot_v3 q
JOIN institution i ON i.institution_id = q.institution_id
JOIN capital_snapshot cs ON cs.institution_id = i.institution_id
JOIN financial_snapshot f ON f.party_id = 'PTY-' || i.institution_id
WHERE q.exception_flag = 1
GROUP BY i.institution_id, i.institution_name, cs.net_capital, f.total_assets
HAVING COUNT(*) >= 8
ORDER BY pct_of_capital DESC, i.institution_name;"""),
    dict(
        id="BRB2-0487", difficulty="medium", features=[],
        penalty_law_zh="《银行业监管统计管理暂行办法》关于监管报送事项应按时限如实完成的法定义务，逾期漏报将依法处罚。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人监管报送事项台账尚未完成，存在监管数据漏报、迟报风险。",
        question="测算各机构贷款拨备计提不足的借据规模，并与其监管报送事项中已逾期未完成记录的关联情况进行比对，输出机构名称、监管报送逾期记录数、台账平均金额、拨备不足借据数与拨备缺口金额（保留两位小数），仅保留逾期记录数不少于 25 条的机构，按拨备缺口金额降序排列。",
        sql="""WITH prov AS (
    SELECT a.institution_id AS institution_id,
           COUNT(DISTINCT ld.loan_id) AS shortfall_loans,
           ROUND(SUM(ps.required_amount - ps.recognized_amount), 2) AS shortfall_amount
    FROM provision_snapshot ps
    JOIN loan_drawdown ld ON ld.loan_id = ps.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    WHERE ps.recognized_amount < ps.required_amount
    GROUP BY a.institution_id
)
SELECT i.institution_name,
       COUNT(*) AS overdue_submissions,
       ROUND(AVG(r.amount_value), 2) AS avg_ledger_amount,
       p.shortfall_loans,
       p.shortfall_amount
FROM regulatory_submission_event_v3 r
JOIN institution i ON i.institution_id = r.institution_id
JOIN prov p ON p.institution_id = r.institution_id
WHERE r.completion_date IS NULL OR r.completion_date > r.deadline_date
GROUP BY i.institution_name, p.shortfall_loans, p.shortfall_amount
HAVING COUNT(*) >= 25
ORDER BY p.shortfall_amount DESC, i.institution_name;"""),
    dict(
        id="BRB2-0488", difficulty="hard", features=[],
        penalty_law_zh="《商业银行授信工作尽职指引》关于授信后管理、风险监测与整改事项应按期完成的尽职要求。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其信贷控制核查逾期末完成，授信后管理与风险监测流于形式。",
        question="测算各机构贷款管控台账中未按期完成记录，与其名下还款计划发生逾期的借据数量及逾期应还本金合计相勾稽，输出机构名称、管控台账逾期记录数、管控记录金额、逾期分期借据数与逾期应还本金合计，仅保留逾期记录数不少于 25 条的机构，按逾期应还本金合计降序排列。",
        sql="""WITH instal AS (
    SELECT a.institution_id AS institution_id,
           COUNT(DISTINCT rs.loan_id) AS overdue_loans,
           ROUND(SUM(CASE WHEN rs.status = 'OVERDUE' THEN rs.principal_due ELSE 0 END), 2) AS overdue_principal
    FROM repayment_schedule rs
    JOIN loan_drawdown ld ON ld.loan_id = rs.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    WHERE rs.status = 'OVERDUE'
    GROUP BY a.institution_id
)
SELECT i.institution_name, COUNT(*) AS overdue_control,
       ROUND(SUM(r.amount_value), 2) AS control_amount,
       iv.overdue_loans, iv.overdue_principal
FROM lending_control_event_v3 r
JOIN institution i ON i.institution_id = r.institution_id
JOIN instal iv ON iv.institution_id = r.institution_id
WHERE r.completion_date IS NULL OR r.completion_date > r.deadline_date
GROUP BY i.institution_name, iv.overdue_loans, iv.overdue_principal
HAVING COUNT(*) >= 25
ORDER BY iv.overdue_principal DESC, i.institution_name;"""),
    dict(
        id="BRB2-0489", difficulty="medium", features=[],
        penalty_law_zh="《商业银行公司治理指引》关于公司治理控制事项应按规定时限完成核验的监管要求。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其公司治理控制核查尚未完成，公司治理风险监测不到位。",
        question="按机构统计授信额度批复总数，并关联公司治理控制台账计算各机构携带异常标记记录的金额合计（保留两位小数）与全部台账记录的平均观测比值（保留四位小数），仅保留治理异常记录数不少于 5 条的机构，输出机构名称、授信额度批复总数、治理异常记录金额与平均观测比值，按治理异常记录金额降序、机构名称升序排列（平均观测比值取台账中的比率字段，而非观测值字段）。",
        sql="""WITH fac AS (
    SELECT institution_id AS institution_id, COUNT(*) AS active_facilities
    FROM credit_facility
    GROUP BY institution_id
)
SELECT i.institution_name, f.active_facilities,
       ROUND(SUM(CASE WHEN r.exception_flag = 1 THEN r.amount_value ELSE 0 END), 2) AS except_amount,
       ROUND(AVG(r.ratio_value), 4) AS avg_ratio
FROM governance_control_record_v3 r
JOIN institution i ON i.institution_id = r.institution_id
JOIN fac f ON f.institution_id = i.institution_id
GROUP BY i.institution_id, i.institution_name, f.active_facilities
HAVING SUM(CASE WHEN r.exception_flag = 1 THEN 1 ELSE 0 END) >= 5
ORDER BY except_amount DESC, i.institution_name;"""),
    dict(
        id="BRB2-0490", difficulty="medium", features=[],
        penalty_law_zh="《商业银行与内部人和股东关联交易管理办法》关于关联交易台账核查、关联风险监测应按期完成的监管要求。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其关联交易核查尚未完成，关联风险防控存在漏洞。",
        question="排查关联交易台账中携带异常标记的客户，关联其作为源主体的关联关系记录统计不重复的目标主体数、关系种类数以及关系类型中文名称非“非关联方”的关联关系笔数，输出客户名称、关联目标主体数、关系种类数与非“非关联方”关系笔数，按关联目标主体数降序、关系种类数降序、客户名称升序排列。",
        sql="""SELECT p.display_name,
       COUNT(DISTINCT pr.target_party_id) AS counterparties,
       COUNT(DISTINCT pr.relation_type) AS relation_kinds,
       SUM(CASE WHEN rt.relation_name_zh <> '非关联方' THEN 1 ELSE 0 END) AS vetted_edges
FROM related_transaction_record_v3 r
JOIN party p ON p.party_id = r.subject_id
JOIN party_relation pr ON pr.source_party_id = r.subject_id
JOIN relation_type_catalog rt ON rt.relation_type = pr.relation_type
WHERE r.exception_flag = 1
GROUP BY p.party_id, p.display_name
ORDER BY counterparties DESC, relation_kinds DESC, p.display_name;"""),
    dict(
        id="BRB2-0491", difficulty="medium", features=[],
        penalty_law_zh="《存款保险条例》关于投保机构费用缴纳与存款信息核验按时完成的法定义务。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其存款保险记录核验尚未完成，存款保险信息管理不规范。",
        question="排查存款保险核查台账中未按期完成的记录，并关联该客户作为主账户持有人在结算账户上的定期存款金额，输出客户名称、定期存款笔数、定期存款本金合计与被核查记录金额合计，按定期存款本金合计降序、客户名称升序排列。",
        sql="""WITH dep AS (
    SELECT ah.party_id AS party_id,
           COUNT(*) AS term_count,
           ROUND(SUM(td.opening_principal), 2) AS term_principal
    FROM term_deposit td
    JOIN account a ON a.account_id = td.account_id
    JOIN account_holder ah ON ah.account_id = a.account_id AND ah.holder_role = 'PRIMARY'
    GROUP BY ah.party_id
)
SELECT p.display_name, d.term_count, d.term_principal,
       ROUND(SUM(r.amount_value), 2) AS protect_amount
FROM deposit_protection_record_v3 r
JOIN party p ON p.party_id = r.subject_id
JOIN dep d ON d.party_id = r.subject_id
WHERE r.completion_date IS NULL OR r.completion_date > r.deadline_date
GROUP BY p.party_id, p.display_name, d.term_count, d.term_principal
ORDER BY d.term_principal DESC, p.display_name;"""),
    dict(
        id="BRB2-0492", difficulty="medium", features=[],
        penalty_law_zh="《金融机构客户身份识别和客户身份资料及交易记录保存管理办法》关于客户尽职调查应按期完成的义务。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其客户尽职调查尚未完成，客户身份识别不到位。",
        question="筛查客户尽职调查台账中带异常标记的记录，并关联该客户在结算与储蓄账户上的存款余额，计算其被核查记录的平均观测值，输出客户名称、存款余额、尽职调查记录数与平均观测值，按存款余额降序、客户名称升序排列。",
        sql="""WITH bal AS (
    SELECT ah.party_id AS party_id,
           ROUND(SUM(ab.ledger_balance), 2) AS deposit_balance
    FROM account_balance_snapshot ab
    JOIN account a ON a.account_id = ab.account_id
    JOIN account_holder ah ON ah.account_id = a.account_id AND ah.holder_role = 'PRIMARY'
    WHERE a.account_kind IN ('SAVINGS', 'CURRENT')
    GROUP BY ah.party_id
)
SELECT p.display_name, b.deposit_balance,
       COUNT(*) AS cdd_records,
       ROUND(AVG(r.observed_value), 4) AS avg_obs
FROM customer_due_diligence_event_v3 r
JOIN party p ON p.party_id = r.subject_id
JOIN bal b ON b.party_id = r.subject_id
WHERE r.exception_flag = 1
GROUP BY p.party_id, p.display_name, b.deposit_balance
ORDER BY b.deposit_balance DESC, p.display_name;"""),
    dict(
        id="BRB2-0493", difficulty="hard", features=[],
        penalty_law_zh="《商业银行操作风险管理指引》关于操作风险事件识别、报告与整改应按期完成的监管要求。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其操作风险事件处置尚未完成，操作风险管控存在缺口。",
        question="分别按机构统计结算账户所属机构下处于有效状态的支付卡发卡张数与持卡客户数，以及操作风险台账中处于有效状态的记录数与携带异常标记记录的金额合计（保留两位小数），仅保留操作风险有效记录数不少于 43 条的机构，关联输出机构名称、有效发卡张数、持卡客户数、操作风险异常金额与操作风险有效记录数，按操作风险异常金额降序、机构名称升序排列。",
        sql="""WITH card_stat AS (
    SELECT a.institution_id,
           COUNT(DISTINCT pc.card_id) AS active_cards,
           COUNT(DISTINCT pc.holder_party_id) AS card_holders
    FROM payment_card pc
    JOIN account a ON a.account_id = pc.settlement_account_id
    WHERE pc.status = 'ACTIVE'
    GROUP BY a.institution_id
),
op_stat AS (
    SELECT institution_id,
           COUNT(*) AS active_op_records,
           ROUND(SUM(CASE WHEN exception_flag = 1 THEN amount_value ELSE 0 END), 2) AS except_amount
    FROM operational_risk_event_v3
    WHERE status_code = 'ACTIVE'
    GROUP BY institution_id
    HAVING COUNT(*) >= 43
)
SELECT i.institution_name, c.active_cards, c.card_holders,
       o.except_amount, o.active_op_records
FROM op_stat o
JOIN card_stat c ON c.institution_id = o.institution_id
JOIN institution i ON i.institution_id = o.institution_id
ORDER BY o.except_amount DESC, i.institution_name;"""),
    dict(
        id="BRB2-0494", difficulty="hard", features=[],
        penalty_law_zh="《中华人民共和国数据安全法》及《银行业金融机构数据安全管理办法》关于数据安全事件整改应按期完成的法定义务。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其数据安全事件整改尚未完成，数据安全管理不到位。",
        question="针对数据安全事件台账中尚未完成或晚于截止日期完成的逾期记录，关联被核查对公客户的行业归属与经营状态，按行业与经营状态汇总携带异常标记的金额合计（保留两位小数）与平均发生笔数（保留两位小数），仅保留逾期记录数不少于 8 条的行业与经营状态组合，输出行业中文名称、经营状态、异常金额合计与平均发生笔数，按异常金额合计降序、行业中文名称升序排列。",
        sql="""SELECT s.sector_name_zh AS sector_name,
       o.operating_status AS operating_status,
       ROUND(SUM(CASE WHEN r.exception_flag = 1 THEN r.amount_value ELSE 0 END), 2) AS except_amount,
       ROUND(AVG(r.count_value), 2) AS avg_count
FROM data_security_event_v3 r
JOIN organization_profile o ON o.party_id = r.subject_id
JOIN industry_sector s ON s.sector_code = o.industry_code
WHERE r.completion_date IS NULL OR r.completion_date > r.deadline_date
GROUP BY s.sector_code, s.sector_name_zh, o.operating_status
HAVING COUNT(*) >= 8
ORDER BY except_amount DESC, s.sector_name_zh;"""),
    dict(
        id="BRB2-0495", difficulty="medium", features=[],
        penalty_law_zh="《银行业消费者权益保护管理办法》及销售适当性规定关于产品行为核查按期完成、违规将受到处罚。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其产品行为事件核查尚未完成，产品合规管理存在隐患。",
        question="测算各发行机构产品销售行为台账中携带异常标记记录的平均比值，并与其名下处于在售状态的理财产品数量及实际募集金额关联，输出机构名称、在售产品数、实际募集合计、产品行为记录数与平均比值，仅保留异常记录数不少于 2 条的机构，按实际募集合计降序排列（平均比值保留四位小数）。",
        sql="""WITH prod AS (
    SELECT issuer_institution_id AS institution_id,
           COUNT(*) AS product_cnt,
           ROUND(SUM(actual_raise_amount), 2) AS raised
    FROM wealth_product
    WHERE status = 'ON_SALE'
    GROUP BY issuer_institution_id
)
SELECT i.institution_name, pr.product_cnt, pr.raised,
       COUNT(*) AS conduct_records,
       ROUND(AVG(r.ratio_value), 4) AS avg_ratio
FROM product_conduct_event_v3 r
JOIN institution i ON i.institution_id = r.institution_id
JOIN prod pr ON pr.institution_id = i.institution_id
WHERE r.exception_flag = 1
GROUP BY i.institution_id, i.institution_name, pr.product_cnt, pr.raised
HAVING COUNT(*) >= 2
ORDER BY pr.raised DESC, i.institution_name;"""),
    dict(
        id="BRB2-0496", difficulty="medium", features=[],
        penalty_law_zh="《金融机构大额交易和可疑交易报告管理办法》关于实际受益人识别应按期完成的义务。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其受益人识别尚未完成，客户受益所有权识别缺失。",
        question="按敞口集团及其类型归并受益所有人核查台账中有效记录的观测值，输出集团名称、敞口类型、集团成员数、带异常标记的观测值合计与台账记录数，仅保留集团成员数不少于 3 户的集团，按集团成员数降序、集团名称升序排列。",
        sql="""SELECT g.group_name, t.name_zh AS group_kind,
       COUNT(DISTINCT egm.party_id) AS member_cnt,
       ROUND(SUM(CASE WHEN r.exception_flag = 1 THEN r.observed_value ELSE 0 END), 4) AS except_obs,
       COUNT(*) AS ubo_records
FROM beneficial_owner_record_v3 r
JOIN exposure_group_member egm ON egm.party_id = r.subject_id
JOIN exposure_group g ON g.exposure_group_id = egm.exposure_group_id
JOIN exposure_group_type_catalog t ON t.group_type = g.group_type
WHERE r.status_code = 'ACTIVE'
GROUP BY g.exposure_group_id, g.group_name, t.group_type, t.name_zh
HAVING COUNT(DISTINCT egm.party_id) >= 3
ORDER BY member_cnt DESC, g.group_name;"""),
    dict(
        id="BRB2-0497", difficulty="medium", features=[],
        penalty_law_zh="《中华人民共和国商业银行法》及行政许可规定关于金融牌照资质核验应按期完成、无资质经营依法处罚。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人有牌照资质核验尚未完成，主体资质管理存在风险。",
        question="先通过员工表与营业单元表按机构汇总下辖营业单元数与员工人数，再与许可管理台账中尚未完成或晚于截止日期完成的逾期记录按机构关联，统计各机构涉及的不重复被核查主体数与平均观测值（保留四位小数），仅保留逾期台账记录数不少于 25 条的机构，输出机构名称、被核查主体数、下辖营业单元数、员工人数与平均观测值，按被核查主体数降序、机构名称升序排列。",
        sql="""WITH staff_stat AS (
    SELECT ou.institution_id AS institution_id,
           COUNT(DISTINCT ou.org_unit_id) AS unit_cnt,
           COUNT(DISTINCT s.staff_id) AS total_staff
    FROM staff_member s
    JOIN organization_unit ou ON ou.org_unit_id = s.home_org_unit_id
    GROUP BY ou.institution_id
)
SELECT i.institution_name,
       COUNT(DISTINCT r.subject_id) AS licensed_people,
       ss.unit_cnt,
       ss.total_staff,
       ROUND(AVG(r.observed_value), 4) AS avg_obs
FROM license_record_v3 r
JOIN institution i ON i.institution_id = r.institution_id
JOIN staff_stat ss ON ss.institution_id = r.institution_id
WHERE r.completion_date IS NULL OR r.completion_date > r.deadline_date
GROUP BY i.institution_id, i.institution_name, ss.unit_cnt, ss.total_staff
HAVING COUNT(*) >= 25
ORDER BY licensed_people DESC, i.institution_name;"""),
    dict(
        id="BRB2-0498", difficulty="medium", features=[],
        penalty_law_zh="《商业银行托管业务管理办法》关于托管运营事项按期完成核验的监管要求。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其托管运营事项尚未完成核验，托管业务管理不规范。",
        question="分别按原始发起机构统计受托管理底层资产的总数与发行金额合计（保留两位小数），以及资产托管台账中处于有效状态的记录数与携带异常标记记录的金额合计（保留两位小数），仅保留资产托管有效记录中携带异常标记记录数不少于 2 条的机构，关联输出机构名称、底层资产数、发行金额合计、托管有效记录数与异常金额合计，按发行金额合计降序、机构名称升序排列。",
        sql="""WITH asset AS (
    SELECT originator_institution_id AS institution_id,
           COUNT(*) AS asset_cnt,
           ROUND(SUM(issued_amount), 2) AS issued
    FROM managed_asset
    GROUP BY originator_institution_id
),
custody AS (
    SELECT institution_id,
           COUNT(*) AS custody_records,
           ROUND(SUM(CASE WHEN exception_flag = 1 THEN amount_value ELSE 0 END), 2) AS except_amount
    FROM custody_operation_event_v3
    WHERE status_code = 'ACTIVE'
    GROUP BY institution_id
    HAVING SUM(CASE WHEN exception_flag = 1 THEN 1 ELSE 0 END) >= 2
)
SELECT i.institution_name, a.asset_cnt, a.issued,
       c.custody_records, c.except_amount
FROM asset a
JOIN institution i ON i.institution_id = a.institution_id
JOIN custody c ON c.institution_id = i.institution_id
ORDER BY a.issued DESC, i.institution_name;"""),
    dict(
        id="BRB2-0499", difficulty="medium", features=[],
        penalty_law_zh="《外汇管理条例》关于外汇业务合规操作与业务事项按期核验的监管要求。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其外汇业务核验尚未完成，外汇业务合规管理存在漏洞。",
        question="测算各机构结售汇台账中有效记录的平均比值，并与其名下贷款发放对应的受托支付指令笔数及受托金额勾稽，输出机构名称、支付指令笔数、受托支付金额合计、结售汇记录数与平均比值，仅保留结售汇记录数不少于 41 条的机构，按受托支付金额合计降序排列。",
        sql="""WITH pi AS (
    SELECT a.institution_id AS institution_id,
           COUNT(*) AS inst_cnt,
           ROUND(SUM(CASE WHEN pm.payment_mode_name_zh = '受托支付' THEN pi.instruction_amount ELSE 0 END), 2) AS entrusted
    FROM payment_instruction pi
    JOIN payment_mode_catalog pm ON pm.payment_mode = pi.payment_mode
    JOIN loan_drawdown ld ON ld.loan_id = pi.loan_id
    JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
    GROUP BY a.institution_id
)
SELECT i.institution_name, p.inst_cnt, p.entrusted,
       COUNT(*) AS fx_records,
       ROUND(AVG(r.ratio_value), 4) AS avg_ratio
FROM fx_business_event_v3 r
JOIN institution i ON i.institution_id = r.institution_id
JOIN pi p ON p.institution_id = r.institution_id
WHERE r.status_code = 'ACTIVE'
GROUP BY i.institution_id, i.institution_name, p.inst_cnt, p.entrusted
HAVING COUNT(*) >= 41
ORDER BY p.entrusted DESC, i.institution_name;"""),
    dict(
        id="BRB2-0500", difficulty="hard", features=[],
        penalty_law_zh="《关于规范银行业金融机构人工智能应用的通知》关于人工智能系统风险核查按期完成的监管要求。",
        penalty_fact_zh="识别出名下有逾期借据的对公借款人其人工智能系统核查尚未完成，自动化风险决策缺乏人工复核支撑。",
        question="将人工智能系统应用台账与监管事项编码表及逾期借据表进行交叉核验：找出名下借据在逾期快照中存在记录、同时在人工智能系统应用台账中存在未完成整改（完成日期为空）记录的借款客户，按机构与监管事项规则大类汇总涉及的不重复逾期借款人户数与台账涉案金额合计（保留两位小数），输出机构名称、监管事项规则大类、逾期借款人户数与台账金额合计，按台账金额合计降序、机构名称升序排列。",
        sql="""WITH overdue_borrowers AS (
  SELECT DISTINCT a.borrower_party_id
  FROM delinquency_snapshot d
  JOIN loan_drawdown ld ON ld.loan_id = d.loan_id
  JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
)
SELECT i.institution_name, rec.rule_family,
       COUNT(DISTINCT r.subject_id) AS overdue_party_cnt,
       ROUND(SUM(r.amount_value), 2) AS total_ledger_amt
FROM ai_system_record_v3 r
JOIN regulatory_event_catalog rec ON rec.event_code = r.event_code
JOIN overdue_borrowers ob ON ob.borrower_party_id = r.subject_id
JOIN institution i ON i.institution_id = r.institution_id
WHERE r.completion_date IS NULL
GROUP BY i.institution_id, i.institution_name, rec.rule_family
ORDER BY total_ledger_amt DESC, i.institution_name;"""),
]

# Synchronize declared feature tags with actual SQL AST operators
import re as _re  # noqa: E402
def _infer_sql_features(sql: str) -> list[str]:
    u = sql.upper()
    feats = set()
    if _re.search(r"\bWITH\s+\w+\s+AS\s*\(", u): feats.add("CTE")
    if _re.search(r"\bOVER\s*\(", u): feats.add("WINDOW")
    if _re.search(r"\bNTILE\s*\(", u): feats.add("NTILE")
    if _re.search(r"\bLAG\s*\(|\bLEAD\s*\(", u): feats.add("LAG")
    if _re.search(r"\bCASE\s+WHEN\b", u): feats.add("CASE")
    if _re.search(r"\bGROUP\s+BY\b", u): feats.add("GROUP_BY")
    if _re.search(r"\bHAVING\b", u): feats.add("HAVING")
    if _re.search(r"\bORDER\s+BY\b", u): feats.add("ORDER_BY")
    if _re.search(r"\bLIMIT\s+\d+", u): feats.add("LIMIT")
    if _re.search(r"\bUNION\b", u): feats.add("UNION")
    if _re.search(r"\bINTERSECT\b", u): feats.add("INTERSECT")
    if _re.search(r"\bEXCEPT\b", u): feats.add("EXCEPT")
    if _re.search(r"\bNOT\s+EXISTS\s*\(", u): feats.add("NOT_EXISTS")
    elif _re.search(r"\bEXISTS\s*\(", u): feats.add("EXISTS")
    if _re.search(r"\bJOIN\b", u): feats.add("JOIN")
    if _re.search(r"\bSUM\s*\(", u): feats.add("SUM")
    if _re.search(r"\bAVG\s*\(", u): feats.add("AVG")
    if _re.search(r"\bCOUNT\s*\(", u): feats.add("COUNT")
    if _re.search(r"\bCOALESCE\s*\(|\bIFNULL\s*\(", u): feats.add("COALESCE")
    if _re.search(r"\bIS\s+(?:NOT\s+)?NULL\b", u): feats.add("IS_NULL")
    if _re.search(r"\bLIKE\b", u): feats.add("LIKE")
    if _re.search(r"\bIN\s*\(", u): feats.add("IN")
    if _re.search(r"\bJULIANDAY\s*\(", u): feats.add("DATE_MATH")
    if "/" in u: feats.add("RATIO")
    if _re.search(r"\bWHERE\b", u): feats.add("FILTER")
    ctes = {m.group(1).lower() for m in _re.finditer(r"(?:WITH|,)\s*(\w+)\s+AS\s*\(", sql, _re.I)}
    tabs = [
        m.group(1).lower()
        for m in _re.finditer(r"\b(?:FROM|JOIN)\s+([a-zA-Z_]\w*)", sql, _re.I)
        if m.group(1).upper() not in ("SELECT", "WHERE") and m.group(1).lower() not in ctes
    ]
    if len(tabs) != len(set(tabs)): feats.add("SELF_JOIN")
    return sorted(feats)

for _q in ITEMS:
    _q["features"] = _infer_sql_features(_q["sql"])

# --- Parallel Zero-Leakage English Questions (question_en) ---
_QUESTIONS_EN = {
  "BRB2-0001": "List all loan drawdown numbers and their classification dates where the risk classification level is \"substandard\", sorted in ascending order by loan drawdown number.",
  "BRB2-0002": "List the loan drawdown numbers, overdue days, and overdue principal amounts for loan drawdowns where the principal overdue days exceed 360 days, sorted by overdue days in descending order.",
  "BRB2-0003": "List the deposit account numbers and book balances for all deposit accounts whose book balance exceeds 5 million CNY, sorted by balance from highest to lowest.",
  "BRB2-0004": "List all account numbers and their account-opening institution names for accounts in a \"dormant\" status.",
  "BRB2-0005": "List the corporate customer IDs and customer names where the registered industry is \"real estate\", sorted by customer ID in ascending order.",
  "BRB2-0006": "List the wealth management product number, product name, and planned fundraising amount for products with risk level R5 that are currently still in an active sales status.",
  "BRB2-0007": "List all write-off loan drawdown numbers and their loan drawdown amounts.",
  "BRB2-0008": "List the transaction ID, business date, and amount for cash withdrawal transactions with an amount exceeding 5 million CNY, sorted by amount in descending order.",
  "BRB2-0009": "List the product numbers, establishment dates, and actual termination dates of all terminated wealth management products.",
  "BRB2-0010": "List all credit agreement numbers and their contract amounts where the guarantee method is \"credit\".",
  "BRB2-0011": "List the collateral number, collateral name, and their most recent appraised value, sorted by appraised value in descending order.",
  "BRB2-0012": "List the customer IDs and annual income of individual customers whose annual income exceeds 1 million CNY, sorted by annual income in descending order.",
  "BRB2-0013": "List the card number, issuance date, and expiration date of all credit cards, sorted by issuance date in ascending order.",
  "BRB2-0014": "List the corporate customer numbers, names, and operating statuses of customers whose registered region is the same as the region where Shanghai Branch ('上海分行') is located, sorted in ascending order by customer number.",
  "BRB2-0015": "List all credit agreements that have matured, showing the agreement number, maturity date, and contract amount, sorted by maturity date in ascending order.",
  "BRB2-0016": "Count the number of loan drawdowns under each institution, and output the institution name and the drawdown count, sorted by the count in descending order.",
  "BRB2-0017": "Count the number of accounts opened under each business unit, and output the business unit ID, business unit name, and account count, sorted by account count in descending order.",
  "BRB2-0018": "Count the number of corporate clients in each industry, output the industry name in Chinese and the client count, and sort by client count in descending order.",
  "BRB2-0019": "Join the employee position assignment table with the business unit where each employee is located, count the number of credit agreements for which that employee's business unit serves as the handling management unit, output the employee ID and the agreement count, take the top 10, sorted by agreement count in descending order.",
  "BRB2-0020": "For each institution, calculate the total loan drawdown amount, and output the institution name and the total drawdown amount, sorted by the total amount in descending order.",
  "BRB2-0021": "For each loan product category, count the number of loan drawdowns and calculate the average loan disbursement amount. Output the product category Chinese name, the count, and the average loan disbursement amount, sorted by the count in descending order.",
  "BRB2-0022": "For each industry, calculate the total credit contract amount for corporate customers, and output the industry name in Chinese and the total contract amount, sorted in descending order by the total amount.",
  "BRB2-0023": "Count the number of accounts held by each customer, and output the customer ID, customer name, and account count, keeping only customers who hold 3 or more accounts, sorted by account count in descending order.",
  "BRB2-0024": "Count the number of credit agreements under each guarantee method, output the guarantee method code and the agreement count, and sort by the agreement count in descending order.",
  "BRB2-0025": "For each wealth management product, calculate the total market value of holdings in the underlying assets. Output the product name and the total market value of holdings, take the top 10, and sort by the total amount in descending order.",
  "BRB2-0026": "Group the related-party relationship records by the business organizational unit to which the source client in the relationship belongs, and for each unit, output the unit number, unit name, and the count of related-party relationships, sorted in descending order by the count.",
  "BRB2-0027": "List the net capital and risk-weighted assets for each institution, and output the institution name, net capital, and risk-weighted assets, sorted by net capital in descending order.",
  "BRB2-0028": "For each borrower's registered industry, calculate the total outstanding loan balance by industry. Output the industry name in Chinese and the total outstanding loan principal balance, sorted in descending order by the total balance.",
  "BRB2-0029": "For each credit card, count the number of card consumption transactions on the card's linked settlement account. Output the card number and the transaction count, sorted by the count in descending order.",
  "BRB2-0030": "For each institution, calculate the total deposit balance (based on the book balance of savings-type accounts). Output the institution name and the total deposit balance, sorted in descending order by the total amount.",
  "BRB2-0031": "List the total outstanding loan principal balance for each institution, showing the institution name and the total balance, and keep only those institutions whose total balance exceeds 1 billion CNY, sorted by the total balance in descending order.",
  "BRB2-0032": "For each institution, calculate the average principal overdue days (considering only loan drawdowns that have an overdue ledger record), and output the institution name and the average overdue days. Keep only institutions whose average overdue days exceed 90 days, and sort the results by the average overdue days in descending order.",
  "BRB2-0033": "Calculate the non-performing loan ratio for each institution (non-performing loan principal balance ÷ total loan principal balance, where non-performing is defined as substandard, doubtful, or loss in the five-category loan classification), and output the institution name and the non-performing loan ratio, sorted by the ratio in descending order.",
  "BRB2-0034": "Calculate the provision coverage ratio for each institution (total provision amount set aside ÷ total required provision amount), and output the institution name and provision coverage ratio, keeping only institutions with a provision coverage ratio below 1.5, sorted by provision coverage ratio in ascending order.",
  "BRB2-0035": "Calculate the number of loan drawdowns for which the provision already accrued is lower than the required provision amount, for each institution. Output the institution name and the number of drawdowns, keeping only institutions with a count of at least 100 drawdowns, sorted by the count in descending order.",
  "BRB2-0036": "Calculate the ratio of each corporate customer's total outstanding loan principal to the capital net amount of its affiliated institution, and output the customer ID, customer name, total outstanding balance, institution name, and this ratio, taking the top 10 customers with the highest ratios, sorted in descending order by the ratio.",
  "BRB2-0037": "For each exposure group, calculate the ratio of the group's total credit exposure amount (summed as the outstanding loan principal balances of the group's member entities at this bank) to the net capital of the group's lead institution. Output the group number, group name, exposure amount, and the exposure-to-net-capital ratio, sorted in descending order by the ratio.",
  "BRB2-0038": "Calculate the loan-to-deposit ratio for each institution (total loan principal balance divided by total savings account book balance), and output the institution name and the loan-to-deposit ratio, sorted by the loan-to-deposit ratio in descending order.",
  "BRB2-0039": "Calculate the deviation ratio of principal balance of loans overdue by more than 90 days to the principal balance of non-performing loans (principal balance overdue by more than 90 days ÷ non-performing loan principal balance) for each institution, and output the institution name, balance overdue by more than 90 days, non-performing balance, and deviation ratio, sorted by deviation ratio in descending order.",
  "BRB2-0040": "For each institution, count the total number of cash transactions (sum of cash deposits and cash withdrawals), and output the institution name and the transaction count, sorted by the count in descending order.",
  "BRB2-0041": "For each account, calculate the total amount of cash withdrawals. Output the account number and the total amount, keeping only accounts with a total amount exceeding 10 million CNY. Sort by the total amount in descending order and take the top 20.",
  "BRB2-0042": "Calculate the proportion of entrusted payment amount for each institution (total payment instruction amount under entrusted payment method ÷ total payment instruction amount for all payment instructions), output the institution name and the proportion, sorted by the proportion in ascending order.",
  "BRB2-0043": "For each industry classified by borrower registration, calculate the proportion of non-performing loans (classified as substandard, doubtful, or loss) to total loans in that industry. Output the industry name, total loan count, non-performing loan count, and non-performing loan ratio, keeping only industries with at least 20 loans, sorted by the ratio in descending order.",
  "BRB2-0044": "For each customer, calculate the total credit contract amount across all institutions. Output the customer ID, customer name, and total contract amount, taking the top 15 records, sorted in descending order by the total amount.",
  "BRB2-0045": "Find customers who have obtained credit from two or more institutions. Output the customer ID, customer name, and the number of credit institutions, sorted in descending order by the number of institutions.",
  "BRB2-0046": "For each loan product category, output the Chinese name of the product, the number of loan drawdowns, and the average contract interest rate. Keep only those product categories with at least 50 drawdowns, and sort the results in descending order by the average interest rate.",
  "BRB2-0047": "For each institution, calculate the total actual fundraising amount and the total planned fundraising amount of wealth management products. Output the institution name, total actual fundraising amount, total planned fundraising amount, and the fundraising completion rate (actual divided by planned), sorted by the fundraising completion rate in ascending order.",
  "BRB2-0048": "Count the number of wealth management products and the average management fee rate for each risk level, and output the risk level, product count, and average management fee rate, sorted by risk level in ascending order.",
  "BRB2-0049": "Calculate the total outstanding guaranteed balance (sum of guarantee commitment amounts) for each guarantor's current valid guarantee commitments (status is valid). Output the guarantor ID, guarantor name, and the total outstanding guaranteed balance. Only include guarantors with a total outstanding guaranteed balance exceeding 500 million CNY, sorted by the total amount in descending order.",
  "BRB2-0050": "For each collateral type, calculate the total appraised value (using the most recent appraisal for each collateral item), and output the collateral type, the number of collateral items, and the total appraised value, sorted in descending order by the total appraised value.",
  "BRB2-0051": "Calculate the loan-to-deposit ratio regulatory gap for each institution: use total loan principal balance ÷ total savings book balance as the loan-to-deposit ratio, output the institution name, the difference between the loan-to-deposit ratio and the regulatory cap of 0.75, keep only institutions with a loan-to-deposit ratio exceeding 0.75, and sort in descending order by the loan-to-deposit ratio.",
  "BRB2-0052": "For each channel, count the number of transactions and sum the transaction amounts. Output the channel code, transaction count, and total transaction amount, sorted by total transaction amount in descending order.",
  "BRB2-0053": "For each institution, count the number of overdue unpaid installments in the repayment plan and sum the principal due, outputting the institution name, installment count, and total principal due; keep only institutions with an installment count of at least 150, and sort by total principal due in descending order.",
  "BRB2-0054": "For each industry, count the number of corporate clients whose operating status is not normal (e.g., revoked, abnormal operation). Output the industry Chinese name and the count of clients that are revoked or have abnormal operation, sorted in descending order by the client count.",
  "BRB2-0055": "Calculate the proportion of wealth management funds invested in non-standardized debt assets held by each institution, and output the institution name, the market value of non-standardized holdings, the total market value of holdings, and the non-standardized proportion, sorted in descending order by the non-standardized proportion.",
  "BRB2-0056": "Count the number of cash transactions handled by each relationship manager (employee), output the employee ID and the transaction count, take the top 10, and sort by transaction count in descending order.",
  "BRB2-0057": "List the total credit contract amount obtained at this bank by each related party (where the related party appears as the source entity in the relationship and the relationship type is not \"non-related party\" ('非关联方')), outputting the customer number, customer name, and total contract amount, keeping only customers whose total exceeds 300 million CNY, sorted by total amount in descending order.",
  "BRB2-0058": "For each institution, count the records flagged as abnormal in the data security incident log and sum the associated behavioral observation values. Output the institution name, the record count, and the total observation value, sorted in descending order by the total observation value.",
  "BRB2-0059": "For each institution, count the number of regulatory reporting items that are overdue and incomplete (where the completion date is empty or later than the deadline). Output the institution name and the overdue record count, keeping only institutions with an overdue record count of at least 20, sorted in descending order by the overdue record count.",
  "BRB2-0060": "Calculate the capital adequacy ratio (net capital ÷ risk-weighted assets) for each institution, and output the institution name and capital adequacy ratio, sorted by capital adequacy ratio in ascending order.",
  "BRB2-0061": "Find loan drawdowns with inaccurate five-tier classification: principal overdue days have exceeded 90 days, but the most recent risk classification is still \"normal\" or \"special mention\". Output the drawdown number, overdue days, classification name, and classification date, sorted by overdue days in descending order.",
  "BRB2-0062": "Find loan drawdowns with severely insufficient provision: where the provision already made is less than 80% of the required provision amount. Output the drawdown number, required provision amount, provision already made, and the shortfall amount (required amount minus provision already made), sorted by the shortfall amount in descending order.",
  "BRB2-0063": "For each institution, calculate the total outstanding principal balance of loan drawdowns with insufficient provision accrual, and output the institution name and the insufficient provision loan balance, keeping only institutions whose insufficient provision loan balance exceeds 100 million CNY, sorted by balance in descending order.",
  "BRB2-0064": "Find payment instructions where credit funds were illegally channeled into restricted industries: the payee's industry risk category is \"restricted\" or \"exit\", and the payment instruction has been executed. Output the payment instruction number, loan drawdown number, payee name, industry Chinese name, and instruction amount, sorted by instruction amount in descending order.",
  "BRB2-0065": "Calculate the proportion of payment instruction amounts where the recipient's industry is classified as restricted or exit, relative to the total payment instruction amount for each institution. Output the institution name, non-compliant inflow amount, total instruction amount, and the proportion, sorted by the proportion in descending order.",
  "BRB2-0066": "Identify institutions where single-client loan concentration exceeds the regulatory threshold: calculate the ratio of the total outstanding principal of loans to a single corporate client at the institution divided by the institution's net capital. Output the institution name, client name, total outstanding balance, net capital, and concentration ratio, keeping only records where the concentration ratio exceeds 0.10, sorted by concentration ratio in descending order.",
  "BRB2-0067": "Find institutions whose group customer credit concentration exceeds the limit: calculate the ratio of the total outstanding loan principal of the group's exposed members at the institution to the institution's net capital. Output the institution name, group name, exposure amount, net capital, and concentration ratio, keeping only records where the concentration ratio exceeds 0.15, sorted by concentration ratio in descending order.",
  "BRB2-0068": "Identify cases of maturity mismatch in wealth management products where the underlying asset's maturity date is later than the product's actual termination date. Output the product number, product name, underlying asset number, asset maturity date, and product termination date, sorted in descending order by asset maturity date.",
  "BRB2-0069": "Find wealth management products that hold underlying assets through two or more levels of nested holding (i.e., penetration level reaching two or more tiers), and output the product number, product name, and the count of nested holdings, sorted in descending order by the count.",
  "BRB2-0070": "For each institution, calculate the total market value of underlying assets held through special purpose vehicles (including multi-layer nested vehicles), and output the institution name and the total market value of nested holdings, sorted by market value in descending order.",
  "BRB2-0071": "Identify employees handling their own transactions: for cash transactions, the handler and the counterparty account holder are the same natural person. Output the transaction ID, business date, employee account number (employee ID) of the handler, account number, and amount, sorted by amount in descending order.",
  "BRB2-0072": "Calculate the total amount of cash transactions handled by each employee (relationship manager) as the originator, and output the employee ID, the number of cash transactions, and the total cash transaction amount. Only retain employees whose total amount exceeds 50 million CNY, and sort the results by total amount in descending order.",
  "BRB2-0073": "Find guarantee contracts with insufficient collateral coverage: where the guaranteed claim amount of the guarantee contract is higher than the latest appraised value of its associated collateral. Output the guarantee contract number, guaranteed claim amount, collateral number, latest collateral appraised value, and the shortfall amount, sorted by the shortfall amount in descending order.",
  "BRB2-0074": "Identify mutual guarantee cases: the same entity is both the guarantor of a credit facility and a borrowing customer of the bank. Output the entity ID, name, the number of commitments where it acts as guarantor, and the number of agreements where it acts as borrower, sorted in descending order by the number of guarantee commitments.",
  "BRB2-0075": "Find large cash transactions: single cash transaction amount exceeding 5 million CNY and transaction status is settled. Output transaction number, business date, Chinese name of transaction type, amount, and name of handling institution unit, sorted by amount in descending order.",
  "BRB2-0076": "Find wealth management products whose risk level does not match the investor type: products with a risk level of R4 or R5 but targeting general investors. Output the product number, product name, risk level, and target investor type, sorted in ascending order by product number.",
  "BRB2-0077": "Find credit agreements where the loan fund usage industry differs from the borrower's registered industry. Output the agreement number, borrower name, borrower's registered industry name, agreement's designated industry name, and contract amount, sorted by contract amount in descending order.",
  "BRB2-0078": "Find credit facilities where the agreement has expired but the loan drawdowns remain unsettled: the credit agreement status is \"expired\", and there exists a drawdown under it with a status of \"normal\". Output the agreement number, agreement expiry date, drawdown number, and loan disbursement amount, sorted by agreement expiry date in ascending order.",
  "BRB2-0079": "Identify suspicious large-value transactions in long-dormant accounts: accounts with a status of \"dormant\" that have any single transaction amount exceeding 1 million CNY in 2026. Output the account number, transaction number, business date, and amount, sorted by amount in descending order.",
  "BRB2-0080": "Find cases where loans are still being extended to corporate clients whose business licenses have been revoked or who are listed as operating abnormally: the client's operating status is not \"normal operation,\" yet the client still has loan drawdowns with a status of \"normal.\" Output the client ID, client name, operating status, and the count of normal drawdowns, sorted in descending order by the count of drawdowns.",
  "BRB2-0081": "Find settled fund transfers between related parties: where the primary holders of the paying account and the receiving account have a relationship record that is not classified as \"non-related party.\" Output the transaction ID, business date, amount, paying customer ID, and receiving customer ID, sorted by amount in descending order.",
  "BRB2-0082": "Find customers who are \"overdue on one side while continuing to draw down on the other\": the customer has loan drawdowns with principal overdue days exceeding 90 days, and at the same time, at the same institution, still has other drawdowns with a status of \"normal\". Output the customer ID, customer name, institution name, the count of overdue drawdowns, and the count of other normal drawdowns, sorted in descending order by the count of overdue drawdowns.",
  "BRB2-0083": "Find loan drawdowns that have been extended multiple times: under the same credit agreement, the number of loan drawdowns is at least 3. Output the agreement number, borrower name, and the number of drawdowns, sorted in descending order by the number of drawdowns.",
  "BRB2-0084": "For each institution, count the number of large cash transactions with a single transaction amount exceeding 5 million CNY, and sum the total amount of these transactions. Output the institution name, transaction count, and total amount, keeping only institutions with a transaction count of at least 50, sorted by total amount in descending order.",
  "BRB2-0085": "Find loan drawdowns where the payment instruction uses entrusted payment, but the payee’s industry does not match the target industry specified in the credit agreement, and the payee’s industry risk category is either restricted or exit. Output the drawdown number, borrower name, payee name, payee industry, and instruction amount, sorted by instruction amount in descending order.",
  "BRB2-0086": "Count the number of transactions handled by each customer manager (employee) where the holder of the receiving account belongs to an industry classified as restricted or exit, output the employee ID and the transaction count, take the top 10, sorted by transaction count in descending order.",
  "BRB2-0087": "For each institution, calculate the proportion of the total credit contract amount extended to related parties (where the institution acts as the source entity in the related-party relationship and the relationship type is not \"non-related party\" ('非关联方')) relative to the institution's total credit contract amount for all parties. Output the institution name, the related-party credit amount, the total credit amount, and the proportion, sorted by the proportion in descending order.",
  "BRB2-0088": "Identify cases where collateral has been repeatedly pledged: the same collateral item is validly linked to two or more guarantee contracts. Output the collateral number, collateral name, the total number of linked guarantee contracts, and the total guaranteed claim amount, sorted in descending order by the number of guarantee contracts.",
  "BRB2-0089": "For each institution, calculate the total observed value of records in the credit control matters ledger that were not completed on time (where the completion date is empty or later than the deadline). Output the institution name and the total observed value, take the top 5, and sort by the total value in descending order.",
  "BRB2-0090": "Identify wealth management products whose actual termination date is more than 30 days later than the planned maturity date. Output the product number, product name, planned maturity date, actual termination date, and the number of days delayed, sorted by the number of days delayed in descending order.",
  "BRB2-0091": "Find records in the customer due diligence matters ledger that remain incomplete (completion date is empty) as of the audit reference date 2026-06-30. Output the ledger record number, institution name, matter occurrence date, statutory deadline, and the day difference from the deadline (calculated as 2026-06-30 minus the statutory deadline). Sort by the day difference in descending order and take the top 20 records.",
  "BRB2-0092": "List the total loan disbursement amount for each institution during the first half of 2026 (from January 1, 2026, to June 30, 2026), showing the institution name and the total disbursement amount, and keep only those institutions whose total disbursement amount exceeds 5 billion CNY, sorted by the total amount in descending order.",
  "BRB2-0093": "Find conflict records where the collateral has been released but the guarantee contract is still active. Output the guarantee contract number, collateral number, collateral status, and guarantee contract status, sorted by guarantee contract number in ascending order.",
  "BRB2-0094": "For each institution, among corporate customers, calculate the total credit contract amount by borrower industry, including only industries whose risk category is \"restricted\" or \"exit\". Output the institution name, industry name, and total contract amount, sorted in descending order by the total amount.",
  "BRB2-0095": "Find records where the loan drawdown has been written off, but the guarantee contract associated with its credit agreement is still in an active status. Output the drawdown number, agreement number, guarantee contract number, and guaranteed claim amount, sorted by guaranteed claim amount in descending order.",
  "BRB2-0096": "For each institution, find the loan drawdown with the largest principal balance, and output the institution name, drawdown number, principal balance, and the balance rank within that institution (in case of ties, the one with the smaller drawdown number comes first), sorted by institution name in ascending order.",
  "BRB2-0097": "List the top 3 loan drawdowns by outstanding principal balance for each borrower registered industry, and output the industry Chinese name, drawdown number, principal balance, and the rank within that industry, sorted by industry name ascending and rank ascending.",
  "BRB2-0098": "Calculate, by institution, the proportion of each loan drawdown's principal balance to the total loan principal balance of that institution. Output the institution name, drawdown number, principal balance, and proportion, retaining only drawdowns with a proportion exceeding 0.4%, sorted by proportion in descending order.",
  "BRB2-0099": "For each business date, calculate the daily cumulative amount of cash withdrawal transactions. Output the business date, the daily amount, and the cumulative amount, keeping only the dates up to and including the first date on which the cumulative amount exceeds 500 million CNY, sorted in ascending order by business date.",
  "BRB2-0100": "For each business date, count the number of transactions and use a window function to calculate the change in transaction count compared to the previous day. Output the business date, the transaction count for that day, and the change in count relative to the previous day, sorted by business date in ascending order.",
  "BRB2-0101": "Find the loan drawdowns whose principal balance is higher than the average principal balance of the institution, and output the institution name, drawdown number, principal balance, the institution's average balance, and the amount by which this drawdown exceeds the average, sorted in descending order by the excess amount.",
  "BRB2-0102": "Find credit agreements that have both collateral registration and third-party guarantee commitments (linked through the guaranteed principal claim bridge table), and output the agreement number, borrower name, and contract amount, sorted by contract amount in descending order.",
  "BRB2-0103": "Find guarantee contracts that have only third-party guarantees and no collateral associated with them. Output the guarantee contract number, the guaranteed claim amount, and the number of guarantors, sorted by the guaranteed claim amount in descending order.",
  "BRB2-0104": "Summarize overdue regulatory matters by institution: combine records from the credit control matters ledger and the corporate governance control ledger that were not completed on time (completion date is empty or later than the deadline), and output the institution name, matter source (labeled as \"credit control\" ('信贷控制') and \"governance control\" ('治理控制') respectively), and the count of overdue records, sorted by institution name in ascending order and source in ascending order.",
  "BRB2-0105": "Find customers who have signed credit agreements but have never had any loan drawdown (i.e., none of their credit agreements have any corresponding loan records), and output the customer ID and customer name, sorted by customer ID in ascending order.",
  "BRB2-0106": "Find the account numbers that have both cash withdrawal transactions and transfer transactions, sorted by account number in ascending order.",
  "BRB2-0107": "First, aggregate each customer's total outstanding loan principal balance at this bank. Then, filter to customers whose total balance falls within the top 10% of all corporate customers, defined as having a total balance at or above the 90th percentile of the aggregate total balance across all corporate customers. Output the customer ID, customer name, and total balance, sorted by total balance in descending order.",
  "BRB2-0108": "For each principal overdue days bucket (not overdue ('未逾期'), 1-30 days ('1-30天'), 31-90 days ('31-90天'), 91-180 days ('91-180天'), 181-360 days ('181-360天'), over 360 days ('360天以上')), count the number of loan drawdowns, and output the overdue bucket and the drawdown count, sorted in ascending order by the lower bound of the bucket.",
  "BRB2-0109": "First calculate the non-performing loan ratio for each institution, then output the institutions whose non-performing loan ratio is higher than the median non-performing loan ratio of all institutions. Output the institution name and non-performing loan ratio, sorted in descending order by the non-performing loan ratio.",
  "BRB2-0110": "Find cases where the same collateral has two appraisal records on the same appraisal date. Output the collateral number, appraisal date, and the count of duplicated appraisal records, sorted in ascending order by collateral number.",
  "BRB2-0111": "Find employees of the bank who are borrowers under a credit agreement, and where the managing organizational unit of that credit agreement is exactly the organizational unit to which the employee belongs. Output the employee ID, employee name, and the name of the organizational unit, sorted by employee ID in ascending order.",
  "BRB2-0112": "For each institution, aggregate the latest appraised value of related collateral by the institution to which the guarantee contract belongs, and output the names of the top three institutions with the highest total appraised value, their total appraised value, and their ranking among all institutions, sorted by total appraised value in descending order.",
  "BRB2-0113": "For each corporate customer, count the number of loans, sum the principal balance, and calculate the average amount per loan. Output the top 5 customers with the highest average amount per loan, sorted by average amount per loan in descending order.",
  "BRB2-0114": "Summarize the total number of regulatory ledger records for each institution: add up the record counts for the three ledger types—credit control, governance control, and regulatory reporting—and output the institution name and the combined total of the three ledger record counts, sorted in descending order by the total.",
  "BRB2-0115": "Find large-value transactions whose transaction amount exceeds 10 times the average payment transaction amount of their payment account. Output the payment account number, transaction number, amount, and the account's average transaction amount, sorted by amount in descending order, and return the top 20 records.",
  "BRB2-0116": "Identify institutions that rank in the top 3 across all institutions by number of cash transactions, and whose average cash transaction amount exceeds 11.5 million CNY. Output the institution name, number of cash transactions, and average transaction amount, sorted by average transaction amount in descending order.",
  "BRB2-0117": "For each business unit, count the number of cash transactions handled by its subordinate employees (aggregated by the employee's assigned business unit, based on the transaction's handling employee), and output the business unit name, the number of employees, and the transaction count, sorted by transaction count in descending order, limited to the top 10.",
  "BRB2-0118": "For each customer tier, count the number of individual customers, calculate their average annual income, and compute the proportion of customers whose annual income exceeds 1 million CNY. Output the customer tier, customer count, average annual income, and high-income customer proportion, sorted by customer tier in ascending order.",
  "BRB2-0119": "Calculate the total principal balance for each institution by loan product, and output the product with the highest balance within each institution along with its proportion, sorted by proportion in descending order.",
  "BRB2-0120": "For each institution, calculate the total amount of related-party transactions (where a related-party relationship record exists between the primary holder of the paying account and the primary holder of the receiving account, and the relationship is not classified as \"non-related party\") and its proportion of the total transaction amount. Output the institution name, related-party transaction amount, total transaction amount, and the proportion, sorted by the proportion in descending order. Institutions are attributed based on the institution to which the paying account belongs (or, if there is no paying account, the institution to which the receiving account belongs). The related-party relationship is determined with the primary holder of the paying account as the initiating party and the primary holder of the receiving account as the target party.",
  "BRB2-0121": "For each institution, as of the audit reference date, count the number of loan customers and the number of loan drawdowns, and calculate the average loan principal balance per customer. Output the institution name, customer count, loan drawdown count, and average balance per customer, sorted by the average balance per customer in descending order.",
  "BRB2-0122": "Find wealth management products that meet all of the following conditions: the number of underlying assets held is no less than 3, and the market value proportion of non-standard assets in the portfolio exceeds 30%. Output the product number, product name, number of underlying assets, and non-standard asset proportion, sorted in descending order by the non-standard asset proportion.",
  "BRB2-0123": "For each month in the first half of 2026 (from 2026-01-01 to 2026-06-30), count the number of loan drawdowns and sum the drawdown amounts by institution. Output the month, institution name, number of drawdowns, and total drawdown amount, sorted by month in ascending order and by drawdown amount in descending order.",
  "BRB2-0124": "Find individual customers who hold both a credit card and a time deposit account at this bank. Output the customer ID, customer name, number of credit cards held, and number of time deposit accounts, sorted in descending order by the number of time deposit accounts.",
  "BRB2-0125": "Calculate the proportion of cash withdrawal amount to total transaction amount for each institution, rank them from highest to lowest proportion, and output the institution name, cash withdrawal amount, total transaction amount, proportion, and rank, sorted by rank in ascending order.",
  "BRB2-0126": "List the customer ID and customer name of customers whose name contains '科技', sorted by customer ID in ascending order.",
  "BRB2-0127": "List all ledger record numbers, transaction occurrence dates, and statutory deadlines for records where customer due diligence has not been completed (completion date is empty), sorted by statutory deadline in ascending order.",
  "BRB2-0128": "List the drawdown number, principal balance, and principal overdue days for all loan drawdowns (treating drawdowns without an overdue record as 0 days), include only drawdowns with a non-zero balance, sort by principal overdue days in descending order, and return the top 30 records.",
  "BRB2-0129": "Calculate the average loan age (the number of days between the audit reference date 2026-06-30 and the loan drawdown date) for each institution, and output the institution name and the average loan age in days, sorted by the average loan age in descending order.",
  "BRB2-0130": "List the loan drawdown numbers, drawdown dates, maturity dates, and remaining days for unsettled loan drawdowns with 0 to 90 days remaining until maturity as of the audit reference date 2026-06-30, sorted by remaining days in ascending order.",
  "BRB2-0131": "Group all loan drawdowns into four equal groups by principal balance (quartiles), output the drawdown number, principal balance, and the assigned quartile group number, sorted by quartile group in ascending order, balance in descending order, and drawdown number in ascending order, and return only the first 40 rows; quartile group 1 is the group with the highest principal balance.",
  "BRB2-0132": "Calculate, by borrower registered industry, the cumulative proportion of total loan principal balance for each industry, ranked from highest to lowest balance. Output the industry name, total balance, and cumulative proportion, keeping only industries with a cumulative proportion not exceeding 0.8, and sort the results in ascending order of cumulative proportion.",
  "BRB2-0133": "Find cases where the same customer has two or more unsettled loan drawdowns at the same institution, and output the customer number, customer name, institution name, and the count of unsettled loan drawdowns, sorted in descending order by the count.",
  "BRB2-0134": "Create a cross-tabulation of loans and deposits: by institution, calculate the total outstanding principal of corporate loans, the total outstanding principal of retail loans, and the total outstanding balance of savings deposits. Output the institution name and the three amounts, sorted in descending order by the corporate loan balance.",
  "BRB2-0135": "Group by institution and loan product, count the number of loan drawdowns and sum the disbursed amount. Output the institution name, product Chinese name, number of loan drawdowns, and total disbursed amount, sorted by institution name in ascending order and disbursed amount in descending order.",
  "BRB2-0136": "List all corporate customers in industries whose risk category is \"restricted\" or \"exit\", and output the customer ID, customer name, industry name, and risk category, sorted in ascending order by risk category and then by customer ID.",
  "BRB2-0137": "Find the account number, account type, and opening institution name for accounts with no transaction records, sorted by account number in ascending order, and return only the first 30 records.",
  "BRB2-0138": "For each month, compare the number of cash transactions versus transfer transactions. Output the month, the number of cash transactions, and the number of transfer transactions, sorted by month in ascending order.",
  "BRB2-0139": "Find the guarantee contracts where the latest appraised value of the collateral is more than twice the secured claim amount under the guarantee contract. Output the guarantee contract number, secured claim amount, collateral number, and latest appraised value, sorted in descending order by the difference between the appraised value and the secured claim amount.",
  "BRB2-0140": "Find personal customers who have opened accounts at more than two institutions, and output the customer ID, customer name, and the number of institutions where they have opened accounts, sorted in descending order by the number of institutions.",
  "BRB2-0141": "Find account-date combinations where three or more transactions occurred on the same day and at the same payment account, output the account number, transaction date, and the number of transactions on that day, sorted by transaction count in descending order, and limit the results to the top 20 rows.",
  "BRB2-0142": "Calculate the monthly total cash withdrawal amount by institution, and for each institution, identify the month with the highest monthly amount along with that amount. Output the institution name, month, and the cash withdrawal amount for that month, sorted by amount in descending order.",
  "BRB2-0143": "For each institution, count the number of customers that are members of an exposure group and sum the outstanding loan principal balances of these members at the bank. Output the institution name, the count of group member customers, and the total balance, sorted by the total balance in descending order.",
  "BRB2-0144": "Find loan drawdowns where the difference between the drawdown amount and the total amount of payment instructions under the same loan exceeds 5% of the drawdown amount. Output the loan drawdown number, drawdown amount, total payment instruction amount, and the difference ratio, sorted by the difference ratio in descending order, and return only the top 20 records.",
  "BRB2-0145": "For each institution, count the number of wealth management products issued to ordinary investors and sum their actual raised amounts. Output the institution name, product count, and total raised amount, sorted by total raised amount in descending order.",
  "BRB2-0146": "Find cases where the same borrower has both entrusted payment and self-payment loan drawdowns at the same institution. Output the customer ID, customer name, institution name, count of entrusted payment drawdowns, and count of self-payment drawdowns, sorted by customer ID in ascending order.",
  "BRB2-0147": "Find guarantors who have provided guarantees for multiple guarantee contracts with a total guaranteed amount exceeding 300 million CNY. Output the guarantor ID, guarantor name, number of guarantee contracts, and total guaranteed amount, sorted in descending order by the total amount.",
  "BRB2-0148": "Calculate the proportion of individual customers versus corporate customers among loan clients for each institution, and output the institution name, number of corporate customers, number of individual customers, and the proportion of individual customers, sorted in descending order by the proportion of individual customers.",
  "BRB2-0149": "For each institution, identify the loan product with the lowest provision coverage ratio. Output the institution name, the Chinese name of the product, the total provision already set aside, the total required provision, and the coverage ratio, sorted by the coverage ratio in ascending order.",
  "BRB2-0150": "For each institution, calculate the non-performing loan ratio, provision coverage ratio, and capital adequacy ratio, and output the institution name along with these three metrics. Keep only institutions where the non-performing loan ratio is below 0.25 and the capital adequacy ratio is above 0.1, and sort the results in ascending order of the non-performing loan ratio.",
  "BRB2-0151": "Count the number of currently valid loan drawdowns using entrusted payment for each institution, and output the institution name and the number of loan drawdowns, sorted in descending order by the number of loan drawdowns.",
  "BRB2-0152": "Find loan drawdowns whose drawdown amount exceeds the total amount of their current payment instructions (indicating the drawdown amount is not fully covered by instructions, suggesting a potential lack of entrusted payment control), and output the drawdown number, drawdown amount, total payment instructions, and the difference, sorted by the difference in descending order.",
  "BRB2-0153": "For each institution, count the number of loan IOUs in the loan balance snapshot that, as of the audit reference date (2026-06-30), have been overdue for at least 90 days from the date the overdue status began. Output the institution name and the count of such IOUs, sorted in descending order by the count.",
  "BRB2-0154": "Find loan drawdowns that use entrusted payment but where the payee on the payment instruction is the same entity as the borrower (suspected entrusted funds flowing back to the borrower). Output the drawdown number, borrower name, instruction amount, and payee name, sorted by instruction amount in descending order, and return only the top 200 records.",
  "BRB2-0155": "For each institution, calculate the average amount and the number of entrusted payment instructions. Output the institution name, average amount, and instruction count, sorted by average amount in descending order.",
  "BRB2-0156": "Find contracts issued to corporate clients whose subject status is frozen and whose credit facility is still effective. Output the contract number, borrower name, and contract amount, sorted by contract amount in descending order.",
  "BRB2-0157": "In credit management, the total signed amount of multiple credit contracts under the same credit line must not exceed the approved credit line; exceeding the limit constitutes a violation. Output the credit line number, credit subject name, credit type, approved credit line, and cumulative signed amount, listing only records where the cumulative signed amount is greater than the approved credit line, sorted by cumulative signed amount in descending order, then by credit line number in ascending order.",
  "BRB2-0158": "For active RMB deposit accounts jointly held by at least two different customers, group by account type to count the number of joint accounts and the total number of associated holders, keep only account types with more than 100 joint accounts, and output the account type, the number of joint accounts, and the total number of associated holders, sorted by the number of joint accounts in descending order and by account type in ascending order.",
  "BRB2-0159": "Find the loan drawdowns that use entrusted payment and whose total payment instruction amount exceeds the credit contract amount (i.e., the entrusted payment amount exceeds the contract agreement). Output the drawdown number, contract amount, total payment instruction amount, and the excess amount, sorted by the excess amount in descending order, and return only the top 200 records.",
  "BRB2-0160": "Find the loan drawdowns where the product type is working capital and the investment industry is classified as exit (working capital is prohibited from being used in restricted business areas), and output the drawdown number, product Chinese name, investment industry, and loan amount, sorted by loan amount in descending order, taking only the top 200 records (the drawdown status must be normal).",
  "BRB2-0161": "Find the loan drawdowns that are currently active and use the self-payment method for fixed asset loans. Output the drawdown number, disbursed amount, and payment method, sorted by disbursed amount in descending order, and limit the results to the top 200 records.",
  "BRB2-0162": "Calculate the difference between the total loan drawdown amount and the total payment instruction amount for each institution (total drawdown minus total instructions), and output the institution name and the difference amount, sorted by the difference amount in descending order.",
  "BRB2-0163": "Count the number of payment instructions that are in pending status and use entrusted payment, grouped by institution, and output the institution name and the count, sorted by the count in descending order.",
  "BRB2-0164": "Calculate the average payment deviation rate for each loan drawdown under each institution (the deviation rate is based on the loan amount, calculated as the absolute value of the difference between the total payment instructions and the loan amount, divided by the loan amount), and output the institution name and the average deviation rate, sorted in descending order by the average deviation rate.",
  "BRB2-0165": "Find contracts issued to related parties with a credit guarantee method (credit loans must not be issued to related parties), and output the contract number, borrower name, and contract amount, sorted by contract amount in descending order. Related parties ('非关联方' is not referenced here; the query refers to related parties, i.e., '关联方').",
  "BRB2-0166": "For one-time (non-revolving) credit facilities, the higher the multiple by which the contracted amount within the approved limit exceeds the limit, the more severe the unauthorized over-limit. Output the credit facility ID, credit type, approved credit limit, cumulative contracted amount, and over-limit multiple (total contracted amount divided by approved limit). List only records where the credit type is one-time credit and the contracted amount exceeds the approved limit. Sort by the over-limit multiple in descending order, and then by credit facility ID in ascending order.",
  "BRB2-0167": "Calculate, for each corporate customer that is a related party (as either party in a related-party relationship), the total credit contract amount, keeping only customers whose total exceeds 500 million CNY, output customer number, customer name, and total contract amount, sorted by total in descending order, take the top 10.",
  "BRB2-0168": "Find entrusted payment instructions where the payee and the borrower have a relationship other than \"non-related party\" (suspected of transferring credit funds through related parties). Output the loan drawdown number, borrower name, payee name, and instruction amount, sorted by instruction amount in descending order, and take the top 200 records.",
  "BRB2-0169": "For one-time (non-revolving) credit facilities, funds can only be drawn in a single installment; multiple loan drawdowns under the same credit contract may indicate splitting the facility into smaller amounts or repeated drawdowns. Output the credit contract number, credit type, number of drawdowns, and cumulative disbursed amount, listing only records where the credit type is not revolving credit and the number of drawdowns under the same contract is greater than or equal to 3, sorted by number of drawdowns in descending order, then by credit contract number in ascending order.",
  "BRB2-0170": "List the credit contract number, borrower name, contract amount, number of loan drawdowns using self-payment, and cumulative self-payment amount for credit contracts where entrusted payment was required but actual disbursements used self-payment, which constitutes a violation of failing to implement entrusted payment regulatory requirements. Only include records where entrusted payment was agreed but self-payment was actually used. Sort the results by cumulative self-payment amount in descending order, then by credit contract number in ascending order.",
  "BRB2-0171": "Find the loan drawdowns whose principal balance exceeds twice the average loan balance of their lending institution, and output the institution name, drawdown number, principal balance, institution average balance, and the excess difference, sorted by the difference in descending order.",
  "BRB2-0172": "Find the credit limit pool entries for credit limits issued to related-party customers that are still effective, output the customer number, customer name, and limit amount, sorted by limit amount in descending order, and take only the top 200 rows. (related-party customers: '关联方')",
  "BRB2-0173": "For each institution, calculate the proportion of credit contract amounts from non-related-party customers (i.e., customers with no relationship other than \"non-related party\", based on records where the customer is the initiating party of the relationship) to the institution's total credit contract amount. Output the institution name, non-related-party amount, total amount, and proportion, sorted by proportion in descending order.",
  "BRB2-0174": "For the same borrower, among consecutive credit facility contracts ordered by contract signing date, where the signing date of the later contract is earlier than the maturity date of the previous contract (i.e., a new credit facility is signed before the old contract matures, creating overlapping multi-credit exposure during the validity period), output the borrower name, new credit facility contract number, new contract signing date, previous contract maturity date, and the difference between the two dates (new contract signing date minus previous contract maturity date, in days; a negative value indicates the number of days the new contract was signed early). List only records where the new contract signing date is earlier than the previous contract maturity date, sorted by the day difference in ascending order and then by new credit facility contract number in ascending order, and return only the first 300 records.",
  "BRB2-0175": "List the source entity customer name, target entity customer name, and relationship Chinese name for records where a \"shadow shareholder\" related-party relationship exists, and output the source entity name, target entity name, and relationship name, sorted in ascending order by source entity name and then by target entity name.",
  "BRB2-0176": "Calculate the ratio of each corporate borrower's total outstanding loan principal balance to the capital net amount of its originating institution, identify records where the single-client loan concentration exceeds 10 percent, and output the institution name, customer name, total balance, capital net amount, and ratio, sorted by ratio in descending order, limited to the top 200 records.",
  "BRB2-0177": "List the credit contract number, borrower name, executed annual interest rate, average interest rate of the target industry, and the percentage markup over the industry average, for records where the executed interest rate exceeds the industry average by more than 10%, sorted by the markup percentage in descending order, and then by the credit contract number in ascending order. The markup percentage should be expressed as a percentage figure, e.g., 12.5 for a 12.5% markup, rounded to two decimal places.",
  "BRB2-0178": "For each institution, count the number of corporate clients whose outstanding loan principal balance exceeds 10% of that institution's net capital. Output the institution name and the count of such over-limit clients, sorted in descending order by the count.",
  "BRB2-0179": "Find the exposure groups whose group customer credit concentration exceeds the regulatory cap (calculated as 10% of net capital), and output the group number, group name, total balance, net capital, and concentration ratio, sorted by the ratio in descending order (net capital is taken from the group's lead institution, and only include loan drawdowns under credit contracts signed by that lead institution itself).",
  "BRB2-0180": "Output the credit contract number, contract maturity date, unsettled loan drawdown number, drawdown status, and contract amount for records where the credit contract status is marked as expired but the loan drawdown status under it is still registered as normal and unsettled, reflecting a disconnect between the contract status and the drawdown lifecycle status. Only list records where the credit contract status is expired and the drawdown status is normal, sorted by drawdown number in ascending order.",
  "BRB2-0181": "Calculate the ratio of the credit limit amount for each single borrowing entity within each credit facility to the capital net amount of its originating institution, identify the facility records where the ratio exceeds 10 percent, and output the facility number, customer name, facility amount, capital net amount, and ratio, sorted by ratio in descending order, limited to the top 200 records.",
  "BRB2-0182": "Identify the exposure groups of the related-party type where the total loan balance of group members exceeds the regulatory cap (calculated as 15% of net capital), and output the institution name, group name, total balance, number of members, net capital, and the ratio, sorted by the ratio in descending order.",
  "BRB2-0183": "List the loan drawdowns where the drawdown account had a large fund transfer shortly after disbursement, indicating possible diversion or round-tripping of loan proceeds to a related party. Output the loan receipt number, drawdown account number, drawdown date, transfer transaction number, transfer date, transfer amount, and the number of days between drawdown and transfer. Include only records where the transfer occurred within 7 days after the drawdown date, and where the transfer transaction status is settled. Sort the results by the number of days between drawdown and transfer in ascending order, then by transfer amount in descending order, and then by loan receipt number in ascending order.",
  "BRB2-0184": "For each institution, identify the corporate client with the highest ratio of outstanding loan principal balance to the institution's net capital, taking the top one client per institution. Output the institution name, client name, and the ratio, sorted by institution name in ascending order.",
  "BRB2-0185": "List the contracts whose fund usage is directed to an industry in the exit category and whose credit facility is still active, and output the contract number, borrower name, target industry, and contract amount, sorted by contract amount in descending order.",
  "BRB2-0186": "For each institution and customer registered industry, calculate the total approved credit facility amount extended to enterprises in exit-class industries (where the customer profile's registered industry risk category is \"exit-class\"). Output the institution name, industry name, and total contract amount, sorted by total amount in descending order.",
  "BRB2-0187": "For each credit product line, calculate the total number of contracts and the number of contracts disbursed with collateral as the guarantee method, then compute the proportion of collateral-backed contracts. Keep only product lines where this proportion is below 19 percent. Output the product line, total contract count, and collateral-backed contract count, sorted by total contract count in descending order and product line in ascending order.",
  "BRB2-0188": "Within each institution, divide the loan drawdowns into four equal tiers by principal balance, from highest to lowest. Output the drawdown number, principal balance, and tier, sorted by tier in ascending order and balance in descending order, and return only the top 300 rows.",
  "BRB2-0189": "List the loan drawdowns where there are overdue installments but the ending balance still shows zero overdue principal, i.e., overdue amounts are only recorded on the books without being recognized, and only interest is collected without recognizing overdue principal, which may conceal defaults. Output the drawdown number, total overdue principal due, ending book overdue principal, and number of overdue installments. Only include records with overdue installments but zero ending book overdue principal. Sort by total overdue principal due in descending order, then by drawdown number in ascending order.",
  "BRB2-0190": "List corporate clients whose registered industry is classified as \"exit\" and who have obtained credit, outputting the client ID, client name, and industry name, sorted in ascending order by industry name and client ID.",
  "BRB2-0191": "List the active customers who belong to the VIP or large customer segment and have no related-party records under their name, outputting the customer ID and customer segment, sorted in ascending order by customer segment and then by customer ID.",
  "BRB2-0192": "For credit contracts where the investment target industry is classified as restricted, list the top 5 contracts by contract amount, outputting the investment target industry, contract number, contract amount, and ranking, sorted in ascending order by industry name and ranking.",
  "BRB2-0193": "For accounts that are still in active status, group by account type and count the number of accounts other than the earliest opened account within each type, keeping only those types with a count of less than 900. Output the account type and the account count, sorted by account count in descending order and then by account type in ascending order.",
  "BRB2-0194": "Find corporate clients that are both members of an exposure group and have received credit in restricted or exit industries. Output the client ID, client name, industry name, and the total credit contract amount, sorted in descending order by the total amount.",
  "BRB2-0195": "For each institution, count the number of credit contracts and sum the contract amounts for those directed to the real estate industry. Output the institution name, the count, and the total amount, sorted by the count in descending order.",
  "BRB2-0196": "Calculate the proportion of each loan drawdown's principal balance to the total loan principal balance of its owning institution, and output the drawdown number, institution name, principal balance, and proportion, with proportions sorted in descending order within the same institution, taking only the top 300 records (proportions expressed as percentages rounded to two decimal places, institutions sorted by name in ascending order, and within the same institution, drawdowns with the same proportion sorted by drawdown number in ascending order).",
  "BRB2-0197": "For each business unit to which the source entity belongs, count the distinct number of source customers in related-party records where the relationship type is \"key management personnel\" or \"actual controller\". Output the business unit code, business unit name, and the distinct source customer count, sorted in descending order by the count.",
  "BRB2-0198": "List the loan drawdowns where the drawdown status is still \"normal\" despite multiple overdue periods, which may indicate improper concealment of default and maintenance of a normal classification. Output the drawdown number, cumulative disbursed amount, drawdown status, total overdue principal, and number of overdue periods. Only include records where the status is \"normal\" and the number of overdue periods is greater than or equal to 2. Sort the results by number of overdue periods in descending order, then by total overdue principal in descending order, and finally by drawdown number in ascending order.",
  "BRB2-0199": "Find loan drawdown combinations where the same drawdown account has two or more drawdowns on the same day, suspected of splitting a loan into smaller amounts to evade limits. Output the drawdown account number, the drawdown date, and the number of drawdowns on that date, sorted by the count in descending order, and return only the top 200 records.",
  "BRB2-0200": "Find loan drawdowns whose settlement date is later than the credit facility expiry date (indicating abnormal loan term management), and output the drawdown number, drawdown date, settlement date, and maturity date, sorted by settlement date in descending order, limited to the first 200 records.",
  "BRB2-0201": "List the loan drawdowns whose principal overdue days have reached forty-five days but are still classified as \"normal\" risk classification level, and output the drawdown number, principal overdue days, and overdue principal, sorted by principal overdue days in descending order.",
  "BRB2-0202": "For each account subtype, count the number of accounts currently in a dormant status, keeping only those subtypes with a count of at least 55. Output the account subtype and the count, sorted by count in descending order and then by account subtype in ascending order.",
  "BRB2-0203": "For each collateral item, sort its appraisals by appraisal date, calculate the percentage increase in appraised value between consecutive appraisals, and identify appraisal records where the appraised value rose by more than 50% compared to the previous appraisal, as suspected artificially inflated valuations. Output the collateral ID, current appraised value, previous appraised value, and the percentage increase, sorted by the percentage increase in descending order.",
  "BRB2-0204": "For each assessment business unit and classification determination method, count the number of loan drawdown risk classification records. Output the business unit name, classification determination method, and record count, sorted by record count in descending order.",
  "BRB2-0205": "For each institution, aggregate the total outstanding principal balance of loan drawdowns classified as non-performing (substandard, doubtful, or loss), and output the institution name and the total non-performing principal balance, sorted by the balance in descending order.",
  "BRB2-0206": "Find customers who are both deposit account holders with time deposits and borrowers who have signed credit facility agreements with the bank, output the customer ID, sorted by customer ID in ascending order.",
  "BRB2-0207": "Count the number of loan drawdowns classified as \"loss\" by institution, and output the institution name and the drawdown count, sorted by the count in descending order.",
  "BRB2-0208": "Calculate the loan provision coverage ratio by institution (total provision amount divided by total required provision amount, rounded to four decimal places), and output the institution name and provision coverage ratio, sorted by the ratio in ascending order.",
  "BRB2-0209": "List employees who are still in active service but have no account holder records at this bank (reflecting missing employee-account relationship records), output the employee customer ID, sorted by employee customer ID in ascending order.",
  "BRB2-0210": "List savings-type accounts that have never had any cash withdrawal records, suspected of long-term deposits-only activity with abnormal fund accumulation. Output the account number, sorted by account number in ascending order, and return only the first 300 records.",
  "BRB2-0211": "List the collateral whose appraised value is lower than its pledged guarantee amount, and output the collateral number, collateral name, appraised value, and pledged guarantee amount, sorted by appraised value in ascending order.",
  "BRB2-0212": "List the active guarantee agreements that use mortgage or pledge as the guarantee method but have no registered collateral-related records, and output the guarantee agreement number and guarantee amount, sorted by guarantee amount in descending order.",
  "BRB2-0213": "List savings-type accounts that lack a primary holder record after account opening, reflecting a disconnect between account controller and account registration. Output the account number, sorted by account number in ascending order, and limit the results to the first 300 records.",
  "BRB2-0214": "List the valid collateral-related records that are in the first lien position and have a pledge ratio exceeding 70 percent, outputting the collateral number, lien position, and pledge ratio, sorted by pledge ratio from highest to lowest.",
  "BRB2-0215": "For each institution and guarantee method, summarize the total guaranteed amount of active guarantee agreements. Output the institution name, guarantee method, and total guaranteed amount, sorted by the total amount in descending order.",
  "BRB2-0216": "List the records where the guarantee agreement status is expired but the associated collateral is still in normal status, output the guarantee agreement number and collateral number, sorted in ascending order by guarantee agreement number and collateral number.",
  "BRB2-0217": "List the guarantor commitment records whose status is expired, and output the guarantee agreement number and the guaranteed amount, sorted by the guaranteed amount in descending order.",
  "BRB2-0218": "Group loan drawdowns by remaining term as of the audit reference date (2026-06-30) into three buckets: already due (less than 0 days), nearing due (0 to 90 days), and normal (greater than 90 days); count the number of drawdowns in each bucket, and output the bucket label and count, ordered by normal, nearing due, then already due.",
  "BRB2-0219": "List the collateral items that are pledged under multiple active guarantee agreements, output the collateral ID and the number of associated agreements, sorted by the number of associated agreements in descending order (the associated record status must be active).",
  "BRB2-0220": "For each collateral type, calculate the average appraised value and the number of appraisals for collateral that was internally assessed by the bank. Output the collateral type, average appraised value, and number of appraisals, sorted by average appraised value in descending order.",
  "BRB2-0221": "List the loan receipt number, cumulative disbursed amount, payment instruction number, pending instruction amount, and instruction status for loans that have been fully drawn down and are in normal status, but whose corresponding entrusted payment instructions are still pending, indicating that the loan was disbursed before the instruction was executed, which may violate proper procedures. Only include records where the instruction status is pending and the loan receipt status is normal. Sort the results by instruction amount in descending order, then by loan receipt number in ascending order.",
  "BRB2-0222": "Under the same credit agreement, the cumulative amount of self-operated payments as a proportion of the contract amount is excessively high, raising suspicion of splitting payments into smaller amounts to circumvent the entrusted payment cap. Output the credit agreement number, borrower name, contract amount, cumulative self-operated payment amount, and self-operated payment ratio, listing only records where the cumulative self-operated payment amount exceeds 30% of the contract amount, sorted in ascending order by credit agreement number.",
  "BRB2-0223": "List the repayment account number, loan receipt number, drawdown date, drawdown amount, and the count of loan receipts undertaken by that account, for accounts that have undertaken at least 3 loan receipts, showing only the first 2 loan receipts in chronological order of drawdown for each such account, sorted by repayment account number and drawdown date in ascending order.",
  "BRB2-0224": "List the teller-type system operators with the highest authorization level (L3), output the operator ID and corresponding employee ID, sorted by operator ID in ascending order.",
  "BRB2-0225": "Count the number of distinct employees currently holding each position, grouped by position name, and output the position name along with the employee count, sorted by the count in descending order.",
  "BRB2-0226": "Output the loan receipt number, drawdown date, credit facility number, facility effective date, approval date, and drawdown amount for records where the drawdown date is earlier than the facility effective date, indicating that the loan was disbursed before the credit facility took effect, potentially involving unauthorized or out-of-sequence lending. Sort the results by credit facility number in ascending order.",
  "BRB2-0227": "Under the same credit contract, where the cumulative loan drawdown amount exceeds the contract amount, indicating disbursement beyond the approved amount or failure to control the lending scale per the contract. Output the credit contract number, contract amount, cumulative loan drawdown amount, amount disbursed in excess of the contract, and number of drawdowns, listing only records where the cumulative loan drawdown amount is greater than the contract amount, sorted by credit contract number in ascending order.",
  "BRB2-0228": "List the loan drawdown account number, the number of loan drawdowns it carries, and the total drawdown amount, for accounts carrying at least 5 loan drawdowns, sorted by the number of drawdowns in descending order, and then by the drawdown account number in ascending order.",
  "BRB2-0229": "List the credit contract number, borrower name, and the number of loan drawdowns under self-operated payment for each credit contract, showing only those contracts where the count of self-operated payment drawdowns is at least 5, sorted by the count of self-operated payment drawdowns in descending order, and then by credit contract number in ascending order.",
  "BRB2-0230": "For each institution, count the number of accounts where the book balance exceeds the available balance and the difference is greater than 5 million CNY, and also calculate the total difference for those accounts. Output the institution name, the account count, and the total difference, sorted by the total difference in descending order.",
  "BRB2-0231": "List the time deposits that have matured before June 30, 2026, but whose associated accounts are still in a normal status. Output the account number, initial principal, maturity date, and annual interest rate, sorted by maturity date in ascending order.",
  "BRB2-0232": "For each institution, count the number of large cash withdrawal transactions that are settled and have a single transaction amount exceeding 1 million CNY, and sum their amounts. Output the institution name, transaction count, and total amount, sorted by total amount in descending order.",
  "BRB2-0233": "List debit cards issued on or before January 31, 2025, and currently still active, outputting the card number, card type, and issue date, sorted by issue date in ascending order and card number in ascending order.",
  "BRB2-0234": "Output the institution name, cumulative entrusted payment amount, cumulative autonomous payment amount, and entrusted payment ratio, listing only institutions whose entrusted payment ratio is below 52%, sorted by entrusted payment ratio in ascending order, and then by institution name in ascending order (amounts based on loan drawdown amounts, aggregated by the drawdown's payment method).",
  "BRB2-0235": "Under the same credit contract, where a single loan drawdown amount accounts for more than 90% of the total amount drawn under that contract, the bank failed to fulfill the responsibilities of staged approval and entrusted payment for a one-time full disbursement. Output the credit contract number, loan receipt number, single drawdown amount, cumulative drawdown amount under the contract, and the single drawdown ratio, listing only those receipts with a single drawdown ratio greater than 90%, sorted in ascending order by credit contract number (with the ratio expressed as a percentage and rounded to two decimal places).",
  "BRB2-0236": "List the account balance snapshots for accounts whose status is closed, outputting the account number and book balance, ordered by book balance from highest to lowest.",
  "BRB2-0237": "Aggregate the planned fundraising amount for wealth management products currently on sale and the actual fundraising amount for all products by issuing institution, calculate the completion rate of total actual fundraising against total planned fundraising, and output the institution name, total actual fundraising, total planned fundraising, and completion rate, keeping only institutions with a completion rate exceeding 1.2, sorted by completion rate in descending order (planned fundraising amount only includes products on sale, while actual fundraising amount includes all products).",
  "BRB2-0238": "For each lending institution, cross-tabulate the number of entrusted payment and self-operated payment instructions, along with the total amount of entrusted instructions. Output the institution name, entrusted instruction count, self-operated instruction count, and total entrusted amount. Keep only institutions that have both entrusted and self-operated instructions, and sort by total entrusted amount in descending order.",
  "BRB2-0239": "By month and payment account, summarize the cash withdrawal amounts, identify the account-month combinations where the total monthly cash withdrawal exceeds 5 million CNY, and output the month, account number, and total cash withdrawal, sorted by the total in descending order, limited to the top 200 records.",
  "BRB2-0240": "List borrowers who have both overdue loan drawdowns and new non-overdue loan drawdowns, indicating potential risk concealment through new lending while existing overdue loans remain. Output the borrower ID, borrower name, number of overdue loan drawdowns, and total number of loan drawdowns. Only include borrowers who have at least one overdue loan drawdown and at least one new non-overdue loan drawdown. Sort the results by the number of overdue loan drawdowns in descending order, then by borrower ID in ascending order. An overdue loan drawdown is determined by any installment in the repayment schedule with a status of \"overdue\".",
  "BRB2-0241": "List the loan drawdown number, overdue start date, period-end overdue principal, and days overdue as of the snapshot reference date (2026-06-30) for loan drawdowns whose period-end overdue principal exceeds 10 million CNY, whose days overdue from the overdue start date exceed 90 days as of the snapshot reference date, and whose drawdown status remains \"normal\", indicating a potential delay in reporting large non-performing exposure. Only include records where the drawdown status is \"normal\", the period-end overdue principal exceeds 10 million CNY, and the days overdue exceed 90 days. Sort the results by loan drawdown number in ascending order and limit the output to the first 300 records.",
  "BRB2-0242": "List the loan drawdown number, loan account number, total disbursed amount, and account status for records where the drawdown status is \"normal\" but the corresponding loan account has been closed or is \"dormant\", indicating a contradiction between account status and loan status. Only include records where the drawdown status is \"normal\" and the loan account status is not \"normal\", and sort the results in ascending order by account status and then by drawdown number.",
  "BRB2-0243": "List the loan drawdowns that have an overdue installment repayment plan and whose provision already accrued is still lower than the provision that should be accrued, indicating a provision shortfall. Output the drawdown number, the provision amount that should be accrued, the provision amount already accrued, and the provision shortfall amount (should-be-accrued minus already-accrued, rounded to two decimal places). Only include drawdowns with an overdue installment plan and where the accrued provision is lower than the required provision. Sort by drawdown number in ascending order and limit the result to the first 200 rows.",
  "BRB2-0244": "List the payment instruction number, loan receipt number, borrower name, actual payee name, and instruction amount for executed payment instructions where the payee is not the borrower, indicating that loan funds were directed to a third party and requiring a look-through review of the actual fund user. Sort the results by instruction amount in descending order, then by payment instruction number in ascending order.",
  "BRB2-0245": "List the borrower name, loan drawdown certificate number, drawdown date, previous drawdown date, and the number of days between the two drawdowns, for records where the previous drawdown for the same borrower occurred no more than 3 days before the current drawdown, sorted by the interval in ascending order, and then by the drawdown certificate number in ascending order.",
  "BRB2-0246": "List the credit contract number, contract amount, total outstanding balance of loan drawdowns at period end, and the amount exceeding the contract balance, for records under revolving credit where the period-end balance is greater than the contract amount. Sort the results by the amount exceeding the contract balance in descending order, and then by the credit contract number in ascending order.",
  "BRB2-0247": "List the loan drawdown number, loan product Chinese name, drawdown date, original maturity date, the term in months calculated on a 30-day basis (rounded to the nearest integer), and the drawdown amount for working capital loans where the original maturity date exceeds the drawdown date by more than 730 days, indicating a short-term loan used for long-term purposes. Sort the results by the calculated term in months in descending order, and then by the loan drawdown number in ascending order, and limit the output to the first 200 records.",
  "BRB2-0248": "List the loan drawdown number, drawdown date, credit contract number, contract signing date, and drawdown amount for records where the drawdown date is earlier than the contract signing date, indicating a reverse workflow operation where funds were disbursed before the contract was signed. Sort the results in ascending order by loan drawdown number.",
  "BRB2-0249": "Count the number of collateral items in normal status by collateral type, and output the collateral type and the collateral count, sorted by the count in descending order.",
  "BRB2-0250": "Among the loan drawdowns that are in either active or settled status, aggregate the repaid due principal for each drawdown, sort by the loan amount from highest to lowest, and take only the top 30, outputting the drawdown number, loan amount, and total repaid principal, ordered by loan amount in descending order.",
  "BRB2-0251": "Under the same credit contract, where the new loan drawdown date immediately follows the maturity date of the old loan note, it is suspected of using new loans to repay old loans. Output the credit contract number, previous loan note number, previous original maturity date, subsequent loan note number, subsequent drawdown date, and the gap in days between the two. List only records where the subsequent drawdown date is not earlier than the previous maturity date and the gap is less than 30 days, sorted by the gap in ascending order, then by the credit contract number in ascending order.",
  "BRB2-0252": "List the borrower ID, borrower name, number of distinct institutions involved, number of loan drawdowns, and cumulative loan disbursement amount for borrowers who currently hold active loan drawdowns at two or more different institutions simultaneously, indicating concentrated multi-lender credit exposure. Sort the results by the number of loan drawdowns in descending order, and then by borrower ID in ascending order.",
  "BRB2-0253": "List the loan drawdowns where none of the installments in their repayment plans have ever been settled, indicating the borrower has never completed a full installment cycle. Output the drawdown number, the count of unsettled installments, and the total principal due (rounded to two decimal places). Include only drawdowns for which all installment plans under the borrower's name have no settled records. Sort the results by total principal due in descending order, then by drawdown number in ascending order, and limit the output to the first 200 rows.",
  "BRB2-0254": "Identify settled transfer transactions of over 100,000 CNY where the transfer-out account is a loan drawdown account and the transfer-in account is a savings account, indicating possible credit fund diversion back to or misuse into a savings account. Output the transfer transaction ID, transfer-out loan drawdown account ID, transfer-in savings account ID, transfer-in account type, and transfer amount (rounded to two decimal places). Include only transactions where the transfer-out account exists in loan drawdown accounts, the transaction is settled, the transaction type is transfer, and the transfer-in account is a savings account, with a single transaction amount exceeding 100,000 CNY. Sort by transfer transaction ID in ascending order and limit the result to the first 300 rows.",
  "BRB2-0255": "The post-loan balance shows overdue principal, but there are no overdue installments in the installment repayment plan of the loan receipt, creating a contradiction in the overdue information ledger. Output the loan receipt number and the end-of-period book-carrying overdue principal. List only those loan receipts that have book-carrying overdue principal but no overdue installments in their repayment plan. Sort by the end-of-period book-carrying overdue principal in descending order, and then by the loan receipt number in ascending order.",
  "BRB2-0256": "List the loan drawdown number, drawdown date, credit contract number, contract amount, and single drawdown amount for records in credit contracts where the single drawdown amount exceeds the contract amount, indicating a single disbursement that surpasses the approved scale. Only include records where the single drawdown amount is greater than the contract amount, sorted by single drawdown amount in descending order, and then by loan drawdown number in ascending order.",
  "BRB2-0257": "List credit contracts whose pricing is below 90% of the average executed interest rate for the same target industry, indicating potential below-market lending or disguised concessions. Output the credit contract number, borrower name, executed annual interest rate, average interest rate of the corresponding target industry, and the percentage discount relative to the industry average. Include only records where the executed interest rate is below 90% of the industry average, sorted by the discount percentage in ascending order, and then by credit contract number in ascending order.",
  "BRB2-0258": "Output the credit contract number, loan industry name, industry risk category, contract amount, and borrower name for credit contracts where the loan is directed to an industry classified as restricted or exit, sorted by credit contract number in ascending order.",
  "BRB2-0259": "List the loan drawdowns where the drawdown status is marked as \"written-off\" but the remaining principal at period end in the loan balance snapshot still exceeds 10 million CNY, indicating that the book principal was not cleared after a large write-off. Output the drawdown number, remaining principal at period end, and overdue principal at period end (rounded to two decimal places). Only include drawdowns that are written-off and have remaining principal at period end exceeding 10 million CNY. Sort by remaining principal at period end in descending order, then by drawdown number in ascending order, and limit the result to the first 200 rows.",
  "BRB2-0260": "List the loan drawdown records where the drawdown date is earlier than the account opening date of the disbursement account, indicating that the loan was disbursed before the account was opened, resulting in a reversed sequence between the account opening and the loan disbursement. Output the loan receipt number, drawdown date, disbursement account number, and account opening date. Only include records where the drawdown date is earlier than the account opening date of the disbursement account. Sort the results by drawdown date in ascending order, and then by loan receipt number in ascending order.",
  "BRB2-0261": "List the loan drawdowns where the disbursement account is a savings-type account, indicating potential fund pooling or misappropriation. Output the loan receipt number, disbursement account number, account type, and drawdown amount, showing only receipts with savings-type disbursement accounts, sorted by drawdown amount in descending order, then by loan receipt number in ascending order.",
  "BRB2-0262": "List the credit contract number, guarantee method, contract amount, and borrower name for credit facilities that use unsecured credit as the guarantee method and have a contract amount exceeding 8 million CNY, sorted by contract amount in descending order, then by credit contract number in ascending order.",
  "BRB2-0263": "List the loan contracts of borrowing customers who have a related-party relationship with the bank (excluding records marked as \"non-related party\" ('非关联方')), where the contract's annual interest rate is lower than the average annual interest rate of the same product type at the same institution, and output the borrower name, customer ID, contract annual interest rate, average annual interest rate of the same product type at the same institution, and the interest rate spread, sorted by the interest rate spread in descending order.",
  "BRB2-0264": "For borrowing customers confirmed by the bank as related parties (excluding those marked as 'non-related party' ('非关联方')), count their loan contracts obtained on a credit basis (unsecured), and output the borrower name, customer number, number of credit loans, and total approved credit amount, sorted in descending order by total approved credit amount.",
  "BRB2-0265": "For each wealth management product, calculate the fair value ranking and average fair value of its held assets. Identify assets whose individual holding fair value exceeds 1.5 times the product's average holding fair value. Output the product name, asset number, fair value, ranking, and the product's average fair value, sorted by ranking in ascending order.",
  "BRB2-0266": "Find relationship pairs where a related-party relationship exists and both customers have obtained loans from the bank, excluding records where the relationship is \"non-related party\" ('非关联方'). Output the related party A customer ID, related party B customer ID, and relationship name, sorted in ascending order by relationship name and relationship record ID.",
  "BRB2-0267": "For each exposure group, aggregate the total outstanding loan principal balance of its members at this bank, and compare it with the lead institution's net capital to calculate the proportion. Output the group name, number of members, total balance, net capital, and proportion. Keep only groups with at least two members and a proportion exceeding 10 percent, sort by proportion in descending order, and take only the top 200 rows (counting only loan drawdowns under credit contracts signed by the lead institution itself).",
  "BRB2-0268": "Identify transactions where the transfer counterparties are related parties through account holder relationships and customer affiliation penetration, excluding records marked as \"non-related party\" ('非关联方'). Output the payer name, payee name, total number of transfers, and total transfer amount, sorted by total transfer amount in descending order.",
  "BRB2-0269": "Count the number of target customers who actually obtained loans at our bank under each type of related-party relationship, and output the relationship name and the count of target customers who borrowed successfully, sorted in descending order by the count of target customers.",
  "BRB2-0270": "Filter for on-sale wealth management products whose underlying holding path is multi-layer nested and whose product risk level is the highest level (R5), and output the product number, product name, and corresponding underlying asset name, sorted in ascending order by product number.",
  "BRB2-0271": "Count the number of products issued by each financial institution whose underlying assets are liability-type items, keep only institutions with at least 20 products, and output the institution name and product count, sorted by product count in descending order.",
  "BRB2-0272": "For each card issuance year, count the number of credit cards (贷记卡) and debit cards (借记卡) issued, and output the issuance year, credit card issuance count, and debit card issuance count, sorted by issuance year in ascending order.",
  "BRB2-0273": "Identify the exposure groups whose member customers have obtained loan contracts from five or more distinct handling business outlet units. Output the group number, group name, exposure type, the count of handling branches involved, and the total group credit amount, sorted in descending order by the count of handling branches involved.",
  "BRB2-0274": "For each wealth management product, count the number of assets whose underlying investment path is a multi-tier intermediary product. Output only the top 20 products with the highest asset counts, showing the product number and asset count, sorted in descending order by asset count.",
  "BRB2-0275": "Summarize the loan drawdowns whose book principal balance exceeds 90 million CNY and that have overdue principal, calculate their maximum overdue days, keep only those drawdowns whose maximum overdue days are at least 200 days, and output the drawdown number, book principal balance, and maximum overdue days, sorted by maximum overdue days in descending order and drawdown number in ascending order (overdue principal is based on the overdue principal in the loan balance snapshot, and the maximum overdue days is the maximum value across all overdue snapshot records for that drawdown).",
  "BRB2-0276": "Calculate the total credit amount granted to each member of an exposure group at this bank, compare it with the net capital of the respective institution, identify groups where the group credit-to-net-capital ratio is excessively high, and output the group ID, group name, institution name, total group credit, institution net capital, and concentration ratio, sorted by concentration ratio in descending order.",
  "BRB2-0277": "Identify exposure groups where member customers have obtained loans from two or more different institutions, and output the group ID, group name, number of institutions involved, and number of members with credit obtained, sorted in descending order by the number of institutions involved.",
  "BRB2-0278": "Statistically rank groups by the largest member credit scale within each group type. Output the group type, group name, number of members, and number of loan contracts, sorted by the number of loan contracts in descending order, and return the top 15 records.",
  "BRB2-0279": "Statistical report on customers with principal overdue among exposure group members, outputting group ID, group name, number of overdue members, and total overdue principal, sorted in descending order by total overdue principal (overdue is defined as overdue principal greater than zero in the loan balance snapshot).",
  "BRB2-0280": "Trace the group member guarantee chain to identify guarantee commitment records where the guarantor and the borrower of the guaranteed credit facility belong to the same exposure group. Aggregate by guarantor and output the guarantor name, guarantor customer ID, number of intra-group guarantee commitments, and total guaranteed amount (rounded to two decimal places), sorted by total guaranteed amount in descending order and guarantor customer ID in ascending order.",
  "BRB2-0281": "Rank the exposure groups by the total credit amount extended to their members, and output the rank, group name, total group credit amount, and number of members, sorted in descending order by the total credit amount, limited to the top 8.",
  "BRB2-0282": "Identify corporate customers who have both obtained loans from this bank and provided external guarantees, where the total amount of external guarantees exceeds the total amount of their own loans. Output the enterprise name, customer ID, total external guarantees, total own borrowings, and the difference between total external guarantees and total own borrowings, sorted in descending order by the difference (external guarantee amount refers to the guaranteed amount under guarantee commitments; total own borrowings are aggregated based on the credit contract amounts where the customer is the borrower).",
  "BRB2-0283": "List employees who are currently active staff members and also have obtained credit agreements as borrowers, showing employee name, employee ID, and the number of credit agreements, sorted in descending order by the number of agreements.",
  "BRB2-0284": "Identify loan contracts marked as unsecured (credit) but having guarantee coverage records, which is an internal inconsistency. Output the contract number, borrower number, guarantee method, and total guarantee coverage amount, sorted in descending order by total guarantee coverage amount.",
  "BRB2-0285": "Find records where the guarantee coverage amount of a single guarantee contract exceeds the borrower's contract amount. Output the guarantor name, borrower name, contract amount, and guarantee coverage amount, sorted by guarantee coverage amount in descending order.",
  "BRB2-0286": "For each individual borrower, aggregate their total outstanding principal balance of loans, and calculate the multiple of this total balance relative to their personal profile annual income. Output the borrower name, customer ID, total principal balance, annual income, and the multiple, keeping only borrowers whose multiple exceeds two, sorted by the multiple in descending order, and limit the results to the top 200 records (round the multiple to two decimal places).",
  "BRB2-0287": "List the fund transfers made from bank employees' personal accounts to corporate customer accounts, showing the employee name, receiving company name, number of transfers, and total transfer amount, sorted by total transfer amount in descending order, and return the top 20 records.",
  "BRB2-0288": "Identify employees of our bank who hold the role of credit account manager and also have their own loans with the bank, outputting employee name, operator ID, permission level, and the count of self-loan contracts, sorted in descending order by the count of self-loan contracts (credit account manager refers to operators whose type is credit handling officer).",
  "BRB2-0289": "Identify accounts co-held by bank employees and corporate clients, and output the employee name, institution name, employee customer ID, and the number of involved corporate accounts, sorted in descending order by that count.",
  "BRB2-0290": "Identify loan drawdowns where the funds were transferred into accounts held by the bank's own employees, and output the employee name, loan drawdown number, drawdown amount, and drawdown date, sorted by drawdown amount in descending order (only include accounts where the employee is the primary account holder).",
  "BRB2-0291": "For individual borrowers, identify those whose total outstanding loan principal exceeds twice their annual income, and output the borrower name, customer ID, annual income, total outstanding loan principal, and debt-to-income multiple, sorted by the debt-to-income multiple in descending order.",
  "BRB2-0292": "For individual borrowers, aggregate the total outstanding principal and interest (sum of principal payable plus interest payable) across all their installment repayment plans, and calculate the multiple of this total outstanding principal and interest to their individual profile annual income (rounded to two decimal places). Output the borrower name, borrower customer ID, individual annual income, total outstanding principal and interest, and the multiple of annual income, sorted in descending order by the multiple of annual income and ascending order by customer ID, and return only the top 50 records.",
  "BRB2-0293": "For each loan product category, calculate the total number of overdue unpaid installments and the total overdue principal amount. Output the product category name, the total overdue installments, and the total overdue principal, sorted in descending order by the total overdue principal.",
  "BRB2-0294": "For each month, calculate the total number of transactions and the total amount for cash ('现金') transactions and transfer ('转账') transactions separately. Output the month, transaction category, transaction count, and total amount, sorted in ascending order by month and then by category.",
  "BRB2-0295": "For each account-opening institution, classify all time deposits into three pools based on the number of days from the maturity date to the audit reference date (2026-06-30): expired (maturity date earlier than the reference date), maturing within 90 days (0 to 90 days), and maturing after 90 days (more than 90 days). For each institution, count the number of time deposits in each pool. Retain only those institutions with at least 20 expired time deposits. Output the institution name, the count of expired deposits, the count of deposits maturing within 90 days, and the count of deposits maturing after 90 days, sorted by the expired count in descending order and then by the institution name in ascending order.",
  "BRB2-0296": "Count the number of joint accounts held by multiple customers under each business unit, and output the business unit ID, business unit name, and the joint account count, sorted in descending order by the joint account count.",
  "BRB2-0297": "For bank accounts that have both incoming transfers and outgoing transfers, compare their cumulative incoming transfer amount with cumulative outgoing transfer amount, and identify the top 20 accounts with the highest net inflow amount (total incoming minus total outgoing). Output the account number, number of incoming transfers, total incoming transfer amount, total outgoing transfer amount, and net inflow amount (rounded to two decimal places), sorted in descending order by net inflow amount and ascending order by account number.",
  "BRB2-0298": "For each handling business unit, calculate the total overdue principal balance of loans, and output the business unit code, business unit name, number of overdue loans, and total overdue principal, sorted in descending order by total overdue principal (an overdue loan is defined as one whose overdue principal in the loan balance snapshot is greater than zero).",
  "BRB2-0299": "For each handling business outlet unit, count the number of overdue unpaid installment periods, and output the business unit number, business unit name, and the number of overdue installment periods, sorted in descending order by the number of overdue installment periods.",
  "BRB2-0300": "For each handling business outlet unit, summarize loan drawdown activity, and output the business unit number, business unit name, total number of drawdowns, and total drawdown amount, sorted in descending order by total drawdown amount.",
  "BRB2-0301": "For time deposits in an active status, classify them into high, medium, and low tiers based on their annualized interest rate (a rate of at least 3% is high, a rate of at least 2.4% but below 3% is medium, and anything below 2.4% is low). For each tier, count the number of accounts and calculate the average opening principal. Keep only tiers with fewer than 120 accounts. Output the tier, account count, and average opening principal, sorted by average opening principal in descending order and then by tier in ascending order.",
  "BRB2-0302": "Count the number of loans in the installment repayment plan that are already overdue and whose total overdue principal exceeds 120 million CNY, along with the corresponding total number of overdue installments and the total overdue principal amount, and output the loan number, the number of overdue installments, and the total overdue principal, sorted in descending order by the total overdue principal.",
  "BRB2-0303": "For each lending institution, calculate the total number of overdue installments and the total accrued interest payable in the installment repayment plans of loans disbursed to customers under its jurisdiction. Retain only institutions with at least 30 overdue installments. Output the institution name, total overdue installments, and total interest, sorted by overdue installments in descending order.",
  "BRB2-0304": "Statistics on installment repayment plan defaults for self-funded payment versus entrusted payment methods: output the Chinese name of the payment method, the corresponding number of overdue unpaid installments, and the total overdue principal; retain only payment methods with more than 450 overdue installments, and sort by total overdue principal in descending order.",
  "BRB2-0305": "For collateral that is still valid, calculate the maximum pledged amount and the maximum appraised value based on their external appraised value, retain only collateral whose pledge ratio (maximum pledged amount divided by maximum appraised value) is between 50 percent and 98 percent, and output the collateral ID, maximum pledged amount, and maximum appraised value, sorted by maximum appraised value in descending order.",
  "BRB2-0306": "For each institution, count the number of loans with installment repayment overdue, keep only institutions with an overdue loan count of at least 240, output the institution name and the overdue loan count, sorted by the overdue loan count in descending order.",
  "BRB2-0307": "List the installments in the installment repayment plan that have experienced overdue non-repayment and where the current period's principal due exceeds 90 million CNY. Output the loan number, installment sequence number, principal due, and interest due, sorted by principal due in descending order.",
  "BRB2-0308": "For loans with installment repayment plans that have overdue unpaid installments, count the set of loans where the total current outstanding principal balance does not exceed 50 million CNY and the number of overdue unpaid installments is at least two. Output the loan number, number of overdue installments, and current principal balance, sorted in descending order by current principal balance.",
  "BRB2-0309": "For each exposure group, count the number of members that have obtained a loan from the bank and the number of members that have not obtained a loan, and output the group number, group name, count of members with loans, and count of members without loans, sorted in descending order by the count of members with loans.",
  "BRB2-0310": "Find transfer transactions where the payment side is a bank employee's primary controlled account and the receiving side is a corporate customer's primary controlled account. Output the transaction serial number, business date, amount, and institution name, sorted by amount in descending order, and limit the results to the top 200 records.",
  "BRB2-0311": "For each employee of our bank who serves as the guarantee contract manager, count the number of guarantee contracts they manage and sum the total guaranteed amount. Output the employee ID, employee name, number of managed guarantee contracts, and total managed guaranteed amount, sorted in descending order by the total managed guaranteed amount.",
  "BRB2-0312": "Compare by institution the total credit limit, cumulative loan drawdown amount, and net capital; calculate the ratio of drawdown amount to net capital. Output the institution name, total credit limit, total drawdown amount, net capital, and the drawdown-to-net-capital ratio, keeping only institutions whose cumulative drawdown amount exceeds net capital, sorted in descending order by the drawdown-to-net-capital ratio (ratio rounded to four decimal places).",
  "BRB2-0313": "Find guarantee contracts where the total guarantee amount provided by guarantors is less than the guarantee amount specified in the guarantee contract. Output the guarantee contract number, the specified guarantee amount, the number of guarantors, and the total guarantee amount, sorted in descending order by the total guarantee amount. Only include valid guarantee commitments, and only consider guarantee contracts of the type 'Guarantee Guarantee'.",
  "BRB2-0314": "List the credit facility records for revolving credit facilities, outputting the credit facility number, credit limit, and facility status name, sorted by credit limit from highest to lowest (the facility status name is taken from the status code table for the credit contract entity).",
  "BRB2-0315": "For each financial institution, count the number of credit line records with a revolving credit facility and a credit limit exceeding 500 million CNY, and sum their credit limits. Output the institution name, record count, and total credit limit, sorted by total credit limit in descending order.",
  "BRB2-0316": "For each institution, count the number of revolving credit facility records and sum the total credit limits. Keep only institutions with more than twelve revolving credit facility records. Output the institution name, record count, and total credit limit, sorted by total credit limit in descending order.",
  "BRB2-0317": "For institutions where the total credit limit under the same credit type has exceeded 2 billion CNY due to credit line usage, calculate the sum of their credit limits, and output the institution name, credit type code, and total credit limit, sorted in descending order by the total credit limit.",
  "BRB2-0318": "Count the number of credit limit records where the credit limit exceeds 300 million CNY, grouped by credit type, and output the credit type and the record count, sorted by the record count in descending order.",
  "BRB2-0319": "For each credit agreement issuing institution, count the number of distinct credit limit records associated with signed credit agreements. Output the institution name and the count of credit limit records, sorted in descending order by the count of credit limit records.",
  "BRB2-0320": "Calculate the total credit limit for each institution's revolving credit facility, retaining only institutions whose total limit exceeds 5 billion CNY, and output the institution name and total limit, sorted by total limit in descending order.",
  "BRB2-0321": "Find the credit facility record with the highest credit limit for each borrower (in case of ties, take the one with the smallest facility number), and output the borrower number, the maximum credit limit, and the corresponding credit facility type, sorted by the maximum credit limit in descending order, and return only the top 200 records.",
  "BRB2-0322": "For each institution, calculate the total principal of time deposit account openings and provide a ranking, along with the average principal per transaction. Output the rank, institution name, total principal, and average principal per transaction, sorted by rank in ascending order.",
  "BRB2-0323": "For each payment method, count the number of loan drawdown records, and output the Chinese name of the payment method and the record count, sorted by the record count in descending order.",
  "BRB2-0324": "Calculate the total outstanding loan principal balance under entrusted payment and self-payment methods, output the Chinese name of the payment method and the total principal balance, sorted in descending order by the total principal balance.",
  "BRB2-0325": "For each payment method, calculate the total loan drawdown amount and the number of drawdown transactions. Keep only payment methods with more than 1,100 drawdown transactions. Output the Chinese name of the payment method, the number of drawdown transactions, and the total drawdown amount, sorted by total drawdown amount in descending order.",
  "BRB2-0326": "Summarize the total instruction amount for priced transfer instructions by payment method, keeping only payment methods whose total instruction amount is below 1 trillion CNY, and output the Chinese name of the payment method, the number of instructions, and the total instruction amount, sorted in descending order by total instruction amount.",
  "BRB2-0327": "List the instructions in the pricing instructions where the instruction amount exceeds 220 million CNY, and output the Chinese name of the payment method, the instruction amount, and the instruction status, sorted by instruction amount in descending order.",
  "BRB2-0328": "List customers who are individual clients and are not the primary holder of any account under their name. Group the results by customer segment, count the number of customers in each segment, and keep only segments with a count of less than 50. Output the customer segment and the customer count, sorted by customer count in descending order and then by customer segment in ascending order.",
  "BRB2-0329": "For each account-opening business unit, count the number of accounts opened and the number of holder records corresponding to accounts in that unit. Output the business unit name, account count, and holder record count, sorted by holder record count in descending order, and return only the top 200 rows.",
  "BRB2-0330": "First, divide wealth management products currently in the \"on-sale\" status into four equal groups based on actual fundraising amount, sorted from highest to lowest. Then, count the number of products in each group whose minimum holding period is greater than zero. Keep only the groups where this product count is between 31 and 33, inclusive. Output the group sequence number and the product count, sorted by group sequence number in ascending order.",
  "BRB2-0331": "For loans with a revolving credit facility type and entrusted payment method, calculate the total revolving credit limit, and output the total revolving credit limit and the number of disbursements, sorted in descending order by the total revolving credit limit.",
  "BRB2-0332": "For each payment method, count the number of pricing instructions in pending execution status, and output the Chinese name of the payment method and the count of pending execution instructions, sorted in descending order by the count of pending execution instructions.",
  "BRB2-0333": "List all financing instrument type codes and their Chinese names from the financing instrument type code table, outputting the financing instrument type code and Chinese name, sorted by Chinese name.",
  "BRB2-0334": "List all status codes and their Chinese names from the entity status code table that belong to the loan drawdown entity, output the status code and Chinese name, ordered by status code.",
  "BRB2-0335": "Count the number of distinct loan drawdowns for each status in the entity status code table, output the Chinese status name and the drawdown count, sorted by the drawdown count in descending order.",
  "BRB2-0336": "Cross-join the financing instrument type code table with the entity status code table, and output every combination of the financing instrument Chinese name and the entity status Chinese name, sorted by the financing instrument Chinese name and then by the status Chinese name (for entity status, only take the status codes applicable to the loan drawdown entity).",
  "BRB2-0337": "Count the number of loan drawdowns by their status in the entity status code table, keeping only those with a charged-off status, and output the Chinese name of the current status and the number of drawdowns, sorted in descending order by the number of drawdowns.",
  "BRB2-0338": "Count the number of large-value payment transactions with a single transaction amount of no less than 30 million CNY, grouped by different acceptance channels, and keep only channels with a transaction count of less than 1,200. Output the transaction channel and the transaction count, sorted by transaction count in descending order and transaction channel in ascending order.",
  "BRB2-0339": "For loan drawdowns that were disbursed via entrusted payment and have a settled status, calculate the total disbursed amount and the average disbursed amount. Output the Chinese name of the payment method, the total disbursed amount, and the average disbursed amount, sorted in descending order by the total disbursed amount.",
  "BRB2-0340": "For each borrowing entity, count the number of credit facility records and sum the total credit limit, keeping only those borrowing entities with more than three credit facility records. Output the borrowing entity ID, the credit facility record count, and the total credit limit, sorted in descending order by the total credit limit.",
  "BRB2-0341": "For each business unit, count the number of active operators configured, and output the business unit ID, business unit name, total operator count, and the number of operators with senior permissions, sorted by the senior permission count in descending order.",
  "BRB2-0342": "Count the number of credit customer managers assigned to each business unit, and output the business unit code, business unit name, and the number of credit customer managers, sorted in descending order by the number of credit customer managers.",
  "BRB2-0343": "Regulatory inspection requires identifying borrowers who have both non-performing (substandard, doubtful, loss) loan drawdowns and other drawdowns still classified as non-non-performing under the same borrower, in order to determine whether there is concealment of non-performing assets by failing to downgrade the entire exposure despite cross-default. Output the debtor number, debtor name, the total number of drawdowns under the debtor, and the number of non-performing drawdowns among them, sorted by total drawdown count in descending order, and for ties, by debtor number in ascending order.",
  "BRB2-0344": "Regulatory verification requires screening for loan receipts where the principal has been overdue for more than 90 days, yet the five-tier classification has not yet been categorized as non-performing; such loan receipts represent delayed adjustments in risk classification that conceal actual non-performing assets. Output the loan receipt number, disbursed amount, number of days the principal has been overdue, and the five-tier classification name, sorted by the number of days the principal has been overdue in descending order, and for ties, by loan receipt number in ascending order.",
  "BRB2-0345": "Regulatory review requires identifying loan drawdowns whose principal has been overdue for more than 30 days but are still classified as normal, indicating that their classification does not reflect the deterioration in risk. Output the drawdown number, five-tier classification name, principal overdue days, and overdue principal, sorted by principal overdue days in descending order, and for drawdowns with the same overdue days, sorted by drawdown number in ascending order.",
  "BRB2-0346": "For regulatory review, count the number of cross-default customers at each institution where the same debtor has both non-performing and performing loan notes, to identify the scale of institutions masking non-performing assets through selective classification. Output the institution name and the number of cross-default customers for that institution, sorted by customer count in descending order, and for ties, by institution name in ascending order.",
  "BRB2-0347": "For regulatory review, calculate the loss reserve coverage ratio (provision already made divided by required provision) for each individual loan drawdown that has been classified as substandard, doubtful, or loss (i.e., non-performing). Identify the drawdowns with the lowest coverage ratios and clearly insufficient provisions. Output the drawdown number and the coverage ratio, sorted by coverage ratio in ascending order; where coverage ratios are equal, sort by drawdown number in ascending order.",
  "BRB2-0348": "For regulatory review, by institution, count the number of loan drawdowns that are in stage 2 of expected credit losses (significant increase in credit risk) and whose loss provision coverage ratio (provision already made divided by provision required) is below 0.5, to identify institutions with weak provisioning for stage 2 assets. Output the institution name and the count of drawdowns with insufficient coverage, sorted by count in descending order, and for ties, by institution name in ascending order.",
  "BRB2-0349": "Regulatory review requires a loan-by-loan examination of loan drawdowns in the loss stage (Stage 3) to identify the gap between the required and already-accrued loss provisions, and to flag drawdowns where a provision shortfall exists. Output the drawdown number, the provision stage name, and the provision shortfall amount, sorted by the provision shortfall in descending order; where shortfalls are equal, sort by the drawdown number in ascending order.",
  "BRB2-0350": "Regulatory verification requires calculating the total provision shortfall for each institution, defined as the gap where the provision already accrued is less than the required provision, to assess the overall adequacy of provision accruals across institutions. Output the institution name and the total provision shortfall amount, sorted by the total shortfall in descending order; if the shortfalls are equal, sort by institution name in ascending order.",
  "BRB2-0351": "List accounts that are in a dormant status, belong to the savings category, and have no secondary holders registered, and output the account number, account subtype, and book balance, sorted by book balance in descending order.",
  "BRB2-0352": "Count the number of active fixed employees holding each job role, keeping only roles with a count of at least 2 and excluding the role of \"relationship manager\"; output the job role and the corresponding count, sorted by count in descending order and then by job role in ascending order.",
  "BRB2-0353": "Please count the number of individual profile customers with annual income exceeding 1 million CNY, grouped by customer tier, and output the customer tier and customer count, sorted by customer count in descending order; when counts are equal, sort by customer tier in ascending order.",
  "BRB2-0354": "For entrusted management assets invested in restricted industries, aggregate the asset count by major asset category, retaining only categories with a count of less than thirty-three, and output the major asset category and asset count, sorted in descending order by asset count and ascending order by major asset category.",
  "BRB2-0355": "For individual customers with a credit limit, calculate the ratio of their total credit limit to annual income (i.e., debt service ratio), filter for customers whose debt service ratio is greater than three times, output customer ID, annual income, total credit limit, and debt service ratio, sorted by debt service ratio in descending order; when ratios are equal, sort by customer ID in ascending order, and only take the top 10 records (debt service ratio rounded to two decimal places).",
  "BRB2-0356": "Please count the customers who are public officials (with the politically exposed person indicator marked as yes), grouped by employment sector. Output the employment sector and the customer count, sorted by customer count in descending order; when counts are equal, sort by employment sector in ascending order.",
  "BRB2-0357": "Find all loan drawdowns where none of the installment repayment plans under the borrower have any settled installments (indicating the borrower may have never repaid normally), and output the drawdown number, sorted by drawdown number in ascending order, limited to the first 200 records.",
  "BRB2-0358": "For individual customers who have credit contracts, calculate the ratio of their total credit contract amount to annual income, filter for customers whose total contract amount exceeds five times their annual income, and output the customer ID, total contract amount, annual income, and debt service ratio, sorted by debt service ratio in descending order; when tied, sort by customer ID in ascending order, and return only the top 10 records.",
  "BRB2-0359": "Please count the number of individual customers under the occupation and employment sector portfolio, and output the occupation code, employment sector, and customer count, sorted by customer count in descending order; when counts are equal, sort by occupation code in ascending order, and then by employment sector in ascending order.",
  "BRB2-0360": "Please count the number of individual customers with annual income below 150,000 CNY, grouped by the business unit to which the customers belong. Output the business unit code, business unit name, and customer count, sorted in descending order by customer count; when counts are equal, sort in ascending order by business unit name.",
  "BRB2-0361": "For each individual customer with a credit limit, rank them by total credit limit in descending order, calculate the ratio of their total credit limit to annual income, and output the rank, customer ID, total credit limit, and debt service ratio. Select only the top 5 customers by rank and sort them by total credit limit in descending order.",
  "BRB2-0362": "Please count the number of individual customers and their average annual income, grouped by employment sector, for the sectors of financial institutions or securities, and output the employment sector, customer count, and average annual income, sorted by average annual income in descending order; when incomes are equal, sort by employment sector in ascending order.",
  "BRB2-0363": "For each institution type, count the number of institutions included in the regulatory report and calculate their maximum tier 1 capital. Keep only institution types whose maximum tier 1 capital exceeds 20 billion CNY. Output the institution type, institution count, and maximum tier 1 capital, sorted by institution count in descending order and institution type in ascending order.",
  "BRB2-0364": "Please count the number of issued debit cards under each card status, and output the card status and the issued card count, sorted in descending order by the issued card count; when counts are equal, sort in ascending order by card status.",
  "BRB2-0365": "Count the number of cash transactions and the total amount where a credit card settlement account is used as the payer transfer-out account, grouped by the business unit to which the cardholder belongs. Output the business unit code, business unit name, transaction count, and total amount (rounded to two decimal places), sorted by total amount in descending order and business unit name in ascending order.",
  "BRB2-0366": "Retrieve cash transactions where the credit card settlement account was used as the payment transfer-out account, along with the corresponding credit card records. Output the transaction ID, bank card ID, cardholder ID, transaction date, and transaction amount, sorted by transaction amount in descending order, then by transaction ID in ascending order, and then by bank card ID in ascending order, and return only the first 10 records.",
  "BRB2-0367": "For loan drawdowns with principal overdue days between 150 and 250 days that have been provisioned at stage 3, calculate the maximum overdue days and the maximum overdue principal for each drawdown, keep only those drawdowns whose average overdue principal exceeds 2 million CNY, and output the drawdown number, maximum overdue days, and maximum overdue principal, sorted by maximum overdue days in descending order.",
  "BRB2-0368": "Please count, for each credit card holder, the number and total amount of cash transactions (suspected cash-out), filter for holders with more than five cash transactions, and output the holder ID, cash transaction count, and total amount, sorted by cash transaction count in descending order; when counts are equal, sort by total amount in descending order, with amounts rounded to two decimal places.",
  "BRB2-0369": "Summarize the book balance total of the primary controlling accounts under customers in each customer tier, and provide the balance ranking for each tier. Output the customer tier, total book balance, and ranking, sorted by ranking in ascending order.",
  "BRB2-0370": "For credit guarantees registered under the guarantee method, calculate the total guaranteed amount under all guarantee commitments for each guarantee contract, retaining only those guarantees where the total guaranteed amount is still less than their secured amount. Output the guarantee contract number, secured amount, and total guaranteed amount, sorted in ascending order by total guaranteed amount.",
  "BRB2-0371": "Please count the number of issued cards for each bank card holder, filter for holders with more than three cards, and output the holder ID and card count, sorted by card count in descending order; when counts are equal, sort by holder ID in ascending order.",
  "BRB2-0372": "Compare the average single-transaction amount for cash transactions between credit cards and debit cards. Output the card type name, number of transactions, and average single-transaction amount, sorted by average single-transaction amount in descending order; when amounts are equal, sort by type name in ascending order. Round the amount to two decimal places.",
  "BRB2-0373": "Count the number and average amount of settled, non-cash payment transactions by channel, keeping only channels whose average amount exceeds 11.78 million CNY, and output the transaction channel, transaction count, and average amount, sorted by average amount in descending order and transaction channel in ascending order.",
  "BRB2-0374": "Find accounts whose book balance exceeds three times the average book balance of their account-opening institution, suspected of abnormal fund concentration. Output the institution name, account number, book balance, institution average balance, and excess amount, sorted by excess amount in descending order.",
  "BRB2-0375": "List the time deposits whose deposit maturity has already passed but which are still in a normal status, along with the corresponding account status, as they are suspected of not being redeemed or closed after maturity. Output the account number, maturity date, and account status, sorted by maturity date in descending order, and limit the results to the top 200 records.",
  "BRB2-0376": "Find time deposits with a term between thirty days and one year, where the account is still active. Output the account number, opening principal, opening date, maturity date, and term in days, sorted by term in days in descending order, and limit the results to the top 200 records.",
  "BRB2-0377": "For each collateral item, take the highest value from its historical appraisals, but only include collateral items that have been appraised two or more times. Output the collateral item number, name, and highest appraised value, sorted by highest appraised value in descending order.",
  "BRB2-0378": "List the wealth management products that are in the \"on-sale\" status and whose actual fundraising amount is less than half of the planned fundraising amount, outputting the product name, actual fundraising amount, and planned fundraising amount, sorted in descending order by actual fundraising amount and ascending order by product name.",
  "BRB2-0379": "Find individual customers holding two or more dormant accounts, output the customer ID and the number of dormant accounts, sort by the number of dormant accounts in descending order, and return only the top 200 records.",
  "BRB2-0380": "For each authorization level, count the total number of counter system operators, and break down the count into those registered in the two position types: executive supervision and credit review. Output the authorization level, total operator count, credit review position count, and executive supervision position count. Keep only levels where the total operator count is at least 2, and sort the results by total count in descending order, then by authorization level in ascending order.",
  "BRB2-0381": "Identify customers with large deposit-loan linkage: borrowers who both hold time deposits as the primary account holder at this bank with total time deposit opening principal of no less than 10 million CNY, and have an outstanding loan principal balance at this bank. Output the borrower ID, borrower name, outstanding loan balance, total time deposit principal, and the deposit-loan coverage multiple (total time deposit principal divided by outstanding loan balance, rounded to two decimal places), sorted by coverage multiple in descending order and borrower ID in ascending order.",
  "BRB2-0382": "Identify customers with inverted deposit-loan scale anomalies: for corporate customers, compare the total book deposit balance in settlement and savings accounts against the total outstanding loan principal balance with the bank, retaining only customers whose deposit balance exceeds their loan balance and whose loan balance is greater than zero. Output the customer ID, customer name, deposit balance, and loan balance, sorted by deposit balance in descending order and customer ID in ascending order.",
  "BRB2-0383": "Identify borrowers whose loans have already experienced principal overdue but who still hold large time deposits at the same institution, reflecting abnormal fund arrangements such as deposit-backed lending or loan fund round-tripping. Output the debtor number, debtor name, total amount of time deposits held, and the number of deposit certificates, sorted by time deposit amount in descending order, and for equal amounts, by debtor number in ascending order.",
  "BRB2-0384": "Regulatory review requires institution-level statistics on the overall scale of \"deposit-loan linkage\" business: for each institution, the total outstanding balance of loans extended to borrowers who also hold time deposits at the same bank, along with the number of linked customers involved. Output the institution name, the number of linked customers, and the total linked loan balance, sorted by the total linked loan balance in descending order, and for ties, by institution name in ascending order.",
  "BRB2-0385": "Identify \"guarantee period gap\" risk in active credit contracts: through the guaranteed principal claim bridge table linking guarantee contracts with active credit contracts, find bridge records where the guarantee contract expiry date is earlier than the guaranteed credit contract maturity date, and output the guaranteed principal claim bridge number, credit contract number, guarantee contract number, guarantee contract expiry date, and credit contract maturity date, sorted by credit contract maturity date from earliest to latest and by guaranteed principal claim bridge number from smallest to largest.",
  "BRB2-0386": "Regulatory review requires statistics by institution and guarantee method on the number of contracts with maturity mismatch where the guarantee contract maturity date is earlier than the credit facility contract maturity date, to identify institutions and guarantee methods with high exposure to guarantee lapse risk. Output the institution name, guarantee method, and mismatched contract count, sorted by mismatched contract count in descending order, then by institution name and guarantee method in ascending order.",
  "BRB2-0387": "Identify cases of \"multiple pledges on one collateral and over-pledging\": the same collateral is repeatedly pledged in multiple guarantee contracts, and its latest appraised value is lower than the total pledged amount across all such contracts, constituting over-pledging. Output the collateral number, collateral identifier, latest appraised value, total pledged amount, and over-pledged amount, sorted by over-pledged amount in descending order, and for ties, by collateral number in ascending order.",
  "BRB2-0388": "Identify collaterals that are pledged in multiple guarantees, where the total pledged amount exceeds the lowest appraised value among all appraisals, to assess the sufficiency of collateral value in covering debts. Output the collateral number, total pledged amount, lowest appraised value, and the excess pledged amount, sorted by the excess pledged amount in descending order, and for ties, by the collateral number in ascending order.",
  "BRB2-0389": "Identify collaterals repeatedly used in multiple guarantees, and assess how \"one collateral pledged multiple times\" amplifies collateral concentration. Output the collateral number, collateral identifier, the number of times the collateral is referenced, and the number of distinct related guarantee contracts, sorted by the number of references in descending order, and for ties, by collateral number in ascending order (only count collateral-related records with an active status, and include only those with at least two references).",
  "BRB2-0390": "Identify anomalous guarantee records where a single valid guarantee commitment amount from a guarantor exceeds the total actual loan drawdown amount under the corresponding credit contract: first aggregate the actual total loan drawdown amount by credit contract from loan drawdown notes, then link guarantee contracts and valid guarantor commitments through the secured principal claim bridge table, and find records where the single guarantee commitment amount is greater than the total actual loan drawdown amount of the corresponding credit contract. Output the guarantor customer number, guarantor name, credit contract number, guarantee commitment amount, and the total actual loan drawdown amount for that contract (rounded to two decimal places), sorted by guarantee commitment amount in descending order, then by guarantor customer number in ascending order, and then by credit contract number in ascending order.",
  "BRB2-0391": "Identify borrowers whose loans have already experienced principal overdue, yet who still hold active credit cards and continue to incur card purchases or cash withdrawals, indicating a failure to promptly suspend card usage and a widening risk exposure. Output the debtor ID, debtor name, credit card number, transaction reference number, and transaction amount, sorted by transaction amount in descending order, then by debtor ID, card number, and transaction reference number in ascending order, and return the top 100 records with the largest transaction amounts.",
  "BRB2-0392": "Identify borrowers who hold at least one active credit card and whose loans at this bank have already experienced principal overdue, along with the number of active credit cards held by each such borrower. Output the cardholder number and the count of active credit cards, sorted by the count of active credit cards in descending order, and for ties, by cardholder number in ascending order.",
  "BRB2-0393": "For regulatory review, at the institution level, calculate the total amount and number of transactions for credit cards issued to borrowers whose loans have already experienced principal overdue, where card consumption or cash withdrawal transactions still occurred under those borrowers' names, in order to assess the scale of card usage by overdue customers whose cards have not been blocked. Output the institution name, the total card consumption amount for overdue customers, and the number of transactions, sorted by total consumption amount in descending order, and when amounts are equal, sort by institution name in ascending order.",
  "BRB2-0394": "Identify \"insufficient guarantee coverage\" for regulatory review: where a valid credit facility contract is covered by valid guarantee contracts, but the total guaranteed coverage amount is less than the credit facility contract amount, indicating that part of the claim is not fully covered. Output the credit facility contract number, debtor number, credit facility contract amount, total guarantee coverage, and coverage shortfall, sorted by coverage shortfall in descending order, and for ties, by credit facility contract number in ascending order, returning the top 100 records with the largest shortfalls.",
  "BRB2-0395": "Identify fully unsecured credit facilities: credit contracts that are currently active with an amount greater than zero, yet have no active guarantee coverage record of any kind, meaning the claim has no collateral or guarantee support whatsoever. Output the credit contract number, debtor number, and credit contract amount, sorted by credit contract amount in descending order, and for ties, by credit contract number in ascending order, taking the top 100 records by amount.",
  "BRB2-0396": "For regulatory inspection purposes, by institution, among non-performing loan instruments already classified as substandard, count the number of loan instruments where the loss provision actually made is lower than the required provision, so as to identify institutions with insufficient provisioning for substandard assets. Output the institution name, the five-category classification name, and the count of loan instruments with insufficient provisioning, sorted by the count in descending order, and for ties, by institution name in ascending order.",
  "BRB2-0397": "Identify loan drawdowns that exceed the credit limit by at least four times, meaning the current outstanding principal balance of the drawdown is at least four times the credit amount of its associated credit agreement, indicating that actual usage significantly surpasses the contractual limit. Output the debtor number, drawdown number, loan balance, credit amount, and the balance multiple, sorted by the balance multiple in descending order, and for ties, by drawdown number in ascending order. Include cases where the multiple is exactly four, and round the balance multiple to two decimal places.",
  "BRB2-0398": "For regulatory review, statistics must be compiled by each non-performing loan classification level (substandard, doubtful, loss) for the current outstanding principal balance and the number of loan drawdowns, in order to assess the total exposure of each non-performing level. Output the classification name, the number of loan drawdowns, and the total principal amount, sorted by the number of loan drawdowns in descending order; where the counts are equal, sort by the classification name in ascending order.",
  "BRB2-0399": "Regulatory review requires, by institution, the count of loan drawdowns where principal is overdue by more than 90 days but has not been downgraded to substandard, to identify institutions with lagging classification adjustments. Output the institution name and the count of such overdue but not downgraded drawdowns, sorted by count in descending order, and for ties, by institution name in ascending order.",
  "BRB2-0400": "Regulatory review requires statistics by institution and by five-tier classification on the number of non-performing loan drawdowns where the loss provision already recognized exceeds the required provision amount, and the amount of excess provision, to identify institutions with imprudent loss provisioning (excess provisioning, profit manipulation). Output institution name, five-tier classification name, number of excess provision drawdowns, and total excess provision amount, sorted by total excess provision amount in descending order, then by institution name and five-tier classification name in ascending order.",
  "BRB2-0401": "Join the guarantee contract and credit agreement through the guarantee main claim bridge table, and identify records where the covered amount of the guaranteed claim is lower than the credit agreement amount. Output the guarantee contract number, credit agreement number, covered amount of the guaranteed claim, credit agreement amount, and the shortfall amount (credit agreement amount minus covered amount, rounded to two decimal places), sorted by the shortfall amount in descending order.",
  "BRB2-0402": "Summarize the total guaranteed claim amount for each credit agreement linked through the guaranteed main claim bridge table, and compare it with the agreement's contract amount. Identify credit agreements where the total guaranteed amount is still lower than the contract amount. Output the agreement number, borrower number, contract amount, total guaranteed amount, and the shortfall amount, sorted by the shortfall amount in descending order. The shortfall amount is calculated as the contract amount minus the total guaranteed amount, rounded to two decimal places.",
  "BRB2-0403": "List the borrower ID, borrower name, and the total guaranteed claim amount for each borrower, where the total guaranteed claim amount obtained through the guaranteed main claim bridge table for all credit facilities under the borrower exceeds 400 million CNY. Only include borrowers whose total exceeds 400 million CNY. Sort the results by the total amount in descending order, and round the total amount to two decimal places.",
  "BRB2-0404": "For each institution, aggregate the total guaranteed principal amount and the number of guarantee contracts from valid guarantee contracts linked to the institution's credit agreements via the guaranteed principal bridge table. Output the institution name, the number of guarantee contracts, and the total guaranteed amount, sorted in descending order by the total guaranteed amount, with amounts rounded to two decimal places.",
  "BRB2-0405": "For each credit agreement, count how many guarantee contracts it is linked to (via the guaranteed principal claim bridge table), keep only those credit agreements linked to at least two guarantee contracts, and output the agreement number, agreement contract amount, and the count of linked guarantee contracts, sorted by the count of linked guarantee contracts in descending order, with the contract amount rounded to two decimal places.",
  "BRB2-0406": "List the unallocated collateral that has never been linked to any guarantee contract, i.e., collateral that cannot be associated with any guarantee contract through the collateral linkage table. Output the collateral number, collateral name, and collateral type, sorted in ascending order by collateral number.",
  "BRB2-0407": "For collateral that has both internal and external appraisals, take the highest appraised value from the internal appraisal records and the lowest appraised value from the external appraisal records, calculate the difference of the external lowest appraised value minus the internal highest appraised value, and output the collateral number, collateral name, internal highest appraised value, external lowest appraised value, and the difference (rounded to two decimal places), sorted by the difference in descending order.",
  "BRB2-0408": "For collateral that has both internal and external appraisals, take the highest appraised value from the internal appraisal records and the highest appraised value from the external appraisal records, identify the collateral whose external appraised value is lower than its internal appraised value, and output the collateral number, collateral name, highest internal appraised value, highest external appraised value, and the undervaluation difference (internal minus external), keeping only collateral where both highest appraisal values exist, sorted by the undervaluation difference in descending order, with amounts rounded to two decimal places.",
  "BRB2-0409": "Summarize the average value of internal appraisals and external appraisals by collateral type, and calculate the ratio of the external average value to the internal average value (external divided by internal, rounded to four decimal places). Keep only collateral types that have both internal and external appraisals. Output the collateral type, the average internal appraisal value, the average external appraisal value, and the external-to-internal value ratio, sorted by the value ratio in descending order. Round the average values to two decimal places.",
  "BRB2-0410": "For each collateral item, count the number of times it has been appraised, and assign a dense rank based on the appraisal count in descending order. Output the collateral ID, collateral name, appraisal count, and rank, keeping only collateral items with an appraisal count of at least 3. Sort the results by appraisal count in descending order and collateral ID in ascending order.",
  "BRB2-0411": "For each collateral item, retrieve its most recent appraised value and compare it with the total pledged guarantee amount under that collateral, identifying items with a coverage shortfall (i.e., the latest appraised value is insufficient to cover the total pledged amount). Output the collateral number, asset name, latest appraised value, total pledged amount, and coverage shortfall (rounded to two decimal places), sorted by coverage shortfall in descending order. Only include pledge relationships with an active status when summing the total pledged amount; exclude collateral items that have no active pledge relationships.",
  "BRB2-0412": "Summarize by collateral type the number of external appraisal records and the total external appraised value, outputting the collateral type, the number of external appraisals, and the total external appraised value, sorted in descending order by the total external appraised value, with amounts rounded to two decimal places.",
  "BRB2-0413": "List the top 10 guarantors by the total amount of currently valid guarantee commitments (status is active), showing the guarantor ID, guarantor name, and total guarantee commitment amount, sorted in descending order by the total amount, with amounts rounded to two decimal places.",
  "BRB2-0414": "Find guarantors who have both credit borrowings from our bank and provide external guarantees, compare their total valid external guarantee commitment amount with their total own loan contract amount, keep only those guarantors whose total external guarantee amount exceeds their total own loan amount, output the guarantor number, guarantor name, total own loan amount, and total external guarantee amount, sorted in descending order by total external guarantee amount, with amounts rounded to two decimal places.",
  "BRB2-0415": "Summarize the total guaranteed commitment amount of each guarantor under each guarantee contract, compare it with the secured claim amount of that guarantee contract, and identify guarantee contracts where the total guaranteed commitment amount is lower than the secured claim amount. Output the guarantee contract number, secured claim amount, number of guarantors, and total guaranteed commitment amount, sorted in descending order by total guaranteed commitment amount, with amounts rounded to two decimal places (only include guaranteed commitments with an active status).",
  "BRB2-0416": "Find over-guarantee cases where the guarantee commitment amount exceeds the secured claim amount of the guarantee contract to which it belongs. Output the guarantee contract number, secured claim amount, guarantor number, and guarantee commitment amount, sorted in descending order by the difference between the guarantee commitment amount and the secured claim amount, with amounts rounded to two decimal places.",
  "BRB2-0417": "Count individual customers who are public servants with an annual income of at least 300,000 CNY, group the results by customer segment, and output the customer segment and the customer count, sorted by customer count in descending order and then by customer segment in ascending order.",
  "BRB2-0418": "List all exposure groups and join the exposure group type lookup table, output the group ID, group name, Chinese exposure group type name, and the number of group members, sorted in descending order by the number of group members, and for groups with the same member count, sort in ascending order by group ID.",
  "BRB2-0419": "Summarize the number of groups and the distinct count of members for each Chinese exposure group type based on the exposure group type code table. Output the Chinese exposure group type name, the number of groups, and the distinct count of members, sorted by the distinct count of members in descending order.",
  "BRB2-0420": "Group by institution and the Chinese exposure group type name from the exposure group type code table, count the distinct number of group members, keep only institution-type combinations where the distinct member count is at least six, and output the institution name, the Chinese exposure group type name, and the distinct member count, sorted in descending order by the distinct member count.",
  "BRB2-0421": "For each group exposure category (in Chinese) and the managing institution, aggregate the total outstanding loan principal of group members at the bank, then compare it with the managing institution's net capital to calculate the exposure-to-net capital ratio. Output the institution name, the Chinese name of the exposure category, the total member loan balance, the institution's net capital, and the exposure ratio (monetary amounts rounded to two decimal places, ratio rounded to six decimal places), sorted in descending order by the exposure ratio.",
  "BRB2-0422": "Find member customers that belong to two or more different exposure groups, and output the member customer number, customer name, and the number of groups they belong to, sorted by the number of groups in descending order, and by member customer number in ascending order when the counts are the same.",
  "BRB2-0423": "Count the number of related-party relationship records for each Chinese relationship name according to the relationship type code table. Output the Chinese relationship name and the record count, sorted by record count in descending order; if counts are equal, sort by Chinese relationship name in ascending order.",
  "BRB2-0424": "Find entities that have a related-party relationship (excluding non-related parties ('非关联方')) and are also borrowing customers of this bank. Count the number of related-party relationships where they are one of the parties, and the number of their loan contracts. Output the entity ID, entity name, related-party relationship count, and loan contract count, sorted in descending order by the related-party relationship count.",
  "BRB2-0425": "Find the customers who are a party to a shadow shareholder related-party relationship and are also members of an exposure group. Output the customer ID, customer name, and the number of groups they belong to, sorted by the number of groups in descending order, and for ties, by customer ID in ascending order.",
  "BRB2-0426": "List the entities that act as the controlling party in actual controller relationships, along with the distinct count of their associated counterparties. Output the entity ID, entity name, and the distinct count of associated counterparties, sorted by the distinct count in descending order, and for ties, by entity ID in ascending order.",
  "BRB2-0427": "Find the cases where both parties in a related-party transaction relationship (excluding non-related parties ('非关联方')) have loan contracts at this bank, and output the relationship number, the subject number of one party, the subject number of the other party, the number of existing loan contracts of one party, and the number of existing loan contracts of the other party, sorted in descending order by the sum of the loan contract counts of both parties.",
  "BRB2-0428": "For regulatory review, calculate the \"unsecured gap days\" for credit facilities on a look-through basis: for each credit facility contract, identify the guarantee with the earliest guarantee expiry date among all guarantees under the same contract, then compare the interval in days between that guarantee expiry date and the facility maturity date to identify contracts where the guarantee lapses before the facility matures. Output the facility contract number, debtor number, facility maturity date, earliest guarantee expiry date, and unsecured gap days, sorted by facility maturity date in ascending order, and for identical maturity dates, further sorted by facility contract number in ascending order.",
  "BRB2-0429": "Identify collateral where the external valuation is significantly lower than the internal valuation: for the same collateral assessed under both internal and external standards, if the external valuation is lower than the internal valuation, it indicates that the internal assessment is overly optimistic and the collateral value may be inflated. Output the collateral number, collateral identifier, external valuation amount, internal valuation amount, and the percentage of external valuation relative to internal valuation, sorted by the external ratio in ascending order; when ratios are equal, sort by collateral number in ascending order.",
  "BRB2-0430": "Identify collateral assets that are \"booked but with mortgage not actually in place\": collateral assets with an active status that have no active collateral guarantee relationship record, indicating that mortgage registration or guarantee establishment has not been truly completed. Output the collateral number, collateral identifier, and collateral type, sorted by collateral number in ascending order.",
  "BRB2-0431": "Identify guarantors whose guarantee liability exceeds their own debt repayment capacity: calculate the total amount of active guarantee commitments under their name, compare it with their own loan exposure at this bank, retain only those guarantors whose total active external guarantee amount exceeds their own loan exposure, and output the guarantor ID, guarantor name, total active guarantee liability, own loan amount, and excess guarantee amount (rounded to two decimal places), sorted in descending order by excess guarantee amount (own loan exposure is taken as the sum of the current principal balance of the loan drawdowns under their name as the borrower).",
  "BRB2-0432": "Identify borrowers with \"installment backstop long-term risk\": borrowers whose loans have principal overdue for more than 90 days, while they still hold an active credit card, indicating the credit card has not been linked for payment suspension over the long term. Output the cardholder ID, cardholder name, credit card number, and card expiration date, sorted by card expiration date from earliest to latest, and for identical expiration dates, sort by card number in ascending order.",
  "BRB2-0433": "Identify potential \"loan fund round-tripping / borrowing to repay loans\" by tracing accounts that, after receiving a loan drawdown, are subsequently used to repay principal to the same bank; if the same account both receives the loan disbursement and makes a repayment transfer, it indicates circular fund flows. Output the transaction reference number, paying account, receiving account, transaction amount, and business date, sorted by transaction amount in descending order, and for equal amounts, by transaction reference number in ascending order, returning the top 100 records by amount.",
  "BRB2-0434": "Identify borrowers whose loans have already experienced principal overdue while they are still providing valid guarantees to external parties: through guarantee commitment records, find guarantors who have overdue loan drawdowns, and output the guarantor number, guarantor name, guarantee amount, and guarantee status, sorted by guarantee amount in descending order and guarantor number in ascending order (overdue means the guarantor, as a borrower in their own name, has loan drawdowns with principal overdue).",
  "BRB2-0435": "Regulatory review requires summarizing, by five-tier classification level, the loan drawdowns where allowance for expected credit losses at the loss stage (Stage 3) is insufficient, to identify the concentration of provisioning shortfalls across each non-performing tier. Output the five-tier classification name, the number of drawdowns with shortfalls, and the total shortfall amount, sorted by total shortfall amount in descending order, and for ties, by five-tier classification name in ascending order.",
  "BRB2-0436": "From the credit contract management business unit dimension, calculate the risk exposure of overdue loan drawdowns: join the overdue snapshot, loan drawdowns, credit contracts, and loan balance snapshot, and by credit contract management business unit, aggregate the distinct count of borrowers with overdue records and the total principal balance of these overdue drawdowns (rounded to two decimal places). Output the business unit code, business unit name, count of overdue borrowers, and total overdue drawdown principal balance, sorted by total overdue drawdown principal balance in descending order and business unit code in ascending order.",
  "BRB2-0437": "Identify loan drawdowns with abnormal overdue principal accounting: the current principal balance is greater than zero, while the cumulative overdue principal exceeds the current principal balance, indicating passive cross write-off or a mismatch between overdue amount and balance. Output the drawdown number, principal overdue days, overdue principal, current principal balance, and the ratio of overdue principal to current principal balance, sorted by this ratio in descending order, and for ties, by drawdown number in ascending order.",
  "BRB2-0438": "Calculate the average coverage utilization rate of valid guarantee contracts for the realization of guaranteed principal claims by institution: aggregate the guarantee amount of guarantee contracts and the covered credit amount linked via the bridge table, output institution name, total guarantee contract amount, total covered credit amount, and coverage percentage, sorted in ascending order of coverage utilization rate.",
  "BRB2-0439": "Regulatory review requires calculating, at the branch level, the loss provision coverage ratio for non-performing loan instruments: for each branch, the ratio of total provisioned loss reserves to total required provisions for substandard, doubtful, and loss-classified non-performing loan instruments, to identify branches with insufficient provision coverage. Output the branch (business unit) number, name, count of non-performing loan instruments, and provision coverage ratio, sorted by provision coverage ratio in ascending order, and for ties, by branch name in ascending order.",
  "BRB2-0440": "Identify wealth management products whose underlying assets, held through multi-layer nesting, ultimately belong to a final debtor who is also a corporate borrower with overdue loan receivables at the issuing bank (i.e., using wealth management funds to indirectly absorb the assets of the bank's overdue credit customers). Output the product name, underlying asset name, final debtor ID, and the total overdue principal of that debtor at the bank, sorted by product name in ascending order and total overdue principal in descending order.",
  "BRB2-0441": "For entrusted management assets classified under liability, aggregate the asset count by internal rating, retaining only ratings with a count between 25 and 30, and output the internal rating and asset count, sorted by asset count in descending order and internal rating in ascending order.",
  "BRB2-0442": "Find the non-standardized debt underlying asset management assets valued using the amortized cost method, where the external rating is unrated or inconsistent with the internal rating, and filter for assets whose external rating risk score is higher than the internal rating risk score (i.e., the external rating is worse than the internal rating or there is no external rating), based on the custom rating risk scores (AAA=1, AA+=2, AA=3, A+=4, A=5, BBB=6, unrated=7). Output the asset number, asset name, internal rating, and external rating, sorted in ascending order by asset number.",
  "BRB2-0443": "Summarize by guarantee method the number of guarantee contracts and the total guaranteed amount, linked via the guaranteed main claim bridge table to valid credit agreements, and output the guarantee method, the number of guarantee contracts, and the total guaranteed amount, sorted in descending order by the total guaranteed amount, with amounts rounded to two decimal places.",
  "BRB2-0444": "Conduct a review on whether collateral value is fully utilized: group by collateral, aggregate the latest appraised value and the total amount of pledged guarantees under it, and filter for collateral whose latest appraised value is more than twice the cumulative pledged amount. Output the collateral number, asset name, latest appraised value, total pledged amount, and remaining value headroom (latest appraised value minus total pledged amount, rounded to two decimal places), sorted in descending order by remaining value headroom.",
  "BRB2-0445": "Find credit agreements that are secured by both collateral and a third-party guarantee commitment (linked via the guaranteed principal claim bridge table), and output the agreement number, borrower name, contract amount, count of related collateral items, and count of guarantors, sorted by contract amount in descending order, with amounts rounded to two decimal places (only include guarantee agreements with an active status).",
  "BRB2-0446": "For each institution, aggregate the distinct count of members in its affiliated-client exposure groups and the total contract amount of these members at the bank, retaining only institutions with a distinct member count of at least five, and output the institution name, distinct member count, and total contract amount, sorted in descending order by total contract amount, with amounts rounded to two decimal places.",
  "BRB2-0447": "Find wealth management holdings whose book value exceeds fair value (i.e., holdings with an inverted book-to-fair value), and for each wealth management product output the product number, product name, total inverted amount, and the number of holdings constituting the inversion; keep only products with a total inverted amount greater than zero, and sort by total inverted amount in descending order, then by product number in ascending order.",
  "BRB2-0448": "Find wealth management products with a nesting depth of at least three levels, whose look-through underlying assets are issued by borrowers that have overdue loan receivables with our bank, and output the product name, underlying asset name, nesting depth, book value of the holding, and the total overdue principal of that issuer, sorted by nesting depth in descending order and holding number in ascending order (overdue loan receivables are limited to those with our bank, the issuing institution of the wealth management product).",
  "BRB2-0449": "Count the number of valid collateral-linked records for each collateral item where the collateral is registered as the first priority and the pledge rate exceeds 60%. Retain only those collateral items with at least two such records. Output the collateral ID, the count of first-priority valid records, and the count of records with a pledge rate exceeding 60%, sorted in descending order by the count of records exceeding 60%.",
  "BRB2-0450": "For collateral items that have both internal and external appraisals, compare the maximum values of the two appraisal types. Identify the collateral items where the external maximum value is higher than the internal maximum value. Output the collateral ID, name, internal maximum value, external maximum value, and the internal-to-external value ratio (rounded to four decimal places), sorted by the value ratio in descending order.",
  "BRB2-0451": "Output the name, total assets, total liabilities, net assets, and operating income of each banking institution, sorted by operating income in descending order (institutional financial data is stored in the financial snapshot table, with the entity number being \"PTY-\" followed by the institution number).",
  "BRB2-0452": "Calculate and output the asset-liability ratio (total liabilities divided by total assets, rounded to four decimal places) for each banking institution, sorted by the asset-liability ratio in descending order (institutional financial data is stored in the financial snapshot table, with the entity number being \"PTY-\" followed by the institution number).",
  "BRB2-0453": "Calculate and output the ratio of core Tier 1 capital to risk-weighted assets (core Tier 1 capital divided by risk-weighted assets, rounded to four decimal places) for each banking institution, sorted by this ratio in descending order.",
  "BRB2-0454": "Output the name of each banking institution, and its ratio of net capital to total assets (rounded to six decimal places), sorted by that ratio in descending order (the institution's financial data is stored in the financial snapshot table, whose entity number is \"PTY-\" followed by the institution number).",
  "BRB2-0455": "Output the institution name and net profit margin (net assets divided by operating revenue, rounded to four decimal places) for each institution whose net profit margin is below 0.85, sorted by net profit margin in ascending order.",
  "BRB2-0456": "Rank the banking institutions by total assets in descending order using a ranking function, and output the institution name, total assets, and rank, sorted by rank from highest to lowest.",
  "BRB2-0457": "List the institution name, operating revenue, and proportion (rounded to two decimal places) for institutions whose operating revenue accounts for more than 15% of the total operating revenue of all banking institutions, sorted by proportion in descending order (institution financial data is stored in the financial snapshot table, with the entity number being \"PTY-\" followed by the institution number).",
  "BRB2-0458": "Group by the valuation method of the underlying assets, output the count of underlying assets for each valuation method, and sort by the count in descending order.",
  "BRB2-0459": "For each guarantee type, calculate the proportion of guarantee shares whose guaranteed amount is lower than the secured amount within guarantee contracts, retain only those guarantee types where this proportion exceeds 80 percent, and output the guarantee type and the proportion, sorted by the proportion in descending order and by the guarantee type in ascending order.",
  "BRB2-0460": "Group by banking institution, and output the number of underlying assets where the internal rating and external rating are inconsistent for each institution, sorted by the count in descending order.",
  "BRB2-0461": "Group by the valuation method of the underlying assets, and output the total book value (rounded to two decimal places) of the wealth management product holdings verified through look-through for each method, sorted by the total in descending order.",
  "BRB2-0462": "For product holdings with a remaining term exceeding 200 days, aggregate the holding quantity by investment path, retaining only those paths with a total quantity of less than 352, and output the investment path and holding quantity, sorted by holding quantity in descending order and investment path in ascending order.",
  "BRB2-0463": "List the issuing institutions whose underlying assets are measured at fair value and have an external rating of \"no rating\", showing the institution name, the number of assets, the average annualized yield, and the total issuance amount; keep only institutions with at least 10 assets, and sort by total issuance amount in descending order.",
  "BRB2-0464": "For each banking institution, count the number of time deposit accounts opened and calculate the total principal amount (rounded to two decimal places). Output the institution name, the number of accounts, and the total principal amount, sorted by the total principal amount in descending order.",
  "BRB2-0465": "Output the number of certificates of deposit with an annualized fixed deposit interest rate above 3% for each banking institution, sorted by the count in descending order.",
  "BRB2-0466": "Count the number of counter operators and the corresponding number of employees for each authorization level among fixed-hire employees, keeping only levels with at least 10 employees, and output the authorization level, operator count, and employee count, sorted by operator count in descending order and authorization level in ascending order.",
  "BRB2-0467": "Count the number of time deposits maturing on or within 30 days after the audit reference date (2026-06-30), i.e., with days to maturity between 0 and 30 days from the reference date, grouped by the account-opening institution, and output the institution name and the count, sorted by the count in descending order.",
  "BRB2-0468": "For each account-opening institution, aggregate the cumulative opening principal and the number of opening transactions for time deposits, and use a row number function to rank the institutions by principal in descending order. Output the institution name, total principal, number of opening transactions, and rank, keeping only institutions with at least 15 opening transactions, and sort the results by rank in ascending order.",
  "BRB2-0469": "Assess the concentration of each wealth management product's holdings in a single underlying asset's ultimate debtor: calculate the market value of each product's holdings in each ultimate debtor, and determine its proportion of the product's total holdings market value. Retain only records where the proportion exceeds 30 percent, and output the product name, ultimate debtor number, the market value of holdings in that debtor, and the concentration ratio (as a percentage, rounded to two decimal places), sorted by the ratio in descending order and by product name in ascending order.",
  "BRB2-0470": "Calculate, for each institution, the total shortfall in loan impairment provisions (total required provision minus total provision already made) as a percentage of that institution's annual operating income. Output the institution number, the total shortfall, and the percentage of the shortfall relative to operating income, retaining only institutions where the percentage exceeds 5 percent, and sort in descending order by the percentage of the shortfall relative to operating income.",
  "BRB2-0471": "Calculate the ratio of the total under-provisioned loan impairment allowance to net assets for each institution: only include loan drawdowns where the provisioned amount is less than the required amount, output institution ID, institution name, total under-provisioned amount, net assets, and the percentage of under-provisioned amount to net assets (rounded to two decimal places), retain only institutions with under-provisioning, sort by percentage in descending order and institution ID in ascending order (institution financial data is stored in the financial snapshot table, with the entity ID being \"PTY-\" followed by the institution ID).",
  "BRB2-0472": "Calculate the density of risk-weighted assets as a percentage of total assets for each institution, and output it alongside the non-performing loan balance (i.e., the total overdue principal), showing the institution ID, the risk-weighted assets as a percentage of total assets, and the non-performing loan balance (in 100 million CNY), sorted in descending order by the risk-weighted assets as a percentage of total assets.",
  "BRB2-0473": "For manually identified loan instruments classified as non-performing, summarize the count of loan instruments by risk classification name, retaining only those names with a count between 60 and 105, and output the risk classification name and loan instrument count, sorted by loan instrument count in descending order and risk classification name in ascending order.",
  "BRB2-0474": "Group by the industry of the underlying assets in the 'external rating exit' category, summarize the asset count and average annualized yield, output the Chinese industry name, asset count, and average annualized yield, filter to keep only industries with at least 5 assets, and sort by asset count in descending order.",
  "BRB2-0475": "Identify non-performing loans with overdue principal days of 90 or more. For each institution, calculate the total count of non-performing loan notes and the total overdue principal. Determine whether the ratio of total overdue principal to the institution's operating revenue is high. Output the institution number, the count of non-performing loan notes, and the total overdue principal. Retain only institutions where the total overdue principal exceeds 50% of operating revenue. Sort the results by total overdue principal in descending order. (Institution financial data is stored in the financial snapshot table, where the entity number is 'PTY-' followed by the institution number.)",
  "BRB2-0476": "Calculate the holdings of each wealth management product whose book value exceeds fair value (negative carry), and output the product name, average negative carry amount, and number of negative carry holdings, sorted by average negative carry amount in descending order and then by number of negative carry holdings in descending order.",
  "BRB2-0477": "List the bank accounts that are still in an active status, have an account subtype of \"dedicated\", and whose available balance is not lower than the bank-wide average available balance. Output the account number, account subtype, and available balance, sorted by available balance in descending order.",
  "BRB2-0478": "Find borrowers who have at least two non-performing loan instruments with principal overdue days exceeding 90 days, and who are also the ultimate debtors of the underlying assets of a wealth management product. Output the product name, the underlying asset name, and the borrower's single largest overdue principal amount, sorted by the largest overdue principal amount in descending order and by product name in ascending order.",
  "BRB2-0479": "Calculate the ratio of tier 1 capital to risk-weighted assets (tier 1 capital adequacy ratio) for each institution, output the institution name and tier 1 capital adequacy ratio, retain only institutions with a tier 1 capital adequacy ratio below 9 percent, and sort by tier 1 capital adequacy ratio in ascending order.",
  "BRB2-0480": "For each wealth management product, count the number of look-through holdings whose nesting depth reaches three levels or more, and rank these products by that count in descending order. Output the product name, the count of deep holdings, and the rank, sorted by rank in ascending order and then by product name in ascending order.",
  "BRB2-0481": "Calculate for each institution the ratio of the total outstanding loan principal balance to its risk-weighted assets, and output the institution name, total principal balance, risk-weighted assets, and the loan-to-risk-weighted-assets percentage (rounded to two decimal places), sorted in descending order by percentage and ascending order by institution name.",
  "BRB2-0482": "Identify non-standardized debt underlying assets whose issuer has principal-overdue loan drawdowns at our bank. Output the asset number, asset name, issuer number, and the total overdue principal amount for that issuer (sum of overdue principal, rounded to two decimal places), sorted by total overdue amount in descending order and asset number in ascending order.",
  "BRB2-0483": "Please summarize the wealth management underlying assets for restricted and exit industries by industry, outputting the industry code, industry Chinese name, number of assets, and total asset scale (in 100 million CNY), sorted by total asset scale in descending order and industry code in ascending order.",
  "BRB2-0484": "For loan drawdowns that have pending payment instructions and are still in an active status, summarize the count of pending instructions by payment settlement method, keeping only those settlement methods with a count greater than 45, and output the settlement method and the count of pending instructions, sorted in descending order by the count of pending instructions and ascending order by settlement method.",
  "BRB2-0485": "Summarize the holdings where the ultimate debtor is a borrower with overdue loan notes of the issuing institution itself, among the underlying assets held through wealth management products by each issuing institution, grouped by the industry of the underlying assets. Output the issuing institution number, industry code, number of holdings, the amount of wealth management funds invested, and the total wealth management investment of that institution. Only include holdings with a penetration depth of at least two levels. Sort by invested amount in descending order, then by industry code in ascending order.",
  "BRB2-0486": "Calculate, by institution, the ratio of the total amount of indicator records flagged as abnormal in the prudential regulatory indicator ledger to that institution's net capital, and compare it with total assets. Output the institution name, number of abnormal records, total amount of abnormal indicators, net capital, total assets, and the ratio to net capital (as a percentage, rounded to four decimal places). Retain only institutions with at least 8 abnormal records, and sort in descending order by the ratio. (Institutional financial data is stored in the financial snapshot table, where the entity ID is \"PTY-\" followed by the institution ID.)",
  "BRB2-0487": "Calculate the scale of loan drawdowns with insufficient loan loss provisions for each institution, and compare this with the associated overdue records that have not yet been completed in their regulatory reporting. Output the institution name, the number of overdue regulatory reporting records, the average ledger amount, the number of loan drawdowns with insufficient provisions, and the provision gap amount (rounded to two decimal places). Retain only institutions with at least 25 overdue records, and sort the results by the provision gap amount in descending order.",
  "BRB2-0488": "Calculate, for each institution, the reconciliation between records in the loan control ledger that were not completed on time and the number of loan drawdowns with overdue repayment plans under that institution, along with the total overdue principal due. Output the institution name, the count of overdue control ledger records, the amount of control records, the number of overdue installment drawdowns, and the total overdue principal due. Keep only institutions with at least 25 overdue records, and sort by the total overdue principal due in descending order.",
  "BRB2-0489": "For each institution, count the total number of credit limit approvals, and link with the corporate governance control register to calculate the total amount of records carrying an anomaly flag (rounded to 2 decimal places) and the average observation ratio across all register records (rounded to 4 decimal places). Keep only institutions with at least 5 governance anomaly records. Output the institution name, total credit limit approvals, governance anomaly record amount, and average observation ratio, sorted by governance anomaly record amount in descending order and institution name in ascending order (the average observation ratio uses the ratio field in the register, not the observation value field).",
  "BRB2-0490": "Identify customers in the related-party transaction ledger that carry an abnormal flag, and for their related-party relationship records where they serve as the source entity, count the number of distinct target entities, the number of distinct relationship types, and the number of related-party records whose relationship type Chinese name is not \"non-related party\" ('非关联方'). Output the customer name, the count of related target entities, the count of relationship types, and the count of non-\"non-related party\" ('非关联方') relationship records, sorted by the count of related target entities in descending order, then by the count of relationship types in descending order, and then by customer name in ascending order.",
  "BRB2-0491": "List the records in the deposit insurance verification ledger that were not completed on schedule, and link the customer's time deposit amount on the settlement account where the customer is the primary account holder. Output the customer name, the number of time deposit transactions, the total principal of time deposits, and the total amount of the verified records, sorted in descending order by total principal of time deposits and ascending order by customer name.",
  "BRB2-0492": "Screen the customer due diligence ledger for records flagged as abnormal, and link the corresponding customer’s deposit balance in settlement and savings accounts, calculate the average observed value of the reviewed records, and output the customer name, deposit balance, number of due diligence records, and average observed value, sorted by deposit balance in descending order and customer name in ascending order.",
  "BRB2-0493": "For each institution, calculate the number of valid payment cards issued and the number of cardholding customers under the institution to which the settlement account belongs, as well as the count of valid records in the operational risk ledger and the total amount of records carrying abnormal flags (rounded to two decimal places). Retain only institutions with at least 43 valid operational risk records. Output the institution name, number of valid cards issued, number of cardholding customers, operational risk abnormal amount, and count of valid operational risk records, sorted by operational risk abnormal amount in descending order and institution name in ascending order.",
  "BRB2-0494": "For overdue records in the data security incident log that are either not yet completed or completed after the deadline, link the industry classification and operating status of the checked corporate customers, and aggregate by industry and operating status the total amount carrying the anomaly flag (rounded to two decimal places) and the average number of occurrences (rounded to two decimal places). Keep only industry and operating status combinations with at least 8 overdue records, and output the industry Chinese name, operating status, total anomalous amount, and average number of occurrences, sorted by total anomalous amount in descending order and industry Chinese name in ascending order.",
  "BRB2-0495": "Calculate the average ratio of records carrying abnormal flags in each issuer's product sales behavior ledger, and link it with the number of wealth management products currently in active sale status under the issuer and the actual fundraising amount; output the issuer name, number of active products, total actual fundraising amount, number of product behavior records, and the average ratio, keeping only issuers with at least 2 abnormal records, sorted in descending order by total actual fundraising amount (with the average ratio rounded to four decimal places).",
  "BRB2-0496": "Group the valid records in the beneficial owner verification register by exposure group and its type, and output the group name, exposure type, number of group members, total observations with anomaly flags, and the count of register records, keeping only groups with at least 3 group members, sorted by number of group members in descending order and group name in ascending order.",
  "BRB2-0497": "First, aggregate the number of subordinate business units and the number of employees by institution using the employee table and the business unit table. Then, join with overdue records in the license management ledger that are either not yet completed or completed after the deadline, by institution. For each institution, count the distinct number of inspected entities and calculate the average observation value (rounded to four decimal places). Keep only institutions with at least 25 overdue ledger records. Output the institution name, number of inspected entities, number of subordinate business units, number of employees, and average observation value, sorted by the number of inspected entities in descending order, and then by institution name in ascending order.",
  "BRB2-0498": "For each original initiating institution, calculate the total number of underlying assets under entrusted management and the total issuance amount (rounded to two decimal places), as well as the count of records in the asset custody ledger that are in an active status and the total amount of records carrying an anomaly flag (rounded to two decimal places). Retain only those institutions where, among their active custody records, the number of records carrying an anomaly flag is at least 2. Output the institution name, underlying asset count, total issuance amount, active custody record count, and total anomaly amount, sorted by total issuance amount in descending order and institution name in ascending order.",
  "BRB2-0499": "Calculate the average ratio of valid records in each institution's foreign exchange settlement and sale ledger, and reconcile it with the number of entrusted payment instructions and the entrusted amount corresponding to loan drawdowns under the institution. Output the institution name, number of payment instructions, total entrusted payment amount, number of foreign exchange settlement and sale records, and average ratio, keeping only institutions with at least 41 foreign exchange settlement and sale records, sorted in descending order by total entrusted payment amount.",
  "BRB2-0500": "Cross-validate the artificial intelligence system application ledger against the regulatory item code table and the overdue promissory note table: identify borrowing customers who have records in the overdue snapshot for their promissory notes and also have unresolved rectification records (completion date is empty) in the artificial intelligence system application ledger. Aggregate by institution and regulatory item rule category to calculate the distinct count of overdue borrowing customers and the total ledger amount involved (rounded to two decimal places). Output the institution name, regulatory item rule category, overdue borrowing customer count, and total ledger amount, sorted by total ledger amount in descending order and institution name in ascending order."
}
for _item in ITEMS:
    _item['question_en'] = _QUESTIONS_EN[_item['id']]
