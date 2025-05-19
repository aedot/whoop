import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
import os

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    timezone = os.getenv("TIMEZONE", "UTC")
    try:
        tzinfo = ZoneInfo(timezone)
    except Exception:
        tzinfo = ZoneInfo("UTC")

    class TZFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            ct = datetime.fromtimestamp(record.created, tz=tzinfo)
            if datefmt:
                return ct.strftime(datefmt)
            return ct.isoformat()

    formatter = TZFormatter('%(asctime)s %(levelname)s %(name)s - %(message)s')

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)

    return logger
