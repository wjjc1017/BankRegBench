# BankRegBench · Standard 84-Table Evaluation vs. Oracle Dictionary Ablation

Summary of **BankRegBench** (500 questions; Train 300 / Dev 98 / Test 102) comparing **Standard 84-Table Zero-Prior Evaluation (Track L0)** and **Oracle Dictionary Ablation (Track L2)** across 28 configurations (7 frameworks × 4 backbone LLMs) on the held-out split (`Dev+Test N=200`).

---

## 1. Protocol Comparison

| Evaluation Track | Schema & Prior Configuration | Held-Out EX Range | Key Takeaway |
| :--- | :--- | :---: | :--- |
| **Standard 84-Table Evaluation**<br>*(Track L0)* | Raw 84-table SQLite DDL (incl. 20 empty distractors) + **zero bilingual dictionary, zero catalog dumps, zero FK hints** | Strict **23.00% – 77.50%**<br>(Relaxed **24.00% – 84.50%**) | **Primary Protocol**: 25/28 configs score below 60% Strict EX; best is `deepeye_axissql` × `DeepSeek-V4.1-Flash` (Strict 77.50% / Relaxed 84.50%). |
| **Oracle Dictionary Ablation**<br>*(Track L2)* | Pre-filtered 64 populated tables + full bilingual dictionary + catalog value domains + **explicit multi-hop FK & rounding rules** | **47.00% – 89.50%** | **Diagnostic Upper Bound**: Injecting domain hints lifts framework mean EX by **+8.38% to +33.00%**; best is `deepeye_axissql` × `DeepSeek-V4.1-Flash` (89.50%). |

---

## 2. Framework-Level Ablation Mean Across 4 Backbones (`Dev+Test N=200`)

| Framework | Standard Strict EX (%) | Standard Relaxed EX (%) | +Oracle Dict EX (%) | Δ Gain (vs. Strict) | +Oracle Dict Extra EX (%) |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `schemagate` | 26.12% | 28.00% | 59.12% | **+33.00%** | 45.20% |
| `direct_ddl` | 33.00% | 36.00% | 62.75% | **+29.75%** | 49.04% |
| `rsl_sql` | 37.38% | 40.38% | 68.12% | **+30.75%** | 57.69% |
| `dail_sql` | 43.50% | 46.88% | 65.00% | **+21.50%** | 47.11% |
| `chess` | 52.12% | 57.12% | 64.38% | **+12.25%** | 57.69% |
| `m_schema` | 53.50% | 58.12% | 61.88% | **+8.38%** | 50.96% |
| `deepeye_axissql` | 61.38% | 67.12% | 76.12% | **+14.75%** | 67.31% |

---

## 3. Evaluation Notes

1. Stratified fixed split across 500 distinct SQL skeletons: Train 300 / Dev 98 / Test 102. Few-shot pools use Train only.
2. Held-out difficulty breakdown (`N=200`): Easy 24 / Medium 69 / Hard 81 / Extra 26.
3. `EX-Strict` uses 6-decimal multiset matching; `EX-Relaxed` applies bucketed 2/4-decimal float tolerance without relaxing joins, filters, or row counts.
