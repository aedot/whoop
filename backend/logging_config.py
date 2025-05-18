import logging
import sys

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')

    # StreamHandler outputs to console
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)

    # Remove all existing handlers and add the new one
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(ch)

    return logger
