from ..utils.logger import setup_logging
from ..utils.persist import filter_rows, read_csv_df, write_csv_df
from ..constants import COMMON
from typing import Any, Dict, List
from ..utils.jsoncodec import decode_value_if_json, encode_value_for_storage
from ..utils.idgen import generateUUID
from datetime import datetime, timezone
import pandas as pd


logger = setup_logging()

def listAllTransactions() -> List[Dict[str, Any]]:
    """Return all transactions as a list of dicts. Decodes request/response JSON if stored as strings."""
    try:
        df = read_csv_df(COMMON.FileType.TRANSACTION)
    except Exception as exc:
        logger.error("Failed to load transaction details: %s", exc)
        raise
    if df.empty:
        return []
    rows: List[Dict[str, Any]] = df.to_dict(orient="records")  # type: ignore
    for r in rows:
        r["request"] = decode_value_if_json(r.get("request"))
        if isinstance(r.get("request"), dict) and "headers" in r["request"]:
            r["request"]["headers"] = decode_value_if_json(r["request"]["headers"])
        r["response"] = decode_value_if_json(r.get("response"))
        if isinstance(r.get("response"), dict) and "headers" in r["response"]:
            r["response"]["headers"] = decode_value_if_json(r["response"]["headers"])
    return rows


def createTransaction(session: str, action: str, http_method: str, request_snapshot: Any) -> Dict[str, Any]:
    """Create a new transaction row with PENDING status and return the created record."""
    try:
        df = read_csv_df(COMMON.FileType.TRANSACTION)
    except Exception as exc:
        logger.error("Failed to read transactions CSV: %s", exc)
        raise

    txn_id = str(generateUUID())
    now = datetime.now(timezone.utc).isoformat()

    # Encode headers explicitly inside request snapshot before storing
    snapshot_for_storage = request_snapshot
    if isinstance(request_snapshot, dict) and "headers" in request_snapshot:
        snapshot_for_storage = {
            **request_snapshot,
            "headers": encode_value_for_storage(request_snapshot["headers"]),
        }

    row = {
        "transactionId": txn_id,
        "session": session,
        "action": action,
        "http_method": http_method,
        "request": encode_value_for_storage(snapshot_for_storage),
        "response": encode_value_for_storage(None),
        "status": "PENDING",
        "creation_dt": now,
        "last_updation_dt": now,
    }

    try:
        if df.empty:
            df = pd.DataFrame([row])
        else:
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        write_csv_df(df, COMMON.FileType.TRANSACTION)
    except Exception as exc:
        logger.error("Failed to write transactions CSV (create): %s", exc)
        raise

    # Return a decoded view for request/response
    return {
        **row,
        "request": request_snapshot,
        "response": None,
    }


def updateTransaction(transactionId: str, response_snapshot: Any, status: str) -> Dict[str, Any]:
    """Update an existing transaction's response and status. Returns the updated record."""
    try:
        df = read_csv_df(COMMON.FileType.TRANSACTION)
    except Exception as exc:
        logger.error("Failed to read transactions CSV: %s", exc)
        raise

    if df.empty or "transactionId" not in df.columns:
        logger.error("Transactions CSV missing or has no 'transactionId' column")
        raise KeyError("Transactions CSV not initialized properly")

    mask = df["transactionId"] == transactionId
    if not mask.any():
        logger.error("Transaction %s not found", transactionId)
        raise KeyError(f"Transaction {transactionId} not found")

    now = datetime.now(timezone.utc).isoformat()
    try:
        # Encode headers explicitly inside response snapshot before storing
        response_for_storage = response_snapshot
        if isinstance(response_snapshot, dict) and "headers" in response_snapshot:
            response_for_storage = {
                **response_snapshot,
                "headers": encode_value_for_storage(response_snapshot["headers"]),
            }

        df.loc[mask, "response"] = encode_value_for_storage(response_for_storage)
        df.loc[mask, "status"] = status
        df.loc[mask, "last_updation_dt"] = now
        write_csv_df(df, COMMON.FileType.TRANSACTION)
    except Exception as exc:
        logger.error("Failed to write transactions CSV (update): %s", exc)
        raise

    # Build updated record dict
    updated_row = df[mask].iloc[0].to_dict()
    updated_row["request"] = decode_value_if_json(updated_row.get("request"))
    if isinstance(updated_row.get("request"), dict) and "headers" in updated_row["request"]:
        updated_row["request"]["headers"] = decode_value_if_json(updated_row["request"]["headers"])
    updated_row["response"] = decode_value_if_json(updated_row.get("response"))
    if isinstance(updated_row.get("response"), dict) and "headers" in updated_row["response"]:
        updated_row["response"]["headers"] = decode_value_if_json(updated_row["response"]["headers"])
    return updated_row


def listSpecificTransaction(transactionId: str) -> List[Dict[str, Any]]:
    """Return the transaction with the given transactionId as a list (0 or 1 item)."""
    try:
        rows: List[Dict[str, Any]] = filter_rows(COMMON.FileType.TRANSACTION, transactionId=transactionId)
    except Exception as exc:
        logger.error("Failed to get transaction %s: %s", transactionId, exc)
        raise
    for r in rows:
        r["request"] = decode_value_if_json(r.get("request"))
        if isinstance(r.get("request"), dict) and "headers" in r["request"]:
            r["request"]["headers"] = decode_value_if_json(r["request"]["headers"])
        r["response"] = decode_value_if_json(r.get("response"))
        if isinstance(r.get("response"), dict) and "headers" in r["response"]:
            r["response"]["headers"] = decode_value_if_json(r["response"]["headers"])
    return rows
