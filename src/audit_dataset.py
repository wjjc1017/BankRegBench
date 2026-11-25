#!/usr/bin/env python3
"""Three-way consistency quality gate for BankRegBench (Question <-> Gold SQL <-> Warehouse).

Combines:
  1. Programmatic Deep Checks (zero external dependencies, run with --skip-llm):
     - SQL execution & non-empty verification
     - Predicate ablation (tautology detector: checks if removing WHERE/HAVING changes results)
     - Join path & 1:N chasm-trap fan-out checks
     - Feature tag vs. SQL AST alignment
     - Physical schema & code leakage checks (tables, columns, uppercase codes, region codes)
  2. Optional LLM Semantic Audit (via any OpenAI-Compatible API):
     - Audits each (question, sql, referenced_schema, sample_rows, ablation_notes) for semantic
       consistency using environment variables or configs/models.json.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "eval"))

from llm_client import call_llm, load_model_endpoint  # noqa: E402
from questions import ITEMS  # noqa: E402

DB_PATH = ROOT / "data" / "bankreg.sqlite"
SCHEMA_PATH = ROOT / "data" / "schema.json"


def extract_referenced_tables(sql: str) -> list[str]:
    ctes = {m.group(1).lower() for m in re.finditer(r"(?:WITH|,)\s*(\w+)\s+AS\s*\(", sql, re.I)}
    out = []
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+([A-Za-z_]\w*)", sql, re.I):
        t = m.group(1)
        if t.lower() in ctes:
            continue
        if t not in out:
            out.append(t)
    return out


def infer_actual_features(sql: str) -> set[str]:
    u = sql.upper()
    feats = set()
    if re.search(r"\bWHERE\b", u):
        feats.add("FILTER")
    if re.search(r"\bJOIN\b", u):
        feats.add("JOIN")
    if re.search(r"\bGROUP\s+BY\b", u):
        feats.add("GROUP_BY")
    if re.search(r"\bHAVING\b", u):
        feats.add("HAVING")
    if re.search(r"\bSUM\s*\(", u):
        feats.add("SUM")
    if re.search(r"\bAVG\s*\(", u):
        feats.add("AVG")
    if re.search(r"\bCOUNT\s*\(", u):
        feats.add("COUNT")
    if re.search(r"\bCASE\s+WHEN\b|\bCASE\s+\w", u):
        feats.add("CASE")
    if "/" in u:
        feats.add("RATIO")
    if re.search(r"\bORDER\s+BY\b", u):
        feats.add("ORDER_BY")
    if re.search(r"\bLIMIT\b", u):
        feats.add("LIMIT")
    if re.search(r"\bWITH\s+\w+\s+AS\s*\(", u):
        feats.add("CTE")
    if re.search(r"\bOVER\s*\(", u):
        feats.add("WINDOW")
    if re.search(r"\bLAG\s*\(", u):
        feats.add("LAG")
    if re.search(r"\bNTILE\s*\(", u):
        feats.add("NTILE")
    if re.search(r"\bNOT\s+EXISTS\b", u):
        feats.add("NOT_EXISTS")
    elif re.search(r"\bEXISTS\b", u):
        feats.add("EXISTS")
    if re.search(r"\bUNION\b", u):
        feats.add("UNION")
    if re.search(r"\bINTERSECT\b", u):
        feats.add("INTERSECT")
    if re.search(r"\bEXCEPT\b", u):
        feats.add("EXCEPT")
    if re.search(r"\bLIKE\b", u):
        feats.add("LIKE")
    if re.search(r"\bIS\s+(?:NOT\s+)?NULL\b", u):
        feats.add("IS_NULL")
    if re.search(r"\bCOALESCE\s*\(", u):
        feats.add("COALESCE")
    if re.search(r"\bIN\s*\(", u):
        feats.add("IN")
    if re.search(r"\bJULIANDAY\s*\(", u):
        feats.add("DATE_MATH")

    ctes = {m.group(1).lower() for m in re.finditer(r"(?:WITH|,)\s*(\w+)\s+AS\s*\(", sql, re.I)}
    all_tabs = [
        m.group(1).lower()
        for m in re.finditer(r"\b(?:FROM|JOIN)\s+([A-Za-z_]\w*)", sql, re.I)
        if m.group(1).lower() not in ctes
    ]
    if len(all_tabs) != len(set(all_tabs)):
        feats.add("SELF_JOIN")
    return feats


def check_predicate_ablation(conn: sqlite3.Connection, sql: str, orig_rows: list) -> list[str]:
    """Check if removing ANY WHERE or HAVING clause leaves the result identical."""
    warnings = []
    for m in re.finditer(
        r"\bWHERE\s+(.*?)(?=\bGROUP\s+BY\b|\bHAVING\b|\bORDER\s+BY\b|\bLIMIT\b|\bUNION\b|\bINTERSECT\b|\)|;|$)",
        sql,
        re.I | re.S,
    ):
        cond = m.group(1).strip()
        if "(" in cond[:3]:
            continue
        ablated_sql = sql[: m.start()] + "WHERE 1=1 " + sql[m.end() :]
        try:
            ab_rows = conn.execute(ablated_sql).fetchall()
            if ab_rows == orig_rows:
                warnings.append(f"TAUTOLOGY_WHERE: Removing `WHERE {cond}` produces the EXACT same {len(orig_rows)} rows!")
        except Exception:
            pass
        if " OR " not in cond.upper() and " BETWEEN " not in cond.upper():
            parts = [p.strip() for p in re.split(r"\bAND\b", cond, flags=re.I) if p.strip()]
            if len(parts) > 1:
                for i, p in enumerate(parts):
                    rem = " AND ".join(parts[:i] + parts[i + 1 :])
                    sub_sql = sql[: m.start()] + f"WHERE {rem} " + sql[m.end() :]
                    try:
                        sub_rows = conn.execute(sub_sql).fetchall()
                        if sub_rows == orig_rows:
                            warnings.append(
                                f"REDUNDANT_CONJUNCT: Removing conjunct `{p}` leaves all {len(orig_rows)} rows unchanged!"
                            )
                    except Exception:
                        pass
    for m in re.finditer(
        r"\bHAVING\s+(.*?)(?=\bORDER\s+BY\b|\bLIMIT\b|\bUNION\b|\bINTERSECT\b|\)|;|$)",
        sql,
        re.I | re.S,
    ):
        cond = m.group(1).strip()
        ablated_sql = sql[: m.start()] + sql[m.end() :]
        try:
            ab_rows = conn.execute(ablated_sql).fetchall()
            if ab_rows == orig_rows:
                warnings.append(f"TAUTOLOGY_HAVING: Removing `HAVING {cond}` produces the EXACT same {len(orig_rows)} rows!")
        except Exception:
            pass
    return warnings


def check_join_anomalies(sql: str) -> list[str]:
    warnings = []
    if re.search(r"\bON\s+1\s*=\s*1\b", sql, re.I):
        warnings.append("JOIN_ON_1_EQ_1: Contains `JOIN ... ON 1 = 1` Cartesian join!")
    if re.search(r"sa\d*\.institution_id\s*=\s*a\d*\.institution_id", sql, re.I):
        warnings.append(
            "BOGUS_SECURITY_JOIN: Joins `security_agreement` to `credit_agreement` via `institution_id` instead of `secured_obligation`!"
        )
    if re.search(r"\bFROM\s+party_relation\s+pr\b.*?\bJOIN\s+credit_agreement\b.*?\bSUM\s*\(", sql, re.I | re.S) or re.search(
        r"\bFROM\s+credit_agreement\s+a\b.*?\bJOIN\s+party_relation\s+pr\b.*?\bSUM\s*\(", sql, re.I | re.S
    ):
        warnings.append(
            "CHASM_TRAP_FANOUT: Joining `credit_agreement` directly with `party_relation` and summing `contract_amount` causes 1:N fan-out duplication!"
        )
    if re.search(r"\bJOIN\s+party_relation\s+pr\b", sql, re.I) and not re.search(
        r"NON_RELATED|非关联方|relation_type", sql, re.I
    ):
        warnings.append(
            "UNFILTERED_PARTY_RELATION: Joins `party_relation` without filtering `relation_type` (includes `NON_RELATED` / 非关联方)!"
        )
    if re.search(r"\bJOIN\s+account_holder\s+ah\b", sql, re.I) and not re.search(
        r"holder_role|COUNT\s*\(\s*DISTINCT", sql, re.I
    ):
        if re.search(r"\bCOUNT\s*\(\s*\*\s*\)", sql, re.I):
            warnings.append(
                "ACCOUNT_HOLDER_FANOUT: Joins `account_holder` without `holder_role = 'PRIMARY'` while doing `COUNT(*)`, double-counting joint accounts!"
            )
    return warnings


def check_feature_mismatch(declared: list[str], sql: str) -> list[str]:
    actual = infer_actual_features(sql)
    warnings = []
    must_match = {
        "CTE", "WINDOW", "CASE", "HAVING", "LIMIT", "UNION", "INTERSECT", "EXCEPT",
        "SELF_JOIN", "LAG", "NTILE", "JOIN", "GROUP_BY", "SUM", "AVG", "COUNT",
        "EXISTS", "NOT_EXISTS", "CORRELATED_SUBQUERY",
    }
    for tag in declared:
        if tag in must_match and tag not in actual:
            warnings.append(f"FAKE_FEATURE_TAG: Declared `{tag}` in features, but SQL does not contain `{tag}`!")
    for tag in (
        "CTE", "WINDOW", "HAVING", "LIMIT", "UNION", "INTERSECT", "JOIN",
        "GROUP_BY", "SUM", "AVG", "COUNT", "EXISTS", "NOT_EXISTS",
    ):
        if tag in actual and tag not in declared:
            warnings.append(f"MISSING_FEATURE_TAG: SQL uses `{tag}` but it is not listed in features!")
    return warnings


def call_llm_audit(
    item: dict[str, Any],
    schema_info: dict[str, Any],
    sample_rows: list,
    total_rows: int,
    prog_warnings: list[str],
    endpoint: dict[str, Any],
) -> dict[str, Any]:
    tabs = extract_referenced_tables(item["sql"])
    schema_snippet = {}
    for t in tabs:
        if t in schema_info["tables"]:
            raw_t = schema_info["tables"][t]
            schema_snippet[t] = {
                "columns": [f"{c['name']} ({c['type']})" for c in raw_t["columns"]],
                "foreign_keys": raw_t["foreign_keys"],
                "sample_values": raw_t.get("values", [])[:15],
            }
    prompt = f"""你是银行监管数据仓库（BankRegSQL v4）与 SQL 专家审稿人。
