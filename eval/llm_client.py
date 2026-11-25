#!/usr/bin/env python3
"""Standard OpenAI-Compatible LLM client and SQL extractor for BankRegBench.

Credentials are NEVER hardcoded. Endpoints are resolved in order:
  1. Explicit overrides (`api_base`, `api_key`, `model_name`).
  2. Environment variables (`OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL`,
     or `BANKREGBENCH_API_BASE` / `BANKREGBENCH_API_KEY` / `BANKREGBENCH_MODEL`).
  3. JSON config file (`configs/models.json` or path passed via `--models-config`).
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODELS_CONFIG = ROOT / "configs" / "models.json"


def load_model_endpoint(
    model_alias: str,
    config_path: Path | None = None,
    api_base: str | None = None,
    api_key: str | None = None,
    model_name: str | None = None,
) -> dict[str, Any]:
    """Load an OpenAI-Compatible endpoint without hardcoding any credentials."""
    # 1. Explicit overrides
    if api_base and api_key:
        return {
            "alias": model_alias,
            "base_url": api_base.rstrip("/"),
            "api_key": api_key,
            "model": model_name or model_alias,
            "extra_body": {},
        }

    # 2. Config file lookup (preferred when running a multi-model matrix)
    cfg_file = config_path or DEFAULT_MODELS_CONFIG
    if cfg_file.exists():
        cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
        if model_alias in cfg:
            entry = cfg[model_alias]
            resolved_base = (api_base or entry.get("base_url") or os.environ.get("OPENAI_BASE_URL", "")).rstrip("/")
            key_env = entry.get("api_key_env", "OPENAI_API_KEY")
            resolved_key = api_key or entry.get("api_key") or os.environ.get(key_env, "")
            if not resolved_base or not resolved_key:
                raise RuntimeError(
                    f"Model '{model_alias}' in {cfg_file} is missing base_url or API key "
                    f"(expected env var '{key_env}')."
                )
            return {
                "alias": model_alias,
                "base_url": resolved_base,
                "api_key": resolved_key,
                "model": model_name or entry.get("model", model_alias),
                "extra_body": entry.get("extra_body", {}),
            }

    # 3. Environment variable fallback for single-model runs
    env_base = os.environ.get("OPENAI_BASE_URL") or os.environ.get("BANKREGBENCH_API_BASE")
    env_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("BANKREGBENCH_API_KEY")
    env_model = os.environ.get("OPENAI_MODEL") or os.environ.get("BANKREGBENCH_MODEL")
    env_extra_raw = os.environ.get("OPENAI_EXTRA_BODY") or os.environ.get("BANKREGBENCH_EXTRA_BODY")
    env_extra = json.loads(env_extra_raw) if env_extra_raw else {}
    if env_base and env_key:
        return {
            "alias": model_alias,
            "base_url": env_base.rstrip("/"),
            "api_key": env_key,
            "model": model_name or env_model or model_alias,
            "extra_body": env_extra,
        }

    raise RuntimeError(
        f"No API configuration found for model '{model_alias}'. "
        f"Set OPENAI_BASE_URL & OPENAI_API_KEY environment variables, "
        f"or create {DEFAULT_MODELS_CONFIG} from configs/models.example.json."
    )


def call_llm(
    endpoint: dict[str, Any],
    messages: list[dict[str, str]],
    temperature: float = 0.0,
    max_tokens: int = 1200,
    timeout: int = 75,
    max_retries: int = 5,
) -> str:
    """Call an OpenAI-Compatible `/chat/completions` endpoint using Python stdlib only."""
    payload: dict[str, Any] = {
        "model": endpoint["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        **endpoint.get("extra_body", {}),
    }
    url = f"{endpoint['base_url'].rstrip('/')}/chat/completions"
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {endpoint['api_key']}",
                    "User-Agent": "BankRegBench-Eval/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                msg = data["choices"][0]["message"]
                content = (msg.get("content") or "").strip()
                if not content and msg.get("reasoning_content"):
                    content = msg["reasoning_content"].strip()
                return content
        except Exception as exc:
            if attempt == max_retries - 1:
                return f"LLM_ERROR: {exc}"
            time.sleep(3.0 * (attempt + 1))
    return "LLM_ERROR"


def _first_sql_statement(sql: str) -> str:
    """Split on the first top-level semicolon outside single/double quotes."""
    in_sq = False
    in_dq = False
    for i, ch in enumerate(sql):
        if ch == "'" and not in_dq:
            in_sq = not in_sq
        elif ch == '"' and not in_sq:
            in_dq = not in_dq
        elif ch == ";" and not in_sq and not in_dq:
            return sql[: i + 1].strip()
    return sql.strip()


def extract_sql(text: str) -> str:
    """Extract the first executable SQL SELECT/WITH statement from model output."""
    if not text:
        return "SELECT 1 WHERE 0;"
    blocks = re.findall(r"```(?:sql|sqlite)?\s*(.*?)```", text, flags=re.I | re.S)
    if blocks:
        for b in reversed(blocks):
            if re.search(r"\b(?:SELECT|WITH)\b", b, re.I):
                m_inner = re.search(r"((?:WITH\b|SELECT\b).*)", b.strip(), flags=re.I | re.S)
                return _first_sql_statement(m_inner.group(1) if m_inner else b.strip())
    m = re.search(r"((?:WITH\b|SELECT\b).*)", text, flags=re.I | re.S)
    if m:
        return _first_sql_statement(m.group(1).strip())
    return text.strip()
