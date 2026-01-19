from ..utils.logger import setup_logging
from ..models.restapiSchema import RestAPIIn, RestAPIOut
from ..constants import COMMON, RESTAPI
from .variablesInterpolation import listAllVariableByEnvironment, eval as interpolate_vars, upsertEnvironmentVariable
from ..utils.restapi import http_request
from .transactions import createTransaction, updateTransaction
from ..utils.jsoncodec import decode_value_if_json
from ..utils.bas64interpolation import encode_base64, decode_base64
from ..utils import jqinterpolation
from typing import Any, Dict, Optional, cast

import json, re

logger = setup_logging()

def _preview(value: Any, limit: int = 2000) -> str:
    try:
        text = json.dumps(value, default=str)
    except Exception:
        try:
            text = repr(value)
        except Exception:
            text = "<unrepresentable>"
    if len(text) > limit:
        return text[:limit] + "...[truncated]"
    return text

def _interpolate_obj(obj, env_rows):
    """
    Recursively interpolate strings in obj using environment variables.

    - If obj is a string, interpolate with interpolate_vars(expression=obj, data=env_rows)
    - If obj is a dict, recursively interpolate keys' values
    - If obj is a list, recursively interpolate items
    - Otherwise return obj as-is
    """
    if isinstance(obj, str):
        out = interpolate_vars(expression=obj, data=env_rows)
        if out != obj:
            logger.debug("Variable interpolation: %s -> %s", _preview(obj), _preview(out))
        return out
    if isinstance(obj, dict):
        return {k: _interpolate_obj(v, env_rows) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_interpolate_obj(v, env_rows) for v in obj]
    return obj

def _apply_transform(obj, transformer):
    """
    Recursively apply a transformer(str -> Any) to all string leaves in obj.
    """
    if isinstance(obj, str):
        return transformer(obj)
    if isinstance(obj, dict):
        return {k: _apply_transform(v, transformer) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_apply_transform(v, transformer) for v in obj]
    return obj

