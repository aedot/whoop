import os
import re
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from whoop_client import WhoopClient
from storage import store_sleep, store_recovery, store_workout, store_cycle, get_current_time
from logging_config import setup_logging
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

load_dotenv()

logger = setup_logging()

# Config from env
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
USER_TIMEZONE = os.getenv("TIMEZONE", "UTC")

try:
    USER_TZ = ZoneInfo(USER_TIMEZONE)
except Exception as e:
    logger.warning(f"Invalid timezone '{USER_TIMEZONE}' - falling back to UTC. Error: {e}")
    USER_TZ = ZoneInfo("UTC")

if not USERNAME or not PASSWORD:
    logger.error("WHOOP USERNAME and PASSWORD must be set in environment variables.")
    raise EnvironmentError("Missing WHOOP credentials")

def fetch_and_store():
    logger.info(f"Starting WHOOP data fetch at {datetime.now(USER_TZ)}")
    try:
        with WhoopClient(USERNAME, PASSWORD) as client:  # type: ignore
            store_sleep(client.get_sleep_collection(), tz=USER_TIMEZONE)
            store_recovery(client.get_recovery_collection(), tz=USER_TIMEZONE)
            store_workout(client.get_workout_collection(), tz=USER_TIMEZONE)
            store_cycle(client.get_cycle_collection(), tz=USER_TIMEZONE)
        logger.info("WHOOP data fetch and store completed successfully.")
    except Exception as e:
        logger.error(f"Error fetching/storing WHOOP data: {e}", exc_info=True)

# -- Parse FETCH_INTERVAL env variable --
FETCH_INTERVAL_RAW = os.getenv("FETCH_INTERVAL", "8hours").lower()

# Regex to split number + unit, e.g. "5hrs" => ("5", "hrs")
match = re.fullmatch(r"(\d+)([a-z]+)", FETCH_INTERVAL_RAW)

if not match:
    logger.warning(f"Invalid FETCH_INTERVAL format '{FETCH_INTERVAL_RAW}', defaulting to 8 hours")
    interval_value, interval_unit = 8, "hours"
else:
    interval_value, interval_unit = int(match.group(1)), match.group(2)

# Map common unit abbreviations to apscheduler argument names
unit_map = {
    "sec": "seconds",
    "secs": "seconds",
    "second": "seconds",
    "seconds": "seconds",

    "min": "minutes",
    "mins": "minutes",
    "minute": "minutes",
    "minutes": "minutes",

    "hr": "hours",
    "hrs": "hours",
    "hour": "hours",
    "hours": "hours",

    "day": "days",
    "days": "days",
}

interval_unit_mapped = unit_map.get(interval_unit)
if not interval_unit_mapped:
    logger.warning(f"Unknown interval unit '{interval_unit}', defaulting to 'hours'")
    interval_unit_mapped = "hours"

scheduler = BackgroundScheduler()

interval_kwargs = {interval_unit_mapped: interval_value}

logger.info(f"Scheduling fetch job every {interval_value} {interval_unit_mapped}")

scheduler.add_job(fetch_and_store, 'interval', **interval_kwargs, id="fetch_job", replace_existing=True) # type: ignore

def start_scheduler():
    scheduler.start()
    logger.info(f"Scheduler started. Fetching data every {interval_value} {interval_unit_mapped}.")

if __name__ == "__main__":
    fetch_and_store()
    start_scheduler()

    import time
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user.")
        scheduler.shutdown()
