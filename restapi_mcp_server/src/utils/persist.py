import pandas as pd
from ..constants import COMMON
from pathlib import Path
from .logger import setup_logging
from typing import Dict, List, Any

logger = setup_logging()

def get_file_location(file_type: COMMON.FileType) -> Path:
    """
    Return the CSV file path for the given file type under COMMON.STORAGE.
    Does not create the file or directory.
    """
    storage_path = Path(COMMON.STORAGE)
    filename = "environment.csv" if file_type == COMMON.FileType.ENVIRONMENT else "transaction.csv"
    return storage_path / filename

def write_csv_df(incoming_df: pd.DataFrame, file_type: COMMON.FileType):
    """Write a DataFrame to the configured storage CSV.

    This function writes `incoming_df` to either `environment.csv` or
    `transaction.csv` depending on `file_type`, resolving the target
    path via get_file_location(file_type).

    Behavior:
    - If the configured storage folder does not exist, an error is logged.
    - If the target CSV file is missing, an error is logged and no write
      is attempted.
    - On success the DataFrame is written with `index=False` and a debug
      log is emitted.

    Args:
        incoming_df (pd.DataFrame): DataFrame to write to CSV.
        file_type (COMMON.FileType): Target file type (ENVIRONMENT or TRANSACTION).
    """
    storage_path = Path(COMMON.STORAGE)
    path = get_file_location(file_type)

    logger.debug("STORAGE_FOLDER_PATH: %s", storage_path)
    logger.debug("FILE TYPE: %s", file_type.name)
    logger.debug("CSV PATH: %s", path)

    # Ensure storage folder is present
    if not storage_path.is_dir():
        logger.error("Storage folder not configured: %s", storage_path)
        raise FileNotFoundError(f"Storage folder not configured: {storage_path}")

    # Verify target file exists before writing (preserves previous behavior)
    if not path.is_file():
        logger.error("%s file not found: %s", path.name, storage_path)
        raise FileNotFoundError(f"{path.name} file not found in {storage_path}")

    logger.debug("%s file found: %s", path.name, path)
    try:
        incoming_df.to_csv(path, index=False)
    except Exception as exc:
        logger.error("Failed to write CSV %s: %s", path, exc)
        raise
    logger.debug("%s file updated", path.name)

def filter_rows(file_type: COMMON.FileType, **equals: Any) -> List[Dict[str, Any]]:
    """Filter rows from a CSV by equality on provided columns.

    Loads the CSV for the given file type (via get_file_location) and returns rows
    that match all provided equality filters. Matching is performed using exact,
    case-sensitive equality on the specified columns.

    Behavior:
    - If the CSV file is missing or the DataFrame is empty, an empty list is returned.
    - If any requested filter column does not exist in the CSV, an error is logged
      and an empty list is returned.
    - On success, returns a list of dicts (one per matching row).

    Args:
        file_type (COMMON.FileType): Which CSV to read (ENVIRONMENT or TRANSACTION).
        **equals: Column=value pairs to filter by (e.g., key="abc", env="dev").

    Returns:
        List[Dict[str, Any]]: Matching rows as dictionaries (empty if none).
    """
    path = get_file_location(file_type)
    logger.debug("Filtering rows from: %s", path)
    logger.debug("Filter equals: %s", equals)

    df = read_csv_df(file_type)
    if df.empty:
        logger.debug("CSV is empty or missing for %s; no rows to filter.", file_type.name)
        return []

    # Validate requested columns exist
    for col in equals.keys():
        if col not in df.columns:
            logger.error("Column '%s' not found in CSV for %s", col, file_type.name)
            raise KeyError(f"Column '{col}' not found in CSV for {file_type.name}")

    # Apply equality filters
    for col, val in equals.items():
        df = df[df[col] == val]

    match_count = 0 if df.empty else len(df)
    logger.debug("Matched rows: %d", match_count)

    if df.empty:
        return []

    return df.to_dict(orient="records")  # type: ignore

def read_csv_df(file_type: COMMON.FileType = COMMON.FileType.ENVIRONMENT) -> pd.DataFrame :
    """Read a CSV file from the configured STORAGE folder.

    Reads either 'environment.csv' or 'transaction.csv' depending on file_type,
    resolving the path via get_file_location(file_type).

    Returns a pandas.DataFrame (empty if the file is missing). Logs errors and
    debug information. CSV is read with dtype=object to preserve values as strings.

    Args:
        file_type (COMMON.FileType): Which file to read (ENVIRONMENT or TRANSACTION).

    Returns:
        pd.DataFrame: Loaded DataFrame or empty DataFrame if not found.
    """
    storage_path = Path(COMMON.STORAGE)
    path = get_file_location(file_type)
    df = pd.DataFrame()

    logger.debug("STORAGE_FOLDER_PATH: %s", storage_path)
    logger.debug("FILE TYPE: %s", file_type.name)
    logger.debug("CSV PATH: %s", path)

    if not storage_path.is_dir():
        logger.error("Storage folder not configured: %s", storage_path)
        raise FileNotFoundError(f"Storage folder not configured: {storage_path}")

    if not path.is_file():
        logger.error("%s file not found: %s", path.name, storage_path)
        raise FileNotFoundError(f"{path.name} file not found in {storage_path}")

    logger.debug("%s file found: %s", path.name, path)
    try:
        df = pd.read_csv(path, dtype=object)
    except Exception as exc:
        logger.error("Failed to read CSV %s: %s", path, exc)
        raise
    
    return df
