#!/usr/bin/env python3
"""Generate ablation_summary.md and error_taxonomy_summary.md from JSON reports in results/."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_DIR = ROOT / "results"

FWS = ["schemagate", "direct_ddl", "rsl_sql", "dail_sql", "m_schema", "chess", "deepeye_axissql"]
MODELS = [
    "deepseek-v4.1-flash",
    "deepseek-v4-flash",
    "qwen3.5-397b-a17b",
    "qwen3.6-35b-a3b",
]
MODEL_NAME = {
    "deepseek-v4.1-flash": "DeepSeek-V4.1-Flash",
    "deepseek-v4-flash": "DeepSeek-V4-Flash",
    "qwen3.5-397b-a17b": "Qwen3.5-397B-A17B",
    "qwen3.6-35b-a3b": "Qwen3.6-35B-A3B",
}
FW_NOTE = {
    "schemagate": "Schema pruning (no CN hints)",
    "direct_ddl": "Raw 84-table DDL",
    "rsl_sql": "Bidirectional linking + self-correction",
    "dail_sql": "Disjoint cross-table few-shot",
    "m_schema": "SQLAlchemy cell sampling",
    "chess": "IR literal retrieval + UT repair",
    "deepeye_axissql": "Multi-path + execution aggregation",
}
CATS = [
    (
        "E3_VOCAB_ENUM_HALLUCINATION",
        "E3",
        "Vocabulary & Enum Hallucination",
        "Valid SQL returning 0 rows: fails to join controlled vocabulary tables (e.g., `status_catalog`, `payment_type_catalog`) and hardcodes Chinese text or hallucinated enum strings into code columns.",
    ),
    (
        "E1_SYNTAX_EXEC_ERROR",
        "E1",
        "Syntax & Phantom-Column Error",
        "SQLite execution error: mainly hallucinating non-existent FK columns on 3NF tables (e.g., `loan_drawdown.institution_id`) or invalid window function nesting.",
    ),
    (
        "E5B_PREDICATE_OR_JOIN_DRIFT",
        "E5-B",
        "Predicate Drift & Join Polarity",
        "Core & bridge tables match, but row count differs due to missing/spurious filters or `INNER JOIN` vs `LEFT JOIN` polarity errors.",
    ),
    (
        "E4_BRIDGE_JOIN_PATH_DROP",
        "E4",
        "Bridge-Table & Core-Table Mismatch",
        "Executable & non-empty, but drops required bridge tables (`credit_agreement`, `secured_obligation`, `collateral_link`, `account_holder`) or selects an adjacent fact table.",
    ),
    (
        "E7_PRECISION_ROUNDING_ONLY",
        "E7",
        "Precision / Rounding Gap Only",
        "Joins, filters, grouping, and row counts are exact; differs only in decimal rounding (counted as correct under `EX-Relaxed`).",
    ),
    (
        "E5A_AGGREGATION_RATIO_WINDOW",
        "E5-A",
        "Ratio Formula & Chasm-Trap Fan-out",
        "Entity keys and row counts match, but aggregated metrics/ratios differ due to 1:N join fan-out duplication or incorrect window/numerator logic.",
    ),
    (
        "E2_DISTRACTOR_TABLE_TRAP",
        "E2",
        "Distractor-Table Trap",
        "Selects one or more of the 20 empty same-domain distractor tables.",
    ),
    (
        "E6_PROJECTION_COLUMN_MISMATCH",
        "E6",
        "Projection Column Mismatch",
        "`SELECT` output column count or projection deviates from the question specification.",
    ),
]
CAT_COLS = [
    "E1_SYNTAX_EXEC_ERROR",
    "E2_DISTRACTOR_TABLE_TRAP",
    "E3_VOCAB_ENUM_HALLUCINATION",
    "E4_BRIDGE_JOIN_PATH_DROP",
    "E5A_AGGREGATION_RATIO_WINDOW",
    "E5B_PREDICATE_OR_JOIN_DRIFT",
    "E6_PROJECTION_COLUMN_MISMATCH",
    "E7_PRECISION_ROUNDING_ONLY",
]
DIFFS = ["easy", "medium", "hard", "extra"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Build summary Markdown reports from results JSON files.")
    ap.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    args = ap.parse_args()
    out_dir: Path = args.results_dir

    l0 = [
        r
        for r in json.loads((out_dir / "leaderboard_standard.json").read_text(encoding="utf-8"))
        if r["framework"] in FWS and r["model"] in MODELS
    ]
    l2 = [
        r
        for r in json.loads((out_dir / "ablation_oracle_dict.json").read_text(encoding="utf-8"))
        if r["framework"] in FWS and r["model"] in MODELS
    ]
    tax = json.loads((out_dir / "error_taxonomy_summary.json").read_text(encoding="utf-8"))
    qs = [json.loads(l) for l in (ROOT / "data" / "questions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    held = [q for q in qs if q["split"] in ("dev", "test")]
    n = len(held)
    nconf = len(l0)
    diff_n = {d: sum(1 for q in held if q["difficulty"] == d) for d in DIFFS}
    split_n = {s: sum(1 for q in held if q["split"] == s) for s in ("dev", "test")}

    l0k = {(r["framework"], r["model"]): r for r in l0}
    l2k = {(r["framework"], r["model"]): r for r in l2}
    strict = [r["ex_strict_6dec"] for r in l0]
    relax = [r["ex_tolerant_2dec"] for r in l0]
    l2v = [r["ex_heldout_dev_test"] for r in l2]
    below60 = sum(1 for v in strict if v < 60)

    fw_rows = []
    for fw in FWS:
        s = mean(l0k[(fw, m)]["ex_strict_6dec"] for m in MODELS)
        t = mean(l0k[(fw, m)]["ex_tolerant_2dec"] for m in MODELS)
        o = mean(l2k[(fw, m)]["ex_heldout_dev_test"] for m in MODELS)
        ex = mean(l2k[(fw, m)]["by_difficulty"].get("extra", 0) for m in MODELS)
        fw_rows.append((fw, s, t, o, o - s, ex))
    fw_rows.sort(key=lambda r: r[1])
    gains = [r[4] for r in fw_rows]

    # ---------------- ablation_summary.md ----------------
    best_l0 = max(l0, key=lambda r: r["ex_strict_6dec"])
    best_l2 = max(l2, key=lambda r: r["ex_heldout_dev_test"])
    a = [
        "# BankRegBench · Standard 84-Table Evaluation vs. Oracle Dictionary Ablation\n",
        f"Summary of **BankRegBench** (500 questions; Train 300 / Dev {split_n['dev']} / Test {split_n['test']}) comparing **Standard 84-Table Zero-Prior Evaluation (Track L0)** and **Oracle Dictionary Ablation (Track L2)** across {nconf} configurations (7 frameworks × 4 backbone LLMs) on the held-out split (`Dev+Test N={n}`).\n\n---\n",
        "## 1. Protocol Comparison\n",
        "| Evaluation Track | Schema & Prior Configuration | Held-Out EX Range | Key Takeaway |",
        "| :--- | :--- | :---: | :--- |",
        f"| **Standard 84-Table Evaluation**<br>*(Track L0)* | Raw 84-table SQLite DDL (incl. 20 empty distractors) + **zero bilingual dictionary, zero catalog dumps, zero FK hints** | Strict **{min(strict):.2f}% – {max(strict):.2f}%**<br>(Relaxed **{min(relax):.2f}% – {max(relax):.2f}%**) | **Primary Protocol**: {below60}/{nconf} configs score below 60% Strict EX; best is `{best_l0['framework']}` × `{MODEL_NAME[best_l0['model']]}` (Strict {best_l0['ex_strict_6dec']:.2f}% / Relaxed {best_l0['ex_tolerant_2dec']:.2f}%). |",
        f"| **Oracle Dictionary Ablation**<br>*(Track L2)* | Pre-filtered 64 populated tables + full bilingual dictionary + catalog value domains + **explicit multi-hop FK & rounding rules** | **{min(l2v):.2f}% – {max(l2v):.2f}%** | **Diagnostic Upper Bound**: Injecting domain hints lifts framework mean EX by **{min(gains):+.2f}% to {max(gains):+.2f}%**; best is `{best_l2['framework']}` × `{MODEL_NAME[best_l2['model']]}` ({best_l2['ex_heldout_dev_test']:.2f}%). |\n\n---\n",
        f"## 2. Framework-Level Ablation Mean Across 4 Backbones (`Dev+Test N={n}`)\n",
        "| Framework | Standard Strict EX (%) | Standard Relaxed EX (%) | +Oracle Dict EX (%) | Δ Gain (vs. Strict) | +Oracle Dict Extra EX (%) |",
        "| :--- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for fw, s, t, o, d, ex in fw_rows:
        a.append(f"| `{fw}` | {s:.2f}% | {t:.2f}% | {o:.2f}% | **{d:+.2f}%** | {ex:.2f}% |")
    a.append("\n---\n")
    a.append("## 3. Evaluation Notes\n")
    a.append(
        f"1. Stratified fixed split across 500 distinct SQL skeletons: Train 300 / Dev {split_n['dev']} / Test {split_n['test']}. Few-shot pools use Train only."
    )
    a.append(
        f"2. Held-out difficulty breakdown (`N={n}`): Easy {diff_n['easy']} / Medium {diff_n['medium']} / Hard {diff_n['hard']} / Extra {diff_n['extra']}."
    )
    a.append(
        "3. `EX-Strict` uses 6-decimal multiset matching; `EX-Relaxed` applies bucketed 2/4-decimal float tolerance without relaxing joins, filters, or row counts."
    )
    (out_dir / "ablation_summary.md").write_text("\n".join(a) + "\n", encoding="utf-8")

    # ---------------- error_taxonomy_summary.md ----------------
    tot, err = tax["total_evaluations"], tax["total_strict_errors"]
    oc = tax["overall_by_category"]
    e7 = oc.get("E7_PRECISION_ROUNDING_ONLY", 0)
    t = [
        "# BankRegBench · Track L0 Seven-Category Error Taxonomy Analysis\n",
        f"> **Scope**: Held-out `Dev+Test (N={n})` × 7 NL2SQL frameworks × 4 backbone LLMs = **{tot:,} independent SQL evaluations**.\n"
        f"> **Strict Failures**: **{err:,}** ({tax['overall_error_rate_pct']:.2f}% of all evaluations; {tot - err:,} strict passes). Excluding rounding-only `E7`, relaxed error rate is **{(err - e7) / tot * 100:.2f}%**.\n"
        "> **Reproducibility**: Regenerated offline via `python3 eval/analyze_error_taxonomy.py && python3 eval/build_reports.py`.\n\n---\n",
        "## 1. Global Distribution Across Error Categories\n",
        "| Code | Category | Count | Share of Errors | Share of All Queries | Diagnostic Criterion |",
        "| :---: | :--- | ---: | ---: | ---: | :--- |",
    ]
    for key, code, en, desc in CATS:
        c = oc.get(key, 0)
        t.append(f"| **{code}** | **{en}** | **{c}** | {c / err * 100:.2f}% | {c / tot * 100:.2f}% | {desc} |")
    t.append(f"| **Total** | **All Strict Errors** | **{err}** | 100.00% | {err / tot * 100:.2f}% | Overall Strict EX = {(tot - err) / tot * 100:.2f}% |\n\n---\n")

    per_fw = n * len(MODELS)
    t.append(f"## 2. Error Breakdown by Framework ({per_fw} Queries / Framework)\n")
    t.append("| Framework | E1 | E2 | E3 | E4 | E5-A | E5-B | E6 | E7 | Total Errors | Strict EX | Relaxed EX |")
    t.append("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    bf = tax["by_framework"]
    for fw in FWS:
        row = bf[fw]
        vals = [row.get(k, 0) for k in CAT_COLS]
        s = mean(l0k[(fw, m)]["ex_strict_6dec"] for m in MODELS)
        r = mean(l0k[(fw, m)]["ex_tolerant_2dec"] for m in MODELS)
        t.append(f"| `{fw}` *({FW_NOTE[fw]})* | " + " | ".join(str(v) for v in vals) + f" | **{sum(vals)}** | {s:.2f}% | {r:.2f}% |")

    t.append(f"\n---\n\n## 3. Error Breakdown by Backbone LLM ({len(FWS) * n} Queries / Model)\n")
    t.append("| Backbone LLM | E1 | E2 | E3 | E4 | E5-A | E5-B | E6 | E7 | Total Errors | Strict EX | Relaxed EX |")
    t.append("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    bm = tax["by_model"]
    for m in MODELS:
        row = bm[m]
        vals = [row.get(k, 0) for k in CAT_COLS]
        s = mean(l0k[(f, m)]["ex_strict_6dec"] for f in FWS)
        r = mean(l0k[(f, m)]["ex_tolerant_2dec"] for f in FWS)
        t.append(f"| `{MODEL_NAME[m]}` | " + " | ".join(str(v) for v in vals) + f" | **{sum(vals)}** | {s:.2f}% | {r:.2f}% |")

    t.append("\n---\n\n## 4. Error Breakdown by Question Difficulty\n")
    t.append(f"| Difficulty | Held-Out N | Evaluations (×{nconf}) | E1 | E2 | E3 | E4 | E5-A | E5-B | E6 | E7 | Strict Errors | Error Rate |")
    t.append("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    bd = tax["by_difficulty"]
    for d in DIFFS:
        row = bd.get(d, {})
        vals = [row.get(k, 0) for k in CAT_COLS]
        ev = diff_n[d] * nconf
        t.append(f"| **{d.capitalize()}** | {diff_n[d]} | {ev} | " + " | ".join(str(v) for v in vals) + f" | **{sum(vals)}** | {sum(vals) / ev * 100:.2f}% |")
    t.append(
        f"| **Total** | **{n}** | **{tot:,}** | "
        + " | ".join(str(oc.get(k, 0)) for k in CAT_COLS)
        + f" | **{err}** | **{err / tot * 100:.2f}%** |\n\n---\n"
    )

    t.append("## 5. Representative Real Error Cases\n")
    for i, r in enumerate(tax.get("representative_examples", []), 1):
        t.append(f"### Case {i}: `{r.get('case_title', r['category'])}` (`{r['question_id']}`)")
        t.append(f"- **Question**: *{r['question']}*")
        t.append("- **Gold SQL**:\n  ```sql\n  " + r["gold_sql"].replace("\n", "\n  ") + "\n  ```")
        t.append(
            f"- **Predicted SQL (`{r['framework']}` @ `{MODEL_NAME.get(r['model'], r['model'])}`)**:\n  ```sql\n  "
            + r["predicted_sql"].replace("\n", "\n  ")
            + "\n  ```"
        )
        t.append(f"- **Diagnostic Note**: {r['detail']}\n")

    (out_dir / "error_taxonomy_summary.md").write_text("\n".join(t) + "\n", encoding="utf-8")
    print(f"Built ablation_summary.md and error_taxonomy_summary.md ({err}/{tot} strict errors)")


if __name__ == "__main__":
    main()
