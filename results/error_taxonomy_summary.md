# BankRegBench · Track L0 Seven-Category Error Taxonomy Analysis

> **Scope**: Held-out `Dev+Test (N=200)` × 7 NL2SQL frameworks × 4 backbone LLMs = **5,600 independent SQL evaluations**.
> **Strict Failures**: **3,144** (56.14% of all evaluations; 2,456 strict passes). Excluding rounding-only `E7`, relaxed error rate is **52.30%**.
> **Reproducibility**: Regenerated offline via `python3 eval/analyze_error_taxonomy.py && python3 eval/build_reports.py`.

---

## 1. Global Distribution Across Error Categories

| Code | Category | Count | Share of Errors | Share of All Queries | Diagnostic Criterion |
| :---: | :--- | ---: | ---: | ---: | :--- |
| **E3** | **Vocabulary & Enum Hallucination** | **928** | 29.52% | 16.57% | Valid SQL returning 0 rows: fails to join controlled vocabulary tables (e.g., `status_catalog`, `payment_type_catalog`) and hardcodes Chinese text or hallucinated enum strings into code columns. |
| **E1** | **Syntax & Phantom-Column Error** | **596** | 18.96% | 10.64% | SQLite execution error: mainly hallucinating non-existent FK columns on 3NF tables (e.g., `loan_drawdown.institution_id`) or invalid window function nesting. |
| **E5-B** | **Predicate Drift & Join Polarity** | **568** | 18.07% | 10.14% | Core & bridge tables match, but row count differs due to missing/spurious filters or `INNER JOIN` vs `LEFT JOIN` polarity errors. |
| **E4** | **Bridge-Table & Core-Table Mismatch** | **524** | 16.67% | 9.36% | Executable & non-empty, but drops required bridge tables (`credit_agreement`, `secured_obligation`, `collateral_link`, `account_holder`) or selects an adjacent fact table. |
| **E7** | **Precision / Rounding Gap Only** | **215** | 6.84% | 3.84% | Joins, filters, grouping, and row counts are exact; differs only in decimal rounding (counted as correct under `EX-Relaxed`). |
| **E5-A** | **Ratio Formula & Chasm-Trap Fan-out** | **204** | 6.49% | 3.64% | Entity keys and row counts match, but aggregated metrics/ratios differ due to 1:N join fan-out duplication or incorrect window/numerator logic. |
| **E2** | **Distractor-Table Trap** | **80** | 2.54% | 1.43% | Selects one or more of the 20 empty same-domain distractor tables. |
| **E6** | **Projection Column Mismatch** | **29** | 0.92% | 0.52% | `SELECT` output column count or projection deviates from the question specification. |
| **Total** | **All Strict Errors** | **3144** | 100.00% | 56.14% | Overall Strict EX = 43.86% |

---

## 2. Error Breakdown by Framework (800 Queries / Framework)

| Framework | E1 | E2 | E3 | E4 | E5-A | E5-B | E6 | E7 | Total Errors | Strict EX | Relaxed EX |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `schemagate` *(Schema pruning (no CN hints))* | 150 | 17 | 234 | 76 | 26 | 66 | 7 | 15 | **591** | 26.12% | 28.00% |
| `direct_ddl` *(Raw 84-table DDL)* | 101 | 12 | 234 | 69 | 24 | 68 | 4 | 24 | **536** | 33.00% | 36.00% |
| `rsl_sql` *(Bidirectional linking + self-correction)* | 71 | 18 | 205 | 77 | 27 | 75 | 4 | 24 | **501** | 37.38% | 40.38% |
| `dail_sql` *(Disjoint cross-table few-shot)* | 81 | 7 | 145 | 69 | 35 | 86 | 2 | 27 | **452** | 43.50% | 46.88% |
| `m_schema` *(SQLAlchemy cell sampling)* | 104 | 5 | 26 | 82 | 25 | 90 | 2 | 38 | **372** | 53.50% | 58.12% |
| `chess` *(IR literal retrieval + UT repair)* | 59 | 14 | 74 | 70 | 32 | 87 | 7 | 40 | **383** | 52.12% | 57.12% |
| `deepeye_axissql` *(Multi-path + execution aggregation)* | 30 | 7 | 10 | 81 | 35 | 96 | 3 | 47 | **309** | 61.38% | 67.12% |

---

## 3. Error Breakdown by Backbone LLM (1400 Queries / Model)

| Backbone LLM | E1 | E2 | E3 | E4 | E5-A | E5-B | E6 | E7 | Total Errors | Strict EX | Relaxed EX |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `DeepSeek-V4.1-Flash` | 31 | 5 | 206 | 107 | 39 | 127 | 11 | 69 | **595** | 57.50% | 62.29% |
| `DeepSeek-V4-Flash` | 85 | 7 | 310 | 156 | 73 | 147 | 8 | 43 | **829** | 40.79% | 43.86% |
| `Qwen3.5-397B-A17B` | 322 | 14 | 168 | 120 | 45 | 141 | 4 | 50 | **864** | 38.29% | 41.86% |
| `Qwen3.6-35B-A3B` | 158 | 54 | 244 | 141 | 47 | 153 | 6 | 53 | **856** | 38.86% | 42.64% |

---

## 4. Error Breakdown by Question Difficulty

