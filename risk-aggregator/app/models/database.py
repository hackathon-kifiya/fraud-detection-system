"""
Database models and connection management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# ============================================================================
# Database Models
# ============================================================================


class RiskAssessment(Base):
    """Risk assessment database model."""

    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String, index=True, nullable=False)
    entity_type = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    components = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AggregationJob(Base):
    """Aggregation job database model."""

    __tablename__ = "aggregation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    job_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    total_entities = Column(Integer, nullable=False)
    processed_entities = Column(Integer, default=0)
    successful = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    entity_type = Column(String, nullable=False)
    configuration = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class RiskCache(Base):
    """Risk cache database model for temporary storage."""

    __tablename__ = "risk_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, unique=True, index=True, nullable=False)
    entity_id = Column(String, index=True, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    data = Column(JSON, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# Database Utilities
# ============================================================================


def get_db() -> Session:
    """
    Get database session.

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)

