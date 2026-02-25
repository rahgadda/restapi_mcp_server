"""
REST API orchestration routes.

Endpoints:
- POST /restapi/call
    Execute an HTTP call after interpolating variables, creating a transaction
    before the call, and updating it after the call completes.
"""
from fastapi import APIRouter, HTTPException
from fastapi import Request
from ....models.restapiSchema import RestAPIIn, RestAPIOut, RestAPIFileIn
from ....services.restapi import restapiCall
from typing import Any, Dict
import json
from starlette.datastructures import UploadFile

# Router for REST API orchestration
router = APIRouter(prefix="/restapi", tags=["REST API"])


def _parse_json_text(raw: Any) -> Any:
    if raw is None:
        return None
    if not isinstance(raw, str):
        return raw
    text = raw.strip()
    if text == "":
        return ""
    return json.loads(text)


def _add_form_value(form_data: Dict[str, Any], key: str, value: Any) -> None:
    if key not in form_data:
        form_data[key] = value
        return
    existing = form_data[key]
    if isinstance(existing, list):
        existing.append(value)
    else:
        form_data[key] = [existing, value]


async def _build_payload_from_multipart(request: Request) -> RestAPIIn:
    form = await request.form()

    known_keys = {
        "method",
        "url",
        "session",
        "environment",
        "action",
        "request_headers",
        "request_body",
        "request_form_data",
        "post_script",
    }

    payload: Dict[str, Any] = {}
    inferred_form_data: Dict[str, Any] = {}
    files: list[RestAPIFileIn] = []

    for key, value in form.multi_items():
        # Uploaded files become multipart parts for downstream call
        if isinstance(value, UploadFile):
            file_bytes = await value.read()
            files.append(
                RestAPIFileIn(
                    field_name=key,
                    filename=value.filename or "upload.bin",
                    content_type=getattr(value, "content_type", None),
                    content=file_bytes,
                )
            )
            continue

        if key in known_keys:
            payload[key] = value
        else:
            _add_form_value(inferred_form_data, key, value)

    for json_key in ("request_headers", "request_form_data", "post_script"):
        if json_key in payload:
            payload[json_key] = _parse_json_text(payload[json_key])

    if "request_body" in payload:
        raw_body = payload["request_body"]
        if isinstance(raw_body, str):
            stripped = raw_body.strip()
            if stripped and stripped[0] in "{[\"'tfn-0123456789":
                try:
                    payload["request_body"] = _parse_json_text(raw_body)
                except Exception:
                    payload["request_body"] = raw_body

    if inferred_form_data:
        explicit_form_data = payload.get("request_form_data")
        if isinstance(explicit_form_data, dict):
            merged = dict(inferred_form_data)
            merged.update(explicit_form_data)
            payload["request_form_data"] = merged
        elif explicit_form_data is None:
            payload["request_form_data"] = inferred_form_data

    if files:
        payload["request_files"] = files

    return RestAPIIn.model_validate(payload)

@router.post(
    "/call",
    response_model=RestAPIOut,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["method", "url", "session", "environment", "action"],
                        "properties": {
                            "method": {
                                "type": "string",
                                "description": "HTTP method: GET, POST, PUT, PATCH, DELETE",
                            },
                            "url": {"type": "string", "description": "Target URL"},
                            "session": {"type": "string", "description": "Session identifier"},
                            "environment": {"type": "string", "description": "Environment name"},
                            "action": {
                                "type": "string",
                                "description": "Logical action name for transaction logging",
                            },
                            "request_headers": {
                                "type": "object",
                                "description": "Optional outgoing headers",
                                "additionalProperties": True,
                            },
                            "request_body": {
                                "description": "Optional downstream request body",
                                "nullable": True,
                            },
                            "request_form_data": {
                                "type": "object",
                                "description": "Optional form fields for downstream form/multipart request",
                                "additionalProperties": True,
                            },
                            "request_files": {
                                "type": "array",
                                "description": "Optional multipart file entries sent to downstream API",
                                "items": {
                                    "type": "object",
                                    "required": ["field_name", "filename", "content"],
                                    "properties": {
                                        "field_name": {
                                            "type": "string",
                                            "description": "Multipart form field name for the file",
                                        },
                                        "filename": {
                                            "type": "string",
                                            "description": "File name sent to downstream API",
                                        },
                                        "content_type": {
                                            "type": "string",
                                            "description": "Optional MIME type",
                                        },
                                        "content": {
                                            "type": "string",
                                            "format": "byte",
                                            "description": "Base64-encoded file bytes",
                                        },
                                    },
                                },
                            },
                            "post_script": {
                                "type": "object",
                                "description": "Template object evaluated after successful downstream call",
                                "additionalProperties": True,
                            },
                        },
                        "additionalProperties": True,
                    },
                },
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["method", "url", "session", "environment", "action"],
                        "properties": {
                            "method": {"type": "string", "description": "HTTP method"},
                            "url": {"type": "string", "description": "Target URL"},
                            "session": {"type": "string", "description": "Session identifier"},
                            "environment": {"type": "string", "description": "Environment name"},
                            "action": {"type": "string", "description": "Action name"},
                            "request_headers": {
                                "type": "string",
                                "description": "JSON string for downstream headers (e.g. {\"appId\":\"CMNCORE\"})",
                            },
                            "request_body": {
                                "type": "string",
                                "description": "Optional downstream request body (plain text or JSON string)",
                            },
                            "request_form_data": {
                                "type": "string",
                                "description": "Optional JSON string map for downstream form fields",
                            },
                            "Content-Type": {
                                "type": "string",
                                "description": "Optional passthrough form field (for example form-data)",
                            },
                            "post_script": {
                                "type": "string",
                                "description": "Optional JSON string for post_script map",
                            },
                            "file": {
                                "type": "string",
                                "format": "binary",
                                "description": "Primary file input for curl --form 'file=@/path/to/file.csv'",
                            },
                            "request_files": {
                                "type": "array",
                                "items": {"type": "string", "format": "binary"},
                                "description": "Alternative multi-file input; any uploaded file field is accepted and forwarded",
                            },
                        },
                        "additionalProperties": True,
                    },
                },
            },
        }
    },
)
async def restapi_call(request: Request) -> RestAPIOut:
    """
    Execute an HTTP call using the provided payload.

    Behavior:
    - Interpolates variables in URL/headers/body based on the provided environment
    - Creates a transaction (PENDING) prior to the HTTP call
    - Performs the HTTP call
    - Updates the transaction with response and final status (SUCCESS/FAILED/ERROR)

    Returns:
        RestAPIOut: status, response headers, and response body from downstream.
    """
    try:
        content_type = request.headers.get("content-type", "").lower()
        if "multipart/form-data" in content_type:
            payload = await _build_payload_from_multipart(request)
        else:
            body = await request.json()
            payload = RestAPIIn.model_validate(body)
        return restapiCall(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
