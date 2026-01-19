"""Models for variable interpolation and environment management.

Defines request/response shapes for the variable APIs exposed under /variable.
"""
from typing import Any, Dict, List
from pydantic import BaseModel, Field, ConfigDict, RootModel

class EvalIn(BaseModel):
    """Input payload for variable interpolation.

    Attributes:
        expression: Expression containing {{VARIABLE}} placeholders.
        data: List of variable mappings to merge. Each item may be:
              - {"variable": "<NAME>", "value": <Any>}
              - {"<NAME>": <Any>}
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "expression": "string",
            "data": [
                {"variable": "value"}
            ]
        }
    })
    expression: str = Field(..., description="String expression to be replaced with variables in {{<<variable>>}} format")
    data: List[Dict[str, Any]] = Field(
        ...,
        description="List of variable dicts to merge (e.g., [{\"variable\": \"value\"}])",
        examples=[{"variable": "value"}],
    )

class EvalOut(BaseModel):
    """Output payload for variable interpolation.

    Attributes:
        result: The interpolated string after placeholder substitution.
    """
    result: Any = Field(..., description="Replaced expression")

class EnvVarItem(BaseModel):
    """Environment variable item.

    Attributes:
        environment: Environment name.
        variable: Variable name.
        value: Variable value (string or JSON-serializable).
    """
    environment: str = Field(..., description="Environment name")
    variable: str = Field(..., description="Variable name")
    value: Any = Field(..., description="Variable value")

class GetAllEnvOut(RootModel[List[EnvVarItem]]):
    """Top-level response as a list of environment variable items (no 'data' wrapper)."""
    model_config = ConfigDict(json_schema_extra={
        "example": [
            {"environment": "dev", "variable": "CMC-BASE-SERVICES", "value": "http://example.com/base"},
            {"environment": "dev", "variable": "MAKER-ID", "value": "RAHGADDAMAK"}
        ]
    })
    root: List[EnvVarItem]
