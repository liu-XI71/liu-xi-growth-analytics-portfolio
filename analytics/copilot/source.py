from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FACTS_PATH = PROJECT_ROOT / "data" / "case_facts" / "source_facts.json"


def load_source_facts(path: Path | None = None) -> dict[str, Any]:
    source = path or SOURCE_FACTS_PATH
    payload = json.loads(source.read_text(encoding="utf-8"))
    required = {"snapshot_id", "as_of_date", "data_boundary", "referral", "retention"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Missing source-fact sections: {sorted(missing)}")
    return payload
