#!/usr/bin/env python3
"""Build the BankRegBench-v2 dataset artefacts from `src/questions.py`.

For every authored item it

1. executes the gold SQL against ``data/bankreg.sqlite`` and refuses to ship an
   item that errors;
2. re-executes it to prove the result is deterministic;
3. records the result set, the tables referenced, and the SQL feature tags;
4. assigns a stratified train/dev/test split;
5. writes ``data/questions.jsonl`` (the dataset), ``data/schema.json`` (machine
   readable schema + value domains, for models and for the dataset card) and
   ``data/dataset_stats.json``.

The result set is materialised *after* the question and SQL are frozen, so the
gold answer is a consequence of the authored query rather than a value the query
was fitted to.

Usage: python3 src/build_dataset.py [--db data/bankreg.sqlite] [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from questions import ITEMS  # noqa: E402

DB_ID = "bankreg_main"
SPLITS = {"train": 0.6, "dev": 0.2, "test": 0.2}


def tables_of(sql: str) -> list[str]:
    ctes = {m.group(1).lower() for m in re.finditer(r"(?:WITH|,)\s*(\w+)\s+AS\s*\(", sql, re.I)}
    out = []
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+([A-Za-z_]\w*)", sql, re.I):
        t = m.group(1)
        if t.lower() in ctes:
            continue
        if t not in out:
            out.append(t)
    return out


def run(conn: sqlite3.Connection, sql: str):
    cur = conn.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = [[("" if v is None else v) for v in r] for r in cur.fetchall()]
    return cols, rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=ROOT / "data" / "bankreg.sqlite")
    ap.add_argument("--check", action="store_true", help="report problems, write nothing")
    args = ap.parse_args()

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    conn.execute("PRAGMA foreign_keys = ON")

    problems, records = [], []
    feature_counter, difficulty_counter, table_counter = Counter(), Counter(), Counter()
    ids = set()
    for it in ITEMS:
        qid = it["id"]
        if qid in ids:
            problems.append((qid, "duplicate id"))
        ids.add(qid)
        for field in ("question", "sql", "difficulty", "features"):
            if not it.get(field):
                problems.append((qid, f"missing {field}"))
        try:
            cols, rows = run(conn, it["sql"])
        except Exception as exc:  # noqa: BLE001
            problems.append((qid, f"SQL error: {exc}"))
            continue
        cols2, rows2 = run(conn, it["sql"])
        if (cols, rows) != (cols2, rows2):
            problems.append((qid, "non-deterministic result between two runs"))
        if not rows:
            problems.append((qid, "gold result is empty"))
        tabs = tables_of(it["sql"])
        difficulty_counter[it["difficulty"]] += 1
        for f in it["features"]:
            feature_counter[f] += 1
        for t in tabs:
            table_counter[t] += 1
        records.append(dict(
            question_id=qid, db_id=DB_ID, question=it["question"],
            question_en=it.get("question_en", ""),
            sql=it["sql"].strip(),
            difficulty=it["difficulty"], features=sorted(it["features"]),
            tables=tabs, num_tables=len(tabs),
            answer_columns=cols, num_answer_rows=len(rows), answer=rows,
            sql_sha256=hashlib.sha256(it["sql"].strip().encode()).hexdigest(),
            penalty_law_zh=it.get("penalty_law_zh", ""),
            penalty_fact_zh=it.get("penalty_fact_zh", ""),
        ))

    if args.check:
        print(f"items: {len(records)}/{len(ITEMS)}  problems: {len(problems)}")
        for qid, msg in problems:
            print(f"  {qid}: {msg}")
        return

    # stratified split, deterministic (preserving exact v2.0 split on BRB2-0001..0150,
    # BRB2-0151..0300, and stratifying BRB2-0301..0500 identically)
    assign = {}
    for batch_filter in (
        lambda qid: qid <= "BRB2-0150",
        lambda qid: "BRB2-0150" < qid <= "BRB2-0300",
        lambda qid: qid > "BRB2-0300",
    ):
        rng = random.Random(20260630)
        by_diff = defaultdict(list)
        for r in records:
            if batch_filter(r["question_id"]):
                by_diff[r["difficulty"]].append(r["question_id"])
        for diff, qids in by_diff.items():
            qids = sorted(qids)
            rng.shuffle(qids)
            n = len(qids)
            n_train = int(round(n * SPLITS["train"]))
            n_dev = int(round(n * SPLITS["dev"]))
            for i, qid in enumerate(qids):
                assign[qid] = "train" if i < n_train else ("dev" if i < n_train + n_dev else "test")

    for r in records:
        r["split"] = assign[r["question_id"]]
    records.sort(key=lambda r: r["question_id"])

    (ROOT / "data").mkdir(exist_ok=True)
    with (ROOT / "data" / "questions.jsonl").open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # machine-readable schema + value domains
    schema = {"db_id": DB_ID, "tables": {}}
    for (name,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"):
        cols = []
        for cid, cname, ctype, notnull, dflt, pk in conn.execute(f'PRAGMA table_info("{name}")'):
            cols.append({"name": cname, "type": ctype, "not_null": bool(notnull),
                         "pk": bool(pk)})
        fks = [{"column": r[3], "ref_table": r[2], "ref_column": r[4]}
               for r in conn.execute(f'PRAGMA foreign_key_list("{name}")')]
        n = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        entry = {"columns": cols, "foreign_keys": fks, "row_count": n}
        if n and n <= 120:                       # small tables: publish the domain
            entry["values"] = [
                list(r) for r in conn.execute(f'SELECT * FROM "{name}" LIMIT 120').fetchall()]
        schema["tables"][name] = entry
    (ROOT / "data" / "schema.json").write_text(
        json.dumps(schema, ensure_ascii=False, indent=1), encoding="utf-8")

    stats = {
        "db_id": DB_ID,
        "num_questions": len(records),
        "num_tables_in_schema": len(schema["tables"]),
        "num_tables_referenced": len(table_counter),
        "populated_tables": sum(1 for t in schema["tables"].values() if t["row_count"]),
        "total_rows": sum(t["row_count"] for t in schema["tables"].values()),
        "questions_by_difficulty": dict(sorted(difficulty_counter.items())),
        "questions_by_split": dict(sorted(Counter(r["split"] for r in records).items())),
        "questions_by_num_tables": dict(sorted(Counter(r["num_tables"] for r in records).items())),
        "feature_frequency": dict(sorted(feature_counter.items(), key=lambda x: -x[1])),
        "distinct_sql_skeletons": len({_skeleton(r["sql"]) for r in records}),
        "most_referenced_tables": table_counter.most_common(15),
        "avg_question_chars": round(sum(len(r["question"]) for r in records) / len(records), 1),
        "avg_answer_rows": round(sum(r["num_answer_rows"] for r in records) / len(records), 2),
        "problems": problems,
    }
    (ROOT / "data" / "dataset_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1))


def _skeleton(sql: str) -> str:
    s = re.sub(r"'[^']*'", "'?'", sql)
    s = re.sub(r"\b\d+(\.\d+)?\b", "?", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


if __name__ == "__main__":
    main()
