"""
REST API orchestration routes.

Endpoints:
- POST /restapi/call
    Execute an HTTP call after interpolating variables, creating a transaction
    before the call, and updating it after the call completes.
"""
from fastapi import APIRouter, HTTPException
from ....models.restapiSchema import RestAPIIn, RestAPIOut
from ....services.restapi import restapiCall

# Router for REST API orchestration
router = APIRouter(prefix="/restapi", tags=["REST API"])

@router.post("/call", response_model=RestAPIOut)
def restapi_call(payload: RestAPIIn) -> RestAPIOut:
    """
    Execute an HTTP call using the provided payload.

    Behavior:
    - Interpolates variables in URL/headers/body based on the provided environment
    - Creates a transaction (PENDING) prior to the HTTP call
    - Performs the HTTP call
    - Updates the transaction with response and final status (SUCCESS/FAILED/ERROR)

    Returns:
        RestAPIOut: status, response headers, and response body from downstream.
    """
    try:
        print("here")
        return restapiCall(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
