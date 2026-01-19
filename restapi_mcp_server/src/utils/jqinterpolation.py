from __future__ import annotations

import json
import jq
from typing import Any, List
from .logger import setup_logging

logger = setup_logging()

__all__ = ["jqinterpolate"]


def jqinterpolate(expression: str, json_input: Any) -> List[Any]:
    """
    Evaluate a jq expression against JSON (text or Python object) and return all results.

    Parameters:
        expression (str): A valid jq program/filter, e.g. ".foo", "map(.a)",
                          or ".items[] | .name".
        json_input (Any): JSON document as a string/bytes or a Python object
                          (dict, list, str, int, float, bool, or None).

    Returns:
        List[Any]: A list of results produced by jq's `.all()` for the given input.
                   Items can be any JSON-compatible type (dict, list, str, int,
                   float, bool, or None).

    Raises:
        json.JSONDecodeError: If `json_input` is not valid JSON text.
        jq.jq.CompileError: If `expression` is not a valid jq program.

    Notes:
        - The JSON is parsed using json.loads.
        - The jq expression is compiled per call and then evaluated with `.all()`,
          which collects all outputs of the filter into a Python list.
    """
    logger.debug("jqinterpolate called: expression=%s", expression)
    if isinstance(json_input, (str, bytes, bytearray)):
        logger.debug("jqinterpolate input text length: %d", len(json_input))
    else:
        logger.debug("jqinterpolate input type: %s", type(json_input).__name__)

    # Accept either JSON text (str/bytes/bytearray) or a Python object (dict/list/etc.)
    if isinstance(json_input, (str, bytes, bytearray)):
        text = json_input.decode("utf-8") if isinstance(json_input, (bytes, bytearray)) else json_input
        # Try to parse as JSON; if it is not valid JSON, pass the raw string to jq
        try:
            json_data = json.loads(text)
        except Exception as exc:
            logger.debug("jqinterpolate: non-JSON text input, passing as string: %s", exc)
            json_data = text
    else:
        json_data = json_input

    try:
        # Compile jq expression into a reusable filter
        jq_filter = jq.compile(expression)
    except Exception as exc:
        logger.error("jqinterpolate: failed to compile jq expression: %s", exc)
        raise

    try:
        # Run the filter and collect all results into a list
        result = jq_filter.input(json_data).all()
    except Exception as exc:
        logger.error("jqinterpolate: evaluation failed: %s", exc)
        raise
    
    logger.debug("jqinterpolate: produced %d result(s)", len(result))
    return result
