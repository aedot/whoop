from flask import Flask, jsonify
from models import SessionLocal, init_db, Sleep, Recovery, Workout, Cycle
from scheduler import start_scheduler, fetch_and_store
from dotenv import load_dotenv
from logging_config import setup_logging
import os

load_dotenv()

logger = setup_logging()
app = Flask(__name__)

@app.route('/api/sleep')
def get_sleep():
    session = SessionLocal()
    records = session.query(Sleep).order_by(Sleep.fetched_at.desc()).limit(10).all()
    session.close()
    logger.info(f"Returned {len(records)} sleep records")
    return jsonify([r.data for r in records])

@app.route('/api/recovery')
def get_recovery():
    session = SessionLocal()
    records = session.query(Recovery).order_by(Recovery.fetched_at.desc()).limit(10).all()
    session.close()
    logger.info(f"Returned {len(records)} recovery records")
    return jsonify([r.data for r in records])

@app.route('/api/workout')
def get_workout():
    session = SessionLocal()
    records = session.query(Workout).order_by(Workout.fetched_at.desc()).limit(10).all()
    session.close()
    logger.info(f"Returned {len(records)} workout records")
    return jsonify([r.data for r in records])

@app.route('/api/cycle')
def get_cycle():
    session = SessionLocal()
    records = session.query(Cycle).order_by(Cycle.fetched_at.desc()).limit(10).all()
    session.close()
    logger.info(f"Returned {len(records)} cycle records")
    return jsonify([r.data for r in records])

if __name__ == "__main__":
    logger.info("Initializing database schema...")
    init_db()

    logger.info("Running initial WHOOP data fetch...")
    fetch_and_store()

    logger.info("Starting scheduler for periodic WHOOP data fetches...")
    start_scheduler()

    app.run(host="0.0.0.0", port=4000, debug=True)
