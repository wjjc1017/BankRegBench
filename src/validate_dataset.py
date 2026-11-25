#!/usr/bin/env python3
"""Independent validation of the BankRegBench-v2 dataset.

Every check is a *falsifiable* statement about the shipped artefacts; the script
fails loudly rather than warning.  It exists so that the dataset can be checked
without trusting the builder.

Checks
------
1. every gold query executes and returns at least one row;
2. every gold query is deterministic (two executions agree);
3. the frozen answer in ``questions.jsonl`` reproduces exactly;
4. no question names a physical table, a physical column or a business code
   (the questions must be answerable from business language only);
5. the answer columns are unique and non-empty;
6. splits are disjoint and cover every question;
7. every referenced table exists in the schema and is populated;
8. difficulty labels are from the declared set and feature tags are declared;
9. SQL skeletons are distinct (no template collapse);
10. the warehouse passes ``PRAGMA foreign_key_check`` and ``PRAGMA integrity_check``.

Usage: python3 src/validate_dataset.py [--json data/validation_report.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "bankreg.sqlite"
QUESTIONS = ROOT / "data" / "questions.jsonl"
SCHEMA = ROOT / "data" / "schema.json"

DIFFICULTIES = {"easy", "medium", "hard", "extra"}
FEATURES = {
    "FILTER", "JOIN", "GROUP_BY", "HAVING", "SUM", "AVG", "COUNT", "CASE", "RATIO",
    "ORDER_BY", "LIMIT", "CTE", "WINDOW", "LAG", "NTILE", "CORRELATED_SUBQUERY",
    "EXISTS", "NOT_EXISTS", "UNION", "INTERSECT", "EXCEPT", "SELF_JOIN", "LIKE",
    "IS_NULL", "COALESCE", "IN", "DATE_MATH",
}


def skeleton(sql: str) -> str:
    s = re.sub(r"'[^']*'", "'?'", sql)
    s = re.sub(r"\b\d+(\.\d+)?\b", "?", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=ROOT / "data" / "validation_report.json")
    args = ap.parse_args()

    questions = [json.loads(l) for l in QUESTIONS.read_text(encoding="utf-8").splitlines() if l.strip()]
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    tables = schema["tables"]
    columns = {c["name"] for v in tables.values() for c in v["columns"]}
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    failures: list[str] = []
    stats: Counter = Counter()

    # 10. warehouse integrity
    fk = list(conn.execute("PRAGMA foreign_key_check"))
    if fk:
        failures.append(f"foreign_key_check reported {len(fk)} violations")
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        failures.append(f"integrity_check: {integrity}")

    # 1-4, 5 per question
    for q in questions:
        qid = q["question_id"]
        # 1/2/3
        try:
            rows = conn.execute(q["sql"]).fetchall()
            rows2 = conn.execute(q["sql"]).fetchall()
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{qid}: gold SQL failed: {exc}")
            continue
        if not rows:
            failures.append(f"{qid}: gold result is empty")
        if rows != rows2:
            failures.append(f"{qid}: gold result is not deterministic")
        # the frozen answer stores NULL as "" for JSON; normalise both sides
        def norm(v):
            if v is None or v == "":
                return None
            if isinstance(v, float):
                return round(v, 6)
            if isinstance(v, int):
                return float(v)
            return str(v).strip()

        frozen = [tuple(norm(v) for v in r) for r in q["answer"]]
        live = [tuple(norm(v) for v in r) for r in rows]
        if len(frozen) != len(live):
            failures.append(f"{qid}: frozen answer has {len(frozen)} rows, live run has {len(live)}")
        elif frozen != live:
            failures.append(f"{qid}: frozen answer differs from the live result")
        # 4. Zero physical schema/code leakage on Chinese question and English question_en
        text = q["question"]
        for t in tables:
            if re.search(r"(?<![A-Za-z_])" + re.escape(t) + r"(?![A-Za-z_])", text):
                failures.append(f"{qid}: question names the table {t}")
        for c in columns:
            if len(c) > 4 and re.search(r"(?<![A-Za-z_])" + re.escape(c) + r"(?![A-Za-z_])", text):
                failures.append(f"{qid}: question names the column {c}")
        for code in set(re.findall(r"\b[A-Z][A-Z_]{3,}\b", text)):
            failures.append(f"{qid}: question contains the code literal {code}")

        text_en = q.get("question_en", "")
        if not text_en or not text_en.strip():
            failures.append(f"{qid}: missing question_en")
        else:
            # In English text, strictly forbid any snake_case physical table/column identifier
            # and any UPPER_CASE enum code literal (common single words like 'status' or 'amount' are natural English).
            for t in tables:
                if "_" in t and re.search(r"(?<![A-Za-z_])" + re.escape(t) + r"(?![A-Za-z_])", text_en, re.I):
                    failures.append(f"{qid}: question_en names the table {t}")
            for c in columns:
                if "_" in c and re.search(r"(?<![A-Za-z_])" + re.escape(c) + r"(?![A-Za-z_])", text_en, re.I):
                    failures.append(f"{qid}: question_en names the column {c}")
            allowed_en_acronyms = {"EAST", "CBIRC", "NFRA", "PBOC", "SPV", "SQL", "SME", "NPL", "CAR", "LCR", "NSFR", "KYC", "AML", "VIP", "TOP", "USD", "CNY", "RMB", "FX", "AI", "IT", "HR", "II", "III", "IV", "R1", "R2", "R3", "R4", "R5"}
            for code in set(re.findall(r"\b[A-Z][A-Z_]{3,}\b", text_en)):
                if code not in allowed_en_acronyms:
                    failures.append(f"{qid}: question_en contains the code literal {code}")
        # 5
        if len(set(q["answer_columns"])) != len(q["answer_columns"]):
            failures.append(f"{qid}: duplicate output column names")
        if not q["answer_columns"]:
            failures.append(f"{qid}: no output columns")
        # 7/8
        for t in q["tables"]:
            if t not in tables:
                failures.append(f"{qid}: references unknown table {t}")
            elif tables[t]["row_count"] == 0:
                failures.append(f"{qid}: references empty table {t}")
        if q["difficulty"] not in DIFFICULTIES:
            failures.append(f"{qid}: unknown difficulty {q['difficulty']}")
        for f in q["features"]:
            if f not in FEATURES:
                failures.append(f"{qid}: unknown feature tag {f}")
        stats["tables_referenced" + str(q["num_tables"])] += 1

    # 6 splits
    split_of = {}
    for q in questions:
        if q["question_id"] in split_of:
            failures.append(f"{q['question_id']}: appears twice")
        split_of[q["question_id"]] = q["split"]
    for s in ("train", "dev", "test"):
        if not any(v == s for v in split_of.values()):
            failures.append(f"split {s} is empty")
    train = {k for k, v in split_of.items() if v == "train"}
    rest = {k for k, v in split_of.items() if v != "train"}
    if train & rest:
        failures.append("train overlaps dev/test")

    # 9 skeletons
    sk = Counter(skeleton(q["sql"]) for q in questions)
    dupes = {k: v for k, v in sk.items() if v > 1}
    if dupes:
        failures.append(f"{len(dupes)} duplicated SQL skeletons, e.g. {list(dupes)[:3]}")

    report = {
        "questions": len(questions),
        "distinct_sql_skeletons": len(sk),
        "schema_tables": len(tables),
        "tables_referenced": len({t for q in questions for t in q["tables"]}),
        "warehouse_rows": sum(v["row_count"] for v in tables.values()),
        "by_difficulty": dict(Counter(q["difficulty"] for q in questions)),
        "by_split": dict(Counter(q["split"] for q in questions)),
        "by_num_tables": dict(sorted(Counter(q["num_tables"] for q in questions).items())),
        "foreign_key_violations": len(fk),
        "integrity_check": integrity,
        "failures": failures,
    }
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "failures"}, ensure_ascii=False, indent=1))
    print(f"\nFAILURES: {len(failures)}")
    for f in failures[:40]:
        print("  -", f)
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
