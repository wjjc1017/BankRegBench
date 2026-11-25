# Third-Party Notices & Baseline Attributions

BankRegBench integrates or adapts evaluation protocols from the following open-source Text-to-SQL projects. We gratefully acknowledge their authors and communities.

## 1. Vendored Helper Code (`third_party/m_schema/`)

- **M-Schema (XiYan-SQL)** — Alibaba DAMO Academy / XGenerationLab
  - Upstream Repository: https://github.com/XGenerationLab/M-Schema
  - License: Apache License 2.0 (see `third_party/m_schema/LICENSE`)
  - Included files: `m_schema.py`, `schema_engine.py`, `utils.py` (minimal SQLAlchemy schema representation helper, ~28 KB).

## 2. Optional PyPI Dependency

- **SchemaGate** — Identity-scoped schema selection for Text-to-SQL
  - Package: `schemagate` (`pip install schemagate`)
  - License: Apache License 2.0

## 3. Referenced Open-Source NL2SQL Baseline Paradigms

The following frameworks' prompting / retrieval / self-correction / execution-aggregation paradigms are faithfully adapted inside `eval/run_standard_eval.py` and `eval/run_oracle_ablation.py` without redistributing their full upstream repositories:

1. **DAIL-SQL** (PVLDB 2024): https://github.com/BeachWang/DAIL-SQL
2. **CHESS** (ACL 2024 Findings): https://github.com/ShayanTalaei/CHESS
3. **RSL-SQL** (2024): https://github.com/LaurieJoel/RSL-SQL
4. **DeepEye-SQL** (2025): https://github.com/HKUSTDial/DeepEye-SQL
5. **AxisSQL** (2025): Multi-generator execution-grounded aggregation paradigm
