#!/usr/bin/env python3
"""Export BankRegBench to standard BIRD / Spider benchmark format.

Generates under `data/bird_format/`:
  - train.json, dev.json, test.json, all.json
  - train_gold.sql, dev_gold.sql, test_gold.sql, all_gold.sql
  - dev_tables.json, tables.json, column_meaning.json
  - dev_databases/bankreg_main/database_description/<table>.csv
  - (optional, with --copy-db) dev_databases/bankreg_main/bankreg_main.sqlite
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "bankreg.sqlite"
QUESTIONS_PATH = ROOT / "data" / "questions.jsonl"
SCHEMA_PATH = ROOT / "data" / "schema.json"
OUT_DIR = ROOT / "data" / "bird_format"

TABLE_DESC_ZH = {
    "institution": "银行法人机构信息表（institution_id 机构编号, institution_name 机构名称, institution_type 机构类型）",
    "organization_unit": "营业机构单元/分支行层级表（org_unit_id 机构单元编号, institution_id 所属机构, unit_name 机构单元名称, unit_type 类型, region_code 地区代码）",
    "staff_member": "银行员工表（staff_id 员工工号, person_party_id 员工个人客户编号, home_org_unit_id 所属机构单元）",
    "staff_assignment": "员工岗位分配表（assignment_id, staff_id 员工工号, org_unit_id 机构单元编号, role_code 岗位角色, role_title 岗位名称）",
    "service_operator": "业务经办操作员表（operator_id 操作员编号, staff_id 员工工号, org_unit_id 机构单元编号）",
    "party": "客户与当事人主表（party_id 客户编号, party_type 客户类型 CORPORATE对公/INDIVIDUAL个人/STAFF本行员工, display_name 客户名称, customer_segment 客户分层, home_org_unit_id 归属机构单元, status 状态）",
    "person_profile": "个人客户画像表（party_id 客户编号, occupation_code 职业, annual_income 年收入, is_public_official 是否公职人员）",
    "organization_profile": "对公企业客户画像表（party_id 客户编号, industry_code 行业代码, registered_region 注册地区代码, operating_status 经营状态 OPERATING正常/REVOKED吊销/ABNORMAL异常）",
    "industry_sector": "行业分类受控词表（sector_code 行业代码, sector_name_zh 行业中文名称, risk_category 风险类别 NORMAL/RESTRICTED限制类/EXIT退出类）",
    "party_relation": "关联方关系表（relation_id, source_party_id 源主体客户编号, target_party_id 目标主体客户编号, relation_type 关联关系类型代码）",
    "relation_type_catalog": "关联关系类型受控词表（relation_type 关系代码, relation_name_zh 中文名称 如非关联方/实际控制人/同受控制企业等）",
    "exposure_group": "集团客户与关联敞口集团表（exposure_group_id 集团编号, institution_id 主办机构编号, group_name 集团名称, group_type 集团类型）",
    "exposure_group_member": "敞口集团成员表（exposure_member_id, exposure_group_id 集团编号, party_id 成员客户编号）",
    "account": "存款与内部账户表（account_id 账户编号, institution_id 开户机构编号, org_unit_id 开户机构单元编号, account_kind 账户类型 SAVINGS储蓄/CURRENT活期/LOAN贷款/INTERNAL内部, status 账户状态 ACTIVE正常/DORMANT久悬/CLOSED销户）",
    "account_holder": "账户持有人关联表（account_holder_id, account_id 账户编号, party_id 持有人客户编号, holder_role 持有人角色 PRIMARY主持有人/SECONDARY副持有人）",
    "account_balance_snapshot": "账户余额快照表（account_balance_id, account_id 账户编号, as_of_date 快照日期, ledger_balance 账面余额, available_balance 可用余额）",
    "term_deposit": "定期存款账户表（account_id 账户编号, opening_principal 开户本金, booked_on 起息日, maturity_on 到期日, annual_interest_rate 年利率）",
    "payment_card": "银行卡/信用卡表（card_id 卡号, settlement_account_id 结算账户编号, holder_party_id 持卡人客户编号, card_type 卡种 CREDIT贷记卡/DEBIT借记卡/SEMI_CREDIT准贷记卡, issued_on 发卡日期, expires_on 到期日期, status 状态）",
    "payment_event": "支付交易流水表（payment_id 交易编号, from_account_id 付款账户编号, to_account_id 收款账户编号, business_date 业务日期, amount 交易金额, payment_type 交易类型代码, channel 渠道, is_cash 是否现金交易 1/0, operator_id 经办操作员编号, origin_org_unit_id 经办机构单元编号, status 状态 SETTLED已清算/REVERSED已冲正）",
    "payment_type_catalog": "支付交易类型受控词表（payment_type 交易类型代码, name_zh 中文名称 转账/现金存入/现金支取/贷款发放/贷款还款/卡消费/内部转账）",
    "credit_facility": "授信额度表（facility_id 额度编号, institution_id 机构编号, obligor_party_id 授信客户编号, limit_amount 授信额度金额）",
    "credit_agreement": "授信协议合同表（agreement_id 协议编号, facility_id 额度编号, institution_id 机构编号, borrower_party_id 借款人客户编号, managing_org_unit_id 经办管理机构单元编号, product_family 产品族, target_industry_code 协议约定投向行业代码, contract_amount 合同金额, signed_on 签署日, maturity_on 到期日, annual_interest_rate 合同年利率, payment_mode 支付方式, security_type 担保方式代码 CREDIT信用/GUARANTEE保证/MORTGAGE抵押/PLEDGE质押/NONE, status 状态 ACTIVE正常/MATURED已到期）",
    "loan_drawdown": "贷款借据放款表（loan_id 借据编号, agreement_id 授信协议编号, loan_account_id 贷款账户编号, disbursed_amount 放款金额, disbursed_on 放款日, original_maturity_on 原到期日, current_maturity_on 当前到期日, closed_on 结清日, drawdown_type 贷款品种代码, payment_mode 支付方式 ENTRUSTED_PAYMENT受托支付/SELF_PAYMENT自主支付, status 借据状态 ACTIVE正常/SETTLED已结清/WRITTEN_OFF已核销）",
    "loan_product_catalog": "贷款品种受控词表（product_code 品种代码, product_name_zh 品种中文名称, product_family 产品族, is_revolving 是否循环贷）",
    "loan_balance_snapshot": "贷款借据余额快照表（loan_balance_id, loan_id 借据编号, as_of_date 快照日期, principal_balance 本金余额, overdue_principal 逾期本金余额）",
    "repayment_schedule": "贷款分期还款计划表（installment_id 分期编号, loan_id 借据编号, installment_no 期次, due_date 应还日期, principal_due 应还本金, interest_due 应还利息, paid_on 实还日期, status 状态 PAID已还/OVERDUE逾期）",
    "payment_instruction": "贷款受托/自主支付指令表（instruction_id 支付指令编号, loan_id 借据编号, payment_mode 支付方式 ENTRUSTED_PAYMENT受托支付/SELF_PAYMENT自主支付, intended_payee_party_id 收款方客户编号, intended_payee_account_id 收款方账户编号, instruction_date 指令日期, instruction_amount 指令金额, status 状态 EXECUTED已执行/PENDING待执行）",
    "classification_grade": "贷款五级分类等级受控词表（grade_code 等级代码, grade_name_zh 等级中文名称 正常/关注/次级/可疑/损失, grade_ordinal 级次序数 1-5, is_nonperforming 是否不良 1不良/0非不良）",
    "risk_classification": "贷款风险五级分类结果表（classification_id, loan_id 借据编号, as_of_date 分类日期, grade_code 五级分类代码）",
    "delinquency_snapshot": "贷款逾期台账快照表（delinquency_id, loan_id 借据编号, as_of_date 快照日期, principal_overdue_days 本金逾期天数, interest_overdue_days 利息逾期天数, overdue_principal 逾期本金金额, overdue_interest 逾期利息金额）",
    "provision_snapshot": "贷款损失准备拨备计提快照表（provision_id, loan_id 借据编号, as_of_date 快照日期, provision_stage 阶段, required_amount 计提要求金额, recognized_amount 已计提拨备金额）",
    "security_agreement": "担保合同表（security_id 担保合同编号, institution_id 所属机构编号, security_type 担保类型, secured_amount 担保债权金额, status 担保合同状态 ACTIVE有效/EXPIRED已过期/RELEASED已解除）",
    "secured_obligation": "被担保主债权桥接表（secured_obligation_id, security_id 担保合同编号, agreement_id 授信协议编号, covered_amount 担保覆盖金额）",
    "guarantor_commitment": "第三方保证人担保承诺表（commitment_id, security_id 担保合同编号, guarantor_party_id 担保人客户编号, guaranteed_amount 担保承诺金额, status 状态 ACTIVE有效/EXPIRED已过期）",
    "collateral_asset": "抵质押物主表（collateral_id 抵押物编号, owner_party_id 所有权人客户编号, collateral_type 抵押物类型, asset_label 抵押物名称, status 抵押物状态 ACTIVE有效/RELEASED已释放）",
    "collateral_link": "担保合同与抵质押物关联表（collateral_link_id, security_id 担保合同编号, collateral_id 抵押物编号, pledged_amount 抵押金额, pledge_ratio 抵质押率, status 关联状态 ACTIVE有效/RELEASED已释放）",
    "collateral_valuation": "抵质押物评估价值表（valuation_id, collateral_id 抵押物编号, valued_on 评估日期, valuation_amount 评估价值）",
    "capital_snapshot": "机构资本充足率与资本净额快照表（capital_snapshot_id, institution_id 机构编号, as_of_date 快照日期, net_capital 资本净额, tier1_capital 一级资本, total_capital 总资本, risk_weighted_assets 风险加权资产）",
    "wealth_product": "理财产品主表（product_id 产品编号, issuer_institution_id 发行机构编号, product_name 产品名称, risk_level 风险等级 R1-R5, target_investor_type 目标投资者类型 GENERAL普通投资者/PROFESSIONAL/PRIVATE, planned_raise_amount 计划募集金额, actual_raise_amount 实际募集金额, inception_on 成立日期, scheduled_maturity_on 计划到期日, actual_termination_on 实际终止日期, management_fee_rate 管理费率, status 状态 ON_SALE在售/TERMINATED已终止）",
    "managed_asset": "理财底层资产表（asset_id 底层资产编号, originator_institution_id 机构编号, asset_name 资产名称, asset_scope 资产属性 STANDARDIZED标准化/NON_STANDARDIZED非标准化债权类资产, asset_category_primary 资产大类, maturity_on 资产到期日, status 状态）",
    "product_holding_snapshot": "理财产品底层资产持仓穿透快照表（holding_id, product_id 理财产品编号, asset_id 底层资产编号, investment_path 投资路径 DIRECT/SPV/NESTED_SPV, lookthrough_depth 穿透嵌套层级, intermediary_party_id 通道中介主体编号, fair_value 持仓公允市值）",
    "status_catalog": "实体状态值域受控词表（entity 实体表名, status_code 状态代码, name_zh 状态中文名称）",
    "payment_mode_catalog": "支付方式受控词表（payment_mode 代码, name_zh 中文名 受托支付/自主支付）",
    "card_type_catalog": "银行卡类型受控词表（card_type 代码, name_zh 中文名 贷记卡/借记卡/准贷记卡）",
    "party_type_catalog": "客户类型受控词表（party_type 代码, name_zh 中文名 对公客户/个人客户/本行员工）",
    "regulatory_event_catalog": "监管事项编码受控词表（event_code 事项代码, event_name_zh 事项中文名称, event_family 事项大类）",
    "lending_control_event_v3": "信贷业务管控事项监管台账（record_id 记录编号, institution_id 机构编号, subject_id 主体编号, event_date 发生日, deadline_date 法定截止日, completion_date 完成日, observed_value 行为观测值, exception_flag 异常标记）",
    "governance_control_record_v3": "公司治理控制事项监管台账（record_id 记录编号, institution_id 机构编号, event_date 发生日, deadline_date 法定截止日, completion_date 完成日, observed_value 行为观测值, exception_flag 异常标记）",
    "regulatory_submission_event_v3": "监管数据报送事项台账（record_id 记录编号, institution_id 机构编号, event_date 发生日, deadline_date 法定截止日, completion_date 完成日, observed_value 行为观测值, exception_flag 异常标记）",
    "customer_due_diligence_event_v3": "客户尽职调查事项台账（record_id 记录编号, institution_id 机构编号, event_date 发生日, deadline_date 法定截止日, completion_date 完成日, observed_value 行为观测值, exception_flag 异常标记）",
    "data_security_event_v3": "数据安全事件监管台账（record_id 记录编号, institution_id 机构编号, event_date 发生日, deadline_date 法定截止日, completion_date 完成日, observed_value 行为观测值, exception_flag 异常标记）",
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Export BankRegBench to standard BIRD format.")
    ap.add_argument("--db", type=Path, default=DB_PATH)
    ap.add_argument("--questions", type=Path, default=QUESTIONS_PATH)
    ap.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument(
        "--copy-db",
        action="store_true",
        help="Also copy bankreg.sqlite into dev_databases/bankreg_main/bankreg_main.sqlite",
    )
    args = ap.parse_args()

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    db_dir = out_dir / "dev_databases" / "bankreg_main"
    desc_dir = db_dir / "database_description"
    desc_dir.mkdir(parents=True, exist_ok=True)

    target_db = db_dir / "bankreg_main.sqlite"
    if args.copy_db:
        if target_db.exists() or target_db.is_symlink():
            target_db.unlink()
        shutil.copy2(args.db, target_db)
        print(f"Copied database to {target_db}")

    questions = [json.loads(l) for l in args.questions.read_text(encoding="utf-8").splitlines() if l.strip()]
    schema = json.loads(args.schema.read_text(encoding="utf-8"))

    # Build BIRD tables.json
    table_names = list(schema["tables"].keys())
    column_names_original = [[-1, "*"]]
    column_names = [[-1, "*"]]
    column_types = ["text"]
    primary_keys = []
    foreign_keys = []
    col_map = {}

    for t_i, t_name in enumerate(table_names):
        t_info = schema["tables"][t_name]
        for c_info in t_info["columns"]:
            c_idx = len(column_names_original)
            c_name = c_info["name"]
            col_map[(t_name, c_name)] = c_idx
            column_names_original.append([t_i, c_name])
            column_names.append([t_i, c_name])
            ctype = c_info["type"].lower()
            column_types.append("number" if ctype in ("real", "integer", "int") else "text")
            if c_info.get("pk"):
                primary_keys.append(c_idx)

    for t_name in table_names:
        t_info = schema["tables"][t_name]
        for fk in t_info["foreign_keys"]:
            src = col_map.get((t_name, fk["column"]))
            dst = col_map.get((fk["ref_table"], fk["ref_column"]))
            if src is not None and dst is not None:
                foreign_keys.append([src, dst])

    bird_table_entry = [{
        "db_id": "bankreg_main",
        "table_names_original": table_names,
        "table_names": [TABLE_DESC_ZH.get(t, t).split("（")[0] for t in table_names],
        "column_names_original": column_names_original,
        "column_names": column_names,
        "column_types": column_types,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
    }]
    (out_dir / "dev_tables.json").write_text(json.dumps(bird_table_entry, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "tables.json").write_text(json.dumps(bird_table_entry, ensure_ascii=False, indent=2), encoding="utf-8")

    # Build database_description/*.csv and column_meaning.json
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    column_meaning = {}
    for t_name in table_names:
        t_info = schema["tables"][t_name]
        csv_path = desc_dir / f"{t_name}.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["original_column_name", "column_name", "column_description", "data_format", "value_description"])
            for c_info in t_info["columns"]:
                cname = c_info["name"]
                samples = [
                    str(r[0])
                    for r in conn.execute(
                        f'SELECT DISTINCT "{cname}" FROM "{t_name}" WHERE "{cname}" IS NOT NULL LIMIT 8'
                    ).fetchall()
                ]
                val_desc = f"示例值: {', '.join(samples[:6])}" if samples else ""
                col_desc = f"{TABLE_DESC_ZH.get(t_name, t_name)}中的字段 {cname}"
                w.writerow([cname, cname, col_desc, c_info["type"], val_desc])
                column_meaning[f"bankreg_main|{t_name}|{cname}"] = f"{col_desc} ({c_info['type']}). {val_desc}"
    conn.close()
    (out_dir / "column_meaning.json").write_text(json.dumps(column_meaning, ensure_ascii=False, indent=2), encoding="utf-8")

    # Export splits in BIRD format
    diff_map = {"easy": "simple", "medium": "moderate", "hard": "challenging", "extra": "challenging"}
    by_split: dict[str, list] = {"train": [], "dev": [], "test": [], "all": []}
    for idx, q in enumerate(questions):
        entry = {
            "question_id": idx,
            "orig_question_id": q["question_id"],
            "db_id": "bankreg_main",
            "question": q["question"],
            "question_en": q.get("question_en", ""),
            "evidence": "",
            "SQL": q["sql"],
            "difficulty": diff_map.get(q["difficulty"], "moderate"),
            "orig_difficulty": q["difficulty"],
            "split": q["split"],
        }
        by_split[q["split"]].append(entry)
        by_split["all"].append(entry)

    for s_name, items in by_split.items():
        (out_dir / f"{s_name}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        with (out_dir / f"{s_name}_gold.sql").open("w", encoding="utf-8") as fh:
            for it in items:
                clean_sql = " ".join(it["SQL"].splitlines())
                fh.write(f"{clean_sql}\tbankreg_main\n")

    print(f"Exported BIRD format to {out_dir}:")
    for s_name, items in by_split.items():
        print(f"  {s_name}.json: {len(items)} questions")


if __name__ == "__main__":
    main()
