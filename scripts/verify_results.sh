#!/usr/bin/env bash
# Zero-cost offline verification of all 56 benchmark prediction files (28 Standard L0 + 28 Oracle Ablation L2).
# Requires ONLY Python >= 3.10 standard library and zero API keys.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/4] Verifying 28 Standard 84-Table (Track L0) prediction files..."
python3 eval/run_standard_eval.py \
  --eval-only \
  --preds-dir results/predictions_standard \
  --out-json results/leaderboard_standard.json \
  --out-md results/leaderboard_standard.md

echo "[2/4] Verifying 28 Oracle Dictionary Ablation (Track L2) prediction files..."
python3 eval/run_oracle_ablation.py \
  --eval-only \
  --eval-only-heldout \
  --preds-dir results/predictions_oracle_ablation \
  --out-json results/ablation_oracle_dict.json \
  --out-md results/ablation_oracle_dict.md

echo "[3/4] Running 7-category error taxonomy analysis on Standard Track L0..."
python3 eval/analyze_error_taxonomy.py \
  --preds-dir results/predictions_standard \
  --out-summary results/error_taxonomy_summary.json

echo "[4/4] Rebuilding ablation and error taxonomy Markdown reports..."
python3 eval/build_reports.py --results-dir results

echo "OK: All 56 prediction files, leaderboards, ablation tables, and 3,144 error taxonomy instances verified."
