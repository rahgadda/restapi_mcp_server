from collections.abc import Mapping
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, model_validator

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

        Canonical `request_*` keys always take precedence when both are present.
        """
        if not isinstance(data, Mapping):
            return data

        payload = dict(data)
        aliases = {
            "headers": "request_headers",
            "body": "request_body",
        }

        for legacy_key, canonical_key in aliases.items():
            if canonical_key not in payload and legacy_key in payload:
                payload[canonical_key] = payload[legacy_key]

        return payload

class RestAPIOut(BaseModel):
    response_status: int = Field(..., description="HTTP status code from the downstream request")
    response_headers: Dict[str, Any] = Field(..., description="Headers returned by the downstream service")
    response_body: Any = Field(..., description="Parsed JSON body if available; otherwise raw text")
