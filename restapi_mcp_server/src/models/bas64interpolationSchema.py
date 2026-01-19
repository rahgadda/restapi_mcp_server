"""Pydantic models for Base64 encode/decode operations."""
from pydantic import BaseModel, Field


class Base64EncodeIn(BaseModel):
    """Input payload for Base64 encoding.

    Attributes:
        text: Plain text to encode as base64.
    """
    text: str = Field(..., description="Plain text to encode as base64")

class Base64EncodeOut(BaseModel):
    """Response payload for Base64 encoding.

    Attributes:
        encoded: Base64-encoded representation of the input text.
    """
    encoded: str = Field(..., description="Base64-encoded representation of the input text")

class Base64DecodeIn(BaseModel):
    """Input payload for Base64 decoding.

    Attributes:
        encodedString: Base64-encoded string to decode.
    """
    encodedString: str = Field(..., description="Base64-encoded string to decode")

class Base64DecodeOut(BaseModel):
    """Response payload for Base64 decoding.

    Attributes:
        text: Decoded plain text from the provided base64 string.
    """
    text: str = Field(..., description="Decoded plain text from the provided base64 string")
