"""
CRUD operations for AutoQA Web Application using SQLAlchemy
"""

from sqlalchemy.orm import Session
from datetime import datetime
import json
import uuid
from typing import List, Dict, Any, Optional

from .database import TestRun, TestPlan, TestCase, TestLog


# Test Run operations
def create_test_run(db: Session, user_id: int, url: str, scenario: str) -> TestRun:
    """
    Create a new test run in the database
    """
    run_id = f"run-{uuid.uuid4().hex[:8]}"
    db_test_run = TestRun(
        run_id=run_id,
        user_id=user_id,
        url=url,
        scenario=scenario,
        status="in_progress",
    )
    db.add(db_test_run)
    db.commit()
    db.refresh(db_test_run)
    return db_test_run


def get_test_run(db: Session, run_id: str) -> Optional[TestRun]:
    """
    Get a test run by its run_id
    """
    return db.query(TestRun).filter(TestRun.run_id == run_id).first()


def get_test_runs(db: Session, skip: int = 0, limit: int = 100) -> List[TestRun]:
    """
    Get all test runs with pagination
    """
    return db.query(TestRun).order_by(TestRun.created_at.desc()).offset(skip).limit(limit).all()


def get_user_test_runs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[TestRun]:
    """
    Get test runs for a specific user with pagination
    """
    return db.query(TestRun).filter(TestRun.user_id == user_id).order_by(TestRun.created_at.desc()).offset(skip).limit(limit).all()


def update_test_run_status(db: Session, run_id: str, status: str) -> Optional[TestRun]:
    """
    Update the status of a test run
    """
    db_test_run = get_test_run(db, run_id)
    if db_test_run:
        db_test_run.status = status
        db_test_run.updated_at = datetime.utcnow()
        db.add(db_test_run)
        db.commit()
        db.refresh(db_test_run)
    return db_test_run


# Test Plan operations
def create_test_plan(
    db: Session, test_run_id: int, plan_data: Dict[str, Any]
) -> TestPlan:
    """
    Create a test plan for a test run
    """
    plan_json = json.dumps(plan_data)
    db_test_plan = TestPlan(
        test_run_id=test_run_id,
        plan_json=plan_json,
    )
    db.add(db_test_plan)
    db.commit()
    db.refresh(db_test_plan)
    return db_test_plan


def get_test_plan(db: Session, test_run_id: int) -> Optional[TestPlan]:
    """
    Get the test plan for a test run
    """
    return db.query(TestPlan).filter(TestPlan.test_run_id == test_run_id).first()


# Test Case operations
def create_test_case(
    db: Session,
    test_run_id: int,
    tc_id: str,
    description: str,
    steps: List[str],
    expected_result: str,
) -> TestCase:
    """
    Create a test case for a test run
    """
    steps_json = json.dumps(steps)
    db_test_case = TestCase(
        test_run_id=test_run_id,
        tc_id=tc_id,
        description=description,
        steps=steps_json,
        expected_result=expected_result,
    )
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case


def get_test_cases(db: Session, test_run_id: int) -> List[TestCase]:
    """
    Get all test cases for a test run
    """
    return db.query(TestCase).filter(TestCase.test_run_id == test_run_id).all()


def update_test_case(
    db: Session,
    test_case_id: int,
    actual_result: str,
    status: str,
    notes: Optional[str] = None,
) -> Optional[TestCase]:
    """
    Update a test case with results
    """
    db_test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if db_test_case:
        db_test_case.actual_result = actual_result
        db_test_case.status = status
        db_test_case.notes = notes
        db_test_case.executed_at = datetime.utcnow()
        db.add(db_test_case)
        db.commit()
        db.refresh(db_test_case)
    return db_test_case


# Test Log operations
def create_test_log(db: Session, test_run_id: int, log_text: str) -> TestLog:
    """
    Create a log entry for a test run
    """
    db_test_log = TestLog(
        test_run_id=test_run_id,
        log_text=log_text,
    )
    db.add(db_test_log)
    db.commit()
    db.refresh(db_test_log)
    return db_test_log


def get_test_logs(db: Session, test_run_id: int) -> List[TestLog]:
    """
    Get all logs for a test run
    """
    return db.query(TestLog).filter(TestLog.test_run_id == test_run_id).order_by(TestLog.timestamp).all()
