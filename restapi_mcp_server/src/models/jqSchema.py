"""Pydantic models for JQ expression evaluation."""
from typing import Any
from pydantic import BaseModel, Field

class JQExpressionIn(BaseModel):
    """Input payload for JQ expression evaluation.

    Attributes:
        expression: jq filter expression.
        data: Input JSON value (object/array/scalar) to run through the jq expression.
    """
    expression: str = Field(..., min_length=1, description="jq filter expression")
    data: Any = Field(
        default=None,
        description="Input JSON value to run through the jq expression",
    )


class JQExpressionOut(BaseModel):
    """Output payload for JQ expression evaluation.

    Attributes:
        result: Result produced by evaluating the jq expression.
    """
    result: Any = Field(..., description="Result produced by evaluating the jq expression")
