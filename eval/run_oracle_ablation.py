#!/usr/bin/env python3
"""Oracle Dictionary Ablation Evaluation Harness (Track L2) for BankRegBench.

Protocol (Diagnostic Upper-Bound Ablation):
  1. Pre-filters to the 64 populated tables (excludes the 20 empty distractor tables).
  2. Injects bilingual table/column descriptions (`TABLE_DESC_ZH`) and full controlled
     vocabulary value domains (`CATALOG_TABLES`).
  3. Provides explicit multi-hop FK join rules, audit date `'2026-06-30'`, and rounding conventions.
  4. Strict anti-leakage safeguards:
     - Ground-truth fields (`sql`, `answer`, `tables`) are stripped before inference.
     - `dail_sql` retrieves strictly from `split == 'train'` with a zero-table-overlap guard.

Modes:
  - Online generation + evaluation:
      python3 eval/run_oracle_ablation.py --frameworks direct_ddl --models my-model --eval-only-heldout
  - Offline verification of existing predictions (zero API calls, stdlib only):
      python3 eval/run_oracle_ablation.py --eval-only --eval-only-heldout --preds-dir results/predictions_oracle_ablation
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sqlite3
import sys
import threading
import time
from pathlib import Path
from typing import Any

os.environ["TOKENIZERS_PARALLELISM"] = "false"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "third_party" / "m_schema"))

from evaluate import evaluate as run_eval_metrics, result_multiset  # noqa: E402
from export_bird_format import TABLE_DESC_ZH  # noqa: E402
from llm_client import call_llm, extract_sql, load_model_endpoint  # noqa: E402

PIPELINE_VERSION = "v2.1-zero-leakage-audited"

DB_PATH = ROOT / "data" / "bankreg.sqlite"
QUESTIONS_PATH = ROOT / "data" / "questions.jsonl"
SCHEMA_PATH = ROOT / "data" / "schema.json"
DDL_PATH = ROOT / "schema" / "bankreg_v4.sqlite.sql"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "oracle_ablation"

DEFAULT_FRAMEWORKS = [
    "direct_ddl",
    "m_schema",
    "schemagate",
    "dail_sql",
    "rsl_sql",
    "chess",
    "deepeye_axissql",
]
DEFAULT_MODELS = [
    "deepseek-v4.1-flash",
    "deepseek-v4-flash",
    "qwen3.5-397b-a17b",
    "qwen3.6-35b-a3b",
]
MODEL_DISPLAY = {
    "deepseek-v4.1-flash": "DeepSeek-V4.1-Flash",
    "deepseek-v4-flash": "DeepSeek-V4-Flash",
    "qwen3.5-397b-a17b": "Qwen3.5-397B-A17B",
    "qwen3.6-35b-a3b": "Qwen3.6-35B-A3B",
}

CATALOG_TABLES = [
    "classification_grade",
    "industry_sector",
    "loan_product_catalog",
    "status_catalog",
    "relation_type_catalog",
    "payment_mode_catalog",
    "payment_type_catalog",
    "card_type_catalog",
    "party_type_catalog",
    "instrument_type_catalog",
]
CATALOG_SET = set(CATALOG_TABLES)

SQL_GENERATION_RULES = """### 银行监管数仓 SQL 编写准则（严格遵守）：
1. 数据库为 SQLite，只输出一条合法的只读 SQL 查询（包裹在 ```sql ... ``` 中），不要输出解释。
2. 严格按照题目要求选择输出列与列顺序（例如题目要求输出“机构名称与借据笔数”，则 SELECT 必须且只能输出这 2 列）。
3. 数值精度与过滤口径规范：
   - 汇总/平均金额（SUM/AVG）与平均天数统一使用 `ROUND(..., 2)` 保留 2 位小数；平均利率使用 `ROUND(..., 4)`；比率/占比/覆盖率/集中度统一使用 `ROUND(... * 1.0 / ..., 6)` 保留 6 位小数。
   - 除非题面明确提及状态（如“已清算”、“正常”、“有效”、“久悬”、“已核销”、“已到期”），否则不要额外添加 `status = ...` 过滤条件。
