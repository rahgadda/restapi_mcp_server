"""
Variable interpolation and environment variable management routes.

Endpoints:
- POST /variable/eval
    Interpolate an expression using provided variables.

- GET /variable/listAllEnvironmentVariables
    List all variables for a given environment as a list of
    {environment, variable, value} objects.

- GET /variable/listSpecificVariableByEnvironment
    Return a specific variable for an environment as a list
    (0 or 1 items) of {environment, variable, value}.

- PUT /variable/upsertEnvironmentVariable
    Upsert (insert or update) a variable value for an environment.
"""
from fastapi import APIRouter, HTTPException
from ....models.variablesSchema import EvalIn, EvalOut, GetAllEnvOut, EnvVarItem
from ....services.variablesInterpolation import eval, listAllVariableByEnvironment, listSpecificVariableByEnvironment, upsertEnvironmentVariable

# Router for variable-related operations under the /variable prefix
router = APIRouter(prefix="/variables", tags=["Variables"])

@router.post("/eval", response_model=EvalOut)
def evaluate_Expression(payload: EvalIn):
    """
    Interpolate an expression using provided variables.

    Request body (EvalIn):
      - expression: str
          The expression containing placeholders like {{VARIABLE-NAME}}.
      - data: List[Dict[str, Any]]
          A list of variable dictionaries to merge. Each entry can be either:
            - {"variable": "<NAME>", "value": <Any>}  (VariableItem-like)
            - {"<NAME>": <Any>}  (already a mapping)

    Returns:
      EvalOut with 'result' containing the interpolated string.
    """
    try:
        return EvalOut(result=eval(expression=payload.expression, data=payload.data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/listAllEnvironmentVariables", response_model=GetAllEnvOut)
def get_all_environment_variables(environment: str):
    """Return all variables for the given environment.
    Each item has keys: environment, variable, value.
    """
    return listAllVariableByEnvironment(environment)


@router.get("/listSpecificVariableByEnvironment", response_model=GetAllEnvOut)
def list_specific_variable_by_environment(environment: str, variable: str):
    """Return the specific variable for the given environment as a list
    (0 or 1 items). Each item has keys: environment, variable, value.
    """
    return listSpecificVariableByEnvironment(environment=environment, variable=variable)


@router.put("/upsertEnvironmentVariable", response_model=EnvVarItem)
def upsert_environment_variable(payload: EnvVarItem):
    """
    Upsert an environment variable. If the (environment, variable) exists, update its value;
    otherwise create a new entry.
    """
    try:
        result = upsertEnvironmentVariable(
            environment=payload.environment,
            variable=payload.variable,
            value=payload.value,
        )
        return EnvVarItem(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
