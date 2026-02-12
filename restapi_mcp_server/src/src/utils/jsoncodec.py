"""JSON encode/decode helpers for storing values in CSV and reading them back.

- encode_value_for_storage(value): Ensures complex values (dict/list/scalars/None)
  are serialized to JSON strings before persisting in CSV.
- decode_value_if_json(value): Attempts to parse JSON-like strings (object/array)
  back to Python objects when reading from CSV; returns original value otherwise.
"""
from __future__ import annotations
from typing import Any
import json
import re


def encode_value_for_storage(value: Any) -> str:
    """Encode a Python value for storage in CSV.

    - dict/list: JSON-encode
    - int/float/bool/None: JSON-encode
    - str and others: cast to str
    """
    try:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, (int, float, bool)) or value is None:
            return json.dumps(value, ensure_ascii=False)
        return str(value)
    except Exception:
        return str(value)


def decode_value_if_json(value: Any) -> Any:
    """Decode JSON-like content back to Python values, including scalars, and normalize nested structures.

    Behavior:
    - If value is a JSON object/array string, parse it and recursively normalize children.
    - If value is a JSON scalar string (true/false/null/number), parse into bool/None/number.
    - If value is a dict/list, recursively normalize string children that look like JSON scalars.
    - Otherwise return value unchanged.
    """

    def _coerce_scalar(s: str) -> Any:
        sl = s.strip()
        # Only attempt json.loads for JSON scalars: true/false/null or numbers
        if sl in ("true", "false", "null") or re.fullmatch(r"-?\d+(\.\d+)?([eE][+-]?\d+)?", sl):
            try:
                return json.loads(sl)
            except Exception:
                return s
        return s

    def _normalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _normalize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_normalize(v) for v in obj]
        if isinstance(obj, str):
            return _coerce_scalar(obj)
        return obj

    if isinstance(value, str):
        s = value.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                parsed = json.loads(s)
                return _normalize(parsed)
            except Exception:
                return value
        # Try scalar coercion (e.g., "true" -> True, "123" -> 123)
        return _coerce_scalar(s)

    if isinstance(value, (dict, list)):
        return _normalize(value)

    return value


__all__ = ["encode_value_for_storage", "decode_value_if_json"]
