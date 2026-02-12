"""
JQ expression evaluation routes.

Endpoints:
- POST /jq/eval
    Evaluate a JQ expression against supplied JSON input.
"""
from fastapi import APIRouter, HTTPException
from ....utils import jqinterpolation
from ....models.jqSchema import JQExpressionIn, JQExpressionOut

router = APIRouter(prefix="/jq", tags=["JQ"])

@router.post("/eval", response_model=JQExpressionOut)
def jq_expression_evaluation(payload: JQExpressionIn):
    """
    Evaluate a JQ expression against provided JSON input.

    Request body (JQExpressionIn):
      - expression: JQ expression string to evaluate.
      - data: JSON input object/array the expression applies to.

    Returns:
      JQExpressionOut: Pydantic model with 'result' containing the evaluation output.
    """
    try:
        return JQExpressionOut(result=jqinterpolation.jqinterpolate(expression=payload.expression,json_input=payload.data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
