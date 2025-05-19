import os
from sqlalchemy import create_engine, Column, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # Python 3.9+

Base = declarative_base()

# Get timezone from environment variable USER_TIMEZONE, fallback to UTC
timezone_str = os.getenv("USER_TIMEZONE", "UTC")

try:
    DEFAULT_TZ = ZoneInfo(timezone_str)
except ZoneInfoNotFoundError:
    print(f"Warning: Timezone '{timezone_str}' not found, falling back to UTC.")
    DEFAULT_TZ = ZoneInfo("UTC")

class WhoopBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    fetched_at = Column(DateTime, nullable=False)

    def __init__(self, data, tz: ZoneInfo | None = None, fetched_at: datetime | None = None):
        tz = tz or DEFAULT_TZ
        self.fetched_at = fetched_at or datetime.now(tz)
        self.data = data

class Sleep(WhoopBase):
    __tablename__ = 'sleep'

class Recovery(WhoopBase):
    __tablename__ = 'recovery'

class Workout(WhoopBase):
    __tablename__ = 'workout'

class Cycle(WhoopBase):
    __tablename__ = 'cycle'

DATABASE_URL = "sqlite:///whoop.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db():
    Base.metadata.create_all(bind=engine)
