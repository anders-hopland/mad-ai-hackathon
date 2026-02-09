"""
Database configuration and models for AutoQA Web Application using SQLAlchemy
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

# Create SQLite database engine
# Using SQLite for development, can be easily switched to PostgreSQL later
DATABASE_URL = "sqlite:///./autoqa.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create declarative base
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Database Models
class User(Base):
    """Model representing a user"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    google_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_runs = relationship("TestRun", back_populates="user")


class TestPlan(Base):
    """Model representing a test plan"""

    __tablename__ = "test_plans"

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), unique=True, nullable=False)
    plan_json = Column(Text, nullable=True)  # JSON representation of the test plan
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="test_plan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "plan": json.loads(self.plan_json) if self.plan_json else None,
            "generated_at": self.generated_at.isoformat(),
        }


class TestCase(Base):
    """Model representing a test case"""

    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)
    tc_id = Column(String, nullable=False)  # e.g., "TC001"
    description = Column(Text, nullable=False)
    steps = Column(Text, nullable=False)  # JSON array of steps
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=True)
    status = Column(String, default="pending")  # PASS, FAIL, ERROR, pending
    notes = Column(Text, nullable=True)
    executed_at = Column(DateTime, nullable=True)

    # Relationships
    test_run = relationship("TestRun", back_populates="test_cases")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.tc_id,
            "description": self.description,
            "steps": json.loads(self.steps),
            "expected_result": self.expected_result,
            "actual_result": self.actual_result,
            "status": self.status,
            "notes": self.notes,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }


class TestLog(Base):
    """Model representing test logs"""

    __tablename__ = "test_logs"

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)
    log_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="logs")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "log_text": self.log_text,
            "timestamp": self.timestamp.isoformat(),
        }


class TestRun(Base):
    """Model representing a test run"""

    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True, nullable=False)  # External ID for API
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    scenario = Column(Text, nullable=False)
    status = Column(String, default="in_progress")  # in_progress, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="test_runs")
    test_plan = relationship("TestPlan", back_populates="test_run", uselist=False)
    test_cases = relationship("TestCase", back_populates="test_run")
    logs = relationship("TestLog", back_populates="test_run")


# Create all tables in the database
def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(bind=engine)


# Get a database session
def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
