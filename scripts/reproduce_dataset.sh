#!/usr/bin/env bash
# End-to-end deterministic dataset reproduction and validation (Python stdlib only).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/6] Building 84-table STRICT 3NF warehouse (SEED=20260630)..."
python3 src/build_db.py

echo "[2/6] Executing 500 gold queries, freezing answers, and stratifying splits..."
python3 src/build_dataset.py

echo "[3/6] Exporting clean BIRD-compatible text format..."
python3 src/export_bird_format.py

echo "[4/6] Running independent 10-group dataset validation..."
python3 src/validate_dataset.py

echo "[5/6] Running programmatic 3-way consistency gate (predicate ablation + fan-out + leakage)..."
python3 src/audit_dataset.py --skip-llm

echo "[6/6] Running evaluator self-tests (Oracle=100%, Empty=0%)..."
python3 eval/evaluate.py --oracle
python3 eval/evaluate.py --empty

echo "OK: BankRegBench dataset reproduced and validated cleanly."
