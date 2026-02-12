import uuid
from .logger import setup_logging

logger = setup_logging()

def generateUUID() -> uuid.UUID:
    """
    Generates a random UUID (Universally Unique Identifier) using the uuid4 algorithm.

    Returns:
        uuid.UUID: A random UUID object.

    Notes:
        This function utilizes the uuid.uuid4() method to generate a random UUID.
    """
    try:
        uid = uuid.uuid4()
    except Exception as exc:
        logger.error("Failed to generate UUID v4: %s", exc)
        raise
    
    logger.debug("Generated UUID v4: %s", uid)
    return uid
