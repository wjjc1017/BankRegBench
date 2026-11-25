#!/usr/bin/env bash
# Example runner for evaluating a custom model via any OpenAI-Compatible API.
#
# Usage:
#   export OPENAI_BASE_URL="https://api.openai.com/v1"
#   export OPENAI_API_KEY="sk-..."
#   export OPENAI_MODEL="gpt-4o"
#   bash scripts/run_eval.sh standard direct_ddl gpt-4o zh
#   bash scripts/run_eval.sh standard m_schema gpt-4o en
#
# Or configure multiple models in `configs/models.json` (copied from `configs/models.example.json`).
set -euo pipefail
cd "$(dirname "$0")/.."

TRACK="${1:-standard}"
FRAMEWORK="${2:-direct_ddl}"
MODEL="${3:-${OPENAI_MODEL:-custom-model}}"
LANG_MODE="${4:-zh}"
WORKERS="${WORKERS:-8}"

if [[ "$TRACK" == "standard" ]]; then
  python3 eval/run_standard_eval.py \
    --frameworks "$FRAMEWORK" \
    --models "$MODEL" \
    --lang "$LANG_MODE" \
    --workers "$WORKERS"
elif [[ "$TRACK" == "ablation" ]]; then
  python3 eval/run_oracle_ablation.py \
    --frameworks "$FRAMEWORK" \
    --models "$MODEL" \
    --lang "$LANG_MODE" \
    --eval-only-heldout \
    --workers "$WORKERS"
else
  echo "Unknown track: $TRACK (expected 'standard' or 'ablation')" >&2
  exit 1
fi
