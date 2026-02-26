from collections.abc import Mapping
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import base64


class RestAPIFileIn(BaseModel):
    field_name: str = Field(..., description="Multipart form field name for the file")
    filename: str = Field(..., description="File name sent to the downstream API")
    content_type: Optional[str] = Field(
        None,
        description="Optional MIME type (for example application/pdf, image/png)",
    )
    content: bytes = Field(..., description="Raw file bytes")

    @field_validator("content", mode="before")
    @classmethod
    def decode_base64_content(cls, value: Any) -> bytes:
        """
        Accept JSON base64 string input for file content and decode to bytes.

        Supported inputs:
        - bytes / bytearray: returned as-is
        - str: treated as base64 and decoded (whitespace ignored)
        """
        if isinstance(value, bytes):
            return value
        if isinstance(value, bytearray):
            return bytes(value)
        if isinstance(value, str):
            cleaned = "".join(value.strip().split())
            if cleaned == "":
                return b""
            try:
                return base64.b64decode(cleaned, validate=True)
            except Exception as exc:
                raise ValueError("request_files[].content must be valid base64 string") from exc
        raise ValueError("request_files[].content must be base64 string or bytes")

class RestAPIIn(BaseModel):
    method: str = Field(..., description="HTTP method: GET, POST, PUT, PATCH, DELETE")
    url: str = Field(..., description="Target URL")
    session: str = Field(..., description="Session identifier")
    environment: str = Field(..., description="Environment name")
    action: str = Field(..., description="Logical action name for transaction logging")
    request_headers: Optional[Dict[str, Any]] = Field(
        None,
        description="Headers to include with the outgoing HTTP request (name:value map)",
    )
    request_body: Optional[Any] = Field(
        None,
        description="Optional JSON body for the downstream request",
    )
    request_form_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional form fields for downstream form/multipart requests",
    )
    request_files: Optional[list[RestAPIFileIn]] = Field(
        None,
        description="Optional multipart file parts for downstream requests",
    )
    post_script: Optional[Dict[str, Any]] = Field(
        None,
        description="Template object evaluated after the HTTP call; can read response fields and update env/envstore",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_payload_keys(cls, data: Any) -> Any:
        """
        Backward compatibility for payloads that use older key names.

        Supported aliases:
        - headers -> request_headers
        - body -> request_body
        - form_data -> request_form_data
        - files -> request_files

        Canonical `request_*` keys always take precedence when both are present.
        """
        if not isinstance(data, Mapping):
            return data

        payload = dict(data)
        aliases = {
            "headers": "request_headers",
            "body": "request_body",
            "form_data": "request_form_data",
            "files": "request_files",
        }

        for legacy_key, canonical_key in aliases.items():
            if canonical_key not in payload and legacy_key in payload:
                payload[canonical_key] = payload[legacy_key]

        return payload

class RestAPIOut(BaseModel):
    response_status: int = Field(..., description="HTTP status code from the downstream request")
    response_headers: Dict[str, Any] = Field(..., description="Headers returned by the downstream service")
    response_body: Any = Field(..., description="Parsed JSON body if available; otherwise raw text")
