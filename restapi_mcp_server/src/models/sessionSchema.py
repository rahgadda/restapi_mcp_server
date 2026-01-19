"""Pydantic models for session management."""
from pydantic import BaseModel, Field
import uuid

class SessionOut(BaseModel):
    """Response payload returning a newly created session identifier."""
    session: uuid.UUID = Field(..., description="A new unique session id")
