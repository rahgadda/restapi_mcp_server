from __future__ import annotations
from .logger import setup_logging
from typing import Any, Dict, Optional, Union
import httpx
import time
from ..constants import COMMON

logger = setup_logging()
DEFAULT_HTTP_TIMEOUT = COMMON.DEFAULT_HTTP_TIMEOUT

def _redact_headers(headers: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    Return a copy of headers with sensitive values redacted for logging.
    """
    if headers is None:
        return None
    sensitive = {
        "authorization",
        "proxy-authorization",
        "x-api-key",
        "x-auth-token",
        "x-access-token",
        "cookie",
        "set-cookie",
    }
    redacted: Dict[str, str] = {}
    for k, v in headers.items():
        redacted[k] = "<redacted>" if k.lower() in sensitive else v
    return redacted

def _preview_body(body: Any | None, limit: int = 512) -> str:
    """
    Create a safe, truncated preview string for request/response bodies.
    """
    if body is None:
        return "None"
    if isinstance(body, (bytes, bytearray)):
        return f"<bytes {len(body)} bytes>"
    try:
        text = body if isinstance(body, str) else repr(body)
    except Exception:
        text = "<unrepresentable body>"
    return text

def _build_send_kwargs(body: Any | None) -> Dict[str, Any]:
    """
    Build keyword arguments for httpx.Client.request() based on the provided body.

    - dict/list -> send as JSON (json=...)
    - str/bytes/bytearray -> send as raw content (content=...)
    - None -> no body is sent
    - any other type -> converted to string and sent as raw content
    """
    if body is None:
        return {}
    if isinstance(body, (dict, list)):
        return {"json": body}
    if isinstance(body, (str, bytes, bytearray)):
        return {"content": body}
    # Fallback: send string representation
    return {"content": str(body)}

def _format_response(response: httpx.Response) -> Dict[str, Any]:
    """
    Convert httpx.Response into a simple, uniform dictionary.
    Attempts to decode JSON; falls back to response text if not JSON.
    """
    # httpx.Headers is a case-insensitive mapping; convert to a plain dict
    headers: Dict[str, str] = {k: v for k, v in response.headers.items()}

    # Try to parse JSON; otherwise return text content
    try:
        body: Any = response.json()
    except (ValueError, httpx.DecodingError):
        body = response.text

    return {
        "status": response.status_code,
        "headers": headers,
        "body": body,
    }

def _request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Any | None = None,
    timeout: Union[float, httpx.Timeout] = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    """
    Internal helper to perform an HTTP request and return a normalized response dict.
    """
    send_kwargs = _build_send_kwargs(body)
    method_upper = method.upper()
    start_ts = time.monotonic()

    # Log request start
    logger.debug("Request method: %s", method_upper)
    logger.debug("Request url: %s",url)
                
    if headers:
        logger.debug("Request headers: %s", _redact_headers(headers))
    if body is not None:
        logger.debug("Request body: %s", _preview_body(body))

    try:
        # Use a short-lived client for a single request.
        # If you need connection pooling across many calls, consider sharing a Client.
        with httpx.Client(timeout=timeout) as client:
            response = client.request(method=method_upper, url=url, headers=headers, **send_kwargs)

        elapsed_ms = (time.monotonic() - start_ts) * 1000.0
        status_code = response.status_code

        # Log status
        logger.debug("Request status: %d",status_code)
        logger.debug("Request elapsed_ms: (%.1f ms)",elapsed_ms)
        logger.debug("Response headers: %s", {k: v for k, v in response.headers.items()})
        
        # Log a safe, truncated preview of the response body
        try:
            preview = response.text
        except Exception:
            preview = "<unavailable>"
        if preview is not None:
            logger.debug("Response body: %s", preview)

        return _format_response(response)

    except httpx.RequestError as exc:
        elapsed_ms = (time.monotonic() - start_ts) * 1000.0
        logger.error("HTTP %s %s failed after %.1f ms: %s", method_upper, url, elapsed_ms, str(exc))
        logger.exception("HTTP request error")
        raise

def http_get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Any | None = None,
    timeout: Union[float, httpx.Timeout] = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    """
    Perform an HTTP GET request.

    Although GET typically does not include a body, this utility accepts a body if provided.
    """
    return _request("GET", url, headers=headers, body=body, timeout=timeout)

def http_post(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Any | None = None,
    timeout: Union[float, httpx.Timeout] = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    """
    Perform an HTTP POST request.
    """
    return _request("POST", url, headers=headers, body=body, timeout=timeout)

def http_put(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Any | None = None,
    timeout: Union[float, httpx.Timeout] = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    """
    Perform an HTTP PUT request.
    """
    return _request("PUT", url, headers=headers, body=body, timeout=timeout)

def http_delete(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Any | None = None,
    timeout: Union[float, httpx.Timeout] = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    """
    Perform an HTTP DELETE request.

    Although DELETE typically does not include a body, this utility accepts a body if provided.
    """
    return _request("DELETE", url, headers=headers, body=body, timeout=timeout)

def http_patch(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Any | None = None,
    timeout: Union[float, httpx.Timeout] = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    """
    Perform an HTTP PATCH request.
    """
    return _request("PATCH", url, headers=headers, body=body, timeout=timeout)

def http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Any | None = None,
    timeout: Union[float, httpx.Timeout] = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    """
    Perform an HTTP request using a match/case switch on the method.

    Supported methods: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS.
    Falls back to _request for HEAD/OPTIONS. Raises ValueError for unsupported methods.
    """
    method_upper = method.upper()
    match method_upper:
        case "GET":
            return http_get(url, headers=headers, body=body, timeout=timeout)
        case "POST":
            return http_post(url, headers=headers, body=body, timeout=timeout)
        case "PUT":
            return http_put(url, headers=headers, body=body, timeout=timeout)
        case "PATCH":
            return http_patch(url, headers=headers, body=body, timeout=timeout)
        case "DELETE":
            return http_delete(url, headers=headers, body=body, timeout=timeout)
        case "HEAD" | "OPTIONS":
            return _request(method_upper, url, headers=headers, body=body, timeout=timeout)
        case _:
            logger.error("Unsupported HTTP method: %s", method)
            raise ValueError(f"Unsupported HTTP method: {method}")

__all__ = [
    "http_get",
    "http_post",
    "http_put",
    "http_delete",
    "http_patch",
    "http_request",
]