def apply_restapi_constants(obj):
    """
    Replace any string equal to a RESTAPI constant reference like "$RESPONSE_BODY"
    with the corresponding value from constants.RESTAPI. Traverses dicts/lists.
    """
    if isinstance(obj, str):
        s_strip = obj.strip()
        if s_strip.startswith("$") and len(s_strip) > 1:
            name = s_strip[1:]
            val = getattr(RESTAPI, name, obj)
            logger.debug("RESTAPI constant: %s -> %s", obj, _preview(val))
            return val
        return obj
    if isinstance(obj, dict):
        return {k: apply_restapi_constants(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [apply_restapi_constants(v) for v in obj]
    return obj

def apply_base64_transforms(obj):
    """
    Apply base64 encode/decode transforms across all string leaves.
    """
    return _apply_transform(obj, _transform_base64_string)

def apply_jq_transforms(obj):
    """
    Apply jq_expression('<filter>', <json-literal | $RESTAPI_CONST>) across all string leaves.
    """
    return _apply_transform(obj, _transform_jq_string)

def _transform_base64_string(s: str) -> Any:
    """
    Apply base64 encode/decode transforms if s matches the unified regex patterns.
    Assumes variable interpolation already occurred earlier in the pipeline.
    """
    s_strip = s.strip()

    # Base64 encode
    m = re.fullmatch(COMMON.BASE64_ENCODE_REGEX, s_strip)
    if m:
        groups = m.groups()
        content = next((g for g in groups if g is not None), "")
        content = content.strip()
        res = encode_base64(content)
        logger.debug("Base64 encode: %s -> %s", _preview(content), _preview(res))
        return res

    # Base64 decode
    m = re.fullmatch(COMMON.BASE64_DECODE_REGEX, s_strip)
    if m:
        groups = m.groups()
        b64_text = next((g for g in groups if g is not None), "")
        b64_text = b64_text.strip()
        res = decode_base64(b64_text)
        logger.debug("Base64 decode: %s -> %s", _preview(b64_text), _preview(res))
        return res

    return s

def _transform_jq_string(s: str) -> Any:
    """
    Apply jq_expression('<filter>', <json-literal | $RESTAPI_CONST>) if present.
    """
    s_strip = s.strip()
    m = re.fullmatch(COMMON.JQ_EXPRESSION_REGEX, s_strip)
    if not m:
        return s

    groups = m.groups()
    try:
        jq_filter = groups[1]
        data_src = groups[2].strip()
    except IndexError:
        # Fallback for older regex with 2 groups (filter, data)
        jq_filter = groups[0] if len(groups) > 0 else ""
        data_src = groups[1].strip() if len(groups) > 1 else ""

    # Resolve RESTAPI constants (e.g., $RESPONSE_BODY) in the data argument
    data_val = apply_restapi_constants(data_src)
    logger.debug("JQ before: filter=%r, data=%s", jq_filter, _preview(data_val))

    # If still a string, try to parse JSON literal or strip outer quotes
    if isinstance(data_val, str):
        try:
            if data_val and (data_val[0] in "{[\"'"):
                if (data_val[0] in "\"'" and data_val[-1] == data_val[0]):
                    data_val = data_val[1:-1]
                else:
                    data_val = json.loads(data_val)
        except Exception:
            pass

    _res = jqinterpolation.jqinterpolate(expression=jq_filter, json_input=data_val)
    logger.debug("JQ after: result=%s", _preview(_res))
    if isinstance(_res, list) and len(_res) == 1:
        return _res[0]
    return _res


def resolve_interpolations(obj, env_rows):
    """
    Iteratively resolve interpolations in the order:
      1) Variable interpolation ({{VAR}})
      2) RESTAPI constant references ($RESPONSE_BODY, etc.)
      3) Base64 transforms (encode/decode)
      4) JQ expression transforms
    """
    logger.debug("Resolve start: %s", _preview(obj))
    # 1) Variables
    var_pass = _interpolate_obj(obj, env_rows)
    logger.debug("After variables: %s", _preview(var_pass))
    # 2) RESTAPI constants (bare $NAME)
    const_pass = apply_restapi_constants(var_pass)
    logger.debug("After RESTAPI constants: %s", _preview(const_pass))
    # 3) Base64
    b64_pass = apply_base64_transforms(const_pass)
    logger.debug("After base64: %s", _preview(b64_pass))
    # 4) JQ
    jq_pass = apply_jq_transforms(b64_pass)
    logger.debug("After jq: %s", _preview(jq_pass))
    return jq_pass

def restapiCall(request: RestAPIIn):

    logger.info("Invoking RestAPI")
    logger.debug(f"method: {request.method}")
    logger.debug(f"url: {request.url}")
    logger.debug(f"session: {request.session}")
    logger.debug(f"environment: {request.environment}")
    logger.debug(f"action: {request.action}")
    logger.debug(f"request_headers: {request.request_headers}")
    logger.debug(f"request_body: {request.request_body}")
    logger.debug(f"post_script: {request.post_script}")

    # Loading environment variables
    environment_details = listAllVariableByEnvironment(request.environment)

    # Interpolate URL, headers, and body using environment variables (safe; no Python eval)
    try:
        # Resolve interpolations iteratively: variables -> RESTAPI constants -> base64 -> jq
        url_resolved = resolve_interpolations(request.url, environment_details)
        if not isinstance(url_resolved, str):
            url_resolved = str(url_resolved)
        request.url = url_resolved
        logger.debug(f"interpolated url: {request.url}")

        headers_resolved = resolve_interpolations(request.request_headers or {}, environment_details)
        if not isinstance(headers_resolved, dict):
            logger.info("Resolved headers not a dict; defaulting to empty dict")
            headers_resolved = {}
        request.request_headers = cast(Dict[str, Any], headers_resolved)
        logger.debug(f"resolved request_headers: {request.request_headers}")

        raw_body = getattr(request, "request_body", None)

        parsed = None
        # If body is a single variable reference like {{VAR}}, use native value from env store
        if isinstance(raw_body, str):
            mvar = re.fullmatch(COMMON.BRACED_VARIABLE_REGEX, raw_body.strip())
            if mvar and (mvar.lastindex or 0) >= 1:
                var_name = mvar.group(1)
                var_row = next((r for r in (environment_details or []) if isinstance(r, dict) and r.get("variable") == var_name), None)
                if var_row is not None:
                    val = var_row.get("value")
                    # Keep dict/list as-is; decode strings that look like JSON/scalars
                    parsed = val if isinstance(val, (dict, list)) else decode_value_if_json(val)

        if parsed is None:
            body_resolved = resolve_interpolations(raw_body, environment_details)
            # If interpolation yields a string (e.g., from an env variable), attempt JSON/scalar decode
            if isinstance(body_resolved, str):
                parsed = decode_value_if_json(body_resolved)
            else:
                parsed = body_resolved

        # Allow dict/list/str/bytes/bytearray/None; coerce exotic types to string
        if parsed is not None and not isinstance(parsed, (dict, list, str, bytes, bytearray)):
            parsed = str(parsed)

        request.request_body = parsed
        logger.debug(f"resolved request_body: {request.request_body}")

    except Exception as e:
        logger.error("Failed to interpolate request components: %s", e)
        raise

    # Create transaction record and perform the HTTP request via utility switch
    # Coerce headers to str->str mapping for httpx
    send_headers: Dict[str, str] = {str(k): str(v) for k, v in (request.request_headers or {}).items()}
    request_snapshot = {"url": request.url, "headers": send_headers, "body": request.request_body}

    # Populate RESTAPI request constants and snapshot previous response
    RESTAPI.PREVIOUS_RESPONSE_BODY = getattr(RESTAPI, "RESPONSE_BODY", None)
    RESTAPI.PREVIOUS_HTTP_STATUS_CODE = getattr(RESTAPI, "RESPONSE_HTTP_STATUS_CODE", None)
    RESTAPI.REQUEST_HEADERS = send_headers
    RESTAPI.REQUEST_BODY = request.request_body

    txn_id: Optional[str] = None
    try:
        created_txn = createTransaction(
            session=request.session,
            action=request.action,
            http_method=request.method,
            request_snapshot=request_snapshot,
        )
        txn_id = created_txn["transactionId"]

        response = http_request(
            method=request.method,
            url=request.url,
            headers=send_headers,
            body=request.request_body,
        )

        status_code = int(response.get("status", 0))
        final_status = "SUCCESS" if 200 <= status_code < 400 else "FAILED"
        if txn_id is None:
            raise RuntimeError("Transaction ID not set")
        updateTransaction(transactionId=txn_id, response_snapshot=response, status=final_status)
    except Exception as e:
        # Attempt to update transaction with error, then re-raise
        try:
            if txn_id is not None:
                updateTransaction(transactionId=txn_id, response_snapshot={"error": str(e)}, status="ERROR")
        except Exception as upd_exc:
            logger.error("Failed to update transaction on error: %s", upd_exc)
        logger.error("HTTP request failed: %s", e)
        # Populate RESTAPI response constants with error info
        RESTAPI.RESPONSE_HTTP_STATUS_CODE = None
        RESTAPI.RESPONSE_HEADERS = {}
        RESTAPI.RESPONSE_BODY = {"error": str(e)}
        raise

    logger.info("RestAPI Call Executed Successfully")
    # Coerce header values like "true"/"null"/numbers to native types for response consistency
    resp_headers: Dict[str, Any] = {k: decode_value_if_json(v) for k, v in (response.get("headers", {}) or {}).items()}

    # Populate RESTAPI response constants
    RESTAPI.RESPONSE_HTTP_STATUS_CODE = response["status"]
    RESTAPI.RESPONSE_HEADERS = resp_headers
    RESTAPI.RESPONSE_BODY = response["body"]

    # Execute post_script only on SUCCESS
    if isinstance(response["status"], int) and 200 <= response["status"] < 400:
        post_script = getattr(request, "post_script", None)
        if isinstance(post_script, dict) and post_script:
            outputs: Dict[str, Any] = {}
            for key, expr in post_script.items():
                try:
                    # Evaluate expression with iterative interpolation (vars -> RESTAPI consts -> base64 -> jq)
                    value = resolve_interpolations(expr, environment_details)
                    # Extract variable name from {{NEW_VARIABLE}} or use key as-is (robust to missing capture groups)
                    mvar = re.fullmatch(COMMON.BRACED_VARIABLE_REGEX, str(key))
                    if mvar and (mvar.lastindex or 0) >= 1:
                        var_name = mvar.group(1)
                    else:
                        var_name = str(key)
                    outputs[var_name] = value
                except Exception as exc:
                    logger.error("post_script evaluation failed for key %r: %s", key, exc)
            
            # Upsert evaluated variables into the environment
            for var_name, out_val in outputs.items():
                try:
                    upsertEnvironmentVariable(request.environment, var_name, out_val)
                except Exception as exc:
                    logger.error("Failed to upsert post_script variable %r: %s", var_name, exc)

    return RestAPIOut(
        response_status=response["status"],
        response_headers=resp_headers,
        response_body=response["body"],
    )
