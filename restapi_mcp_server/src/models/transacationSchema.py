from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, RootModel, ConfigDict

class TransactionItem(BaseModel):
    transactionId: str = Field(..., description="Unique identifier of the transaction")
    session: str = Field(..., description="Session identifier this transaction belongs to")
    action: str = Field(..., description="Logical action name grouping related requests")
    http_method: Optional[str] = Field(default=None, description="HTTP method used, if applicable")
    request: Optional[Any] = Field(default=None, description="Request snapshot or payload")
    response: Optional[Any] = Field(default=None, description="Response payload or error details")
    status: Optional[str] = Field(default=None, description="Current status of the transaction")
    creation_dt: str = Field(..., description="Creation timestamp in ISO format")
    last_updation_dt: str = Field(..., description="Last update timestamp in ISO format")

class GetAllTransactionsOut(RootModel[List[TransactionItem]]):
    model_config = ConfigDict(json_schema_extra={
        "example": [
            {
                "transactionId": "txn-123",
                "session": "7f4f8e1a-2b6c-4b6a-9b7d-9f3a1d2c4e5f",
                "action": "user_login",
                "http_method": "POST",
                "request": {"url": "/api/v001/auth/login", "body": {"username": "alice"}},
                "response": {"status": 200, "body": {"ok": True}},
                "status": "SUCCESS",
                "creation_dt": "2025-01-01T12:00:00Z",
                "last_updation_dt": "2025-01-01T12:00:02Z"
            },
            {
                "transactionId": "txn-124",
                "session": "7f4f8e1a-2b6c-4b6a-9b7d-9f3a1d2c4e5f",
                "action": "get_profile",
                "http_method": "GET",
                "request": {"url": "/api/v001/users/alice"},
                "response": {"status": 404, "error": "Not Found"},
                "status": "FAILED",
                "creation_dt": "2025-01-01T12:05:00Z",
                "last_updation_dt": "2025-01-01T12:05:01Z"
            }
        ]
    })
    root: List[TransactionItem]
