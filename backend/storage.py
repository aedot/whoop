import os
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from models import SessionLocal, Sleep, Recovery, Workout, Cycle
from logging_config import setup_logging

logger = setup_logging()

# Load default timezone from env, fallback to UTC (same logic as models.py)
timezone_str = os.getenv("USER_TIMEZONE", "UTC")
try:
    DEFAULT_TZ = ZoneInfo(timezone_str)
except ZoneInfoNotFoundError:
    logger.warning(f"Timezone '{timezone_str}' not found, falling back to UTC.")
    DEFAULT_TZ = ZoneInfo("UTC")

def get_current_time(tz: str | None = None) -> datetime:
    """Returns the current time in the given timezone string or default timezone."""
    if tz is None:
        return datetime.now(DEFAULT_TZ)
    try:
        return datetime.now(ZoneInfo(tz))
    except ZoneInfoNotFoundError as e:
        logger.error(f"Invalid timezone '{tz}': {e}. Falling back to default timezone.")
        return datetime.now(DEFAULT_TZ)

def store_sleep(data, tz: str | None = None):
    with SessionLocal() as session:
        sleep_record = Sleep(data=data, fetched_at=get_current_time(tz))
        session.add(sleep_record)
        session.commit()
    logger.info("Stored sleep record")

def store_recovery(data, tz: str | None = None):
    with SessionLocal() as session:
        recovery_record = Recovery(data=data, fetched_at=get_current_time(tz))
        session.add(recovery_record)
        session.commit()
    logger.info("Stored recovery record")

def store_workout(data, tz: str | None = None):
    with SessionLocal() as session:
        workout_record = Workout(data=data, fetched_at=get_current_time(tz))
        session.add(workout_record)
        session.commit()
    logger.info("Stored workout record")

def store_cycle(data, tz: str | None = None):
    with SessionLocal() as session:
        cycle_record = Cycle(data=data, fetched_at=get_current_time(tz))
        session.add(cycle_record)
        session.commit()
    logger.info("Stored cycle record")
