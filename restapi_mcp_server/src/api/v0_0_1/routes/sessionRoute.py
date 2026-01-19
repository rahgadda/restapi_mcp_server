"""
Session management routes.

Endpoints:
- POST /session/createSession
    Create and return a new session identifier.
"""
from fastapi import APIRouter, HTTPException
from ....utils import idgen
from ....models.sessionSchema import SessionOut

router = APIRouter(prefix="/session", tags=["Session"])

@router.post("/createSession", response_model=SessionOut)
def createSession():
    """
    Create a new session.

    Returns:
        SessionOut: Pydantic model containing a generated session UUID.
    """
    try:
        return SessionOut(session=idgen.generateUUID()) 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
