"""
Transactions routes.

Endpoints:
- GET /transactions/listAllTransactions
    Return all transactions as a list (no wrapper).

- GET /transactions/listSpecificTransaction
    Return a single transaction by transactionId (404 if not found).
"""
from fastapi import APIRouter, HTTPException
from ....models.transacationSchema import TransactionItem, GetAllTransactionsOut
from ....services.transactions import listSpecificTransaction, listAllTransactions

# Router for transaction operations
router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/listAllTransactions", response_model=GetAllTransactionsOut)
def get_all_transactions():
    """
    Return all transactions.

    Returns:
        GetAllTransactionsOut: Top-level list of TransactionItem (no wrapper).
    """
    try:
        return listAllTransactions()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/listSpecificTransaction", response_model=TransactionItem)
def list_specific_transaction(transactionId: str):
    """
    Return a single transaction by transactionId.

    - 200: TransactionItem if found
    - 404: If no transaction exists with given ID
    """
    try:
        rows = listSpecificTransaction(transactionId=transactionId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not rows:
        raise HTTPException(status_code=404, detail="Transaction not found")
    # Ensure a single object is returned to match response_model
    return rows[0]
