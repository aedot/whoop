from models import SessionLocal, Sleep, Recovery, Workout, Cycle
from datetime import datetime
from zoneinfo import ZoneInfo
from logging_config import setup_logging

logger = setup_logging()
PACIFIC_TZ = ZoneInfo("America/Los_Angeles")

def store_sleep(data):
    with SessionLocal() as session:
        sleep_record = Sleep(data=data, fetched_at=datetime.now(PACIFIC_TZ))
        session.add(sleep_record)
        session.commit()
    logger.info("Stored sleep record")

def store_recovery(data):
    with SessionLocal() as session:
        recovery_record = Recovery(data=data, fetched_at=datetime.now(PACIFIC_TZ))
        session.add(recovery_record)
        session.commit()
    logger.info("Stored recovery record")

def store_workout(data):
    with SessionLocal() as session:
        workout_record = Workout(data=data, fetched_at=datetime.now(PACIFIC_TZ))
        session.add(workout_record)
        session.commit()
    logger.info("Stored workout record")

def store_cycle(data):
    with SessionLocal() as session:
        cycle_record = Cycle(data=data, fetched_at=datetime.now(PACIFIC_TZ))
        session.add(cycle_record)
        session.commit()
    logger.info("Stored cycle record")
