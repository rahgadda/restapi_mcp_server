from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from .src.api.router import api_v001
from .src.constants import COMMON
import uvicorn
import os
from .src.utils.logger import setup_logging
from fastapi import Request
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any
import httpx
import asyncio
import threading
from .src.utils.env import load_common_from_env

logger = setup_logging()

# Create the ASGI app at module scope so Uvicorn can import it via string path
app = FastAPI(
    title="Rest API Orchestrator",
    version="0.0.1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
app.include_router(api_v001)

# Guard error logging middleware to avoid double-send issues under certain ASGI flows
if os.getenv("ENABLE_ERROR_LOG_MW", "0").lower() in ("1", "true", "yes", "on"):
    @app.middleware("http")
    async def error_logging_middleware(request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled exception: %s %s", request.method, request.url.path)
            raise
        if response.status_code >= 400:
            logger.error("Request failed: %s %s -> %d", request.method, request.url.path, response.status_code)
        return response

def startAppServer():
    host = COMMON.HOST
    port = COMMON.API_PORT
    log_level = COMMON.log_level

    # Use an import string that points to this module's app object
    import_string = "restapi_mcp_server.__main__:app"

    # Disable reload by default in container to avoid multi-process duplication issues
    # Enable via UVICORN_RELOAD=1 if needed for local dev
    reload_flag = os.getenv("UVICORN_RELOAD", "0").lower() in ("1", "true", "yes", "on")

    uvicorn.run(
        import_string,
        host=host,
        port=port,
        log_level=log_level,
        reload=reload_flag,
        reload_dirs=["."] if reload_flag else None,
        proxy_headers=False,
        workers=1,
    )

def createMCPServerWithTools():

    mcp_host: str = COMMON.HOST
    mcp_port: int = COMMON.MCP_API_PORT
    # Allow overriding the orchestrator base URL (default stays local for dev)
    # Set env var RESTAPI_ORCHESTRATOR_BASE (or ORCHESTRATOR_BASE) to target a remote host
    API_BASE: str = os.getenv("RESTAPI_ORCHESTRATOR_BASE") or f"http://127.0.0.1:{COMMON.API_PORT}"
    logger.info(f"[MCP] Orchestrator base: {API_BASE}")
    mcp = FastMCP("restapi_orchestrator_tools", host=mcp_host, port=mcp_port)

    @mcp.tool()
    def createSession() -> Dict[str, Any]:
        """Create a new session id.
        Returns: { "session": string }
        """
        with httpx.Client(timeout=30.0) as client:
            r = client.post(f"{API_BASE}/api/v001/session/createSession")
            r.raise_for_status()
            return r.json()

    @mcp.tool()
    def createEnvironmentVariables(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Upsert environment variables via REST API.
        
        Endpoint: PUT /api/v001/variables/upsertEnvironmentVariable
        Input: items: list of { "environment": str, "variable": str, "value": Any }
        Returns: list of upserted items (echoed from API)
        """
        results: List[Dict[str, Any]] = []
        with httpx.Client(timeout=30.0) as client:
            for it in items:
                r = client.put(f"{API_BASE}/api/v001/variables/upsertEnvironmentVariable", json=it)
                r.raise_for_status()
                results.append(r.json())
        return results

    @mcp.tool()
    def upsertEnvironmentVariable(environment: str, variable: str, value: Any) -> Dict[str, Any]:
        """Upsert a single environment variable via REST API.
        
        Endpoint: PUT /api/v001/variables/upsertEnvironmentVariable
        Inputs:
          - environment: target environment name
          - variable: variable name
          - value: variable value (any JSON-serializable type)
        Returns: { environment, variable, value }
        """
        payload: Dict[str, Any] = {
            "environment": environment,
            "variable": variable,
            "value": value,
        }
        with httpx.Client(timeout=30.0) as client:
            r = client.put(
                f"{API_BASE}/api/v001/variables/upsertEnvironmentVariable",
                json=payload,
            )
            r.raise_for_status()
            return r.json()

    @mcp.tool()
    def listAllEnvironmentVariables(environment: str) -> List[Dict[str, Any]]:
        """List all variables for the given environment.
        Returns: array of { environment, variable, value }
        """
        with httpx.Client(timeout=30.0) as client:
            r = client.get(
                f"{API_BASE}/api/v001/variables/listAllEnvironmentVariables", params={"environment": environment}
            )
            r.raise_for_status()
            return r.json()

    @mcp.tool()
    def listSpecificEnvironmentVariable(environment: str, variable: str) -> List[Dict[str, Any]]:
        """Get a specific environment variable.
        Returns: { environment, variable, value }
        """
        with httpx.Client(timeout=30.0) as client:
            r = client.get(
                f"{API_BASE}/api/v001/variables/listSpecificVariableByEnvironment",
                params={"environment": environment, "variable": variable},
            )
            r.raise_for_status()
            return r.json()

    @mcp.tool()
    def deleteAllByEnvironment(environment: str) -> Dict[str, Any]:
        """Delete all variables for the given environment via REST API.

        Endpoint: DELETE /api/v001/variables/deleteAllByEnvironment
        Returns: { environment, deletedCount }
        """
        with httpx.Client(timeout=30.0) as client:
            r = client.delete(
                f"{API_BASE}/api/v001/variables/deleteAllByEnvironment",
                params={"environment": environment},
            )
            r.raise_for_status()
            return r.json()

    @mcp.tool()
    def health() -> Dict[str, Any]:
        """Check API health.
        
        Endpoint: GET /api/v001/health
        Returns: {"status": "ok"} on healthy server.
        """
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{API_BASE}/api/v001/health")
            r.raise_for_status()
            return r.json()

    @mcp.tool()
    def createRestAPICall(
        method: str,
        url: str,
        action: str,
        environment: str,
        session: str,
        request_headers: Dict[str, Any] | None = None,
        request_body: Any | None = None,
        pre_script: Any | None = None,
        post_script: Any | None = None,
        debug: bool | None = None,
    ) -> Dict[str, Any]:
        """Call the RestAPI Orchestrator HTTP endpoint.
        
        Endpoint: POST /api/v001/restapi/call
        
        Inputs:
        - method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        - url: Target URL (supports variable/base64/jq interpolation server-side)
        - action: Logical action name for transaction logging
        - environment: Environment name
        - session: Session identifier
        - request_headers: Optional headers map (values may use interpolation syntax)
        - request_body: Optional JSON body (values may use interpolation syntax)
        - pre_script: Reserved (not used currently)
        - post_script: Optional dict of {"{{VARIABLE_NAME}}": "expression"}; evaluated on 2xx/3xx status
        - debug: Optional flag
        
        Returns: { response_status, response_headers, response_body }
        """
        payload: Dict[str, Any] = {
            "method": method,
            "url": url,
            "action": action,
            "environment": environment,
            "session": session,
        }
        if request_headers is not None:
            payload["request_headers"] = request_headers
        if request_body is not None:
            payload["request_body"] = request_body
        if pre_script is not None:
            payload["pre_script"] = pre_script
        if post_script is not None:
            payload["post_script"] = post_script
        if debug is not None:
            payload["debug"] = bool(debug)

        with httpx.Client(timeout=60.0) as client:
            r = client.post(f"{API_BASE}/api/v001/restapi/call", json=payload)
            r.raise_for_status()
            return r.json()

    def _run_mcp_in_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            mcp.run(transport="sse")
        except Exception as e:
            print(f"[MCP] MCP server thread exited: {e}")

    thread = threading.Thread(target=_run_mcp_in_thread, name="mcp-sse", daemon=True)
    thread.start()

def main():
    load_common_from_env()
    global logger
    logger = setup_logging()
    createMCPServerWithTools()
    startAppServer()

if __name__ == "__main__":
    main()
