"""Pure Python stdlib (`sqlite3`) fallback engine for M-Schema.

Builds the exact same `MSchema` representation as `schema_engine.py` without requiring
`sqlalchemy` or `llama-index-core`, enabling zero-dependency execution on SQLite warehouses.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from m_schema import MSchema


class SQLiteSchemaEngine:
    """Lightweight SQLite-only M-Schema builder using Python stdlib `sqlite3`."""

    def __init__(
        self,
        db_path: str | Path,
        db_name: str = "bankreg_main",
        schema: Optional[str] = "main",
        sample_rows: int = 3,
    ) -> None:
        self._db_path = Path(db_path)
        self._db_name = db_name
        self._schema = schema or "main"
        self._sample_rows = sample_rows
        self._mschema = MSchema(db_id=db_name, schema=self._schema)
        self._init_mschema()

    @property
    def mschema(self) -> MSchema:
        return self._mschema

    def _init_mschema(self) -> None:
        conn = sqlite3.connect(f"file:{self._db_path}?mode=ro", uri=True)
        conn.execute("PRAGMA query_only = ON;")
        try:
            tables = [
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
                ).fetchall()
            ]
            for table_name in tables:
                full_tname = f"{self._schema}.{table_name}" if self._schema else table_name
                self._mschema.add_table(full_tname, fields={}, comment="")

                for fk in conn.execute(f'PRAGMA foreign_key_list("{table_name}")').fetchall():
                    # fk tuple: (id, seq, ref_table, from_col, to_col, on_update, on_delete, match)
                    ref_table = fk[2]
                    from_col = fk[3]
                    to_col = fk[4]
                    ref_full = f"{self._schema}.{ref_table}" if self._schema else ref_table
                    self._mschema.add_foreign_key(full_tname, from_col, self._schema, ref_full, to_col)

                for col in conn.execute(f'PRAGMA table_info("{table_name}")').fetchall():
                    # col tuple: (cid, name, type, notnull, dflt_value, pk)
                    cname = col[1]
                    ctype = (col[2] or "TEXT").upper()
                    nullable = not bool(col[3])
                    default = col[4]
                    pk = bool(col[5])
                    examples = [
                        r[0]
                        for r in conn.execute(
                            f'SELECT DISTINCT "{cname}" FROM "{table_name}" '
                            f'WHERE "{cname}" IS NOT NULL LIMIT {int(self._sample_rows)}'
                        ).fetchall()
                    ]
                    self._mschema.add_field(
                        full_tname,
                        cname,
                        field_type=ctype,
                        primary_key=pk,
                        nullable=nullable,
                        default=default,
                        autoincrement=False,
                        comment="",
                        examples=examples,
                    )
        finally:
            conn.close()