4. 重要外键路径提示：
   - 借据 `loan_drawdown` 通过 `agreement_id` 关联授信协议 `credit_agreement`，再通过 `credit_agreement.institution_id` 关联法人机构 `institution`，通过 `credit_agreement.borrower_party_id` 关联借款人 `party` 及对公画像 `organization_profile`。
   - 担保合同 `security_agreement` 通过被担保主债权桥接表 `secured_obligation (security_id, agreement_id)` 关联授信协议 `credit_agreement`；通过 `collateral_link` 关联抵质押物 `collateral_asset` 及评估表 `collateral_valuation`；通过 `guarantor_commitment` 关联保证人。
   - 审计基准日（当前快照日）统一为 `'2026-06-30'`。"""


def sanitize_item_for_inference(q: dict[str, Any]) -> dict[str, Any]:
    """Strip all ground-truth fields (`sql`, `answer`, `answer_columns`, `tables`) before inference."""
    return {
        "question_id": q["question_id"],
        "db_id": q["db_id"],
        "question": q["question"],
        "question_en": q.get("question_en", ""),
        "split": q["split"],
    }


def _qtext(q: dict[str, Any], lang: str = "zh") -> str:
    return q["question_en"] if lang == "en" and q.get("question_en") else q["question"]


class WarehouseContext:
    """Shared read-only Oracle-dictionary warehouse context with lazy adapter initialization."""

    def __init__(self, train_pool: list[dict[str, Any]], preds_dir: Path, lang: str = "zh") -> None:
        self.preds_dir = preds_dir
        self.lang = lang
        self.schema_json = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.ddl_text = DDL_PATH.read_text(encoding="utf-8")
        self.tables_ddl: dict[str, str] = {}
        self.fk_neighbors: dict[str, set[str]] = {}
        for m in re.finditer(r"CREATE TABLE (\w+)\s*\((.*?)\)\s*STRICT;", self.ddl_text, re.S):
            tname = m.group(1)
            self.tables_ddl[tname] = m.group(0).strip()
            self.fk_neighbors.setdefault(tname, set())
            for ref in re.findall(r"REFERENCES\s+(\w+)", m.group(0)):
                self.fk_neighbors[tname].add(ref)
                self.fk_neighbors.setdefault(ref, set()).add(tname)

        lines = ["### 受控词表（码表）完整取值域："]
        for ct in CATALOG_TABLES:
            if ct in self.schema_json["tables"]:
                tinfo = self.schema_json["tables"][ct]
                cols = [c["name"] for c in tinfo["columns"]]
                vals = tinfo.get("values", [])
                lines.append(f"- `{ct}` ({', '.join(cols)}): {json.dumps(vals, ensure_ascii=False)}")
        self.catalog_values_prompt = "\n".join(lines)

        self._mschema_obj = None
        self._full_mschema_str: str | None = None
        self._schemagate_cat = None

        self.train_pool = train_pool
        self._init_lock = threading.Lock()
        self._sg_lock = threading.Lock()
        self._sg_cache: dict[tuple[str, int], list[str]] = {}
        self._local = threading.local()

    @property
    def full_mschema_str(self) -> str:
        if self._full_mschema_str is None:
            with self._init_lock:
                if self._full_mschema_str is None:
                    try:
                        from sqlalchemy import create_engine
                        from schema_engine import SchemaEngine

                        engine = create_engine(f"sqlite:///{DB_PATH.resolve()}")
                        self._mschema_obj = SchemaEngine(engine=engine, db_name="bankreg_main").mschema
                    except ImportError:
                        from sqlite_schema_engine import SQLiteSchemaEngine

                        self._mschema_obj = SQLiteSchemaEngine(db_path=DB_PATH, db_name="bankreg_main").mschema
                    self._full_mschema_str = self._mschema_obj.to_mschema()
        return self._full_mschema_str

    @property
    def schemagate_cat(self):
        if self._schemagate_cat is None:
            with self._init_lock:
                if self._schemagate_cat is None:
                    try:
                        from schemagate import Catalog
                    except ImportError as exc:
                        raise RuntimeError(
                            "Framework requires `schemagate`. Install with: pip install -r requirements-eval.txt"
                        ) from exc
                    cat = Catalog().bootstrap(f"sqlite:///{DB_PATH.resolve()}")
                    cat.describe(TABLE_DESC_ZH)
                    for tname, desc in TABLE_DESC_ZH.items():
                        if tname in self.tables_ddl:
                            cat.hint(tname, desc)
                    self._schemagate_cat = cat
        return self._schemagate_cat

    def get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn"):
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
            conn.execute("PRAGMA query_only = ON;")
            self._local.conn = conn
        return self._local.conn

    def get_cached_pred(self, framework: str, model_alias: str, qid: str) -> str | None:
        suffix = "_en" if self.lang == "en" else ""
        p = self.preds_dir / f"preds_l2_{framework}_{model_alias}{suffix}.jsonl"
        if not p.exists():
            return None
        cache_attr = f"_pred_cache_{framework}_{model_alias}{suffix}"
        mp = getattr(self, cache_attr, None)
        if mp is None or qid not in mp:
            mp = {}
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    d = json.loads(line)
                    if d.get("pipeline_version") != PIPELINE_VERSION:
                        continue
                    sql = d.get("predicted_sql", "")
                    if sql and "LLM_ERROR" not in sql:
                        mp[d["question_id"]] = sql
            setattr(self, cache_attr, mp)
        return mp.get(qid)

    def try_execute(self, sql: str) -> tuple[bool, list[tuple], str | None]:
        if not sql or not sql.strip():
            return False, [], "Empty SQL"
        conn = self.get_conn()
        t0 = time.time()
        conn.set_progress_handler(lambda: 1 if time.time() - t0 > 2.5 else 0, 10000)
        try:
            rows = conn.execute(sql).fetchall()
            return True, rows, None
        except Exception as exc:
            return False, [], str(exc)
        finally:
            conn.set_progress_handler(None, 0)

    def build_compact_ddl(self, selected_tables: list[str] | None = None) -> str:
        if selected_tables is None:
            selected_tables = [t for t, v in self.schema_json["tables"].items() if v["row_count"] > 0]
        out = []
        for t in selected_tables:
            if t in self.tables_ddl:
                desc = TABLE_DESC_ZH.get(t, "")
                header = f"-- {t}: {desc}\n" if desc else ""
                clean_lines = [
                    line for line in self.tables_ddl[t].splitlines() if "CONSTRAINT ck_" not in line
                ]
                out.append(header + "\n".join(clean_lines))
        return "\n\n".join(out)

    def expand_fk_closure(self, tables: list[str], hops: int = 1) -> list[str]:
        cur = set(tables) | CATALOG_SET
        for _ in range(hops):
            nxt = set(cur)
            for t in list(cur):
                for nb in self.fk_neighbors.get(t, ()):
                    if self.schema_json["tables"].get(nb, {}).get("row_count", 0) > 0:
                        nxt.add(nb)
            cur = nxt
        return [t for t in self.schema_json["tables"] if t in cur]


def run_direct_ddl(ctx: WarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    ddl = ctx.build_compact_ddl()
    prompt = f"""你是银行监管数仓 SQL 专家。请根据以下 SQLite 数据库表结构与受控词表取值，将自然语言问题转化为准确的 SQL。