请严格检查以下 NL2SQL 数据集样本的【问题（Question）】、【标准SQL（Gold SQL）】与【数据库Schema及执行结果】三者是否完全一致。

### 题目信息
- ID: {item['id']}
- 难度: {item['difficulty']}
- 声明特征: {item['features']}
- 自然语言问题: {item['question']}
- Gold SQL:
```sql
{item['sql']}
```

### 执行结果与程序静态检测告警
- 结果总行数: {total_rows}
- 前 3 行结果样本: {json.dumps(sample_rows[:3], ensure_ascii=False)}
- 程序化检测告警: {json.dumps(prog_warnings, ensure_ascii=False)}

### 涉及表结构（含外键与受控词表值域）
```json
{json.dumps(schema_snippet, ensure_ascii=False)}
```

### 数仓全局设计契约（重要背景，请勿将以下设计契约误判为错误）：
1. 所有快照表（`loan_balance_snapshot`, `account_balance_snapshot`, `delinquency_snapshot`, `risk_classification`, `provision_snapshot`, `capital_snapshot`）在本数仓中均为单日审计基准日快照（`as_of_date = '2026-06-30'`），每个实体仅有唯一一条最新快照记录（存在 UNIQUE 约束），因此无需再按 `as_of_date` 去重或过滤。
2. `payment_event` 表具有严格 CHECK 约束：当 `is_cash = 1`（现金交易）时，`from_account_id`（现金支取）与 `to_account_id`（现金存入）必有且仅有一个非空，因此 `COALESCE(from_account_id, to_account_id)` 在现金交易中能唯一定位交易账户。
3. SQL 中的 `ROUND(..., 2/4/6)` 以及 `ORDER BY` 末尾附加主键（如 `, loan_id`）属于保证结果确定性的标准写法，不视为与题面冲突。
4. 除非题面明确要求筛选特定状态（如“有效”、“正常”、“已清算”、“久悬”），否则 SQL 默认统计全量记录。

