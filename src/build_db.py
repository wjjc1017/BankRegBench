#!/usr/bin/env python3
"""Generate the BankRegBench-v2 warehouse.

Deterministic: the same seed always yields byte-identical data.  The warehouse is
built at a realistic volume (tens of thousands of rows) on purpose --- the point
of the dataset is that answers require joins, aggregation, ratios and temporal
reasoning over many rows, not the retrieval of a single planted record.

Usage: python3 src/build_db.py [--out data/bankreg.sqlite] [--seed 20260630]
"""

from __future__ import annotations

import argparse
import datetime as dt
import random
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DDL = ROOT / "schema" / "bankreg_v4.sqlite.sql"

SEED = 20260630
AS_OF = "2026-06-30"          # every snapshot is taken on this date
FY_START = "2026-01-01"

# ---------------------------------------------------------------------------
# vocabulary
# ---------------------------------------------------------------------------
PRODUCTS = [
    ("WC_TERM", "流动资金贷款", "WORKING_CAPITAL", 1),
    ("WC_REVOLVING", "流动资金循环贷款", "WORKING_CAPITAL", 1),
    ("FIXED_ASSET", "固定资产贷款", "PROJECT", 0),
    ("PROJECT_FINANCE", "项目融资", "PROJECT", 0),
    ("SYNDICATED", "银团贷款", "CORPORATE", 0),
    ("MERGER_ACQ", "并购贷款", "CORPORATE", 0),
    ("HOUSEHOLD_MORTGAGE", "个人住房按揭贷款", "RETAIL", 0),
    ("PERSONAL_BUSINESS", "个人经营性贷款", "RETAIL", 0),
    ("MICRO_LOAN", "小微企业贷款", "SME", 1),
    ("TECH_RENOVATION", "技术改造贷款", "SME", 0),
    ("GREEN_CREDIT", "绿色信贷", "GREEN", 0),
    ("EXPORT_REFINANCE", "出口退税质押贷款", "TRADE", 1),
]
SECTORS = [
    ("REAL_ESTATE", "房地产业", "Real estate", None, "RESTRICTED"),
    ("SECURITIES", "证券期货业", "Securities and futures", None, "RESTRICTED"),
    ("LOCAL_GOV_FIN", "地方政府融资平台", "Local government financing vehicle", None, "RESTRICTED"),
    ("MANUFACTURING", "制造业", "Manufacturing", None, "NORMAL"),
    ("WHOLESALE_RETAIL", "批发和零售业", "Wholesale and retail", None, "NORMAL"),
    ("CONSTRUCTION", "建筑业", "Construction", None, "NORMAL"),
    ("TRANSPORT", "交通运输业", "Transport", None, "NORMAL"),
    ("AGRICULTURE", "农林牧渔业", "Agriculture", None, "NORMAL"),
    ("MINING", "采矿业", "Mining", None, "NORMAL"),
    ("UTILITIES", "电力热力燃气及水生产供应业", "Utilities", None, "NORMAL"),
    ("INFO_TECH", "信息传输软件和信息技术服务业", "IT services", None, "NORMAL"),
    ("HEALTHCARE", "卫生和社会工作", "Healthcare", None, "NORMAL"),
    ("EDUCATION", "教育", "Education", None, "NORMAL"),
    ("HOSPITALITY", "住宿和餐饮业", "Hospitality", None, "NORMAL"),
    ("LEASING", "租赁和商务服务业", "Leasing and business services", None, "NORMAL"),
    ("STEEL", "黑色金属冶炼和压延加工业", "Steel", None, "EXIT"),
    ("COAL", "煤炭开采和洗选业", "Coal", None, "EXIT"),
    ("PHOTOVOLTAIC", "光伏设备及元器件制造", "Photovoltaics", None, "NORMAL"),
    ("CULTURE", "文化体育和娱乐业", "Culture and sports", None, "RESTRICTED"),
    ("OTHER", "其他行业", "Other", None, "NORMAL"),
]
GRADES = [
    ("NORMAL", "正常", "Normal", 1, 0),
    ("SPECIAL_MENTION", "关注", "Special mention", 2, 0),
    ("SUBSTANDARD", "次级", "Substandard", 3, 1),
    ("DOUBTFUL", "可疑", "Doubtful", 4, 1),
    ("LOSS", "损失", "Loss", 5, 1),
]
PARTY_TYPES = [("CORPORATE", "对公客户"), ("INDIVIDUAL", "个人客户"), ("STAFF", "本行员工")]
RELATION_TYPES = [
    ("SHADOW_SHAREHOLDER", "影子股东"), ("DE_FACTO_CONTROLLER", "实际控制人"),
    ("AFFILIATE", "重大关联方"), ("COMMON_CONTROL", "同受控制企业"),
    ("SENIOR_MANAGER", "关键管理人员"), ("NON_RELATED", "非关联方"),
]
PAYMENT_MODES = [("ENTRUSTED_PAYMENT", "受托支付"), ("SELF_PAYMENT", "自主支付")]
INSTRUMENTS = [
    ("BANK_ACCEPTANCE_DRAFT", "银行承兑汇票"),
    ("COMMERCIAL_ACCEPTANCE_DRAFT", "商业承兑汇票"),
    ("LETTER_OF_CREDIT", "信用证"),
]
CARD_TYPES = [("CREDIT", "贷记卡"), ("DEBIT", "借记卡"), ("SEMI_CREDIT", "准贷记卡")]
PAYMENT_TYPES = [
    ("TRANSFER", "转账"), ("CASH_DEPOSIT", "现金存入"), ("CASH_WITHDRAWAL", "现金支取"),
    ("LOAN_DISBURSEMENT", "贷款发放"), ("LOAN_REPAYMENT", "贷款还款"),
    ("CARD_PURCHASE", "卡消费"), ("INTERNAL_TRANSFER", "内部转账"),
]
EXPOSURE_GROUPS = [("GROUP_CUSTOMER", "集团客户"), ("CONNECTED_CUSTOMER", "关联客户群")]
STATUSES = [
    ("party", "ACTIVE", "正常"), ("party", "FROZEN", "冻结"), ("party", "CLOSED", "销户"),
    ("account", "ACTIVE", "正常"), ("account", "DORMANT", "久悬"),
    ("account", "CLOSED", "销户"),
    ("loan_drawdown", "ACTIVE", "正常"), ("loan_drawdown", "SETTLED", "已结清"),
    ("loan_drawdown", "WRITTEN_OFF", "已核销"),
    ("credit_agreement", "ACTIVE", "正常"), ("credit_agreement", "MATURED", "已到期"),
    ("wealth_product", "ON_SALE", "在售"), ("wealth_product", "TERMINATED", "已终止"),
    ("regulatory_event", "ACTIVE", "有效"), ("regulatory_event", "VOID", "作废"),
    ("payment", "SETTLED", "已清算"), ("payment", "REVERSED", "已冲正"),
]

ORGS = ["总行", "北京分行", "上海分行", "深圳分行", "杭州分行", "成都分行"]
CITY_REGION = ["110000", "310000", "440300", "330100", "510100", "110000"]
FAMILY_NAMES = ["张", "王", "李", "赵", "陈", "刘", "杨", "黄", "周", "吴", "徐", "孙", "马", "朱"]
GIVEN_NAMES = ["伟", "芳", "娜", "敏", "静", "强", "磊", "洋", "艳", "勇", "军", "杰", "娟", "涛"]
CORP_SUFFIX = ["科技有限公司", "贸易有限公司", "实业有限公司", "建设集团有限公司",
               "物流有限公司", "农业开发有限公司", "医药有限公司", "新能源有限公司",
               "置业有限公司", "供应链管理有限公司"]
COLLATERAL_TYPES = ["LAND_USE_RIGHT", "REAL_ESTATE", "EQUIPMENT", "RECEIVABLE", "DEPOSIT", "EQUITY"]
EVENT_TABLES = {
    "prudential_metric_snapshot_v3": ["prud_metric"],
    "regulatory_submission_event_v3": ["submission"],
    "lending_control_event_v3": ["lending_control"],
    "governance_control_record_v3": ["governance"],
    "related_transaction_record_v3": ["related_txn"],
    "deposit_protection_record_v3": ["deposit"],
    "customer_due_diligence_event_v3": ["kYC"],
    "operational_risk_event_v3": ["op_risk"],
    "data_security_event_v3": ["data_sec"],
    "product_conduct_event_v3": ["conduct"],
    "beneficial_owner_record_v3": ["ubo"],
    "license_record_v3": ["license"],
    "custody_operation_event_v3": ["custody"],
    "fx_business_event_v3": ["fx"],
    "ai_system_record_v3": ["ai"],
}