{ddl}

{ctx.catalog_values_prompt}

{SQL_GENERATION_RULES}

### 自然语言问题：
{q['question']}

### SQL："""
    return extract_sql(call_llm(endpoint, [{"role": "user", "content": prompt}]))


def run_m_schema(ctx: WarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    desc_block = "\n".join(f"- {t}: {d}" for t, d in TABLE_DESC_ZH.items())
    prompt = f"""You are now a sqlite data analyst, and you are given a database schema in M-Schema format as follows:

【Table Descriptions】
{desc_block}

【Schema】
{ctx.full_mschema_str}

{ctx.catalog_values_prompt}

{SQL_GENERATION_RULES}

【Question】
{q['question']}

Please read and understand the database schema carefully, and generate an executable SQL based on the user's question. The generated SQL is protected by ```sql and ```."""
    return extract_sql(call_llm(endpoint, [{"role": "user", "content": prompt}]))


def schemagate_select_tables(ctx: WarehouseContext, question: str, top_k: int = 14) -> list[str]:
    key = (question, top_k)
    with ctx._sg_lock:
        if key in ctx._sg_cache:
            return ctx._sg_cache[key]
        sel = ctx.schemagate_cat.select(question, top_k=top_k)
        picked = [o["name"] for o in sel.object_list]
        q_grams = {question[i : i + 2] for i in range(len(question) - 1)}
        scored = []
        for tname, desc in TABLE_DESC_ZH.items():
            d_grams = {desc[i : i + 2] for i in range(len(desc) - 1)}
            scored.append((len(q_grams & d_grams), tname))
        scored.sort(reverse=True)
        for _, tname in scored[:10]:
            if tname not in picked:
                picked.append(tname)
        res = ctx.expand_fk_closure(picked, hops=1)
        ctx._sg_cache[key] = res
        return res


def run_schemagate(ctx: WarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    selected = schemagate_select_tables(ctx, q["question"], top_k=12)
    ddl = ctx.build_compact_ddl(selected)
    prompt = f"""你是银行监管数仓 SQL 专家。以下是通过 SchemaGate 外键感知选择器筛选出的相关表结构与受控词表：

{ddl}

{ctx.catalog_values_prompt}

{SQL_GENERATION_RULES}

### 自然语言问题：
{q['question']}

### SQL："""
    return extract_sql(call_llm(endpoint, [{"role": "user", "content": prompt}]))


def _question_skeleton_tokens(text: str) -> set[str]:
    cleaned = re.sub(r"“[^”]*”|'[^']*'|\d+(\.\d+)?", "?", text)
    return {cleaned[i : i + 2] for i in range(len(cleaned) - 1)}


def retrieve_disjoint_dail_shots(ctx: WarehouseContext, q: dict[str, Any], k: int = 3) -> list[dict[str, Any]]:
    qid = q["question_id"]
    question = q["question"]
    q_grams = {question[i : i + 2] for i in range(len(question) - 1)}
    scored_tabs = []
    for tname, desc in TABLE_DESC_ZH.items():
        if tname in CATALOG_SET:
            continue
        d_grams = {desc[i : i + 2] for i in range(len(desc) - 1)}
        scored_tabs.append((len(q_grams & d_grams), tname))
    scored_tabs.sort(reverse=True)
    predicted_core = {t for score, t in scored_tabs[:5] if score > 0}

    target_toks = _question_skeleton_tokens(question)
    scored = []
    for cand in ctx.train_pool:
        if cand["question_id"] == qid:
            continue
        cand_core = set(cand["tables"]) - CATALOG_SET
        if cand_core & predicted_core:
            continue
        cand_toks = _question_skeleton_tokens(cand["question"])
        jacc = len(target_toks & cand_toks) / max(1, len(target_toks | cand_toks))
        scored.append((jacc, cand))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:k]]


