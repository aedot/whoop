from sqlalchemy import create_engine, Column, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

Base = declarative_base()

PACIFIC_TZ = ZoneInfo("America/Los_Angeles")

class WhoopBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    fetched_at = Column(DateTime, default=lambda: datetime.now(PACIFIC_TZ))

class Sleep(WhoopBase):
    __tablename__ = 'sleep'

class Recovery(WhoopBase):
    __tablename__ = 'recovery'

class Workout(WhoopBase):
    __tablename__ = 'workout'

class Cycle(WhoopBase):
    __tablename__ = 'cycle'

DATABASE_URL = "sqlite:///data/whoop.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db():
    Base.metadata.create_all(bind=engine)
