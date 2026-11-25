# Dataset Card for BankRegBench

## 1. Dataset Summary

**BankRegBench** is a clean-room Text-to-SQL benchmark modeling enterprise commercial banking regulatory compliance and off-site supervision over a strictly normalized relational warehouse (**BankRegSQL v4**).

| Property | Value |
| :--- | :--- |
| **Database Engine** | SQLite 3 (`STRICT` tables, `PRAGMA foreign_keys = ON`) |
| **Total Schema Tables** | 84 tables (`54` populated business/event tables + `10` controlled vocabulary tables + `20` empty same-domain distractor tables) |
| **Populated Table Coverage** | 64 / 64 (100.0% referenced by the question set) |
| **Total Warehouse Rows** | 74,184 deterministic synthetic rows (`SEED = 20260630`, `0` FK violations) |
| **Audit Snapshot Date** | `2026-06-30` |
| **Total Questions** | 500 hand-authored bilingual (ZH + parallel EN) regulatory questions (`BRB2-0001` – `BRB2-0500`) |
| **Distinct SQL Skeletons** | 500 / 500 (100.0% mutually distinct after literal masking) |
| **Splits (Stratified)** | `Train`: 300 (60.0%) · `Dev`: 98 (19.6%) · `Test`: 102 (20.4%) |
| **Difficulty Tiers** | `Easy`: 60 (12.0%) · `Medium`: 172 (34.4%) · `Hard`: 204 (40.8%) · `Extra`: 64 (12.8%) |
| **Joined Tables per Query** | 1 table (65), 2 (150), 3 (114), 4 (88), 5 (40), 6 (32), 7 (9), 8 (2) |
| **License** | Apache-2.0 |

---

## 2. Data Fields (`data/questions.jsonl`)

Each line in `data/questions.jsonl` is a JSON object with:

- `question_id` (`str`): Unique identifier (`BRB2-0001` to `BRB2-0500`).
- `db_id` (`str`): Database identifier (`bankreg_main`).
- `question` (`str`): Natural-language Chinese banking compliance question with zero physical table/column/code leakage.
- `question_en` (`str`): Parallel zero-leakage English translation preserving all business constraints, units, column ordering, and any database-native Chinese entity literals where required.
- `sql` (`str`): Verified Oracle Gold SQLite query.
- `difficulty` (`str`): One of `easy`, `medium`, `hard`, `extra`.
- `features` (`list[str]`): AST-verified SQL operator tags (e.g., `JOIN`, `GROUP_BY`, `HAVING`, `CTE`, `WINDOW`, `RATIO`, `SELF_JOIN`).
- `tables` (`list[str]`): Physical tables referenced by the gold SQL.
- `num_tables` (`int`): Number of referenced physical tables (`1`–`8`).
- `answer_columns` (`list[str]`): Output column names of the gold query.
- `num_answer_rows` (`int`): Number of rows returned by the gold query (`>= 1`).
- `answer` (`list[list]`): Frozen deterministic gold result rows (`NULL` serialized as `""`).
- `sql_sha256` (`str`): SHA-256 hash of the gold SQL.
- `split` (`str`): One of `train`, `dev`, `test`.
- `penalty_law_zh` / `penalty_fact_zh` (`str`): Statutory grounding metadata for regulatory penalty compliance items (`BRB2-0151`–`BRB2-0500`).

---

## 3. Quality Assurance & Validation Gates

Every released item passes **two independent programmatic verification suites**:

1. **Independent Validator (`src/validate_dataset.py`, 10 assertion groups)**:
   - Gold execution & non-empty result check
   - Two-run determinism check & exact match against frozen `answer`
   - Zero physical schema/column/code-literal leakage regex assertion
   - Unique non-empty output column names
   - Disjoint stratified `train`/`dev`/`test` splits
   - 100% distinct SQL skeletons (`500/500`)
   - SQLite `PRAGMA foreign_key_check` (`0` violations) and `PRAGMA integrity_check` (`ok`)

2. **Three-Way Consistency Quality Gate (`src/audit_dataset.py`)**:
   - **Predicate Ablation (Anti-Tautology)**: Removes each `WHERE` / conjunct / `HAVING` clause and verifies the query output strictly changes (`0%` tautological predicates).
   - **Chasm-Trap & Join-Path Guard**: Prevents Cartesian `ON 1=1` joins, bogus security-to-agreement shortcuts bypassing `secured_obligation`, and 1:N `SUM`/`COUNT` inflation.
   - **AST Feature Alignment & Semantic Audit**: `500/500` PASS (`0` programmatic warnings, `0` semantic flags; see `data/audit_summary.json`).

---

## 4. Ethical Considerations & Privacy

- All entities (institutions, branches, staff, corporate/retail parties, loan drawdowns, transactions, wealth products) are **100% synthetically generated** by `src/build_db.py` with fixed seed `20260630`.
- No real customer PII, no proprietary institutional data, and no confidential regulatory reporting templates are present.