| Difficulty | Held-Out N | Evaluations (×28) | E1 | E2 | E3 | E4 | E5-A | E5-B | E6 | E7 | Strict Errors | Error Rate |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Easy** | 24 | 672 | 36 | 3 | 156 | 35 | 22 | 56 | 9 | 0 | **317** | 47.17% |
| **Medium** | 69 | 1932 | 217 | 16 | 293 | 179 | 59 | 203 | 15 | 19 | **1001** | 51.81% |
| **Hard** | 81 | 2268 | 238 | 57 | 372 | 187 | 90 | 246 | 1 | 153 | **1344** | 59.26% |
| **Extra** | 26 | 728 | 105 | 4 | 107 | 123 | 33 | 63 | 4 | 43 | **482** | 66.21% |
| **Total** | **200** | **5,600** | 596 | 80 | 928 | 524 | 204 | 568 | 29 | 215 | **3144** | **56.14%** |

---

## 5. Representative Real Error Cases

### Case 1: `E1: Syntax & Phantom-Column Error` (`BRB2-0001`)
- **Question**: *列出所有风险分类等级为“次级”的借据编号及其分类日期，按借据编号升序排列。*
- **Gold SQL**:
  ```sql
  SELECT rc.loan_id, rc.as_of_date
  FROM risk_classification rc
  JOIN classification_grade g ON g.grade_code = rc.grade_code
  WHERE g.grade_name_zh = '次级'
  ORDER BY rc.loan_id;
  ```
- **Predicted SQL (`direct_ddl` @ `DeepSeek-V4-Flash`)**:
  ```sql
  SELECT loan_id, classification_date
  FROM risk_classification
  WHERE grade_code = '次级'
  ORDER BY loan_id ASC;
  ```
- **Diagnostic Note**: no such column: classification_date

### Case 2: `E2: Distractor-Table Trap` (`BRB2-0007`)
- **Question**: *列出所有已核销的借据编号及其放款金额。*
- **Gold SQL**:
  ```sql
  SELECT ld.loan_id, ld.disbursed_amount
  FROM loan_drawdown ld
  JOIN status_catalog s ON s.entity = 'loan_drawdown' AND s.status_code = ld.status
  WHERE s.name_zh = '已核销'
  ORDER BY ld.loan_id;
  ```
- **Predicted SQL (`direct_ddl` @ `Qwen3.5-397B-A17B`)**:
  ```sql
  SELECT 
      ld.loan_id,
      ld.disbursed_amount
  FROM 
      loan_drawdown ld
  JOIN 
      asset_resolution_event are ON ld.loan_id = are.loan_id
  WHERE 
      are.event_type = 'WRITE_OFF'
      AND are.status = 'COMPLETED';
  ```
- **Diagnostic Note**: Selected empty distractor table(s): ['asset_resolution_event']

### Case 3: `E3: Vocabulary & Enum Hallucination` (`BRB2-0007`)
- **Question**: *列出所有已核销的借据编号及其放款金额。*
- **Gold SQL**:
  ```sql
  SELECT ld.loan_id, ld.disbursed_amount
  FROM loan_drawdown ld
  JOIN status_catalog s ON s.entity = 'loan_drawdown' AND s.status_code = ld.status
  WHERE s.name_zh = '已核销'
  ORDER BY ld.loan_id;
  ```
- **Predicted SQL (`direct_ddl` @ `DeepSeek-V4-Flash`)**:
  ```sql
  SELECT loan_id, disbursed_amount
  FROM loan_drawdown
  WHERE status = '已核销';
  ```
- **Diagnostic Note**: 0 rows & missed catalog table(s): ['status_catalog']

### Case 4: `E4: Bridge-Table & Core-Table Mismatch` (`BRB2-0454`)
- **Question**: *输出各银行机构的名称、净资本与总资产之比（保留六位小数），按该比值从高到低排列（机构财务数据存放在财务快照表中，其主体编号为 PTY- 加机构编号）。*
- **Gold SQL**:
  ```sql
  SELECT i.institution_name, ROUND(c.net_capital/f.total_assets,6) AS leverage_val FROM institution i JOIN capital_snapshot c ON c.institution_id=i.institution_id JOIN financial_snapshot f ON f.party_id='PTY-'||i.institution_id ORDER BY leverage_val DESC;
  ```
- **Predicted SQL (`direct_ddl` @ `Qwen3.5-397B-A17B`)**:
  ```sql
  SELECT 
      i.institution_name,
      ROUND(fs.net_assets * 1.0 / fs.total_assets, 6) AS capital_ratio
  FROM 
      institution i
  JOIN 
      financial_snapshot fs ON fs.party_id = 'PTY-' || i.institution_id
  ORDER BY 
      capital_ratio DESC;
  ```
- **Diagnostic Note**: Table mismatch: gold=['capital_snapshot', 'financial_snapshot', 'institution'] pred=['financial_snapshot', 'institution']

### Case 5: `E5-A: Ratio Formula & Chasm-Trap Fan-out` (`BRB2-0465`)
- **Question**: *输出各银行机构定期存款年化利率高于3%的存单数量，按数量从多到少排列。*
- **Gold SQL**:
  ```sql
  SELECT i.institution_name, COUNT(*) AS high_rate_cnt FROM term_deposit td JOIN account a ON a.account_id=td.account_id JOIN institution i ON i.institution_id=a.institution_id WHERE td.annual_interest_rate>3.0 GROUP BY i.institution_name ORDER BY high_rate_cnt DESC;
  ```
- **Predicted SQL (`direct_ddl` @ `Qwen3.5-397B-A17B`)**:
  ```sql
  SELECT i.institution_name, COUNT(td.account_id) AS deposit_count
  FROM institution i
  JOIN account a ON i.institution_id = a.institution_id
  JOIN term_deposit td ON a.account_id = td.account_id
  WHERE td.annual_interest_rate > 0.03
  GROUP BY i.institution_id, i.institution_name
  ORDER BY deposit_count DESC;
  ```
- **Diagnostic Note**: Same entity keys & row count, but aggregated/calculated metric differs

