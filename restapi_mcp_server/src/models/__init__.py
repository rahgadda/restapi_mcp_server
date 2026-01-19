"""
Models package for Pydantic schemas.

This file makes `restapi_mcp_server.src.models` an importable package so that
relative imports from nested API routes resolve correctly, e.g.:

from ....models.bas64interpolationSchema import Base64EncodeIn
"""
__all__ = ["bas64interpolationSchema"]
