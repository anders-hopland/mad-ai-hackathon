"""
Service for integrating AutoQA with the web application
"""

import asyncio
import json
import logging
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from autoqa.core import AutoQA
from autoqa.models import TestCase as AutoQATestCase

from . import crud
from .database import get_db, TestRun

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autoqa-service")


class LogCapture:
    """
    Capture logs from AutoQA and broadcast them via WebSocket
    """

    def __init__(self, test_run_id: str, db: Session, connection_manager):
        self.test_run_id = test_run_id
        self.db = db
        self.connection_manager = connection_manager
        self.logs = []

    async def log(self, message: str):
        """Log a message and broadcast it"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)

        db_test_run = crud.get_test_run(self.db, self.test_run_id)
        if db_test_run:
            crud.create_test_log(self.db, db_test_run.id, message)

        await self.connection_manager.safe_broadcast(
            self.test_run_id,
            {"message": message, "timestamp": timestamp},
            "log"
        )


class AutoQAService:
    """
    Service for running AutoQA tests and managing their state
    """

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.active_runs: Dict[str, Dict[str, Any]] = {}

    async def run_test(self, test_run_id: str, url: str, scenario: str):
        """
        Run an AutoQA test and update the database with results
        """
        # Get database session
        db = next(get_db())

        try:
            # Create log capture
            log_capture = LogCapture(test_run_id, db, self.connection_manager)

            # Get the database test run
            db_test_run = crud.get_test_run(db, test_run_id)
            if not db_test_run:
                await log_capture.log(f"Error: Test run {test_run_id} not found")
                return

            # Update status to 'generating_plan'
            crud.update_test_run_status(db, test_run_id, "generating_plan")
            await self.connection_manager.safe_broadcast(
                test_run_id,
                {
                    "status": "generating_plan",
                    "message": "Generating test plan...",
                },
                "status_update"
            )

            # Initialize AutoQA
            await log_capture.log(f"Initializing AutoQA for URL: {url}")
            autoqa = AutoQA(url=url, scenario=scenario)

            # Create test plan
            await log_capture.log("Creating test plan...")
            test_plan = await autoqa.create_test_plan()

            if not test_plan:
                await log_capture.log("Error: Failed to create test plan")
                crud.update_test_run_status(db, test_run_id, "failed")
                await self.connection_manager.safe_broadcast(
                    test_run_id,
                    {
                        "status": "failed",
                        "message": "Failed to create test plan",
                    },
                    "status_update"
                )
                return

            # Store test plan in database
            await log_capture.log(
                f"Test plan created with {len(test_plan.test_cases)} test cases"
            )
            plan_data = test_plan.to_dict()
            crud.create_test_plan(db, db_test_run.id, plan_data)

            # Create test cases in database
            for tc in test_plan.test_cases:
                crud.create_test_case(
                    db,
                    db_test_run.id,
                    tc.id,
                    tc.description,
                    tc.steps,
                    tc.expected_result,
                )

            # Update status to 'executing_tests'
            crud.update_test_run_status(db, test_run_id, "executing_tests")
            await self.connection_manager.safe_broadcast(
                test_run_id,
                {
                    "status": "executing_tests",
                    "message": "Executing test cases...",
                },
                "status_update"
            )

            # Execute test cases
            await log_capture.log("Executing test cases...")
            for i, tc in enumerate(test_plan.test_cases):
                await log_capture.log(
                    f"Executing test case {tc.id} ({i + 1}/{len(test_plan.test_cases)}): {tc.description}"
                )

                # Notify about current test case
                await self.connection_manager.safe_broadcast(
                    test_run_id,
                    {
                        "tc_id": tc.id,
                        "status": "running",
                        "current": i + 1,
                        "total": len(test_plan.test_cases),
                    },
                    "test_case_update"
                )

                # Execute the test case
                updated_tc = await autoqa.execute_test_case(tc)

                # Update test case in database
                db_test_cases = crud.get_test_cases(db, db_test_run.id)
                for db_tc in db_test_cases:
                    if db_tc.tc_id == updated_tc.id:
                        crud.update_test_case(
                            db,
                            db_tc.id,
                            updated_tc.actual_result or "",
                            updated_tc.status or "ERROR",
                            updated_tc.notes,
                        )
                        break

                # Notify about test case result
                await log_capture.log(
                    f"Test case {tc.id} completed with status: {updated_tc.status}"
                )
                await self.connection_manager.safe_broadcast(
                    test_run_id,
                    {
                        "tc_id": tc.id,
                        "status": updated_tc.status,
                        "actual_result": updated_tc.actual_result,
                        "notes": updated_tc.notes,
                    },
                    "test_case_update"
                )

            # Generate report
            await log_capture.log("Generating test report...")
            report = autoqa.generate_report()

            # Update status to 'completed'
            crud.update_test_run_status(db, test_run_id, "completed")
            await self.connection_manager.safe_broadcast(
                test_run_id,
                {
                    "status": "completed",
                    "message": "Test run completed",
                    "summary": report["summary"],
                },
                "status_update"
            )

            await log_capture.log(
                f"Test run completed. {report['summary']['passed']}/{report['summary']['total_tests']} tests passed."
            )

        except Exception as e:
            logger.error(f"Error running test: {e}")
            await self.connection_manager.safe_broadcast(
                test_run_id,
                {"status": "error", "message": f"Error: {str(e)}"},
                "status_update"
            )
            crud.update_test_run_status(db, test_run_id, "failed")
        finally:
            db.close()
