"""Data models for the AutoQA system."""

import json
from typing import List, Dict, Any, Optional


class TestCase:
    """Represents a single test case with steps and results."""

    def __init__(
        self, id: str, description: str, steps: List[str], expected_result: str
    ):
        self.id = id
        self.description = description
        self.steps = steps
        self.expected_result = expected_result
        self.actual_result: Optional[str] = None
        self.status: Optional[str] = None  # "PASS", "FAIL", or "ERROR"
        self.notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the test case to a dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "steps": self.steps,
            "expected_result": self.expected_result,
            "actual_result": self.actual_result,
            "status": self.status,
            "notes": self.notes,
        }


class TestPlan:
    """Collection of test cases for a specific URL and scenario."""

    def __init__(self, url: str, scenario: str, test_cases: List[TestCase] = None):
        self.url = url
        self.scenario = scenario
        self.test_cases = test_cases or []

    def add_test_case(self, test_case: TestCase):
        """Add a test case to the test plan."""
        self.test_cases.append(test_case)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the test plan to a dictionary."""
        return {
            "url": self.url,
            "scenario": self.scenario,
            "test_cases": [tc.to_dict() for tc in self.test_cases],
        }

    def to_json(self) -> str:
        """Convert the test plan to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)
