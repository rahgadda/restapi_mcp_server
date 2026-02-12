from __future__ import annotations
import base64
import binascii
from typing import Final
from ..constants import COMMON
from .logger import setup_logging

logger = setup_logging()

__all__ = ["encode_base64", "decode_base64"]

# Default text encoding used for converting between Python str and bytes.
_DEFAULT_TEXT_ENCODING: Final[str] = COMMON.DEFAULT_TEXT_ENCODING


def encode_base64(text: str, *, encoding: str = _DEFAULT_TEXT_ENCODING) -> str:
    """
    Encode a string into a Base64-encoded ASCII string.

    Parameters:
        text (str): Input Unicode string to encode.
        encoding (str, optional): Text encoding used to convert the string to bytes.
            Defaults to "utf-8".

    Returns:
        str: Base64-encoded representation (ASCII characters only).

    Raises:
        TypeError: If `text` is not a string.
        LookupError: If the provided `encoding` is unknown.

    Notes:
        - The output is safe to transport as text (ASCII).
        - For non-UTF-8 text, specify the correct `encoding`.

    Example:
        >>> encode_base64("café")
        'Y2Fmw6k='
    """

    logger.debug("encode_base64 called (type=%s, encoding=%s)", type(text).__name__, encoding)

    if not isinstance(text, str):
        logger.error("encode_base64: expected str, got %s", type(text).__name__)
        raise TypeError(f"encode_base64 expects a str, got {type(text).__name__}")

    # Convert the input string to bytes using the specified encoding
    try:
        raw_bytes = text.encode(encoding)
    except Exception as exc:
        logger.error("encode_base64: failed to encode text with encoding=%s: %s", encoding, exc)
        raise

    # Base64 encode the bytes; the result is bytes containing only ASCII characters
    try:
        b64_bytes = base64.b64encode(raw_bytes)
    except Exception as exc:
        logger.error("encode_base64: base64 encoding failed: %s", exc)
        raise
    logger.debug("encode_base64: produced base64 length=%d", len(b64_bytes))

    # Decode to str using ASCII (safe because Base64 alphabet is ASCII)
    try:
        return b64_bytes.decode("ascii")
    except Exception as exc:
        logger.error("encode_base64: ASCII decode failed: %s", exc)
        raise


def decode_base64(b64_text: str, *, encoding: str = _DEFAULT_TEXT_ENCODING) -> str:
    """
    Decode a Base64-encoded ASCII string back into a Unicode string.

    Parameters:
        b64_text (str): Base64-encoded string (ASCII).
        encoding (str, optional): Text encoding used to decode the resulting bytes
            into a Python string. Defaults to "utf-8".

    Returns:
        str: Decoded Unicode string.

    Raises:
        TypeError: If `b64_text` is not a string.
        ValueError: If `b64_text` is not valid Base64.
        UnicodeDecodeError: If the decoded bytes cannot be decoded with `encoding`.
        LookupError: If the provided `encoding` is unknown.

    Example:
        >>> decode_base64("Y2Fmw6k=")
        'café'
    """

    logger.debug("decode_base64 called (type=%s, target_encoding=%s)", type(b64_text).__name__, encoding)

    if not isinstance(b64_text, str):
        logger.error("decode_base64: expected str, got %s", type(b64_text).__name__)
        raise TypeError(f"decode_base64 expects a str, got {type(b64_text).__name__}")

    try:
        # validate=True ensures invalid characters/padding raise an exception
        decoded_bytes = base64.b64decode(b64_text, validate=True)
    except (binascii.Error, ValueError) as exc:
        logger.error("decode_base64: invalid base64 input: %s", exc)
        raise ValueError(f"Invalid Base64 input: {exc}") from exc

    # Convert the decoded bytes back into a string using the specified encoding
    try:
        return decoded_bytes.decode(encoding)
    except UnicodeDecodeError as exc:
        logger.error("decode_base64: failed to decode bytes with encoding=%s: %s", encoding, exc)
        raise
