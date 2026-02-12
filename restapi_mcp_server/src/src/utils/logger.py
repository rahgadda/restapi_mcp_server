import logging
import sys
from uvicorn.logging import DefaultFormatter
from ..constants import COMMON

logger = logging.getLogger(__name__)

def setup_logging() -> logging.Logger:
    """
    Setup the logging configuration for the application. 
    """          

    debug=COMMON.DEBUG

    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False

    # Remove all existing handlers to prevent accumulation
    for handler in logger.handlers:
        logger.removeHandler(handler)
    
    handlers = []
           
    # Create a new handler
    try:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG if debug else logging.INFO)
        formatter = DefaultFormatter("%(levelprefix)s %(message)s", use_colors=True)
        handler.setFormatter(formatter)
        handlers.append(handler)
    except Exception as e:
        print(f"Failed to create stdout log handler: {e}", file=sys.stderr)

    # Add the handlers to the logger
    for handler in handlers:
        logger.addHandler(handler)
    
    return logger
