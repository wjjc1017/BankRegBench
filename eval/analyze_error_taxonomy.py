#!/usr/bin/env python3
"""7-Category Error Taxonomy Analysis for BankRegBench Standard Evaluation (Track L0).

Reproduces the deterministic error attribution across all 28 configurations
(7 frameworks x 4 models x 200 held-out questions = 5,600 evaluations) using Python stdlib only.

Outputs:
  - Compact summary JSON (`results/error_taxonomy_summary.json`, ~4 KB)
  - Optional full per-instance error records JSON (`--write-full-records`, ~5.5 MB)
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))

from evaluate import result_multiset, rows_match_tolerant  # noqa: E402

DB_PATH = ROOT / "data" / "bankreg.sqlite"
QUESTIONS_PATH = ROOT / "data" / "questions.jsonl"
SCHEMA_PATH = ROOT / "data" / "schema.json"
DEFAULT_PREDS_DIR = ROOT / "results" / "predictions_standard"
DEFAULT_OUT_SUMMARY = ROOT / "results" / "error_taxonomy_summary.json"

CATALOG_TABLES = {
    "classification_grade",
    "industry_sector",
    "loan_product_catalog",
    "status_catalog",
    "relation_type_catalog",
    "payment_mode_catalog",
    "payment_type_catalog",
    "card_type_catalog",
    "party_type_catalog",
    "instrument_type_catalog",
    "regulatory_event_catalog",
    "exposure_group_type_catalog",
}
BRIDGE_TABLES = {
    "credit_agreement",
    "secured_obligation",
    "collateral_link",
    "account_holder",
    "exposure_group_member",
    "service_operator",
}

DEFAULT_MODELS = [
    "deepseek-v4-flash",
    "deepseek-v4.1-flash",
    "qwen3.5-397b-a17b",
    "qwen3.6-35b-a3b",
]
DEFAULT_FRAMEWORKS = [
    "direct_ddl",
    "m_schema",
    "schemagate",
    "dail_sql",
    "rsl_sql",
    "chess",
    "deepeye_axissql",
]


def extract_tables(sql: str, valid_tables: set[str]) -> set[str]:
    ctes = {m.group(1).lower() for m in re.finditer(r"(?:WITH|,)\s*(\w+)\s+AS\s*\(", sql, re.I)}
    out = set()
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+(?:main\.)?([A-Za-z_]\w*)", sql, re.I):
        t = m.group(1).lower()
        if t not in ctes and t in valid_tables:
            out.add(t)
    return out


def classify_error(
    conn: sqlite3.Connection,
    q: dict,
    pred_sql: str,
    g_rows: list[tuple],
    valid_tables: set[str],
    empty_tables: set[str],
) -> tuple[str, str]:
    if not pred_sql or not pred_sql.strip():
        return "E1_SYNTAX_EXEC_ERROR", "Empty SQL"
    t0 = time.time()
    conn.set_progress_handler(lambda: 1 if time.time() - t0 > 2.5 else 0, 10000)
    try:
        p_rows = conn.execute(pred_sql).fetchall()
    except Exception as exc:
        return "E1_SYNTAX_EXEC_ERROR", str(exc)
    finally:
        conn.set_progress_handler(None, 0)

    if result_multiset(g_rows) == result_multiset(p_rows):
        return "CORRECT_STRICT", ""
    if rows_match_tolerant(g_rows, p_rows):
        return "E7_PRECISION_ROUNDING_ONLY", "Matches at 2-dec tolerance (missing ROUND)"

    g_tabs = set(q["tables"])
    p_tabs = extract_tables(pred_sql, valid_tables)

    if p_tabs & empty_tables:
        return "E2_DISTRACTOR_TABLE_TRAP", f"Selected empty distractor table(s): {sorted(p_tabs & empty_tables)}"

    g_cats = g_tabs & CATALOG_TABLES
    if len(p_rows) == 0:
        if g_cats and not (p_tabs & g_cats):
            return "E3_VOCAB_ENUM_HALLUCINATION", f"0 rows & missed catalog table(s): {sorted(g_cats)}"
        return "E3_VOCAB_ENUM_HALLUCINATION", "0 rows (hallucinated enum/filter literal)"

    g_core = g_tabs - CATALOG_TABLES
    p_core = p_tabs - CATALOG_TABLES
    missed_bridges = (g_core & BRIDGE_TABLES) - p_core
    if missed_bridges:
        return "E4_BRIDGE_JOIN_PATH_DROP", f"Missed bridge table(s): {sorted(missed_bridges)}"
    if g_core != p_core:
        return "E4_BRIDGE_JOIN_PATH_DROP", f"Table mismatch: gold={sorted(g_core)} pred={sorted(p_core)}"

    if len(p_rows[0]) != len(g_rows[0]):
        return "E6_PROJECTION_COLUMN_MISMATCH", f"Column count: gold={len(g_rows[0])} pred={len(p_rows[0])}"

    if len(p_rows) == len(g_rows):
        g_first = {str(r[0]) for r in g_rows}
        p_first = {str(r[0]) for r in p_rows}
        if g_first == p_first:
            return "E5A_AGGREGATION_RATIO_WINDOW", "Same entity keys & row count, but aggregated/calculated metric differs"

    return "E5B_PREDICATE_OR_JOIN_DRIFT", f"Row count diff: gold={len(g_rows)} pred={len(p_rows)}"


def select_representative_examples(records: list[dict]) -> list[dict]:
    picks = [
        ("E1_SYNTAX_EXEC_ERROR", "E1: Syntax & Phantom-Column Error"),
        ("E2_DISTRACTOR_TABLE_TRAP", "E2: Distractor-Table Trap"),
        ("E3_VOCAB_ENUM_HALLUCINATION", "E3: Vocabulary & Enum Hallucination"),
        ("E4_BRIDGE_JOIN_PATH_DROP", "E4: Bridge-Table & Core-Table Mismatch"),
        ("E5A_AGGREGATION_RATIO_WINDOW", "E5-A: Ratio Formula & Chasm-Trap Fan-out"),
    ]
    examples = []
    for key, title in picks:
        cand = [
            r for r in records
            if r["category"] == key and r["framework"] == "direct_ddl" and r["difficulty"] in ("easy", "medium")
        ] or [r for r in records if r["category"] == key]
        if cand:
            chosen = dict(min(cand, key=lambda x: len(x["predicted_sql"])))
            chosen["case_title"] = title
            examples.append(chosen)
    return examples


def main() -> None:
    ap = argparse.ArgumentParser(description="Run 7-category error taxonomy analysis on Standard Track L0 predictions.")
    ap.add_argument("--preds-dir", type=Path, default=DEFAULT_PREDS_DIR)
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--frameworks", nargs="+", default=DEFAULT_FRAMEWORKS)
    ap.add_argument("--out-summary", type=Path, default=DEFAULT_OUT_SUMMARY)
    ap.add_argument(
        "--write-full-records",
        type=Path,
        default=None,
        help="Optional path to also write all per-instance error records (~5.5 MB)",
    )
    args = ap.parse_args()

    questions = [json.loads(l) for l in QUESTIONS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    heldout = [q for q in questions if q["split"] in ("dev", "test")]
    by_id = {q["question_id"]: q for q in heldout}
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    valid_tables = set(schema["tables"].keys())
    empty_tables = {t for t, v in schema["tables"].items() if v["row_count"] == 0}

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")
    gold_rows_map = {q["question_id"]: conn.execute(q["sql"]).fetchall() for q in heldout}

    overall: Counter = Counter()
    by_fw: dict[str, Counter] = defaultdict(Counter)
    by_model: dict[str, Counter] = defaultdict(Counter)
    by_diff: dict[str, Counter] = defaultdict(Counter)
    records = []

    for m in args.models:
        for fw in args.frameworks:
            p = args.preds_dir / f"preds_l0_{fw}_{m}.jsonl"
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                d = json.loads(line)
                qid = d["question_id"]
                if qid not in by_id:
                    continue
                q = by_id[qid]
                cat, detail = classify_error(
                    conn, q, d["predicted_sql"], gold_rows_map[qid], valid_tables, empty_tables
                )
                if cat != "CORRECT_STRICT":
                    overall[cat] += 1
                    by_fw[fw][cat] += 1
                    by_model[m][cat] += 1
                    by_diff[q["difficulty"]][cat] += 1
                    records.append(
                        {
                            "question_id": qid,
                            "difficulty": q["difficulty"],
                            "split": q["split"],
                            "framework": fw,
                            "model": m,
                            "category": cat,
                            "detail": detail,
                            "question": q["question"],
                            "gold_sql": q["sql"],
                            "predicted_sql": d["predicted_sql"],
                        }
                    )
    conn.close()

    total_evals = len(args.models) * len(args.frameworks) * len(heldout)
    total_errs = sum(overall.values())

    summary_out = {
        "total_evaluations": total_evals,
        "total_strict_errors": total_errs,
        "overall_error_rate_pct": round(total_errs / total_evals * 100, 2) if total_evals else 0.0,
        "overall_by_category": dict(overall),
        "by_framework": {k: dict(v) for k, v in by_fw.items()},
        "by_model": {k: dict(v) for k, v in by_model.items()},
        "by_difficulty": {k: dict(v) for k, v in by_diff.items()},
        "representative_examples": select_representative_examples(records),
    }
    args.out_summary.parent.mkdir(parents=True, exist_ok=True)
    args.out_summary.write_text(json.dumps(summary_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved taxonomy summary to {args.out_summary} ({total_errs}/{total_evals} strict errors)")

    if args.write_full_records:
        full_out = dict(summary_out)
        full_out["error_records"] = records
        args.write_full_records.parent.mkdir(parents=True, exist_ok=True)
        args.write_full_records.write_text(json.dumps(full_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Saved full error records ({len(records)} items) to {args.write_full_records}")


if __name__ == "__main__":
    main()
