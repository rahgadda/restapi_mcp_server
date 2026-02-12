from __future__ import annotations
import re
from typing import Any, Dict, List
from .logger import setup_logging
from ..constants import COMMON

logger = setup_logging()

# Matches any content between {{ and }} (non-greedy)
_PLACEHOLDER_RE = re.compile(COMMON.INTERPOLATION_REGEX)

def interpolate(expression: str, variables_groups: List[Dict[str, Any]]) -> str:
    """
    Interpolate an expression by replacing {{variable}} placeholders.

    Args:
        expression: A string that may contain one or more placeholders like {{var}}.
        variables: A mapping of variable names to values. Values are converted to str.
                   If a value is None, it is replaced with an empty string.

    Behavior:
        - Any content between {{ and }} is treated as the variable name; surrounding whitespace is ignored.
        - Whitespace inside the braces is ignored, e.g. {{  var  }} is valid.
        - Unknown/missing variables raise a KeyError.
        - Interpolation is a single pass (results are not recursively re-interpolated).

    Returns:
        The interpolated string with placeholders replaced.
    """
    if not expression:
        return expression

    # Merge a list of variable dicts into a single mapping
    merged: Dict[str, Any] = {}
    for item in (variables_groups or []):
        if isinstance(item, dict):
            merged.update(item)

    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in merged:
            value = merged[name]
            rendered = "" if value is None else str(value)
            logger.debug("Interpolating variable '%s' -> %r", name, rendered)
            return rendered
        logger.error("Interpolation variable '%s' not provided", name)
        raise KeyError(f"Interpolation variable '{name}' not provided")

    logger.debug("Interpolating expression: %s", expression)
    try:
        result = _PLACEHOLDER_RE.sub(_replace, expression)
    except Exception as exc:
        logger.error("Interpolation failed: %s", exc)
        raise
    
    logger.debug("Interpolated result: %s", result)
    return result


__all__ = ["interpolate"]
