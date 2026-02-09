import os
from enum import Enum, auto

class FileType(Enum):
    ENVIRONMENT = auto()
    TRANSACTION = auto()   

DEBUG = True
STORAGE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'storage') 
DEFAULT_HTTP_TIMEOUT: float = 30.0

# Regular Expressions
INTERPOLATION_REGEX = r"\{\{(.*?)\}\}"
BRACED_VARIABLE_REGEX = r"\{\{\s*(.*?)\s*\}\}"
BASE64_ENCODE_REGEX = r"(?:\{\{\s*base64_encode\.(.*?)\s*\}\}|\{\{\s*base64_encode\(\s*(.*?)\s*\)\s*\}\}|base64_encode\(\s*(.*?)\s*\))"
BASE64_DECODE_REGEX = r"(?:\{\{\s*base64_decode\.(.*?)\s*\}\}|\{\{\s*base64_decode\(\s*(.*?)\s*\)\s*\}\}|base64_decode\(\s*(.*?)\s*\))"
JQ_EXPRESSION_REGEX = r"jq_expression\(\s*(['\"])((?:\\.|(?!\1).)*?)\1\s*,\s*(.*?)\s*\)"
DEFAULT_TEXT_ENCODING = "utf-8"

# Constant for API Server
HOST: str="0.0.0.0"
API_PORT: int=9090
RESTAPI_ORCHESTRATOR_BASE: str = os.getenv("RESTAPI_ORCHESTRATOR_BASE") or f"http://127.0.0.1:{API_PORT}"
MCP_API_PORT: int=8765
log_level: str= "debug" if DEBUG else "info"
