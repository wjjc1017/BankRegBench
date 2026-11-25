#!/usr/bin/env python3
"""BankRegBench Execution Accuracy (EX-Strict & EX-Relaxed) Evaluation Harness.

Metrics
-------
1. **EX-Strict (6-decimal exact multiset match)**:
   Predicted query is executed read-only against `data/bankreg.sqlite`. Its result set must
   equal the gold result set as a multiset of rows (floats rounded to 6 decimals, ints cast
   to float, NULL/"" -> None, strings stripped). Column order is significant; row order is
   ignored unless `--ordered` is given.
2. **EX-Relaxed (bucketed decimal tolerance)**:
   Same multiset comparison, except numeric values with `|v| >= 1` are rounded to 2 decimals
   and ratios with `|v| < 1` are rounded to 4 decimals. This prevents penalizing semantically
   exact queries that omit an explicit `ROUND(..., 2)` wrapper.

Usage
-----
    python3 eval/evaluate.py --oracle
    python3 eval/evaluate.py --empty
    python3 eval/evaluate.py --predictions results/predictions_standard/preds_l0_deepeye_axissql_deepseek-v4.1-flash.jsonl --split dev test
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "bankreg.sqlite"
DEFAULT_QUESTIONS = ROOT / "data" / "questions.jsonl"


def normalise(v):
    if v is None or v == "":
        return None
    if isinstance(v, float):
        return round(v, 6)
    if isinstance(v, int):
        return float(v)
    if isinstance(v, str):
        return v.strip()
    return v


def result_multiset(rows) -> Counter:
    return Counter(tuple(normalise(v) for v in row) for row in rows)


def rows_match_tolerant(gold_rows: list[tuple], pred_rows: list[tuple]) -> bool:
    """Compare two result sets as multisets with bucketed 2-dec / 4-dec float tolerance."""
    if len(gold_rows) != len(pred_rows):
        return False
    if not gold_rows:
        return True
    if len(gold_rows[0]) != len(pred_rows[0]):
        return False

    def _bucket_row(r: tuple) -> tuple:
        out = []
        for v in r:
            if v is None or v == "":
                out.append(("N", None))
            elif isinstance(v, (int, float)):
                f = float(v)
                out.append(("F", round(f, 2) if abs(f) >= 1.0 else round(f, 4)))
            else:
                out.append(("S", str(v).strip()))
        return tuple(out)

    return Counter(_bucket_row(r) for r in gold_rows) == Counter(_bucket_row(r) for r in pred_rows)


_GOLD_CACHE: dict[tuple[str, str], list] = {}


def execute(conn: sqlite3.Connection, sql: str, timeout_sec: float = 2.5) -> list[tuple]:
    t0 = time.time()
    conn.set_progress_handler(lambda: 1 if time.time() - t0 > timeout_sec else 0, 10000)
    try:
        cur = conn.execute(sql)
        return cur.fetchall()
    finally:
        conn.set_progress_handler(None, 0)


def score_one(conn: sqlite3.Connection, db_key: str, gold_sql: str, pred_sql: str | None, ordered: bool = False):
    """Return (strict_ok, relaxed_ok, executable, detail)."""
    cache_key = (db_key, gold_sql)
    try:
        if cache_key not in _GOLD_CACHE:
            _GOLD_CACHE[cache_key] = execute(conn, gold_sql, timeout_sec=5.0)
        gold_rows = _GOLD_CACHE[cache_key]
    except Exception as exc:
        return False, False, False, f"gold failed: {exc}"

    if pred_sql is None or not str(pred_sql).strip():
        return False, False, False, "no prediction"

    try:
        pred_rows = execute(conn, pred_sql, timeout_sec=2.5)
    except Exception as exc:  # noqa: BLE001
        return False, False, False, f"prediction error: {exc}"

    if ordered:
        strict_ok = (
            [tuple(normalise(v) for v in r) for r in pred_rows]
            == [tuple(normalise(v) for v in r) for r in gold_rows]
        )
    else:
        strict_ok = result_multiset(pred_rows) == result_multiset(gold_rows)

    relaxed_ok = rows_match_tolerant(gold_rows, pred_rows)
    if strict_ok:
        return True, relaxed_ok, True, "match"
    if relaxed_ok:
        return False, True, True, "relaxed match (rounding only)"
    return False, False, True, f"row mismatch: gold={len(gold_rows)} pred={len(pred_rows)}"


def evaluate(questions: list[dict], db_path: Path, predictions: dict[str, str | None], ordered: bool = False):
    db_key = str(Path(db_path).resolve())
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")
    per_q = []
    errors: Counter = Counter()

    for q in questions:
        qid = q["question_id"]
        pred = predictions.get(qid)
        strict_ok, relaxed_ok, exec_ok, detail = score_one(conn, db_key, q["sql"], pred, ordered=ordered)
        if not exec_ok and detail.startswith("prediction error"):
            errors[detail.split(":")[0]] += 1
        per_q.append(
            dict(
                question_id=qid,
                difficulty=q["difficulty"],
                num_tables=q["num_tables"],
                features=q["features"],
                split=q.get("split"),
                correct=strict_ok,
                correct_relaxed=relaxed_ok,
                executable=exec_ok,
                detail=detail,
            )
        )
    conn.close()

    n = len(per_q)
    strict_total = sum(r["correct"] for r in per_q)
    relaxed_total = sum(r["correct_relaxed"] for r in per_q)
    exec_total = sum(r["executable"] for r in per_q)

    report = {
        "num_questions": n,
        "correct": strict_total,
        "correct_relaxed": relaxed_total,
        "execution_accuracy": round(strict_total / n, 6) if n else 0.0,
        "execution_accuracy_relaxed": round(relaxed_total / n, 6) if n else 0.0,
        "executable_rate": round(exec_total / n, 6) if n else 0.0,
        "by_difficulty": _group(per_q, "difficulty", "correct"),
        "by_difficulty_relaxed": _group(per_q, "difficulty", "correct_relaxed"),
        "by_num_tables": _group(per_q, "num_tables", "correct"),
        "by_split": _group(per_q, "split", "correct"),
        "by_split_relaxed": _group(per_q, "split", "correct_relaxed"),
        "by_feature": _by_feature(per_q),
        "execution_errors": dict(errors),
    }
    return report, per_q


def _group(per_q: list[dict], key: str, metric_key: str = "correct") -> dict:
    buckets = defaultdict(lambda: [0, 0])
    for r in per_q:
        b = buckets[r[key]]
        b[0] += 1
        b[1] += bool(r[metric_key])
    return {
        str(k): {"n": v[0], "correct": v[1], "accuracy": round(v[1] / v[0], 6) if v[0] else 0.0}
        for k, v in sorted(buckets.items(), key=lambda x: str(x[0]))
    }


def _by_feature(per_q: list[dict]) -> dict:
    buckets = defaultdict(lambda: [0, 0])
    for r in per_q:
        for f in r["features"]:
            buckets[f][0] += 1
            buckets[f][1] += bool(r["correct"])
    return {
        k: {"n": v[0], "correct": v[1], "accuracy": round(v[1] / v[0], 6) if v[0] else 0.0}
        for k, v in sorted(buckets.items(), key=lambda x: -x[1][0])
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Evaluate SQL predictions on BankRegBench.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    ap.add_argument("--predictions", type=Path, help="JSONL file with question_id and predicted_sql")
    ap.add_argument("--split", nargs="+", choices=["train", "dev", "test"], default=None, help="Filter question splits")
    ap.add_argument("--oracle", action="store_true", help="Self-test: score gold SQL against itself (expect 100%%)")
    ap.add_argument("--empty", action="store_true", help="Lower-bound baseline that always returns 0 rows")
    ap.add_argument("--ordered", action="store_true", help="Require exact row ordering in EX-Strict")
    ap.add_argument("--out", type=Path, help="Optional JSON output path")
    args = ap.parse_args()

    questions = [json.loads(l) for l in args.questions.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.split:
        allowed = set(args.split)
        questions = [q for q in questions if q.get("split") in allowed]

    if args.oracle:
        preds = {q["question_id"]: q["sql"] for q in questions}
        label = "oracle (gold SQL)"
    elif args.empty:
        preds = {q["question_id"]: "SELECT 1 WHERE 0" for q in questions}
        label = "empty-result baseline"
    elif args.predictions:
        preds = {}
        for line in args.predictions.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            preds[d["question_id"]] = d.get("predicted_sql")
        label = args.predictions.name
    else:
        ap.error("one of --oracle / --empty / --predictions is required")

    report, _ = evaluate(questions, args.db, preds, ordered=args.ordered)
    report["system"] = label
    report["ordered_rows"] = args.ordered

    print(f"system: {label}")
    print(
        f"questions: {report['num_questions']}   "
        f"EX-Strict: {report['execution_accuracy']*100:.2f}% ({report['correct']}/{report['num_questions']})   "
        f"EX-Relaxed: {report['execution_accuracy_relaxed']*100:.2f}% ({report['correct_relaxed']}/{report['num_questions']})   "
        f"Executable: {report['executable_rate']*100:.2f}%"
    )
    print("\nby difficulty (Strict / Relaxed):")
    for k, v in report["by_difficulty"].items():
        vr = report["by_difficulty_relaxed"][k]
        print(f"  {k:8s} n={v['n']:3d}  Strict={v['accuracy']*100:6.2f}%  Relaxed={vr['accuracy']*100:6.2f}%")
    print("\nby split (Strict / Relaxed):")
    for k, v in report["by_split"].items():
        vr = report["by_split_relaxed"][k]
        print(f"  {k:8s} n={v['n']:3d}  Strict={v['accuracy']*100:6.2f}%  Relaxed={vr['accuracy']*100:6.2f}%")
    if report["execution_errors"]:
        print("\nexecution errors:", report["execution_errors"])
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nreport written to {args.out}")
    return 0 if (not args.oracle or report["correct"] == report["num_questions"]) else 1


if __name__ == "__main__":
    sys.exit(main())
