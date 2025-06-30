"""
Database configuration and models for AutoQA Web Application using SQLModel
"""

from sqlmodel import Field, Session, SQLModel, create_engine, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from pydantic import HttpUrl

# Create SQLite database engine
# Using SQLite for development, can be easily switched to PostgreSQL later
DATABASE_URL = "sqlite:///./autoqa.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# Database Models
class User(SQLModel, table=True):
    """Model representing a user"""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    picture: Optional[str] = None
    google_id: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    test_runs: List["TestRun"] = Relationship(back_populates="user")


class TestPlan(SQLModel, table=True):
    """Model representing a test plan"""

    __tablename__ = "test_plans"

    id: Optional[int] = Field(default=None, primary_key=True)
    test_run_id: int = Field(foreign_key="test_runs.id", unique=True)
    plan_json: Optional[str] = None  # JSON representation of the test plan
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    test_run: "TestRun" = Relationship(back_populates="test_plan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "plan": json.loads(self.plan_json) if self.plan_json else None,
            "generated_at": self.generated_at.isoformat(),
        }


class TestCase(SQLModel, table=True):
    """Model representing a test case"""

    __tablename__ = "test_cases"

    id: Optional[int] = Field(default=None, primary_key=True)
    test_run_id: int = Field(foreign_key="test_runs.id")
    tc_id: str  # e.g., "TC001"
    description: str
    steps: str  # JSON array of steps
    expected_result: str
    actual_result: Optional[str] = None
    status: str = "pending"  # PASS, FAIL, ERROR, pending
    notes: Optional[str] = None
    executed_at: Optional[datetime] = None

    # Relationships
    test_run: "TestRun" = Relationship(back_populates="test_cases")

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


class TestLog(SQLModel, table=True):
    """Model representing test logs"""

    __tablename__ = "test_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    test_run_id: int = Field(foreign_key="test_runs.id")
    log_text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    test_run: "TestRun" = Relationship(back_populates="logs")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "log_text": self.log_text,
            "timestamp": self.timestamp.isoformat(),
        }


class TestRun(SQLModel, table=True):
    """Model representing a test run"""

    __tablename__ = "test_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(unique=True, index=True)  # External ID for API
    user_id: int = Field(foreign_key="users.id")
    url: str
    scenario: str
    status: str = "in_progress"  # in_progress, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="test_runs")
    test_plan: Optional[TestPlan] = Relationship(
        back_populates="test_run", sa_relationship_kwargs={"uselist": False}
    )
    test_cases: List[TestCase] = Relationship(back_populates="test_run")
    logs: List[TestLog] = Relationship(back_populates="test_run")


# Create all tables in the database
def init_db():
    """Initialize the database by creating all tables"""
    SQLModel.metadata.create_all(engine)


# Get a database session
def get_db():
    """Get a database session"""
    with Session(engine) as session:
        yield session
