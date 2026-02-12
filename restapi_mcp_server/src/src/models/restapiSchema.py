from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

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

class RestAPIOut(BaseModel):
    response_status: int = Field(..., description="HTTP status code from the downstream request")
    response_headers: Dict[str, Any] = Field(..., description="Headers returned by the downstream service")
    response_body: Any = Field(..., description="Parsed JSON body if available; otherwise raw text")
