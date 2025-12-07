from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stderr, format="{level} | {message} | {time:YYYY-MM-DD HH:mm:ss}"
)