def d(day: int, month: int = 1, year: int = 2026) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def rand_date(rng: random.Random, start: str, end: str) -> str:
    a = dt.date.fromisoformat(start).toordinal()
    b = dt.date.fromisoformat(end).toordinal()
    return dt.date.fromordinal(rng.randint(a, b)).isoformat()


def add_days(day: str, n: int) -> str:
    return (dt.date.fromisoformat(day) + dt.timedelta(days=n)).isoformat()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "bankreg.sqlite")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        args.out.unlink()
    conn = sqlite3.connect(args.out)
    conn.executescript(DDL.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    # ---------------- vocabulary ------------------------------------------
    c.executemany("INSERT INTO party_type_catalog VALUES (?,?)", PARTY_TYPES)
    c.executemany("INSERT INTO status_catalog VALUES (?,?,?)", STATUSES)
    c.executemany("INSERT INTO loan_product_catalog VALUES (?,?,?,?)", PRODUCTS)
    c.executemany("INSERT INTO payment_mode_catalog VALUES (?,?)", PAYMENT_MODES)
    c.executemany("INSERT INTO relation_type_catalog VALUES (?,?)", RELATION_TYPES)
    c.executemany("INSERT INTO instrument_type_catalog VALUES (?,?)", INSTRUMENTS)
    c.executemany("INSERT INTO card_type_catalog VALUES (?,?)", CARD_TYPES)
    c.executemany("INSERT INTO payment_type_catalog VALUES (?,?)", PAYMENT_TYPES)
    c.executemany("INSERT INTO exposure_group_type_catalog VALUES (?,?)", EXPOSURE_GROUPS)
    c.executemany("INSERT INTO industry_sector (sector_code, sector_name_zh, sector_name_en,"
                  " parent_sector_code, risk_category) VALUES (?,?,?,?,?)", SECTORS)
    c.executemany("INSERT INTO classification_grade VALUES (?,?,?,?,?)", GRADES)

    # ---------------- institutions / org units / staff ---------------------
    INSTS = []
    for i, (iid, name, itype, cap) in enumerate([
            ("INST-001", "华东银行股份有限公司", "COMMERCIAL_BANK", 82_000_000_000),
            ("INST-002", "华南银行股份有限公司", "COMMERCIAL_BANK", 45_000_000_000),
            ("INST-003", "北方农村商业银行", "RURAL_COMMERCIAL_BANK", 12_000_000_000),
            ("INST-004", "西部城市商业银行", "CITY_COMMERCIAL_BANK", 28_000_000_000),
            ("INST-005", "东海村镇银行", "VILLAGE_BANK", 800_000_000),
            ("INST-006", "中原民营银行", "PRIVATE_BANK", 6_000_000_000)]):
        INSTS.append((iid, name, cap))
        c.execute("INSERT INTO institution VALUES (?,?,?,?,?,?,?)",
                  (iid, name, itype, "CN", CITY_REGION[i % 6], d(1, 1, 2005 + i), "ACTIVE"))
    for inst, name, _ in INSTS:
        c.execute("INSERT INTO party (party_id, party_type, display_name, customer_segment,"
                  " home_org_unit_id, onboarded_on, status) VALUES (?,?,?,?,?,?,?)",
                  (f"PTY-{inst}", "CORPORATE", name, "FINANCIAL_INSTITUTION", None,
                   "2005-01-01", "ACTIVE"))
        c.execute("INSERT INTO organization_profile (party_id, legal_form, organization_kind,"
                  " industry_code, business_scope, registered_region, registration_expires_on,"
                  " legal_representative_party_id, operating_status)"
                  " VALUES (?,?,?,?,?,?,?,?,?)",
                  (f"PTY-{inst}", "JOINT_STOCK", "BANK", "OTHER", "吸收公众存款、发放贷款",
                   "110000", "2045-12-31", None, "OPERATING"))

    UNITS = []
    for inst, _, _ in INSTS:
        head = f"{inst}-HQ"
        UNITS.append((head, inst, "总行营业部"))
        c.execute("INSERT INTO organization_unit (org_unit_id, institution_id,"
                  " parent_org_unit_id, unit_name, unit_type, region_code,"
                  " effective_from, status, exception_flag)"
                  " VALUES (?,?,?,?,?,?,?,?,0)",
                  (head, inst, None, "总行营业部", "HEAD_OFFICE", "110000", d(1, 1, 2015), "ACTIVE"))
        for j, branch in enumerate(ORGS[1:], start=1):
            uid = f"{inst}-B{j:02d}"
            UNITS.append((uid, inst, branch))
            c.execute("INSERT INTO organization_unit (org_unit_id, institution_id,"
                      " parent_org_unit_id, unit_name, unit_type, region_code,"
                      " effective_from, status, exception_flag)"
                      " VALUES (?,?,?,?,?,?,?,?,0)",
                      (uid, inst, head, branch, "BRANCH", CITY_REGION[j], d(1, 1, 2016), "ACTIVE"))
    STAFF = []
    sid = 0
    for i, (inst, _, _) in enumerate(INSTS):
        inst_units = [u for u, ui, _ in UNITS if ui == inst]
        for j in range(18 + i):
            sid += 1
            pid = f"PTY-S{sid:05d}"
            unit = inst_units[j % len(inst_units)]
            STAFF.append((f"STAFF-{sid:05d}", pid, inst, unit))
            c.execute("INSERT INTO party (party_id, party_type, display_name,"
                      " customer_segment, home_org_unit_id, onboarded_on, status)"
                      " VALUES (?,?,?,?,?,?,?)",
                      (pid, "STAFF", f"{rng.choice(FAMILY_NAMES)}{rng.choice(GIVEN_NAMES)}",
                       "EMPLOYEE", unit, rand_date(rng, "2015-01-01", "2024-12-31"), "ACTIVE"))
            c.execute("INSERT INTO person_profile VALUES (?,?,?,?,?,?)",
                      (pid, "BANKING", "FINANCE", None, rng.randint(120, 800) * 1000, 0))
            c.execute("INSERT INTO staff_member (staff_id, person_party_id, home_org_unit_id,"
                      " employment_type, employment_status, hired_on, departed_on, exception_flag)"
                      " VALUES (?,?,?,?,?,?,?,0)",
                      (f"STAFF-{sid:05d}", pid, unit,
                       rng.choice(["PERMANENT", "CONTRACT"]), "ACTIVE",
                       rand_date(rng, "2015-01-01", "2025-06-30"), None))

    OPERATORS = []
    for k, (staff_id, person_id, inst, unit) in enumerate(STAFF):
        if k % 3:
            continue
        op = f"OP-{staff_id}"
        OPERATORS.append(op)
        c.execute("INSERT INTO service_operator VALUES (?,?,?,?,?,?,?,?)",
                  (op, staff_id, unit, rng.choice(["TELLER", "CREDIT_OFFICER", "SUPERVISOR"]),
                   rng.choice(["L1", "L2", "L3"]), "2016-01-01", None, "ACTIVE"))
        c.execute("INSERT INTO staff_assignment VALUES (?,?,?,?,?,?,?)",
                  (f"ASG-{staff_id}", staff_id, unit,
                   rng.choice(["TELLER", "CREDIT_OFFICER", "RELATIONSHIP_MANAGER"]),
                   rng.choice(["柜员", "客户经理", "信贷审批"]), "2016-01-01", None))
    if not OPERATORS:
        OPERATORS = [None]

    # ---------------- customers -------------------------------------------
    CORPORATES, INDIVIDUALS = [], []
    for i in range(1, 641):
        pid = f"PTY-C{i:05d}"
        sector = rng.choice(SECTORS)
        unit = rng.choice(UNITS)[0]
        CORPORATES.append((pid, sector[0]))
        c.execute("INSERT INTO party (party_id, party_type, display_name, customer_segment,"
                  " home_org_unit_id, onboarded_on, status) VALUES (?,?,?,?,?,?,?)",
                  (pid, "CORPORATE",
                   f"{rng.choice(['华夏', '东方', '恒昌', '瑞丰', '启元', '博远', '嘉合', '中鼎'])}"
                   f"{rng.choice(CORP_SUFFIX)}", rng.choice(["LARGE", "MID", "SMALL", "MICRO"]),
                   unit, rand_date(rng, "2016-01-01", "2025-12-31"),
                   rng.choices(["ACTIVE", "FROZEN", "CLOSED"], [92, 5, 3])[0]))
        registered = rng.randint(5_000_000, 2_000_000_000)
        c.execute("INSERT INTO organization_profile (party_id, legal_form, organization_kind,"
                  " industry_code, business_scope, registered_region, registration_expires_on,"
                  " legal_representative_party_id, operating_status)"
                  " VALUES (?,?,?,?,?,?,?,?,?)",
                  (pid, "LIMITED_LIABILITY", rng.choice(["SOE", "PRIVATE", "FOREIGN", "JOINT"]),
                   sector[0], f"一般项目：{sector[1]}相关经营", rng.choice(CITY_REGION),
                   d(31, 12, rng.randint(2026, 2045)), None,
                   rng.choices(["OPERATING", "REVOKED", "ABNORMAL"], [90, 5, 5])[0]))
    for i in range(1, 861):
        pid = f"PTY-P{i:05d}"
        unit = rng.choice(UNITS)[0]
        INDIVIDUALS.append(pid)
        segment = rng.choices(["MASS", "AFFLUENT", "PRIVATE_BANKING"], [70, 22, 8])[0]
        c.execute("INSERT INTO party (party_id, party_type, display_name, customer_segment,"
                  " home_org_unit_id, onboarded_on, status) VALUES (?,?,?,?,?,?,?)",
                  (pid, "INDIVIDUAL",
                   f"{rng.choice(FAMILY_NAMES)}{rng.choice(GIVEN_NAMES)}",
                   segment, unit, rand_date(rng, "2016-01-01", "2025-12-31"),
                   rng.choices(["ACTIVE", "FROZEN", "CLOSED"], [95, 3, 2])[0]))
        income = {"MASS": rng.randint(50, 300),
                  "AFFLUENT": rng.randint(300, 1500),
                  "PRIVATE_BANKING": rng.randint(1200, 6000)}[segment] * 1000
        c.execute("INSERT INTO person_profile VALUES (?,?,?,?,?,?)",
                  (pid, rng.choice(["ENGINEER", "TEACHER", "SALES", "CIVIL_SERVANT", "OTHER"]),
                   rng.choice([s[0] for s in SECTORS]), None, income,
                   rng.choices([0, 1], [95, 5])[0]))

    # ---------------- accounts --------------------------------------------
    ACCOUNTS, LOAN_ACCOUNTS = [], []
    for i in range(1, 3001):
        aid = f"ACC-{i:06d}"
        inst = INSTS[i % len(INSTS)][0]
        unit = [u for u, ui, _ in UNITS if ui == inst][i % 6]
        kind = rng.choices(["SAVINGS", "CURRENT", "LOAN", "INTERNAL"], [45, 30, 20, 5])[0]
        ACCOUNTS.append(aid)
        if kind == "LOAN":
            LOAN_ACCOUNTS.append(aid)
        c.execute("INSERT INTO account (account_id, institution_id, org_unit_id, account_kind,"
                  " account_subtype, currency_code, opened_on, closed_on, last_activity_on,"
                  " is_external, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (aid, inst, unit, kind, rng.choice(["BASIC", "GENERAL", "SPECIAL"]),
                   rng.choices(["CNY", "USD"], [96, 4])[0],
                   rand_date(rng, "2016-01-01", "2025-12-31"), None,
                   rand_date(rng, "2026-01-01", AS_OF),
                   0 if kind == "INTERNAL" else 1,
                   rng.choices(["ACTIVE", "DORMANT", "CLOSED"], [90, 6, 4])[0]))
    # employees are customers too: they hold accounts, which is what makes
    # "staff transacting on their own account" a queryable phenomenon.
    CUSTOMER_POOL = INDIVIDUALS + [x[0] for x in CORPORATES] + [pid for _, pid, _, _ in STAFF]
    holders = 0
    for aid in ACCOUNTS:
        owners = rng.sample(CUSTOMER_POOL, k=rng.choice([1, 1, 1, 2]))
        for role, pid in zip(["PRIMARY", "SECONDARY"], owners):
            holders += 1
            c.execute("INSERT INTO account_holder (account_holder_id, account_id, party_id,"
                      " holder_role, effective_from, effective_to) VALUES (?,?,?,?,?,?)",
                      (f"HOLD-{holders:07d}", aid, pid, role, "2016-01-01", None))
    for aid in ACCOUNTS:
        if rng.random() < 0.15:
            continue
        ledger = round(rng.uniform(0, 8_000_000), 2)
        c.execute("INSERT INTO account_balance_snapshot VALUES (?,?,?,?,?,?,?)",
                  (f"BALS-{aid}", aid, AS_OF, ledger, round(ledger * rng.uniform(0.6, 1.0), 2),
                   round(max(0.0, ledger), 2), round(rng.uniform(0, 100000), 2)))
    dep = 0
    for aid in ACCOUNTS:
        if not aid.startswith("ACC-") or rng.random() > 0.28:
            continue
        kind = c.execute("SELECT account_kind FROM account WHERE account_id=?", (aid,)).fetchone()[0]
        if kind != "SAVINGS":
            continue
        dep += 1
        booked = rand_date(rng, "2025-01-01", "2026-05-31")
        term = rng.choice([90, 180, 365, 730, 1095])
        c.execute("INSERT INTO term_deposit VALUES (?,?,?,?,?)",
                  (aid, round(rng.uniform(50_000, 20_000_000), 2), booked,
                   add_days(booked, term), round(rng.uniform(1.1, 3.6), 3)))

    # ---------------- facilities / agreements / loans ----------------------
    RETAIL_PRODUCTS = [p for p in PRODUCTS if p[2] == "RETAIL"]
    CORP_PRODUCTS = [p for p in PRODUCTS if p[2] != "RETAIL"]
    FACILITIES, AGREEMENTS, LOANS = [], [], []
    for i in range(1, 481):
        fid = f"FAC-{i:05d}"
        inst = INSTS[i % len(INSTS)][0]
        is_retail = (i % 5 == 0)
        obligor = rng.choice(INDIVIDUALS) if is_retail else rng.choice(CORPORATES)[0]
        FACILITIES.append((fid, inst, obligor, is_retail))
        c.execute("INSERT INTO credit_facility (facility_id, institution_id, obligor_party_id,"
                  " facility_type, limit_amount, currency_code, approved_on, effective_from,"
                  " effective_to, status, exception_flag) VALUES (?,?,?,?,?,?,?,?,?,?,0)",
                  (fid, inst, obligor, rng.choice(["REVOLVING", "TERM", "GUARANTEE", "ACCEPTANCE"]),
                   round(rng.uniform(200_000, 15_000_000) if is_retail else rng.uniform(5_000_000, 800_000_000), 2),
                   "CNY",
                   rand_date(rng, "2023-01-01", "2025-12-31"),
                   rand_date(rng, "2023-01-01", "2025-12-31"), d(31, 12, 2027), "ACTIVE"))
    for i in range(1, 1201):
        aid = f"AGR-{i:06d}"
        fac = FACILITIES[i % len(FACILITIES)]
        is_retail = fac[3]
        product = rng.choice(RETAIL_PRODUCTS if is_retail else CORP_PRODUCTS)
        signed = rand_date(rng, "2023-01-01", "2026-05-31")
        AGREEMENTS.append((aid, fac[1], fac[2], product))
        c.execute("INSERT INTO credit_agreement (agreement_id, facility_id, institution_id,"
                  " borrower_party_id, managing_org_unit_id, product_family, purpose_text,"
                  " target_industry_code, contract_amount, currency_code, signed_on,"
                  " effective_from, maturity_on, interest_basis, annual_interest_rate,"
                  " rate_spread, payment_mode, security_type, business_context_token, status)"
                  " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (aid, fac[0], fac[1], fac[2],
                   rng.choice([u for u, ui, _ in UNITS if ui == fac[1]]),
                   product[2], f"用于{product[1]}项下约定用途", rng.choice(SECTORS)[0],
                   round(rng.uniform(200_000, 10_000_000) if is_retail else rng.uniform(1_000_000, 500_000_000), 2),
                   "CNY", signed, signed,
                   add_days(signed, rng.choice([365, 730, 1095, 1825])),
                   rng.choice(["LPR", "LPR_MINUS", "FIXED"]),
                   round(rng.uniform(2.8, 6.5), 4), round(rng.uniform(0.0, 2.0), 4),
                   rng.choice([p[0] for p in PAYMENT_MODES]),
                   rng.choice(["CREDIT", "GUARANTEE", "MORTGAGE", "PLEDGE", "NONE"]),
                   rng.choice(["NORMAL", "SPECIAL_ATTENTION"]),
                   rng.choices(["ACTIVE", "MATURED"], [85, 15])[0]))
    # some agreements are drawn down several times (revolving facilities)
    MULTI = {agr[0]: rng.randint(3, 5) for agr in rng.sample(AGREEMENTS, 160)}
    UNDRAWN = {agr[0] for agr in rng.sample(AGREEMENTS, 80)}
    LOAN_PLAN = []
    for agr in AGREEMENTS:
        if agr[0] in UNDRAWN:
            continue
        LOAN_PLAN.extend([agr] * MULTI.get(agr[0], 1))
    LOAN_PLAN = (LOAN_PLAN * 3)[:2400]
    for i, agr in enumerate(LOAN_PLAN, start=1):
        lid = f"LOAN-{i:06d}"
        disbursed = (
            rand_date(rng, "2026-07-01", "2026-07-10")
            if i % 40 == 0
            else rand_date(rng, "2024-01-01", "2026-05-31")
        )
        product = agr[3]
        LOANS.append((lid, agr[0], agr[1], agr[2], product, disbursed))
        maturity = add_days(disbursed, rng.choice([180, 365, 730, 1095, 1825]))
        closed = None
        status = rng.choices(["ACTIVE", "SETTLED", "WRITTEN_OFF"], [80, 17, 3])[0]
        if status == "SETTLED" and disbursed <= AS_OF:
            closed = rand_date(rng, disbursed, AS_OF)
        c.execute("INSERT INTO loan_drawdown (loan_id, agreement_id, loan_account_id,"
                  " disbursement_account_id, repayment_account_id, disbursed_amount,"
                  " currency_code, disbursed_on, original_maturity_on, current_maturity_on,"
                  " closed_on, drawdown_type, payment_mode, status, exception_flag)"
                  " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
                  (lid, agr[0], rng.choice(LOAN_ACCOUNTS), rng.choice(ACCOUNTS),
                   rng.choice(ACCOUNTS), round(rng.uniform(500_000, 300_000_000), 2), "CNY",
                   disbursed, maturity, maturity, closed, product[0],
                   rng.choice([p[0] for p in PAYMENT_MODES]), status))
        # repayment schedule (first three installments)
        principal = c.execute("SELECT disbursed_amount FROM loan_drawdown WHERE loan_id=?",
                              (lid,)).fetchone()[0]
        for k in range(1, 4):
            due = add_days(disbursed, 90 * k)
            paid = add_days(due, rng.randint(-5, 20)) if rng.random() < 0.55 else None
            c.execute("INSERT INTO repayment_schedule VALUES (?,?,?,?,?,?,?,?)",
                      (f"INST-{lid}-{k}", lid, k, due, round(principal / 3, 2),
                       round(principal * 0.001, 2), paid, "PAID" if paid else "OVERDUE"))
    for lid, _, inst, obligor, product, disbursed in LOANS:
        l_status = c.execute("SELECT status FROM loan_drawdown WHERE loan_id=?", (lid,)).fetchone()[0]
        if l_status == "SETTLED" and rng.random() < 0.5:
            bal = 0.0
            overdue = 0.0
        elif obligor.startswith("PTY-P") and inst == "INST-005":
            bal = round(rng.uniform(120_000_000, 280_000_000), 2)
            overdue = 0.0
        else:
            bal = round(rng.uniform(100_000, 200_000_000), 2)
            overdue = round(bal * rng.uniform(0, 0.4), 2) if rng.random() < 0.3 else 0.0
        c.execute("INSERT INTO loan_balance_snapshot VALUES (?,?,?,?,?,?,?,?)",
                  (f"LBAL-{lid}", lid, AS_OF, bal, overdue,
                   round(rng.uniform(0, 2_000_000), 2) if bal > 0 else 0.0,
                   round(rng.uniform(0, 500_000), 2) if bal > 0 else 0.0,
                   add_days(AS_OF, -rng.choice([0, 30, 60, 90, 180, 270, 400]))
                   if overdue else None))

    # Calibrate savings deposit balances so each institution's loan-to-deposit ratio is realistic
    # (4 institutions > 0.75 in 0.78..0.91, and 2 institutions < 0.75 in 0.66..0.71)
    target_ltd = {
        "INST-001": 0.89,
        "INST-002": 0.68,
        "INST-003": 0.82,
        "INST-004": 0.86,
        "INST-005": 0.79,
        "INST-006": 0.71,
    }
    for inst_id, ltd in target_ltd.items():
        loan_sum = c.execute(
            """SELECT SUM(lbs.principal_balance)
               FROM loan_balance_snapshot lbs
               JOIN loan_drawdown ld ON ld.loan_id = lbs.loan_id
               JOIN credit_agreement a ON a.agreement_id = ld.agreement_id
               WHERE a.institution_id = ?""",
            (inst_id,),
        ).fetchone()[0] or 0.0
        dep_sum = c.execute(
            """SELECT SUM(abs.ledger_balance)
               FROM account_balance_snapshot abs
               JOIN account ac ON ac.account_id = abs.account_id
               WHERE ac.institution_id = ? AND ac.account_kind = 'SAVINGS'""",
            (inst_id,),
        ).fetchone()[0] or 1.0
        scale = (loan_sum / ltd) / dep_sum
        c.execute(
            """UPDATE account_balance_snapshot
               SET ledger_balance = ROUND(ledger_balance * ?, 2),
                   available_balance = ROUND(available_balance * ?, 2),
                   debit_balance = ROUND(debit_balance * ?, 2)
               WHERE account_id IN (
                   SELECT account_id FROM account WHERE institution_id = ? AND account_kind = 'SAVINGS'
               )""",
            (scale, scale, scale, inst_id),
        )

    # delinquency + classification + provision: 5-level consistency is enforced by
    # regulation, so a loan's overdue days drive its grade --- with deliberate,
    # queryable exceptions planted below.
    offenders = set()
    for idx, (lid, _, inst, obligor, product, disbursed) in enumerate(LOANS):
        overdue_days = 0
        if rng.random() < 0.28:
            overdue_days = rng.choice([15, 45, 95, 100, 190, 200, 300, 370, 400])
        if overdue_days:
            c.execute("INSERT INTO delinquency_snapshot VALUES (?,?,?,?,?,?,?)",
                      (f"DLQ-{lid}", lid, AS_OF, overdue_days,
                       max(0, overdue_days - rng.randint(0, 20)),
                       round(rng.uniform(10000, 5_000_000), 2),
                       round(rng.uniform(1000, 200_000), 2)))
        if overdue_days == 0:
            grade = rng.choices(["NORMAL", "SPECIAL_MENTION"], [88, 12])[0]
        elif overdue_days < 90:
            grade = "SPECIAL_MENTION" if rng.random() < 0.9 else "NORMAL"
        elif overdue_days < 180:
            grade = "SUBSTANDARD" if rng.random() < 0.85 else "SPECIAL_MENTION"
        elif overdue_days < 360:
            grade = "DOUBTFUL" if rng.random() < 0.85 else "SUBSTANDARD"
        else:
            grade = "LOSS" if rng.random() < 0.85 else "DOUBTFUL"
        c.execute("INSERT INTO risk_classification VALUES (?,?,?,?,?,?,?)",
                  (f"RC-{lid}", lid, AS_OF, grade,
                   rng.choice(["AUTOMATIC", "MANUAL_REVIEW"]),
                   rng.choice([u for u, ui, _ in UNITS if ui == inst]), None))
        c.execute("INSERT INTO provision_snapshot VALUES (?,?,?,?,?,?,?,?)",
                  (f"PROV-{lid}", lid, AS_OF,
                   "STAGE_1" if grade == "NORMAL" else ("STAGE_2" if grade == "SPECIAL_MENTION" else "STAGE_3"),
                   round(rng.uniform(0.01, 0.9) * 10_000_000, 2),
                   round(rng.uniform(0.005, 0.85) * 10_000_000, 2), "CNY",
                   rng.choice(["MODEL", "MANUAL"])))

    # ---------------- related parties / exposure groups ---------------------
    rel = 0
    for p in CORPORATES:
        if rng.random() > 0.25:
            continue
        other = rng.choice(CORPORATES)[0]
        if other == p[0]:
            continue
        rel += 1
        rtype = rng.choices(
            [r[0] for r in RELATION_TYPES],
            [18, 18, 18, 18, 13, 15],
        )[0]
        c.execute("INSERT INTO party_relation (relation_id, source_party_id, target_party_id,"
                  " relation_type, effective_from, effective_to, confidence_level, source_kind)"
                  " VALUES (?,?,?,?,?,?,?,?)",
                  (f"REL-{rel:05d}", p[0], other, rtype,
                   rand_date(rng, "2018-01-01", "2025-12-31"), None,
                   round(rng.uniform(0.5, 1.0), 2),
                   rng.choice(["REGISTRY", "SELF_DECLARED", "MEDIA"])))
    groups = 0
    for i in range(1, 121):
        gid = f"EG-{i:04d}"
        groups += 1
        c.execute("INSERT INTO exposure_group VALUES (?,?,?,?,?,?)",
                  (gid, INSTS[i % len(INSTS)][0], f"集团客户群{i:03d}",
                   "GROUP_CUSTOMER" if i % 2 else "CONNECTED_CUSTOMER",
                   rand_date(rng, "2020-01-01", "2025-12-31"), None))
        for member in rng.sample(CORPORATES, k=rng.randint(2, 6)):
            c.execute("INSERT INTO exposure_group_member VALUES (?,?,?,?,?)",
                      (f"EGM-{gid}-{member[0]}", gid, member[0],
                       rand_date(rng, "2020-01-01", "2025-12-31"), None))

    # ---------------- payments --------------------------------------------
    pe = 0
    for i in range(1, 26001):
        pe += 1
        from_acc = rng.choice(ACCOUNTS)
        to_acc = rng.choice([a for a in ACCOUNTS if a != from_acc])
        ptype = rng.choice([p[0] for p in PAYMENT_TYPES])
        is_cash = 1 if ptype.startswith("CASH") else 0
        if is_cash == 1:               # a cash movement touches exactly one ledger leg
            if ptype == "CASH_DEPOSIT":
                from_acc = None
            else:
                to_acc = None
        bdate = rand_date(rng, "2026-01-01", AS_OF)
        c.execute("INSERT INTO payment_event (payment_id, from_account_id, to_account_id,"
                  " business_date, event_time, amount, currency_code, payment_type, channel,"
                  " is_cash, memo, operator_id, origin_org_unit_id, balance_after, status,"
                  " exception_flag) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
                  (f"PAY-{i:07d}", from_acc, to_acc, bdate,
                   f"{rng.randint(8, 19):02d}:{rng.randint(0, 59):02d}:00",
                   round(rng.choice([rng.uniform(100, 200_000),
                                     rng.uniform(200_000, 5_000_000),
                                     rng.uniform(5_000_000, 60_000_000)]), 2),
                   "CNY", ptype, rng.choice(["COUNTER", "ONLINE", "ATM", "MOBILE"]),
                   is_cash, None,
                   rng.choice(OPERATORS) if rng.random() < 0.3 else None,
                   rng.choice([u for u, _, _ in UNITS]),
                   round(rng.uniform(0, 5_000_000), 2),
                   rng.choices(["SETTLED", "REVERSED"], [97, 3])[0]))
    for i, (lid, agr, inst, obligor, product, disbursed) in enumerate(LOANS[:2500]):
        payee = rng.choice(CORPORATES)[0]
        amount = c.execute("SELECT disbursed_amount FROM loan_drawdown WHERE loan_id=?",
                           (lid,)).fetchone()[0]
        c.execute("INSERT INTO payment_instruction (instruction_id, loan_id, payment_mode,"
                  " intended_payee_party_id, intended_payee_account_id, instruction_date,"
                  " instruction_amount, currency_code, status, exception_flag)"
                  " VALUES (?,?,?,?,?,?,?,?,?,0)",
                  (f"INS-{lid}", lid, rng.choice([p[0] for p in PAYMENT_MODES]), payee,
                   rng.choice(ACCOUNTS), add_days(disbursed, rng.randint(1, 20)),
                   round(amount * rng.uniform(0.3, 1.0), 2), "CNY",
                   rng.choices(["EXECUTED", "PENDING"], [95, 5])[0]))

    # (e) newly opened accounts with no transaction history yet
    fresh = 0
    for i in range(1, 121):
        fresh += 1
        aid = f"ACC-NEW-{fresh:05d}"
        inst = INSTS[i % len(INSTS)][0]
        unit = [u for u, ui, _ in UNITS if ui == inst][i % 6]
        c.execute("INSERT INTO account (account_id, institution_id, org_unit_id, account_kind,"
                  " account_subtype, currency_code, opened_on, closed_on, last_activity_on,"
                  " is_external, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (aid, inst, unit, "SAVINGS", "BASIC", "CNY",
                   rand_date(rng, "2026-05-01", AS_OF), None, None, 1, "ACTIVE"))

    # ---------------- planted business patterns -----------------------------
    # A benchmark warehouse has to actually contain the phenomena its questions
    # ask about; these blocks make staff self-dealing and related-party transfers
    # exist at a realistic frequency instead of relying on chance.
    STAFF_ACCOUNTS = {}
    for staff_id, person_id, inst, unit in STAFF[:60]:
        owned = c.execute("SELECT account_id FROM account_holder WHERE party_id=? LIMIT 1",
                          (person_id,)).fetchone()
        if owned:
            STAFF_ACCOUNTS[staff_id] = owned[0]
    ops = [r[0] for r in c.execute("SELECT operator_id FROM service_operator").fetchall()]
    self_deal = 0
    for staff_id, acc in list(STAFF_ACCOUNTS.items())[:40]:
        op = f"OP-{staff_id}"
        if op not in ops:
            continue
        for _ in range(rng.randint(1, 4)):
            self_deal += 1
            c.execute("INSERT INTO payment_event (payment_id, from_account_id, to_account_id,"
                      " business_date, event_time, amount, currency_code, payment_type, channel,"
                      " is_cash, memo, operator_id, origin_org_unit_id, balance_after, status,"
                      " exception_flag) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
                      (f"PAY-SELF-{self_deal:05d}", acc, None,
                       rand_date(rng, "2026-01-01", AS_OF), "10:00:00",
                       round(rng.uniform(200000, 9000000), 2), "CNY", "CASH_WITHDRAWAL",
                       "COUNTER", 1, "员工自办业务", op,
                       rng.choice([u for u, _, _ in UNITS]), 0.0, "SETTLED"))
    related_pay = 0
    rel_pairs = [(r[0], r[1], r[2]) for r in c.execute(
        "SELECT source_party_id, target_party_id, relation_type FROM party_relation")]
    for src, dst, rtype in rel_pairs[:130]:
        a1 = c.execute("SELECT account_id FROM account_holder WHERE party_id=? AND holder_role='PRIMARY' LIMIT 1",
                       (src,)).fetchone()
        a2 = c.execute("SELECT account_id FROM account_holder WHERE party_id=? AND holder_role='PRIMARY' LIMIT 1",
                       (dst,)).fetchone()
        if not a1 or not a2 or a1[0] == a2[0]:
            continue
        related_pay += 1
        pay_status = "REVERSED" if related_pay % 12 == 0 else "SETTLED"
        c.execute("INSERT INTO payment_event (payment_id, from_account_id, to_account_id,"
                  " business_date, event_time, amount, currency_code, payment_type, channel,"
                  " is_cash, memo, operator_id, origin_org_unit_id, balance_after, status,"
                  " exception_flag) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
                  (f"PAY-REL-{related_pay:05d}", a1[0], a2[0],
                   rand_date(rng, "2026-01-01", AS_OF), "14:00:00",
                   round(rng.uniform(1000000, 40000000), 2), "CNY", "TRANSFER",
                   "ONLINE", 0, "关联方资金往来", None,
                   rng.choice([u for u, _, _ in UNITS]), 0.0, pay_status))

    # ---------------- collateral / guarantee / secured_obligation ----------
    coll = 0
    for i in range(1, 701):
        coll += 1
        cid = f"COL-{i:05d}"
        c.execute("INSERT INTO collateral_asset VALUES (?,?,?,?,?,?)",
                  (cid, rng.choice(CORPORATES)[0], rng.choice(COLLATERAL_TYPES),
                   f"抵押物{i:05d}", "CNY", rng.choices(["ACTIVE", "RELEASED"], [88, 12])[0]))
        for k in range(rng.randint(1, 2)):
            c.execute("INSERT INTO collateral_valuation VALUES (?,?,?,?,?,?,?,?)",
                      (f"VAL-{cid}-{k}", cid, rand_date(rng, "2025-01-01", AS_OF),
                       round(rng.uniform(1_000_000, 900_000_000), 2), "CNY",
                       rng.choice(["EXTERNAL", "INTERNAL"]),
                       rng.choice(["APPRAISAL_FIRM", "BANK_INTERNAL"]), d(31, 12, 2026)))
    GUARANTOR_POOL = [p[0] for p in rng.sample(CORPORATES, 60)] + rng.sample(INDIVIDUALS, 40)
    for cid in rng.sample([f"COL-{i:05d}" for i in range(1, 701)], 12):
        for dup_k in (1, 2):
            c.execute("INSERT INTO collateral_valuation VALUES (?,?,?,?,?,?,?,?)",
                      (f"VALDUP-{cid}-{dup_k}", cid, "2026-03-31",
                       round(rng.uniform(1_000_000, 900_000_000), 2), "CNY",
                       "INTERNAL", "BANK_INTERNAL", "2026-12-31"))
    AGRS_BY_INST = {}
    for agr_id, inst_id, _, _ in AGREEMENTS:
        AGRS_BY_INST.setdefault(inst_id, []).append(agr_id)
    sec = 0
    for i in range(1, 901):
        sec += 1
        sid_ = f"SEC-{i:05d}"
        inst_id = INSTS[i % len(INSTS)][0]
        sec_status = rng.choices(["ACTIVE", "EXPIRED", "RELEASED"], [86, 8, 6])[0]
        sec_amt = round(rng.uniform(1_000_000, 500_000_000), 2)
        eff_from = rand_date(rng, "2023-01-01", "2025-12-31")
        c.execute("INSERT INTO security_agreement VALUES (?,?,?,?,?,?,?,?,?)",
                  (sid_, inst_id,
                   rng.choice(["MORTGAGE", "PLEDGE", "GUARANTEE", "CREDIT"]),
                   sec_amt, "CNY",
                   eff_from, d(31, 12, 2028),
                   rng.choice(STAFF)[0], sec_status))
        linked_agr = rng.choice(AGRS_BY_INST[inst_id])
        c.execute("INSERT INTO secured_obligation VALUES (?,?,?,?,?,?,?)",
                  (f"SO-{sid_}", sid_, linked_agr, None, sec_amt, eff_from, d(31, 12, 2028)))
        if rng.random() < 0.6:
            cl_status = rng.choices(["ACTIVE", "RELEASED"], [88, 12])[0]
            c.execute("INSERT INTO collateral_link VALUES (?,?,?,?,?,?,?,?,?,0)",
                      (f"CL-{sid_}", sid_, f"COL-{rng.randint(1, 700):05d}",
                       round(rng.uniform(1_000_000, 300_000_000), 2),
                       round(rng.uniform(0.3, 1.0), 4), rng.randint(1, 3),
                       eff_from, None, cl_status))
        if rng.random() < 0.45:
            gc_status = rng.choices(["ACTIVE", "EXPIRED"], [88, 12])[0]
            c.execute("INSERT INTO guarantor_commitment VALUES (?,?,?,?,?,?,?,?,0)",
                      (f"GC-{sid_}", sid_, GUARANTOR_POOL[rng.randrange(len(GUARANTOR_POOL))],
                       round(rng.uniform(1_000_000, 200_000_000), 2), "CNY",
                       eff_from, d(31, 12, 2027), gc_status))

    # ---------------- wealth management ------------------------------------
    WEALTH = []
    for i in range(1, 321):
        pid = f"WP-{i:05d}"
        WEALTH.append(pid)
        inception = rand_date(rng, "2024-01-01", "2026-03-31")
        sched = add_days(inception, rng.choice([180, 365, 730, 1095]))
        actual = add_days(sched, rng.randint(-20, 40)) if rng.random() < 0.5 else None
        c.execute("INSERT INTO wealth_product (product_id, issuer_institution_id, product_name,"
                  " product_category, offering_type, operation_mode, investment_nature,"
                  " risk_level, target_investor_type, currency_code, planned_raise_amount,"
                  " actual_raise_amount, offering_start_on, offering_end_on, inception_on,"
                  " scheduled_maturity_on, actual_termination_on, minimum_holding_days,"
                  " customer_redemption_allowed, is_cash_management, is_structured,"
                  " benchmark_floor_rate, benchmark_ceiling_rate, management_fee_rate,"
                  " custody_fee_rate, manager_party_id, custodian_party_id, status, exception_flag)"
                  " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
                  (pid, INSTS[i % len(INSTS)][0], f"{rng.choice(['稳健', '增利', '恒赢', '安心'])}"
                   f"{rng.randint(1, 200)}号", rng.choice(["FIXED_INCOME", "MIXED", "EQUITY", "CASH"]),
                   rng.choice(["PUBLIC", "PRIVATE"]), "CLOSED_END" if i % 3 else "OPEN_END",
                   rng.choice(["PRINCIPAL_GUARANTEED", "NON_GUARANTEED"]),
                   rng.choice(["R1", "R2", "R3", "R4", "R5"]),
                   rng.choice(["GENERAL", "PROFESSIONAL", "PRIVATE"]), "CNY",
                   round(rng.uniform(1e8, 5e9), 2), round(rng.uniform(5e7, 4e9), 2),
                   add_days(inception, -30), add_days(inception, -1), inception, sched, actual,
                   rng.choice([0, 7, 30, 90]), rng.choice([0, 1]), 1 if i % 5 == 0 else 0,
                   rng.choice([0, 1]), round(rng.uniform(1.5, 3.5), 3),
                   round(rng.uniform(3.5, 5.5), 3), round(rng.uniform(0.001, 0.02), 4),
                   round(rng.uniform(0.0005, 0.005), 4), None, None,
                   "TERMINATED" if actual else "ON_SALE"))
    ASSETS = []
    for i in range(1, 901):
        aid = f"AST-{i:05d}"
        ASSETS.append(aid)
        c.execute("INSERT INTO managed_asset VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (aid, INSTS[i % len(INSTS)][0], f"底层资产{i:05d}",
                   rng.choice(["STANDARDIZED", "NON_STANDARDIZED"]),
                   rng.choice(["BOND", "ABS", "TRUST_PLAN", "ASSET_MGMT_PLAN", "DEPOSIT"]),
                   rng.choice(["RATE", "CREDIT", "EQUITY", "COMMODITY"]),
                   rng.choice(CORPORATES)[0], rng.choice(CORPORATES)[0], rng.choice(SECTORS)[0],
                   "CN", rng.choice(["INTERBANK", "EXCHANGE", "OTC"]), "CNY",
                   round(rng.uniform(1e7, 3e9), 2), rand_date(rng, "2023-01-01", "2025-12-31"),
                   add_days(rand_date(rng, "2026-01-01", "2029-12-31"), 0),
                   round(rng.uniform(1.5, 6.0), 3), rng.choice(["AAA", "AA+", "AA", "A+", "BBB"]),
                   rng.choice(["AAA", "AA+", "AA", "A", "NR"]),
                   rng.choice(["AMORTIZED_COST", "FVOCI", "FVTPL"]), AS_OF,
                   1 if i % 7 == 0 else 0, "ACTIVE"))
    holds = 0
    for pid in WEALTH:
        for aid in rng.sample(ASSETS, k=rng.randint(1, 6)):
            holds += 1
            qty = round(rng.uniform(1e6, 2e8), 2)
            c.execute("INSERT INTO product_holding_snapshot VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (f"HOLD-{holds:06d}", pid, aid, AS_OF,
                       rng.choice(["DIRECT", "SPV", "NESTED_SPV"]), rng.randint(1, 3),
                       rng.choice(CORPORATES)[0] if rng.random() < 0.5 else None, "CNY",
                       qty, qty, round(qty * rng.uniform(0.9, 1.1), 2),
                       round(qty * rng.uniform(0.9, 1.1), 2),
                       round(rng.uniform(0.9, 1.1), 6), round(rng.uniform(0.9, 1.1), 6),
                       rng.randint(30, 2000)))

    # (c) employees borrowing from their own branch: an internal-control red flag
    for staff_id, person_id, inst, unit in rng.sample(STAFF, 18):
        agr_id = f"AGR-STAFF-{staff_id}"
        signed = rand_date(rng, "2025-01-01", "2026-05-31")
        c.execute("INSERT INTO credit_agreement (agreement_id, facility_id, institution_id,"
                  " borrower_party_id, managing_org_unit_id, product_family, purpose_text,"
                  " target_industry_code, contract_amount, currency_code, signed_on,"
                  " effective_from, maturity_on, interest_basis, annual_interest_rate,"
                  " rate_spread, payment_mode, security_type, business_context_token, status)"
                  " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (agr_id, FACILITIES[0][0], inst, person_id, unit, "RETAIL", "员工个人消费贷款",
                   "OTHER", round(rng.uniform(200000, 3000000), 2), "CNY", signed, signed,
                   add_days(signed, 730), "LPR", 4.35, 0.5, "SELF_PAYMENT", "CREDIT",
                   "NORMAL", "ACTIVE"))

    # ---------------- cards ------------------------------------------------
    for i in range(1, 901):
        cid = f"CARD-{i:05d}"
        c.execute("INSERT INTO payment_card (card_id, settlement_account_id, holder_party_id,"
                  " card_type, issued_on, expires_on, status, exception_flag)"
                  " VALUES (?,?,?,?,?,?,?,0)",
                  (cid, rng.choice(ACCOUNTS), rng.choice(INDIVIDUALS),
                   rng.choice([x[0] for x in CARD_TYPES]),
                   rand_date(rng, "2020-01-01", "2025-12-31"), d(31, 12, 2030),
                   rng.choices(["ACTIVE", "CLOSED"], [93, 7])[0]))

    # (d) retail channel: some product holdings are sold to individual card holders
    card_holders = [r[0] for r in c.execute(
        "SELECT DISTINCT holder_party_id FROM payment_card").fetchall()]
    for hid in [r[0] for r in c.execute(
            "SELECT holding_id FROM product_holding_snapshot ORDER BY holding_id LIMIT 220")]:
        c.execute("UPDATE product_holding_snapshot SET intermediary_party_id = ?"
                  " WHERE holding_id = ?", (rng.choice(card_holders), hid))

    # ---------------- regulatory event ledgers -----------------------------
    LEDGER_ZH = {
        "prud_metric": ("审慎监管指标", "监管指标快照", [
            "单一集团客户授信集中度超标监测",
            "单一客户贷款集中度超标监测",
            "存贷比与流动性比例异常监测",
            "拨备覆盖率与贷款拨备率不达标监测",
            "全部关联度指标超监管阈值监测",
            "核心一级资本充足率逼近监管红线监测",
            "流动性覆盖率与净稳定资金比例偏低监测",
            "最大十家客户贷款比例超标监测",
            "同业融出资金占一级资本净额超标监测",
            "非标债权资产投资占总资产比例超标监测",
        ]),
        "submission": ("监管报送", "监管数据报送事项", [
            "EAST监管数据错报漏报事项",
            "1104非现场监管报表迟报事项",
            "信贷资产五级分类统计不实报送",
            "涉农与小微企业贷款统计数据失真",
            "案件风险信息瞒报迟报事项",
            "金融统计大集中系统存贷款数据不一致",
            "客户风险统计报表中集团关联关系漏报",
            "理财与表外业务登记系统底层资产漏报",
            "反洗钱大额和可疑交易报告迟报漏报",
            "监管检查发现问题整改情况报告虚假陈述",
        ]),
        "lending_control": ("信贷管控", "信贷业务管控事项", [
            "流动资金贷款违规挪用于房地产或股权投资",
            "个人贷款贷前尽职调查未核实收入与用途",
            "贷款资金受托支付审核不严或违规化整为零自主支付",
            "贷后跟踪检查缺失未发现信贷资金回流借款人",
            "发放借名顶名贷款或向不具备条件借款人放款",
            "违规发放借新还旧或以贷收息掩盖不良",
            "对未取得四证或未竣工验收房地产项目放款",
            "固定资产贷款项目资本金比例不达标即放款",
            "个人经营性贷款违规流入证券市场或购房",
            "授信额度测算脱离企业真实经营现金流",
        ]),
        "governance": ("公司治理", "公司治理控制事项", [
            "违反审贷分离与分级授权越权审批贷款",
            "内部控制缺陷限期整改逾期未完成",
            "分支机构常规稽核与内审监督缺失",
            "信贷绩效考核机制不审慎诱发违规放款",
            "重大风险事项未按规定向董事会或监管报告",
            "关键管理岗位人员长期未实施强制休假与轮岗",
            "对下属分支行负责人离任审计流于形式",
            "薪酬延期支付与违规绩效追索机制未执行",
            "印章与重要空白凭证双人分管双锁制度未落实",
            "合规风险年度评估报告未按期提交董事会审议",
        ]),
        "related_txn": ("关联交易", "关联交易审查事项", [
            "向关系人违规发放信用贷款",
            "向关系人发放担保贷款条件优于同类借款人",
            "重大关联交易未经关联交易控制委员会审批",
            "股东及关联方隐蔽占用银行信贷资金",
            "以贷款资金偿还公司股东个人对外欠款",
            "未按规定及时更新维护商业银行关联方名单",
            "通过同业通道或信托计划向关联方隐性输血",
            "主要股东在本行授信余额超资本净额法定比例",
            "本行信贷经办人员向近亲属控制企业违规放款",
            "关联交易信息披露不完整或未按季报送监管",
        ]),
        "deposit": ("存款保护", "存款人权益保护事项", [
            "月末冲时点办理空存空取虚增存贷款规模",
            "以贷转存或存贷挂钩变相抬高融资成本",
            "违反规定提高利率或不正当手段高息揽存",
            "无故拖延或拒绝支付存款人到期本金和利息",
            "将单位资金违规以个人名义开立账户存储",
            "违规通过第三方中介返利贴息吸收异地存款",
            "对质押定期存单未实行止付冻结即发放贷款",
            "违规扣划存款人账户资金归还他人逾期贷款",
            "开立虚假单位定期存单为企业套取银行信用",
            "向存款客户隐瞒结构性存款收益浮动风险",
        ]),
        "kYC": ("客户尽调", "客户身份识别与尽职调查事项", [
            "开立个人存款账户未严格登记有效实名证件",
            "对公客户开户尽职调查与实地核查未到位",
            "高风险客户持续身份识别与定期复核超期",
            "代理开户未核实代理人与被代理人真实关系",
            "久悬睡眠账户激活前未重新开展身份核验",
            "身份证件过期超合理期限未中止非柜面业务",
            "异常高频开户客户未启动反电诈加强型尽调",
            "政治公众人物及特定非金融机构身份核查缺失",
            "企业法定代表人变更后未及时更新开户留存档案",
            "非面对面电子渠道开户未完成多重交叉验证",
        ]),
        "op_risk": ("操作风险", "操作风险事件", [
            "柜员违规自办业务或代客户保管存折印鉴",
            "员工利用个人账户归集过渡并截留客户资金",
            "重要岗位轮岗与强制休假制度未落实",
            "银企对账制度执行流于形式未发现异常挂账",
            "金库尾箱管理与大额现金支取审核不严",
            "营业场所监控录像缺失或柜面私下交接现金",
            "员工违规参与民间借贷或充当资金掮客",
            "离职或调岗员工系统操作权限未在当日注销",
            "内部过渡账户挂账超期未清理掩盖资金亏空",
            "虚假用印或违规预先在空白合同上加盖公章",
        ]),
        "data_sec": ("数据安全", "数据安全事件", [
            "非法查询冻结或扣划个人储蓄与单位存款",
            "违规向外部第三方泄露客户个人金融信息",
            "未经客户授权批量查询征信与账户流水记录",
            "核心业务系统操作员权限未及时回收越权访问",
            "外包服务机构接触敏感客户数据未脱敏管控",
            "生产环境敏感客户数据未脱敏直接导入测试库",
            "个人征信查询未留存书面授权档案或超范围查询",
            "高管及重要客户账户信息访问未开启双因子审计",
            "重要业务系统日志留存不足法定期限或被篡改",
            "向催收外包机构违规传输借款人通讯录隐私数据",
        ]),
        "conduct": ("产品行为", "产品销售行为规范事项", [
            "向普通投资者违规销售高风险等级理财产品",
            "理财产品销售未严格执行录音录像双录要求",
            "信贷业务浮利分费或违规转嫁抵押评估费用",
            "同业与理财非标债权资产违规提供隐性担保",
            "借贷搭售理财保险产品违背公平自愿原则",
            "对小微企业违规收取承诺费或资金管理顾问费",
            "代销私募资管产品未由总行统一准入审批",
            "理财产品宣传材料使用预期收益率误导刚性兑付",
            "违规调整客户风险承受能力测评结果以促成销售",
            "信用卡分期业务未明示年化综合息费率水平",
        ]),
        "ubo": ("受益所有人", "受益所有人识别事项", [
            "复杂股权结构对公客户未穿透识别受益所有人",
            "多层嵌套资管产品底层最终债务人未穿透登记",
            "集团客户隐匿关联关系规避统一授信管控",
            "空壳公司异常开户未核实实际控制人身份",
            "跨境交易对手受益所有人信息缺失未补录",
            "合伙企业与信托客户未识别拥有控制权自然人",
            "受益所有人持股比例变更超过阈值未重新登记",
            "利用名义股东代持股份掩盖最终受益所有人",
            "离岸注册企业客户未获取经公证股权架构文件",
            "受益所有人身份存疑但未按规定提交可疑报告",
        ]),
        "license": ("许可管理", "经营许可与资质事项", [
            "董事及高级管理人员未经任职资格核准实际履职",
            "未经批准擅自变更分支机构营业场所或名称",
            "金融许可证记载事项变更未按期向监管换证",
            "持有股份总额5%以上股东变更未报监管审批",
            "超经营范围违规从事未经批准的金融业务",
            "分支机构未在营业场所显著位置公示金融许可证",
            "未经批准擅自设立分支机构或延伸网点揽储",
            "高级管理人员代为履职超过法定期限未报批",
            "金融许可证遗失或损坏未按规定公告及申请补发",
            "主要股东以非自有资金或委托资金违规入股银行",
        ]),
        "custody": ("托管业务", "资产托管运作事项", [
            "同业投资与资管计划托管净值复核未尽职",
            "托管账户大额资金划转指令未核验贸易背景",
            "违规开展通道类同业理财规避监管指标",
            "不良金融资产虚假转让或违规出表藏匿风险",
            "抵债资产接收不审慎及保管处置不当造成流失",
            "抵债资产超法定处置期限未处置且未足额减值",
            "信贷资产转让附带回购协议实现非真实出表",
            "批量转让不良资产包违规纳入正常类借据",
            "托管业务部门与本行自营资管业务未严格风险隔离",
            "对托管资管计划超投资比例限制行为未履行监督报告",
        ]),
        "fx": ("外汇业务", "外汇与跨境业务事项", [
            "票据承兑与贴现业务贸易背景真实性审核不严",
            "跨境结售汇交易未核验真实合规单证背景",
            "滚动签发银行承兑汇票并以贴现资金虚增存款",
            "构造虚假跨境贸易合同套取境内外利差汇差",
            "外汇保证金账户异常高频划转未触发合规拦截",
            "为无真实贸易背景企业违规办理内保外贷业务",
            "个人分拆结售汇规避年度便利化额度管控未拦截",
            "转口贸易外汇收支单证核验流于形式未查验提单",
            "内保外贷履约垫款后未按规定登记对外债权",
            "远期结售汇业务未确认客户真实汇率避险需求",
        ]),
        "ai": ("智能系统", "人工智能系统应用事项", [
            "线上个人消费贷款自动化审批模型未识别多头借贷",
            "智能风控规则阈值配置错误放行高风险授信申请",
            "信贷资金回流智能监测模型漏报闭环交易链路",
            "自动化五级分类模型未及时下调逾期超90天借据",
            "反洗钱可疑交易监测模型参数超期未校准验证",
            "信用卡套现识别模型漏报同一商户高频大额刷卡",
            "智能押品估值模型未反映房地产市场价格下跌",
            "关联方图谱识别模型未穿透多层交叉持股关系",
            "电信网络诈骗涉案账户实时阻断模型响应超时",
            "人工智能催收语音系统违规在非工作时段高频外呼",
        ]),
    }
    for code, (family, name, specific_names) in LEDGER_ZH.items():
        for k in range(1, 26):
            ev_name_zh = specific_names[k - 1] if k <= len(specific_names) else f"{name}第{k}项"
            c.execute("INSERT INTO regulatory_event_catalog VALUES (?,?,?)",
                      (f"{code}_{k:03d}", ev_name_zh, family))
    ev = 0
    ledgers = ["prudential_metric_snapshot_v3", "regulatory_submission_event_v3",
               "lending_control_event_v3", "governance_control_record_v3",
               "related_transaction_record_v3", "deposit_protection_record_v3",
               "customer_due_diligence_event_v3", "operational_risk_event_v3",
               "data_security_event_v3", "product_conduct_event_v3",
               "beneficial_owner_record_v3", "license_record_v3",
               "custody_operation_event_v3", "fx_business_event_v3", "ai_system_record_v3"]
    for table in ledgers:
        code = EVENT_TABLES[table][0]
        n = 600 if table == "prudential_metric_snapshot_v3" else 260
        for k in range(n):
            ev += 1
            inst = INSTS[k % len(INSTS)][0]
            subject = (CORPORATES + [(p, None) for p in INDIVIDUALS])[k % 700][0]
            event_date = rand_date(rng, "2026-01-01", AS_OF)
            deadline = add_days(event_date, rng.choice([5, 10, 15, 30, 60]))
            roll = rng.random()
            if roll < 0.45:
                # Completed on time (on or before deadline)
                completion = add_days(deadline, -rng.randint(0, 4))
            elif roll < 0.72:
                # Completed late (after deadline)
                completion = add_days(deadline, rng.randint(1, 60))
            else:
                # Not yet completed (some overdue as of AS_OF, some with future deadline)
                completion = None
            c.execute(f"INSERT INTO {table} (record_id, institution_id, subject_id, event_code,"
                      " event_date, deadline_date, completion_date, observed_value, count_value,"
                      " amount_value, ratio_value, status_code, exception_flag, source_record_id)"
                      " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (f"{code.upper()}-{ev:06d}", inst, subject,
                       f"{code}_{k % 25 + 1:03d}", event_date, deadline, completion,
                       round(rng.uniform(0, 100), 4), rng.randint(0, 500),
                       round(rng.uniform(0, 5e8), 2), round(rng.uniform(0, 150), 4),
                       rng.choices(["ACTIVE", "VOID"], [96, 4])[0],
                       1 if rng.random() < 0.08 else 0, f"SRC-{ev:07d}"))

    # ---------------- financial / exposure snapshots -----------------------
    for i, (inst, _, cap) in enumerate(INSTS):
        # INST-006 is set below 0.10 CAR so CAR > 0.10 filters are non-tautological
        car = 0.088 if i == len(INSTS) - 1 else rng.uniform(0.11, 0.19)
        c.execute("INSERT INTO capital_snapshot VALUES (?,?,?,?,?,?,?,?)",
                  (f"CAP-{inst}", inst, AS_OF, "CNY", round(cap, 2),
                   round(cap * 0.80, 2), round(cap * 0.88, 2), round(cap / car, 2)))
        c.execute("INSERT INTO financial_snapshot VALUES (?,?,?,?,?,?,?,?,?)",
                  (f"FIN-{inst}", f"PTY-{inst}", AS_OF, "CNY",
                   round(cap * rng.uniform(8, 14), 2), round(cap * rng.uniform(0.6, 1.2), 2),
                   round(cap * rng.uniform(0.05, 0.12), 2), round(cap * rng.uniform(0.05, 0.2), 2),
                   "REGULATORY_REPORT"))

    bad = list(c.execute("PRAGMA foreign_key_check").fetchall())
    if bad:
        from collections import Counter
        print("FK violations before commit:", Counter(b[0] for b in bad))
    conn.commit()
    print("table                      rows")
    total = 0
    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' "
                                      "AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()]
    for t in tables:
        n = c.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        total += n
        if n:
            print(f"  {t:38s} {n:>8d}")
    print(f"  {'TOTAL':38s} {total:>8d}")
    print("FK violations:", len(list(c.execute("PRAGMA foreign_key_check").fetchall())))
    conn.close()


if __name__ == "__main__":
    main()
