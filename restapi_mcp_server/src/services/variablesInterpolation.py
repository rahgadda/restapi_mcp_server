from ..utils.interpolation import interpolate
from ..utils.logger import setup_logging
from ..utils.persist import filter_rows, read_csv_df, write_csv_df
from ..constants import COMMON
from typing import Any, Dict, List
from ..utils.jsoncodec import encode_value_for_storage, decode_value_if_json
import json
import pandas as pd

logger = setup_logging()


def listAllVariableByEnvironment(environment: str) -> List[Dict[str, Any]]:
    # Return a list of {environment, variable, value} dictionaries for the given environment
    rows: List[Dict[str, Any]] = []
    try:
        rows = filter_rows(COMMON.FileType.ENVIRONMENT, environment=environment)
    except Exception as exc:
        logger.error("Failed to list variables for environment %s: %s", environment, exc)
        raise
    for r in rows:
        r["value"] = decode_value_if_json(r.get("value"))
    return rows


def listSpecificVariableByEnvironment(environment: str, variable: str) -> List[Dict[str, Any]]:
    # Return a list (typically 0 or 1 item) of {environment, variable, value} for the given env+variable
    rows: List[Dict[str, Any]] = []
    try:
        rows = filter_rows(COMMON.FileType.ENVIRONMENT, environment=environment, variable=variable)
    except Exception as exc:
        logger.error("Failed to get variable %s for environment %s: %s", variable, environment, exc)
        raise
    for r in rows:
        r["value"] = decode_value_if_json(r.get("value"))
    return rows


def upsertEnvironmentVariable(environment: str, variable: str, value: Any) -> Dict[str, Any]:
    # Upsert a row for the given environment/variable; update value if exists else create new.
    try:
        df = read_csv_df(COMMON.FileType.ENVIRONMENT)
    except Exception as exc:
        logger.error("Failed to read environment CSV: %s", exc)
        raise

    encoded_value = encode_value_for_storage(value)

    if df.empty:
        df = pd.DataFrame([{"environment": environment, "variable": variable, "value": encoded_value}])
    else:
        mask = (df["environment"] == environment) & (df["variable"] == variable)
        if mask.any():
            df.loc[mask, "value"] = encoded_value
        else:
            df = pd.concat(
                [df, pd.DataFrame([{"environment": environment, "variable": variable, "value": encoded_value}])],
                ignore_index=True,
            )

    try:
        write_csv_df(df, COMMON.FileType.ENVIRONMENT)
    except Exception as exc:
        logger.error("Failed to write environment CSV: %s", exc)
        raise

    return {"environment": environment, "variable": variable, "value": value}


def eval(expression: str, data: List[Dict[str, Any]]) -> str:
    normalized: List[Dict[str, Any]] = []
    for item in (data or []):
        if isinstance(item, dict):
            if "variable" in item and "value" in item and isinstance(item.get("variable"), str):
                normalized.append({item["variable"]: item.get("value")})
            else:
                normalized.append(item)
    return interpolate(expression, normalized)


def deleteAllVariablesByEnvironment(environment: str) -> int:
    """Delete all variables for the given environment.

    Reads the environment CSV and removes all rows where `environment` matches
    the provided environment value. Returns the number of deleted rows.
    """
    try:
        df = read_csv_df(COMMON.FileType.ENVIRONMENT)
    except Exception as exc:
        logger.error("Failed to read environment CSV: %s", exc)
        raise

    if df.empty:
        return 0

    if "environment" not in df.columns:
        logger.error("'environment' column not found in ENVIRONMENT CSV")
        raise KeyError("'environment' column not found in ENVIRONMENT CSV")

    mask = df["environment"] == environment
    deleted_count = int(mask.sum())
    if deleted_count == 0:
        return 0

    new_df = df[~mask]
    try:
        write_csv_df(new_df, COMMON.FileType.ENVIRONMENT)
    except Exception as exc:
        logger.error("Failed to write environment CSV after delete: %s", exc)
        raise

    return deleted_count
