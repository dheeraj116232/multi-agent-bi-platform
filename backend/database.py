"""
database.py — PostgreSQL connection + table definitions
"""

import os
import json
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, String, Integer,
    Float, Text, DateTime, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fix for Neon SSL requirement
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1
    )

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ── Tables ────────────────────────────────────────────────────────────────────

class JobRecord(Base):
    __tablename__ = "jobs"

    id              = Column(String, primary_key=True)   # job_id (UUID)
    filename        = Column(String, nullable=False)
    status          = Column(String, default="pending")  # pending|running|done|failed
    progress_pct    = Column(Integer, default=0)
    current_agent   = Column(String, nullable=True)
    error           = Column(Text, nullable=True)

    # Results stored as JSON
    cleaning_report = Column(JSON, nullable=True)
    analytics       = Column(JSON, nullable=True)
    forecast        = Column(JSON, nullable=True)
    chart_paths     = Column(JSON, nullable=True)
    chart_metadata  = Column(JSON, nullable=True)
    report_text     = Column(Text, nullable=True)
    pdf_path        = Column(String, nullable=True)
    file_meta       = Column(JSON, nullable=True)
    processing_time = Column(JSON, nullable=True)
    warnings        = Column(JSON, nullable=True)
    errors_list     = Column(JSON, nullable=True)

    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def create_tables():
    """Create all tables in Neon PostgreSQL."""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def get_db():
    """Dependency — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()