def run_dail_sql(ctx: WarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    shots = retrieve_disjoint_dail_shots(ctx, q, k=3)
    shots_text = "\n\n".join(
        f"/* 跨表语法参考示例 {i+1}: {s['question']} */\n{s['sql']}" for i, s in enumerate(shots)
    )
    ddl = ctx.build_compact_ddl()
    prompt = f"""你是银行监管数仓 SQL 专家。请参考数据库 Schema、受控词表以及跨领域 SQL 语法示例，为目标问题编写 SQL。

{ddl}

{ctx.catalog_values_prompt}

{SQL_GENERATION_RULES}

### 跨表语法结构参考示例（DAIL-SQL Disjoint Few-Shot）：
{shots_text}

### 目标自然语言问题：
{q['question']}

### SQL："""
    return extract_sql(call_llm(endpoint, [{"role": "user", "content": prompt}]))


def run_rsl_sql(ctx: WarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    prelim_sql = ctx.get_cached_pred("direct_ddl", endpoint["alias"], q["question_id"]) or run_direct_ddl(ctx, endpoint, q)
    backward_tables = [
        m.group(1)
        for m in re.finditer(r"\b(?:FROM|JOIN)\s+(?:main\.)?([A-Za-z_]\w*)", prelim_sql, re.I)
        if m.group(1) in ctx.tables_ddl
    ]
    forward_tables = schemagate_select_tables(ctx, q["question"], top_k=10)
    bi_tables = ctx.expand_fk_closure(list(dict.fromkeys(backward_tables + forward_tables)), hops=1)
    bi_ddl = ctx.build_compact_ddl(bi_tables)

    step2_prompt = f"""你是银行监管数仓 SQL 专家（RSL-SQL 双向 Schema 增强阶段）。
以下是经正反向双向 Schema Linking 确认的子图 Schema 与受控词表：

{bi_ddl}

{ctx.catalog_values_prompt}

{SQL_GENERATION_RULES}

请仔细核对：
1. 输出列的个数、顺序和含义是否与问题要求完全一致；
2. 跨表连接是否遗漏中间表（如 `credit_agreement` 或 `secured_obligation`），一对多关联求和是否存在重复累加；
3. 比率计算是否乘以 `1.0` 并按准则使用 `ROUND`。

### 自然语言问题：
{q['question']}

### SQL："""
    aug_sql = extract_sql(call_llm(endpoint, [{"role": "user", "content": step2_prompt}]))

    ok1, rows1, _ = ctx.try_execute(prelim_sql)
    ok2, rows2, err2 = ctx.try_execute(aug_sql)

    if ok1 and not ok2:
        chosen = prelim_sql
    elif ok2 and not ok1:
        chosen = aug_sql
    elif ok1 and ok2:
        if rows1 == rows2 or not rows1:
            chosen = aug_sql if rows2 else prelim_sql
        elif not rows2:
            chosen = prelim_sql
        else:
            sel_prompt = f"""给定以下银行监管查询问题与两条候选 SQL 及其执行结果预览，请严格对照编写准则选择完全符合题面要求（输出列顺序、过滤条件、聚合精度、排序方向）的一条，输出最终 SQL（包裹在 ```sql ... ``` 中）。

{SQL_GENERATION_RULES}

### 问题：
{q['question']}

### 候选 SQL A（返回 {len(rows1)} 行，前2行: {json.dumps([list(r) for r in rows1[:2]], ensure_ascii=False)}）：
```sql
{prelim_sql}
```

### 候选 SQL B（返回 {len(rows2)} 行，前2行: {json.dumps([list(r) for r in rows2[:2]], ensure_ascii=False)}）：
```sql
{aug_sql}
```"""
            chosen = extract_sql(call_llm(endpoint, [{"role": "user", "content": sel_prompt}]))
            ok_c, rows_c, _ = ctx.try_execute(chosen)
            if not ok_c or not rows_c:
                chosen = aug_sql if rows2 else prelim_sql
    else:
        fix_prompt = f"""以下 SQL 在 SQLite 上执行报错，请根据 Schema 修复语法或表列名错误，只输出修复后的 SQL（```sql ... ```）：

{bi_ddl}

问题：{q['question']}
原 SQL：{aug_sql}
SQLite 报错：{err2}"""
        chosen = extract_sql(call_llm(endpoint, [{"role": "user", "content": fix_prompt}]))
    return chosen


def run_chess(ctx: WarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    matched_values = []
    for ct in CATALOG_TABLES:
        for row in ctx.schema_json["tables"].get(ct, {}).get("values", []):
            for cell in row:
                if isinstance(cell, str) and len(cell) >= 2 and cell in q["question"]:
                    matched_values.append(f"表 `{ct}` 包含匹配行: {json.dumps(row, ensure_ascii=False)}")
    ir_context = "\n".join(matched_values) if matched_values else "（无直接字面命中，请参考完整受控词表）"

    sub_tables = schemagate_select_tables(ctx, q["question"], top_k=14)
    sub_ddl = ctx.build_compact_ddl(sub_tables)

    cg_prompt = f"""你是 CHESS 框架的 Candidate Generator。请根据 Information Retriever 检索到的词表值与 Schema Selector 筛选的表结构生成 SQL。

### Information Retriever 词表值命中：
{ir_context}

{ctx.catalog_values_prompt}

### Schema Selector 选定表结构：
{sub_ddl}

{SQL_GENERATION_RULES}

### 问题：
{q['question']}

### SQL："""
    cand_sql = extract_sql(call_llm(endpoint, [{"role": "user", "content": cg_prompt}]))
    ok, rows, err = ctx.try_execute(cand_sql)

    if not ok or not rows:
        ut_prompt = f"""你是 CHESS 框架的 Unit Tester & Refiner。候选 SQL 执行失败或返回空集（在监管数仓中所有问题均应返回非空结果）。
请使用全量表结构修复该 SQL：

{ctx.build_compact_ddl()}

{ctx.catalog_values_prompt}

{SQL_GENERATION_RULES}

问题：{q['question']}
原候选 SQL：{cand_sql}
执行反馈：ok={ok}, rows={len(rows)}, error={err}

请只输出修复后的 SQL（```sql ... ```）："""
        fixed = extract_sql(call_llm(endpoint, [{"role": "user", "content": ut_prompt}]))
        ok2, rows2, _ = ctx.try_execute(fixed)
        if ok2 and rows2:
            return fixed
    return cand_sql


def run_deepeye_axissql(ctx: WarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    alias = endpoint["alias"]
    qid = q["question_id"]
    c1 = ctx.get_cached_pred("direct_ddl", alias, qid) or run_direct_ddl(ctx, endpoint, q)
    c2 = ctx.get_cached_pred("m_schema", alias, qid) or run_m_schema(ctx, endpoint, q)
    c3 = ctx.get_cached_pred("dail_sql", alias, qid) or run_dail_sql(ctx, endpoint, q)

    candidates = []
    for label, sql in [("DDL-Generator", c1), ("MSchema-Generator", c2), ("ICL-Generator", c3)]:
        ok, rows, err = ctx.try_execute(sql)
        if not ok or not rows:
            rev_prompt = f"""[DeepEye-SQL Checker Revision] 候选 SQL 执行报错或返回 0 行，请修正：
问题：{q['question']}
原 SQL：{sql}
报错/状态：ok={ok}, rows={len(rows)}, err={err}

{ctx.build_compact_ddl(schemagate_select_tables(ctx, q['question'], top_k=14))}
{ctx.catalog_values_prompt}
{SQL_GENERATION_RULES}

请只输出修正后的 SQL（```sql ... ```）："""
            sql = extract_sql(call_llm(endpoint, [{"role": "user", "content": rev_prompt}]))
            ok, rows, err = ctx.try_execute(sql)
        candidates.append((label, sql, ok, rows, err))

    valid_cands = [c for c in candidates if c[2] and c[3]]
    if not valid_cands:
        return c1

    multisets = [result_multiset(c[3]) for c in valid_cands]
    if all(m == multisets[0] for m in multisets[1:]):
        return valid_cands[0][1]

    cand_desc = []
    for label, sql, _, rows, _ in valid_cands:
        cand_desc.append(
            f"### 候选 [{label}] (返回 {len(rows)} 行, 前3行样本: {json.dumps([list(r) for r in rows[:3]], ensure_ascii=False)}):\n```sql\n{sql}\n```"
        )
    agg_prompt = f"""你是 AxisSQL 的 Execution-Grounded Agentic Aggregator（执行引导聚合选择器）。
现有多个生成器针对同一银行监管问题生成的候选 SQL 及其在真实数据库上的执行结果。
请严格对照编写准则对比各候选 SQL 的：
1. 输出列数、列顺序与题面要求是否完全一致；
2. 过滤谓词（受控词表、状态、非关联方排除、日期区间）是否完整且无多余过滤；
3. 数值精度（ROUND 位数）与表连接路径是否符合准则。

{SQL_GENERATION_RULES}

### 自然语言问题：
{q['question']}

{chr(10).join(cand_desc)}

请选择最准确的一条 SQL，或综合各候选的正确片段合成一条最优 SQL（只输出 ```sql ... ```）："""
    agg_sql = extract_sql(call_llm(endpoint, [{"role": "user", "content": agg_prompt}]))
    ok_a, rows_a, _ = ctx.try_execute(agg_sql)
    if ok_a and rows_a:
        return agg_sql
    for i, m_i in enumerate(multisets):
        if sum(1 for m_j in multisets if m_j == m_i) >= 2:
            return valid_cands[i][1]
    return valid_cands[0][1]


FRAMEWORKS = {
    "direct_ddl": run_direct_ddl,
    "m_schema": run_m_schema,
    "schemagate": run_schemagate,
    "dail_sql": run_dail_sql,
    "rsl_sql": run_rsl_sql,
    "chess": run_chess,
    "deepeye_axissql": run_deepeye_axissql,
}


def evaluate_system(
    ctx: WarehouseContext,
    framework_name: str,
    model_alias: str,
    questions: list[dict[str, Any]],
    preds_dir: Path,
    workers: int = 12,
    eval_only: bool = False,
    models_config: Path | None = None,
) -> dict[str, Any]:
    preds_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_en" if ctx.lang == "en" else ""
    pred_file = preds_dir / f"preds_l2_{framework_name}_{model_alias}{suffix}.jsonl"
    existing: dict[str, dict[str, Any]] = {}
    if pred_file.exists():
        for line in pred_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                if d.get("pipeline_version") and d.get("pipeline_version") != PIPELINE_VERSION:
                    continue
                sql = d.get("predicted_sql", "")
                if sql and "LLM_ERROR" not in sql:
                    existing[d["question_id"]] = d

    todo = [q for q in questions if q["question_id"] not in existing]
    if todo and eval_only:
        raise FileNotFoundError(
            f"--eval-only set, but {len(todo)}/{len(questions)} predictions are missing in {pred_file}"
        )

    if todo:
        endpoint = load_model_endpoint(model_alias, config_path=models_config)
        fn = FRAMEWORKS[framework_name]
        print(
            f"\n>>> [Oracle Ablation L2 | lang={ctx.lang}] Running [{framework_name}] x [{model_alias}] "
            f"({len(todo)}/{len(questions)} to generate, workers={workers})...",
            flush=True,
        )
        lock = threading.Lock()

        def _work(raw_item: dict[str, Any]) -> None:
            blind_item = sanitize_item_for_inference(raw_item)
            if ctx.lang == "en" and blind_item.get("question_en"):
                blind_item["question"] = blind_item["question_en"]
            t0 = time.time()
            sql = fn(ctx, endpoint, blind_item)
            dt_sec = round(time.time() - t0, 3)
            rec = {
                "question_id": blind_item["question_id"],
                "framework": framework_name,
                "model": model_alias,
                "lang": ctx.lang,
                "pipeline_version": PIPELINE_VERSION,
                "predicted_sql": sql,
                "latency_sec": dt_sec,
            }
            with lock:
                existing[blind_item["question_id"]] = rec
                with pred_file.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_work, it) for it in todo]
            done = 0
            for fut in concurrent.futures.as_completed(futs):
                fut.result()
                done += 1
                if done % 25 == 0 or done == len(todo):
                    print(f"    [L2: {framework_name} x {model_alias}] {done}/{len(todo)} done", flush=True)

        sorted_recs = [existing[q["question_id"]] for q in questions if q["question_id"] in existing]
        with pred_file.open("w", encoding="utf-8") as fh:
            for r in sorted_recs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    else:
        sorted_recs = [existing[q["question_id"]] for q in questions if q["question_id"] in existing]

    preds_map = {r["question_id"]: r["predicted_sql"] for r in sorted_recs}
    report_unordered, per_q_u = run_eval_metrics(questions, DB_PATH, preds_map, ordered=False)
    report_ordered, per_q_o = run_eval_metrics(questions, DB_PATH, preds_map, ordered=True)

    heldout_u = [r for r in per_q_u if r["split"] in ("dev", "test")]
    heldout_o = [r for r in per_q_o if r["split"] in ("dev", "test")]
    ex_heldout = round(sum(r["correct"] for r in heldout_u) / max(1, len(heldout_u)) * 100, 2)
    ex_ord_heldout = round(sum(r["correct"] for r in heldout_o) / max(1, len(heldout_o)) * 100, 2)
    exec_rate = round(report_unordered["executable_rate"] * 100, 2)
    avg_lat = round(
        sum(r.get("latency_sec", 0.0) for r in sorted_recs) / max(1, len(sorted_recs)), 2
    )

    summary = {
        "framework": framework_name,
        "model": model_alias,
        "num_questions": len(questions),
        "ex_heldout_dev_test": ex_heldout,
        "ex_ordered_heldout_dev_test": ex_ord_heldout,
        "ex_unordered": round(report_unordered["execution_accuracy"] * 100, 2),
        "ex_ordered": round(report_ordered["execution_accuracy"] * 100, 2),
        "executable_rate": exec_rate,
        "avg_latency_sec": avg_lat,
        "by_split": {k: round(v["accuracy"] * 100, 2) for k, v in report_unordered["by_split"].items()},
        "by_difficulty": {k: round(v["accuracy"] * 100, 2) for k, v in report_unordered["by_difficulty"].items()},
        "by_num_tables": {k: round(v["accuracy"] * 100, 2) for k, v in report_unordered["by_num_tables"].items()},
    }
    print(
        f"✓ [L2-Oracle   | {framework_name:15s} | {model_alias:20s}] "
        f"HeldOut={ex_heldout:6.2f}% | Dev={summary['by_split'].get('dev', 0):6.2f}% | "
        f"Test={summary['by_split'].get('test', 0):6.2f}% | Exec={exec_rate:6.2f}% | Lat={avg_lat}s",
        flush=True,
    )
    return summary


def write_markdown_ablation(all_summaries: list[dict[str, Any]], n_questions: int, out_md: Path) -> None:
    md_lines = [
        f"# BankRegBench · Oracle Dictionary Ablation Leaderboard (Track L2, Dev+Test N={n_questions})",
        "",
        "| Rank | Framework | Backbone LLM | Held-Out EX (%) | Dev EX (%) | Test EX (%) | Strict Unordered EX (%) | Ordered EX (%) | Executable (%) | Easy (%) | Medium (%) | Hard (%) | Extra (%) | Latency (s) |",
        "| :--: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for idx, s in enumerate(
        sorted(all_summaries, key=lambda x: (-x["ex_heldout_dev_test"], -x["ex_unordered"])), start=1
    ):
        bd = s["by_difficulty"]
        bs = s["by_split"]
        m_disp = MODEL_DISPLAY.get(s["model"], s["model"])
        md_lines.append(
            f"| {idx} | `{s['framework']}` | `{m_disp}` | **{s['ex_heldout_dev_test']:.2f}** | "
            f"{bs.get('dev', 0):.2f} | {bs.get('test', 0):.2f} | {s['ex_unordered']:.2f} | "
            f"{s['ex_ordered']:.2f} | {s['executable_rate']:.2f} | "
            f"{bd.get('easy', 0):.2f} | {bd.get('medium', 0):.2f} | {bd.get('hard', 0):.2f} | "
            f"{bd.get('extra', 0):.2f} | {s['avg_latency_sec']:.2f} |"
        )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run or verify Oracle Dictionary Ablation (Track L2) on BankRegBench.")
    ap.add_argument("--frameworks", nargs="+", default=DEFAULT_FRAMEWORKS, choices=list(FRAMEWORKS.keys()))
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--models-config", type=Path, default=None, help="Path to models.json")
    ap.add_argument("--preds-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for prediction JSONL files")
    ap.add_argument("--out-json", type=Path, default=None, help="Output path for ablation JSON")
    ap.add_argument("--out-md", type=Path, default=None, help="Output path for ablation Markdown")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--lang", choices=["zh", "en"], default="zh", help="Question language: zh (default) or en")
    ap.add_argument("--eval-only-heldout", action="store_true", help="Evaluate only on Dev+Test (N=200)")
    ap.add_argument("--limit", type=int, default=None, help="Optional limit on number of questions")
    ap.add_argument("--eval-only", action="store_true", help="Score existing predictions offline without calling any LLM")
    args = ap.parse_args()

    all_questions = [json.loads(l) for l in QUESTIONS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    train_pool = [
        {
            "question_id": q["question_id"],
            "question": _qtext(q, args.lang),
            "sql": q["sql"],
            "tables": q["tables"],
        }
        for q in all_questions
        if q["split"] == "train"
    ]
    questions = [q for q in all_questions if q["split"] in ("dev", "test")] if args.eval_only_heldout else all_questions
    if args.limit is not None:
        questions = questions[: args.limit]

    ctx = WarehouseContext(train_pool=train_pool, preds_dir=args.preds_dir, lang=args.lang)

    all_summaries = []
    for model_alias in args.models:
        for fw in args.frameworks:
            s = evaluate_system(
                ctx,
                fw,
                model_alias,
                questions,
                preds_dir=args.preds_dir,
                workers=args.workers,
                eval_only=args.eval_only,
                models_config=args.models_config,
            )
            all_summaries.append(s)

    out_json = args.out_json or (args.preds_dir / "ablation_oracle_dict.json")
    out_md = args.out_md or (args.preds_dir / "ablation_oracle_dict.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(all_summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown_ablation(all_summaries, len(questions), out_md)
    print(f"\nSaved Oracle Ablation (Track L2) report to {out_md} and {out_json}")


if __name__ == "__main__":
    main()
