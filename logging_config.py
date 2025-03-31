import sys

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="DEBUG", format="{time} {level} {message}", colorize=True)
logger.add("errors.log", level="ERROR", rotation="10 MB", retention="7 days", compression="zip")
