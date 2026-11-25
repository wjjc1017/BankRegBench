#!/usr/bin/env python3
"""Standard 84-Table Zero-Prior Evaluation Harness (Track L0) for BankRegBench.

Protocol (Standard / Pure Blind Evaluation):
  1. Exposes all 84 tables in `schema/bankreg_v4.sqlite.sql` (including 20 empty distractor tables).
  2. NO handcrafted Chinese table/column dictionary is injected into DDL or M-Schema.
  3. NO full dump of controlled vocabulary tables is pasted into prompts.
     - Only frameworks with native DB cell inspection (`m_schema` via SQLAlchemy column sampling,
       and `chess` via its Information Retriever querying SQLite string literals) obtain cell
       values through their own retrieval mechanisms.
  4. NO foreign-key join path spoilers, NO audit date hints, and NO `ROUND(...)` / `status` rules.
  5. Reports both Strict EX (6-decimal exact) and Relaxed EX (bucketed 2/4-decimal rounding).

Modes:
  - Online generation + evaluation (requires OpenAI-Compatible API via env vars or configs/models.json):
      python3 eval/run_standard_eval.py --frameworks direct_ddl --models my-model
  - Offline verification of existing predictions (zero API calls, stdlib only):
      python3 eval/run_standard_eval.py --eval-only --preds-dir results/predictions_standard
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

from evaluate import evaluate as run_eval_metrics, result_multiset, rows_match_tolerant  # noqa: E402
from llm_client import call_llm, extract_sql, load_model_endpoint  # noqa: E402

DB_PATH = ROOT / "data" / "bankreg.sqlite"
QUESTIONS_PATH = ROOT / "data" / "questions.jsonl"
SCHEMA_PATH = ROOT / "data" / "schema.json"
DDL_PATH = ROOT / "schema" / "bankreg_v4.sqlite.sql"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "standard"

PIPELINE_VERSION_L0 = "v2.1-track-l0-pure-blind"

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
    "deepseek-v4-flash",
    "deepseek-v4.1-flash",
    "qwen3.5-397b-a17b",
    "qwen3.6-35b-a3b",
]
MODEL_DISPLAY = {
    "deepseek-v4.1-flash": "DeepSeek-V4.1-Flash",
    "deepseek-v4-flash": "DeepSeek-V4-Flash",
    "qwen3.5-397b-a17b": "Qwen3.5-397B-A17B",
    "qwen3.6-35b-a3b": "Qwen3.6-35B-A3B",
}

BLIND_SQL_RULES = """### SQL 编写要求：
1. 数据库为 SQLite，请根据给定的数据库 Schema 将自然语言问题转换为一条合法的只读 SQL 查询（包裹在 ```sql ... ``` 中），不要输出解释文字。
2. 严格按照题目要求选择输出列与列顺序。
3. 整数相除求比率或占比时请乘以 `1.0`（如 `* 1.0 /`）避免 SQLite 整除截断。"""

BLIND_SQL_RULES_EN = """### SQL Requirements:
1. The database is SQLite. Convert the natural language question into a single valid read-only SQL query wrapped in ```sql ... ``` without extra explanation.
2. Strictly follow the requested output columns and column order.
3. For ratios or percentages involving integer division, multiply by `1.0` (e.g., `* 1.0 /`) to avoid SQLite integer truncation."""


def _qtext(q: dict[str, Any], lang: str = "zh") -> str:
    return q["question_en"] if lang == "en" and q.get("question_en") else q["question"]


def _rules(lang: str = "zh") -> str:
    return BLIND_SQL_RULES_EN if lang == "en" else BLIND_SQL_RULES


def sanitize_item_for_inference(q: dict[str, Any]) -> dict[str, Any]:
    """Strip all ground-truth fields (`sql`, `answer`, `answer_columns`, `tables`) before inference."""
    return {
        "question_id": q["question_id"],
        "db_id": q["db_id"],
        "question": q["question"],
        "question_en": q.get("question_en", ""),
        "split": q["split"],
    }


class BlindWarehouseContext:
    """Pure blind 84-table warehouse context with zero injected domain hints.

    Optional third-party adapters (`M-Schema` and `schemagate`) are initialized lazily
    so lightweight frameworks and `--eval-only` verification run with Python stdlib only.
    """

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

        self._mschema_obj = None
        self._full_mschema_str: str | None = None
        self._schemagate_cat = None
        self._db_text_cells: list[tuple[str, str, str]] | None = None

        self.train_pool = train_pool
        self._init_lock = threading.Lock()
        self._sg_lock = threading.Lock()
        self._sg_cache: dict[tuple[str, int], list[str]] = {}
        self._local = threading.local()

    @property
    def mschema_obj(self):
        if self._mschema_obj is None:
            with self._init_lock:
                if self._mschema_obj is None:
                    try:
                        from sqlalchemy import create_engine
                        from schema_engine import SchemaEngine

                        engine = create_engine(f"sqlite:///{DB_PATH.resolve()}")
                        self._mschema_obj = SchemaEngine(engine=engine, db_name="bankreg_main").mschema
                    except ImportError:
                        from sqlite_schema_engine import SQLiteSchemaEngine

                        self._mschema_obj = SQLiteSchemaEngine(db_path=DB_PATH, db_name="bankreg_main").mschema
                    self._full_mschema_str = self._mschema_obj.to_mschema()
        return self._mschema_obj

    @property
    def full_mschema_str(self) -> str:
        _ = self.mschema_obj
        assert self._full_mschema_str is not None
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
                    self._schemagate_cat = Catalog().bootstrap(f"sqlite:///{DB_PATH.resolve()}")
        return self._schemagate_cat

    @property
    def db_text_cells(self) -> list[tuple[str, str, str]]:
        if self._db_text_cells is None:
            with self._init_lock:
                if self._db_text_cells is None:
                    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
                    cells: list[tuple[str, str, str]] = []
                    for tname, tinfo in self.schema_json["tables"].items():
                        if 0 < tinfo["row_count"] <= 400:
                            for col in tinfo["columns"]:
                                if col["type"].upper() == "TEXT":
                                    cname = col["name"]
                                    for (val,) in conn.execute(
                                        f'SELECT DISTINCT "{cname}" FROM "{tname}" WHERE "{cname}" IS NOT NULL LIMIT 400'
                                    ):
                                        if isinstance(val, str) and len(val.strip()) >= 2:
                                            cells.append((tname, cname, val.strip()))
                    conn.close()
                    self._db_text_cells = cells
        return self._db_text_cells

    def get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn"):
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
            conn.execute("PRAGMA query_only = ON;")
            self._local.conn = conn
        return self._local.conn

    def get_cached_pred(self, framework: str, model_alias: str, qid: str) -> str | None:
        suffix = "_en" if self.lang == "en" else ""
        p = self.preds_dir / f"preds_l0_{framework}_{model_alias}{suffix}.jsonl"
        if not p.exists():
            return None
        cache_attr = f"_l0_cache_{framework}_{model_alias}{suffix}"
        mp = getattr(self, cache_attr, None)
        if mp is None or qid not in mp:
            mp = {}
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    d = json.loads(line)
                    if d.get("pipeline_version") != PIPELINE_VERSION_L0:
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

    def build_raw_ddl(self, selected_tables: list[str] | None = None) -> str:
        """Build raw DDL for all 84 tables (or selected subset) with ZERO Chinese comments."""
        if selected_tables is None:
            selected_tables = list(self.tables_ddl.keys())
        out = []
        for t in selected_tables:
            if t in self.tables_ddl:
                clean_lines = [
                    line for line in self.tables_ddl[t].splitlines() if "CONSTRAINT ck_" not in line
                ]
                out.append("\n".join(clean_lines))
        return "\n\n".join(out)

    def expand_fk_closure(self, tables: list[str], hops: int = 1) -> list[str]:
        cur = set(tables)
        for _ in range(hops):
            nxt = set(cur)
            for t in list(cur):
                for nb in self.fk_neighbors.get(t, ()):
                    nxt.add(nb)
            cur = nxt
        return [t for t in self.tables_ddl if t in cur]


def run_blind_direct_ddl(ctx: BlindWarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    ddl = ctx.build_raw_ddl()
    q_hdr = "### Question:" if ctx.lang == "en" else "### 问题："
    prompt = f"""{ddl}

