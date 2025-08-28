import logging
from . import settings

# MARK: logger
logger: logging.Logger = logging.getLogger(settings.NAME)

logging.basicConfig(
    level=logging.DEBUG if settings.APP_DEBUG else logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s", 
)
logger.setLevel(logging.DEBUG if settings.APP_DEBUG else logging.INFO)