请重点排查以下真正的三方不一致错误：
1. 题面明确要求的业务条件在 SQL 中完全遗漏或写反（如题面要求“信用卡”未筛 `CREDIT`、要求“其他借据”未排除自身）。
2. 表/字段关联错误（如一对多 JOIN 未去重导致 SUM/COUNT 虚增翻倍、关联键写错）。
3. 输出列缺失或顺序与题面要求相反。
4. 程序化检测告警（`programmatic_warnings`）非空。

请只输出合法的 JSON 对象（不要加其他解释文字），格式如下：
{{
  "status": "PASS" | "ISSUE",
  "severity": "NONE" | "MINOR" | "MAJOR" | "CRITICAL",
  "issue_types": ["..."],
  "summary": "简明扼要指出不一致之处（若完全一致则写'三方一致'）",
  "fix_suggestion": "具体修复建议（如何改 question、sql 或 build_db.py）"
}}"""

    text = call_llm(endpoint, [{"role": "user", "content": prompt}], temperature=0.0, max_tokens=1024)
    if text.startswith("LLM_ERROR"):
        return {"status": "API_ERROR", "error": text}
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return {"status": "PARSE_ERROR", "raw": text[:300]}
    return {"status": "PARSE_ERROR", "raw": text[:300]}


def main() -> None:
    ap = argparse.ArgumentParser(description="Run 3-way consistency audit on BankRegBench.")
    ap.add_argument("--db", type=Path, default=DB_PATH)
    ap.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    ap.add_argument("--model", default="default", help="Model alias from configs/models.json or env")
    ap.add_argument("--models-config", type=Path, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--skip-llm", action="store_true", help="Run programmatic checks only (no API calls)")
    ap.add_argument("--out", type=Path, default=None, help="Optional path to write full JSON report")
    args = ap.parse_args()

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    schema_info = json.loads(args.schema.read_text(encoding="utf-8"))
    all_tables = set(schema_info["tables"].keys())
    all_cols = {c["name"] for v in schema_info["tables"].values() for c in v["columns"]}

    prog_results = {}
    for item in ITEMS:
        qid = item["id"]
        sql = item["sql"]
        qtext = item["question"]
        w = []
        try:
            rows = conn.execute(sql).fetchall()
        except Exception as exc:
            prog_results[qid] = {"rows": [], "total_rows": 0, "warnings": [f"SQL_EXEC_ERROR: {exc}"]}
            continue
        if not rows:
            w.append("EMPTY_RESULT: Returns 0 rows!")
        for t in all_tables:
            if re.search(r"(?<![A-Za-z_])" + re.escape(t) + r"(?![A-Za-z_])", qtext):
                w.append(f"LEAK_TABLE: Question names table `{t}`")
        for c in all_cols:
            if len(c) > 4 and re.search(r"(?<![A-Za-z_])" + re.escape(c) + r"(?![A-Za-z_])", qtext):
                w.append(f"LEAK_COLUMN: Question names column `{c}`")
        for code in set(re.findall(r"\b[A-Z][A-Z_]{3,}\b", qtext)):
            w.append(f"LEAK_CODE: Question contains uppercase code `{code}`")
        for reg_code in set(re.findall(r"“\d{6}”|'\d{6}'", qtext)):
            w.append(f"LEAK_REGION_CODE: Question contains raw region code `{reg_code}`")

        w.extend(check_predicate_ablation(conn, sql, rows))
        w.extend(check_join_anomalies(sql))
        w.extend(check_feature_mismatch(item["features"], sql))
        prog_results[qid] = {
            "rows": [list(r) for r in rows[:5]],
            "total_rows": len(rows),
            "warnings": w,
        }
    conn.close()

    llm_results: dict[str, dict[str, Any]] = {}
    if not args.skip_llm:
        endpoint = load_model_endpoint(args.model, config_path=args.models_config)
        print(f"Running LLM audit with {endpoint['model']} across {len(ITEMS)} items (workers={args.workers})...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = {
                ex.submit(
                    call_llm_audit,
                    it,
                    schema_info,
                    prog_results[it["id"]]["rows"],
                    prog_results[it["id"]]["total_rows"],
                    prog_results[it["id"]]["warnings"],
                    endpoint,
                ): it["id"]
                for it in ITEMS
            }
            done = 0
            for fut in concurrent.futures.as_completed(futs):
                qid = futs[fut]
                llm_results[qid] = fut.result()
                done += 1
                if done % 25 == 0 or done == len(ITEMS):
                    print(f"  completed {done}/{len(ITEMS)}", flush=True)

    combined = []
    prog_warn_cnt = 0
    llm_flag_cnt = 0
    for it in ITEMS:
        qid = it["id"]
        pr = prog_results[qid]
        lr = llm_results.get(qid, {})
        has_prog = bool(pr["warnings"])
        has_llm = (not args.skip_llm) and lr.get("status") != "PASS"
        if has_prog:
            prog_warn_cnt += 1
        if has_llm:
            llm_flag_cnt += 1
        combined.append({
            "question_id": qid,
            "difficulty": it["difficulty"],
            "features": it["features"],
            "question": it["question"],
            "sql": it["sql"],
            "total_rows": pr["total_rows"],
            "programmatic_warnings": pr["warnings"],
            "llm_audit": lr,
            "has_issue": has_prog or has_llm,
        })

    report = {
        "total_questions": len(ITEMS),
        "programmatic_warning_questions": prog_warn_cnt,
        "llm_flagged_questions": llm_flag_cnt if not args.skip_llm else None,
        "total_flagged_questions": sum(1 for x in combined if x["has_issue"]),
        "items": combined,
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved full audit report to {args.out}")

    print(f"Audit complete across {report['total_questions']} questions:")
    print(f"  Programmatic warnings: {prog_warn_cnt} questions")
    if not args.skip_llm:
        print(f"  LLM flagged issues:    {llm_flag_cnt} questions")
    print(f"  Total flagged:         {report['total_flagged_questions']} questions")
    raise SystemExit(1 if report["total_flagged_questions"] else 0)


if __name__ == "__main__":
    main()
