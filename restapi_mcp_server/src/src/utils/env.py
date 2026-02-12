import os
from typing import Optional


def _get_env_any(*names: str) -> Optional[str]:
    """Return the first environment variable value found among names."""
    for n in names:
        if n in os.environ:
            return os.environ[n]
    return None


def _parse_bool(v: str) -> bool:
    v_lower = v.strip().lower()
    if v_lower in ("1", "true", "yes", "on", "y", "t"):
        return True
    if v_lower in ("0", "false", "no", "off", "n", "f"):
        return False
    # Fallback: non-empty strings are truthy
    return bool(v_lower)


def load_common_from_env() -> None:
    """
    Load environment variables to override restapi_mcp_server.src.constants.COMMON values.
    If an env var is not set, the existing default in COMMON is retained.

    Supported environment variables (checked in order, first match wins):
      - HOST
      - API_PORT
      - MCP_API_PORT
      - DEFAULT_HTTP_TIMEOUT
      - DEBUG
      - STORAGE
      - LOG_LEVEL, log_level

    Special handling:
      - If LOG_LEVEL is not explicitly provided but DEBUG is set, log_level is recomputed as:
          "debug" if DEBUG else "info"
    """
    # Local import to avoid import-time side effects
    from ..constants import COMMON

    def maybe_set_str(attr: str, *env_names: str) -> bool:
        v = _get_env_any(*env_names)
        if v is not None:
            setattr(COMMON, attr, v)
            return True
        return False

    def maybe_set_int(attr: str, *env_names: str) -> bool:
        v = _get_env_any(*env_names)
        if v is not None:
            try:
                setattr(COMMON, attr, int(v))
            except ValueError:
                print(f"[env] WARN: Invalid int for {env_names}='{v}', keeping default {attr}={getattr(COMMON, attr)}")
            return True
        return False

    def maybe_set_float(attr: str, *env_names: str) -> bool:
        v = _get_env_any(*env_names)
        if v is not None:
            try:
                setattr(COMMON, attr, float(v))
            except ValueError:
                print(
                    f"[env] WARN: Invalid float for {env_names}='{v}', keeping default {attr}={getattr(COMMON, attr)}"
                )
            return True
        return False

    def maybe_set_bool(attr: str, *env_names: str) -> bool:
        v = _get_env_any(*env_names)
        if v is not None:
            setattr(COMMON, attr, _parse_bool(v))
            return True
        return False

    # Apply overrides where present
    maybe_set_str("HOST", "HOST")
    maybe_set_int("API_PORT", "API_PORT")
    maybe_set_int("MCP_API_PORT", "MCP_API_PORT")
    maybe_set_float("DEFAULT_HTTP_TIMEOUT", "DEFAULT_HTTP_TIMEOUT")
    debug_overridden = maybe_set_bool("DEBUG", "DEBUG")
    maybe_set_str("STORAGE", "STORAGE")

    log_level_overridden = maybe_set_str("log_level", "LOG_LEVEL", "log_level")

    # If log level not explicitly set via env but DEBUG was provided/exists,
    # recompute log level based on DEBUG.
    if not log_level_overridden and debug_overridden:
        setattr(COMMON, "log_level", "debug" if getattr(COMMON, "DEBUG", False) else "info")