{_rules(ctx.lang)}

{q_hdr}
{q['question']}

### SQL:""" if ctx.lang == "en" else f"""{ddl}

{BLIND_SQL_RULES}

### 问题：
{q['question']}

### SQL："""
    return extract_sql(call_llm(endpoint, [{"role": "user", "content": prompt}]))


def run_blind_m_schema(ctx: BlindWarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    prompt = f"""You are now a sqlite data analyst, and you are given a database schema in M-Schema format as follows:

【Schema】
{ctx.full_mschema_str}

{_rules(ctx.lang)}

【Question】
{q['question']}

Please generate an executable SQL based on the user's question. The generated SQL is protected by ```sql and ```."""
    return extract_sql(call_llm(endpoint, [{"role": "user", "content": prompt}]))


def blind_schemagate_select(ctx: BlindWarehouseContext, question: str, top_k: int = 16) -> list[str]:
    key = (question, top_k)
    with ctx._sg_lock:
        if key in ctx._sg_cache:
            return ctx._sg_cache[key]
        sel = ctx.schemagate_cat.select(question, top_k=top_k)
        picked = [o["name"] for o in sel.object_list]
        res = ctx.expand_fk_closure(picked, hops=1)
        ctx._sg_cache[key] = res
        return res


def run_blind_schemagate(ctx: BlindWarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    selected = blind_schemagate_select(ctx, q["question"], top_k=16)
    ddl = ctx.build_raw_ddl(selected)
    prompt = f"""{ddl}

{BLIND_SQL_RULES}

### 问题：
{q['question']}

### SQL："""
    return extract_sql(call_llm(endpoint, [{"role": "user", "content": prompt}]))


def _question_skeleton_tokens(text: str) -> set[str]:
    cleaned = re.sub(r"“[^”]*”|'[^']*'|\d+(\.\d+)?", "?", text)
    return {cleaned[i : i + 2] for i in range(len(cleaned) - 1)}


def run_blind_dail_sql(ctx: BlindWarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    qid = q["question_id"]
    prelim = ctx.get_cached_pred("direct_ddl", endpoint["alias"], qid) or run_blind_direct_ddl(ctx, endpoint, q)
    pred_tables = {
        m.group(1).lower()
        for m in re.finditer(r"\b(?:FROM|JOIN)\s+(?:main\.)?([A-Za-z_]\w*)", prelim, re.I)
    }
    target_toks = _question_skeleton_tokens(q["question"])
    scored = []
    for cand in ctx.train_pool:
        if cand["question_id"] == qid:
            continue
        cand_tabs = {t.lower() for t in cand["tables"]}
        if cand_tabs & pred_tables:
            continue
        cand_toks = _question_skeleton_tokens(cand["question"])
        jacc = len(target_toks & cand_toks) / max(1, len(target_toks | cand_toks))
        scored.append((jacc, cand))
    scored.sort(key=lambda x: x[0], reverse=True)
    shots = [x[1] for x in scored[:3]]
    shots_text = "\n\n".join(
        f"/* 示例 {i+1}: {s['question']} */\n{s['sql']}" for i, s in enumerate(shots)
    )
    ddl = ctx.build_raw_ddl()
    prompt = f"""{ddl}

{BLIND_SQL_RULES}

### 跨表 SQL 语法结构参考示例：
{shots_text}

### 目标问题：
{q['question']}

### SQL："""
    return extract_sql(call_llm(endpoint, [{"role": "user", "content": prompt}]))


def run_blind_rsl_sql(ctx: BlindWarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    prelim_sql = ctx.get_cached_pred("direct_ddl", endpoint["alias"], q["question_id"]) or run_blind_direct_ddl(ctx, endpoint, q)
    backward_tables = [
        m.group(1)
        for m in re.finditer(r"\b(?:FROM|JOIN)\s+(?:main\.)?([A-Za-z_]\w*)", prelim_sql, re.I)
        if m.group(1) in ctx.tables_ddl
    ]
    forward_tables = blind_schemagate_select(ctx, q["question"], top_k=12)
    bi_tables = ctx.expand_fk_closure(list(dict.fromkeys(backward_tables + forward_tables)), hops=1)
    bi_ddl = ctx.build_raw_ddl(bi_tables)

    ok1, rows1, err1 = ctx.try_execute(prelim_sql)
    step2_prompt = f"""以下是双向 Schema Linking 召回的相关表 DDL 以及初步候选 SQL 的执行反馈：

{bi_ddl}

{BLIND_SQL_RULES}

### 问题：
{q['question']}

### 初步候选 SQL（可执行={ok1}, 返回行数={len(rows1) if ok1 else 0}, 错误={err1}）：
```sql
{prelim_sql}
```

如果初步候选 SQL 报错、返回 0 行或列/表关联有误，请修正并输出最终 SQL（```sql ... ```）："""
    aug_sql = extract_sql(call_llm(endpoint, [{"role": "user", "content": step2_prompt}]))
    ok2, rows2, _ = ctx.try_execute(aug_sql)
    if ok2 and rows2:
        return aug_sql
    if ok1 and rows1:
        return prelim_sql
    return aug_sql


def run_blind_chess(ctx: BlindWarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    hits = []
    for tname, cname, val in ctx.db_text_cells:
        if val in q["question"]:
            hits.append(f"数据库值匹配: `{tname}.{cname} = '{val}'`")
    ir_text = "\n".join(hits[:15]) if hits else "（未检索到直接匹配的中文字符串字面量）"

    ddl = ctx.build_raw_ddl()
    cg_prompt = f"""{ddl}

### Information Retriever 数据库单元格字面量检索结果：
{ir_text}

{BLIND_SQL_RULES}

### 问题：
{q['question']}

### SQL："""
    cand_sql = extract_sql(call_llm(endpoint, [{"role": "user", "content": cg_prompt}]))
    ok, rows, err = ctx.try_execute(cand_sql)
    if not ok or not rows:
        ut_prompt = f"""[CHESS Unit Tester] 候选 SQL 执行失败或返回空结果（ok={ok}, rows={len(rows)}, err={err}）。
请结合 M-Schema 中的列样本值修复该 SQL：

{ctx.full_mschema_str}

{ir_text}

问题：{q['question']}
原候选 SQL：{cand_sql}
请只输出修复后的 SQL（```sql ... ```）："""
        fixed = extract_sql(call_llm(endpoint, [{"role": "user", "content": ut_prompt}]))
        ok2, rows2, _ = ctx.try_execute(fixed)
        if ok2 and rows2:
            return fixed
    return cand_sql


def run_blind_deepeye_axissql(ctx: BlindWarehouseContext, endpoint: dict[str, Any], q: dict[str, Any]) -> str:
    alias = endpoint["alias"]
    qid = q["question_id"]
    c1 = ctx.get_cached_pred("direct_ddl", alias, qid) or run_blind_direct_ddl(ctx, endpoint, q)
    c2 = ctx.get_cached_pred("m_schema", alias, qid) or run_blind_m_schema(ctx, endpoint, q)
    c3 = ctx.get_cached_pred("chess", alias, qid) or run_blind_chess(ctx, endpoint, q)

    candidates = []
    for label, sql in [("MSchema-Gen", c2), ("CHESS-IR-Gen", c3), ("RawDDL-Gen", c1)]:
        ok, rows, err = ctx.try_execute(sql)
        candidates.append((label, sql, ok, rows, err))

    valid_cands = [c for c in candidates if c[2] and c[3]]
    if not valid_cands:
        return c2

    multisets = [result_multiset(c[3]) for c in valid_cands]
    if all(m == multisets[0] for m in multisets[1:]):
        for _, sql, _, _, _ in valid_cands:
            if "ROUND(" in sql.upper():
                return sql
        return valid_cands[0][1]

    ref_tabs: list[str] = []
    for _, sql, _, _, _ in valid_cands:
        for m_tab in re.finditer(r"\b(?:FROM|JOIN)\s+(?:main\.)?([A-Za-z_]\w*)", sql, re.I):
            tname = m_tab.group(1).lower()
            if tname in ctx.tables_ddl and tname not in ref_tabs:
                ref_tabs.append(tname)
    sub_tabs = ctx.expand_fk_closure(ref_tabs, hops=1) if ref_tabs else list(ctx.tables_ddl.keys())[:15]
    sub_mschema = ctx.mschema_obj.to_mschema(selected_tables=[f"main.{t}" for t in sub_tabs])

    cand_desc = []
    for label, sql, _, rows, _ in valid_cands:
        cand_desc.append(
            f"### 候选 [{label}] (返回 {len(rows)} 行, 前3行: {json.dumps([list(r) for r in rows[:3]], ensure_ascii=False)}):\n```sql\n{sql}\n```"
        )
    agg_prompt = f"""你是 AxisSQL 的 Execution-Grounded Aggregator。
以下是候选 SQL 涉及表的 M-Schema（含真实列样本值 `Examples: [...]` 与外键关系）以及各候选 SQL 在 SQLite 上的真实执行结果。
请重点核查：
1. 候选 SQL 中的过滤字面量是否与 M-Schema 中的 `Examples` 真实列值一致（例如 `MSchema-Gen` 采样了真实列值，而 `RawDDL-Gen` 未采样列值，容易把编码猜错或漏连受控词表）；
2. 跨表外键关联路径（如 `loan_drawdown -> credit_agreement -> institution`、`secured_obligation` 桥接表）、分组粒度与输出列顺序是否最准确。
请直接输出最准确的一条 SQL（包裹在 ```sql ... ``` 中），不要输出解释文字：

{sub_mschema}

### 问题：
{q['question']}

{chr(10).join(cand_desc)}"""
    agg_sql = extract_sql(call_llm(endpoint, [{"role": "user", "content": agg_prompt}]))
    ok_a, rows_a, _ = ctx.try_execute(agg_sql)
    if ok_a and rows_a:
        return agg_sql
    for i, m_i in enumerate(multisets):
        if sum(1 for m_j in multisets if m_j == m_i) >= 2:
            return valid_cands[i][1]
    return valid_cands[0][1]


BLIND_FRAMEWORKS = {
    "direct_ddl": run_blind_direct_ddl,
    "m_schema": run_blind_m_schema,
    "schemagate": run_blind_schemagate,
    "dail_sql": run_blind_dail_sql,
    "rsl_sql": run_blind_rsl_sql,
    "chess": run_blind_chess,
    "deepeye_axissql": run_blind_deepeye_axissql,
}


def evaluate_blind_system(
    ctx: BlindWarehouseContext,
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
    pred_file = preds_dir / f"preds_l0_{framework_name}_{model_alias}{suffix}.jsonl"
    existing: dict[str, dict[str, Any]] = {}
    if pred_file.exists():
        for line in pred_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                if d.get("pipeline_version") and d.get("pipeline_version") != PIPELINE_VERSION_L0:
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
        fn = BLIND_FRAMEWORKS[framework_name]
        print(
            f"\n>>> [Standard Track L0 | lang={ctx.lang}] Running [{framework_name}] x [{model_alias}] "
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
                "track": "L0_blind_84_tables",
                "pipeline_version": PIPELINE_VERSION_L0,
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
                if done % 20 == 0 or done == len(todo):
                    print(f"    [L0: {framework_name} x {model_alias}] {done}/{len(todo)} done", flush=True)

        sorted_recs = [existing[q["question_id"]] for q in questions if q["question_id"] in existing]
        with pred_file.open("w", encoding="utf-8") as fh:
            for r in sorted_recs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    else:
        sorted_recs = [existing[q["question_id"]] for q in questions if q["question_id"] in existing]

    preds_map = {r["question_id"]: r["predicted_sql"] for r in sorted_recs}
    report_strict, per_q = run_eval_metrics(questions, DB_PATH, preds_map, ordered=False)

    ex_strict = round(report_strict["execution_accuracy"] * 100, 2)
    ex_tol = round(report_strict["execution_accuracy_relaxed"] * 100, 2)
    exec_rate = round(report_strict["executable_rate"] * 100, 2)
    avg_lat = round(
        sum(r.get("latency_sec", 0.0) for r in sorted_recs) / max(1, len(sorted_recs)), 2
    )

    summary = {
        "track": "L0_blind_84_tables",
        "framework": framework_name,
        "model": model_alias,
        "num_questions": len(questions),
        "ex_strict_6dec": ex_strict,
        "ex_tolerant_2dec": ex_tol,
        "executable_rate": exec_rate,
        "avg_latency_sec": avg_lat,
        "strict_by_split": {
            k: round(v["accuracy"] * 100, 2) for k, v in report_strict["by_split"].items()
        },
        "tolerant_by_split": {
            k: round(v["accuracy"] * 100, 2) for k, v in report_strict["by_split_relaxed"].items()
        },
        "tolerant_by_difficulty": {
            k: round(v["accuracy"] * 100, 2) for k, v in report_strict["by_difficulty_relaxed"].items()
        },
    }
    print(
        f"✓ [L0-Standard | {framework_name:15s} | {model_alias:20s}] "
        f"Strict-EX={ex_strict:6.2f}% | Relaxed-EX={ex_tol:6.2f}% "
        f"(Dev={summary['tolerant_by_split'].get('dev', 0):5.2f}%, Test={summary['tolerant_by_split'].get('test', 0):5.2f}%) | "
        f"Exec={exec_rate:6.2f}% | Lat={avg_lat}s",
        flush=True,
    )
    return summary


def write_markdown_leaderboard(all_summaries: list[dict[str, Any]], out_md: Path) -> None:
    md_lines = [
        "# BankRegBench · Standard 84-Table Zero-Prior Evaluation Leaderboard (Track L0)",
        "",
        "> **Protocol (Track L0 - Standard Blind)**: Exposes all 84 raw SQLite tables (including 20 empty domain distractor tables) with **zero** injected bilingual table/column dictionaries, **zero** catalog value dumps, **zero** foreign-key join hints, and **zero** rounding/status conventions. Evaluated on the held-out split (`Dev+Test, N=200`).",
        "",
        "| Rank | Framework | Backbone LLM | Relaxed EX (%) | Strict EX (%) | Dev EX (%) | Test EX (%) | Executable (%) | Easy (%) | Medium (%) | Hard (%) | Extra (%) | Latency (s) |",
        "| :--: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for idx, s in enumerate(
        sorted(all_summaries, key=lambda x: (-x["ex_tolerant_2dec"], -x["ex_strict_6dec"])), start=1
    ):
        bd = s["tolerant_by_difficulty"]
        bs = s["tolerant_by_split"]
        m_disp = MODEL_DISPLAY.get(s["model"], s["model"])
        md_lines.append(
            f"| {idx} | `{s['framework']}` | `{m_disp}` | **{s['ex_tolerant_2dec']:.2f}** | "
            f"{s['ex_strict_6dec']:.2f} | {bs.get('dev', 0):.2f} | {bs.get('test', 0):.2f} | "
            f"{s['executable_rate']:.2f} | {bd.get('easy', 0):.2f} | {bd.get('medium', 0):.2f} | "
            f"{bd.get('hard', 0):.2f} | {bd.get('extra', 0):.2f} | {s['avg_latency_sec']:.2f} |"
        )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run or verify Standard 84-Table (Track L0) evaluation on BankRegBench.")
    ap.add_argument("--frameworks", nargs="+", default=DEFAULT_FRAMEWORKS, choices=list(BLIND_FRAMEWORKS.keys()))
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--models-config", type=Path, default=None, help="Path to models.json")
    ap.add_argument("--preds-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for prediction JSONL files")
    ap.add_argument("--out-json", type=Path, default=None, help="Output path for leaderboard JSON")
    ap.add_argument("--out-md", type=Path, default=None, help="Output path for leaderboard Markdown")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--lang", choices=["zh", "en"], default="zh", help="Question language: zh (default) or en")
    ap.add_argument("--limit", type=int, default=None, help="Optional limit on number of held-out questions (smoke test)")
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
    heldout_questions = [q for q in all_questions if q["split"] in ("dev", "test")]
    if args.limit is not None:
        heldout_questions = heldout_questions[: args.limit]

    ctx = BlindWarehouseContext(train_pool=train_pool, preds_dir=args.preds_dir, lang=args.lang)

    all_summaries = []
    for model_alias in args.models:
        for fw in args.frameworks:
            s = evaluate_blind_system(
                ctx,
                fw,
                model_alias,
                heldout_questions,
                preds_dir=args.preds_dir,
                workers=args.workers,
                eval_only=args.eval_only,
                models_config=args.models_config,
            )
            all_summaries.append(s)

    out_json = args.out_json or (args.preds_dir / "leaderboard_standard.json")
    out_md = args.out_md or (args.preds_dir / "leaderboard_standard.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(all_summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown_leaderboard(all_summaries, out_md)
    print(f"\nSaved Standard (Track L0) leaderboard to {out_md} and {out_json}")


if __name__ == "__main__":
    main()
