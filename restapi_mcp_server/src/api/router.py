from fastapi import APIRouter
from .v0_0_1.routes.bas64interpolationRoute import router as b64_router
from .v0_0_1.routes.sessionRoute import router as session_router
from .v0_0_1.routes.jqRoute import router as jq_router
from .v0_0_1.routes.variablesRoute import router as variable_router
from .v0_0_1.routes.transactionRoute import router as transaction_router
from .v0_0_1.routes.restapiRoute import router as restapi_router
from .v0_0_1.routes.healthRouter import router as health_router

api_v001 = APIRouter(prefix="/api/v001")
api_v001.include_router(health_router)
api_v001.include_router(b64_router)
api_v001.include_router(session_router)
api_v001.include_router(jq_router)
api_v001.include_router(variable_router)
api_v001.include_router(transaction_router)
api_v001.include_router(restapi_router)