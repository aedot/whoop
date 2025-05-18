import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from whoop_client import WhoopClient
from storage import store_sleep, store_recovery, store_workout, store_cycle
from logging_config import setup_logging
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# Load .env file
load_dotenv()

# Setup
logger = setup_logging()
PACIFIC = ZoneInfo("America/Los_Angeles")

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
FETCH_INTERVAL_HOURS = int(os.getenv("FETCH_INTERVAL_HOURS", 8))

if not USERNAME or not PASSWORD:
    logger.error("WHOOP USERNAME and PASSWORD must be set in environment variables.")
    raise EnvironmentError("Missing WHOOP credentials")

def fetch_and_store():
    logger.info(f"Starting WHOOP data fetch at {datetime.now(PACIFIC)}")
    try:
        with WhoopClient(USERNAME, PASSWORD) as client: # type: ignore
            store_sleep(client.get_sleep_collection())
            logger.info("Stored sleep data")

            store_recovery(client.get_recovery_collection())
            logger.info("Stored recovery data")

            store_workout(client.get_workout_collection())
            logger.info("Stored workout data")

            store_cycle(client.get_cycle_collection())
            logger.info("Stored cycle data")

        logger.info("WHOOP data fetch and store completed successfully.")
    except Exception as e:
        logger.error(f"Error fetching/storing WHOOP data: {e}", exc_info=True)

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store, 'interval', hours=FETCH_INTERVAL_HOURS, id="fetch_job", replace_existing=True)

def start_scheduler():
    scheduler.start()
    logger.info(f"Scheduler started. Fetching data every {FETCH_INTERVAL_HOURS} hour(s).")

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
