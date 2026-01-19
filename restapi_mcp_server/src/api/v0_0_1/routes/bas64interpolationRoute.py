"""
Base64 encode/decode routes.

Endpoints:
- POST /base64/encode
    Encode plain text to Base64.

- POST /base64/decode
    Decode a Base64-encoded string to plain text.
"""
from fastapi import APIRouter, HTTPException
from ....models.bas64interpolationSchema import (
    Base64EncodeIn,
    Base64EncodeOut,
    Base64DecodeIn,
    Base64DecodeOut,
)
from ....utils.bas64interpolation import encode_base64, decode_base64

# Router for Base64 operations
router = APIRouter(prefix="/base64", tags=["Base64"])

@router.post("/encode", response_model=Base64EncodeOut)
def base64_encode(payload: Base64EncodeIn):
    """
    Encode plain text to a Base64 string.

    Request body (Base64EncodeIn):
      - text: Plain text to encode.

    Returns:
      Base64EncodeOut with 'encoded' containing the Base64 string.
    """
    try:
        base64_encoded_str = encode_base64(text=payload.text)
        response_payload = Base64EncodeOut(encoded=base64_encoded_str)
        return response_payload
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/decode", response_model=Base64DecodeOut)
def base64_decode(payload: Base64DecodeIn):
    """
    Decode a Base64 string to plain text.

    Request body (Base64DecodeIn):
      - encodedString: Base64-encoded string to decode.

    Returns:
      Base64DecodeOut with 'text' containing the decoded plain text.
    """
    try:
        base64_decoded_str = decode_base64(b64_text=payload.encodedString)
        response_payload = Base64DecodeOut(text=base64_decoded_str)
        return response_payload
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
