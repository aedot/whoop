from flask import Flask, jsonify, make_response
from models import SessionLocal, init_db, Sleep, Recovery, Workout, Cycle
from scheduler import start_scheduler, fetch_and_store
from dotenv import load_dotenv
from logging_config import setup_logging
import os

load_dotenv()

logger = setup_logging()
app = Flask(__name__)

def fetch_records(model, limit=10):
    """Helper to fetch records with error handling."""
    try:
        with SessionLocal() as session:
            records = session.query(model).order_by(model.fetched_at.desc()).limit(limit).all()
        logger.info(f"Returned {len(records)} records from {model.__tablename__}")
        return jsonify([r.data for r in records])
    except Exception as e:
        logger.error(f"Failed to fetch records from {model.__tablename__}: {e}", exc_info=True)
        return make_response(jsonify({"error": "Internal Server Error"}), 500)

@app.route('/api/sleep')
def get_sleep():
    return fetch_records(Sleep)

@app.route('/api/recovery')
def get_recovery():
    return fetch_records(Recovery)

@app.route('/api/workout')
def get_workout():
    return fetch_records(Workout)

@app.route('/api/cycle')
def get_cycle():
    return fetch_records(Cycle)

if __name__ == "__main__":
    logger.info("Initializing database schema...")
    init_db()

    logger.info("Running initial WHOOP data fetch...")
    try:
        fetch_and_store()
    except Exception as e:
        logger.error(f"Initial fetch failed: {e}", exc_info=True)

    logger.info("Starting scheduler for periodic WHOOP data fetches...")
    start_scheduler()

    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=4000, debug=debug_mode)
