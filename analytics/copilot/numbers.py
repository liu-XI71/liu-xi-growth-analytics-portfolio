from __future__ import annotations

import math
from collections.abc import Mapping
from numbers import Integral, Real
from typing import Any


def normalize_public_numbers(value: Any, *, field_name: str = "") -> Any:
    """Remove floating-point noise while preserving useful statistical precision."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, Real):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"Non-finite public number in field: {field_name or '<root>'}")
        if "p_value" in field_name:
            return float(f"{number:.6g}")
        if abs(number) < 1e-12:
            return 0.0
        if field_name.endswith("_pct"):
            return round(number, 1)
        if field_name.endswith("_pp") or "percentage_points" in field_name:
            return round(number, 3)
        if field_name in {"z_stat", "statistic"}:
            return round(number, 4)
        return float(f"{number:.8g}")
    if isinstance(value, Mapping):
        return {
            key: normalize_public_numbers(item, field_name=str(key)) for key, item in value.items()
        }
    if isinstance(value, tuple):
        return [normalize_public_numbers(item, field_name=field_name) for item in value]
    if isinstance(value, list):
        return [normalize_public_numbers(item, field_name=field_name) for item in value]
    return value
