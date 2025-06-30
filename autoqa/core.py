"""Core functionality for the AutoQA system."""

import json
import re
import time
from typing import List, Dict, Any
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent

from autoqa.models import TestCase, TestPlan


class AutoQA:
    """Main class for automated web testing."""

    def __init__(self, url: str, scenario: str, llm=None):
        self.url = url
        self.scenario = scenario
        self.test_plan = TestPlan(url, scenario)
        self.results = []
        self.llm = llm or ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")
        self.timing = {
            "planning": {"start": None, "end": None, "duration": None},
            "execution": {"start": None, "end": None, "duration": None, "tests": {}},
            "total": {"start": None, "end": None, "duration": None},
        }

    async def create_test_plan(self):
        """Generate a test plan by exploring the website."""
        # Start timing for planning phase
        self.timing["planning"]["start"] = datetime.now().isoformat()
        self.timing["total"]["start"] = self.timing["planning"]["start"]
        start_time = time.time()

        planning_prompt = f"""You are an expert web QA engineer with access to a browser. 
        
Your task is to explore a website and create a structured test plan for a specific feature.

Website: {self.url}
Scenario: {self.scenario}

First, explore the website to understand how the feature works:
1. Visit the website and navigate to where the feature is used
2. Observe the UI elements and interactions related to the feature
3. Understand the normal user flow and potential edge cases

Then, create a structured test plan with the following format:
```json
{{
  "test_cases": [
    {{
      "id": "TC001",
      "description": "Brief description of test case",
      "steps": [
        "Step 1: Detailed instruction",
        "Step 2: Detailed instruction",
        ...
      ],
      "expected_result": "What should happen if the test passes"
    }},
    ...
  ]
}}
```

Include at least 4-6 test cases, covering:
- Basic functionality (normal usage)
- Edge cases (invalid inputs, boundary conditions)
- Error handling (how the system responds to incorrect usage)

IMPORTANT: You must output ONLY the JSON test plan in the exact format shown above. No additional text or explanations.
"""

        # Use standard JSON output
        agent = Agent(task=planning_prompt, llm=self.llm)
        result = await agent.run()

        # End timing for planning phase
        self.timing["planning"]["end"] = datetime.now().isoformat()
        self.timing["planning"]["duration"] = round(time.time() - start_time, 2)

        # Parse the JSON result
        try:
            # Get the final result as a string
            result_str = result.final_result()

            # Save the raw output for debugging
            with open("autoqa/test_plan.json", "w") as f:
                f.write(result_str)

            # Try to parse as JSON
            try:
                # First try parsing directly
                test_plan_data = json.loads(result_str)

                # Check if test_cases is a top-level key
                if "test_cases" in test_plan_data:
                    test_cases = test_plan_data["test_cases"]
                # Check if it's in a nested structure (browser-use sometimes wraps output)
                elif isinstance(test_plan_data, list) and len(test_plan_data) > 0:
                    for item in test_plan_data:
                        if isinstance(item, dict) and "test_cases" in item:
                            test_cases = item["test_cases"]
                            break
                        elif (
                            isinstance(item, dict)
                            and "done" in item
                            and "data" in item["done"]
                            and "test_cases" in item["done"]["data"]
                        ):
                            test_cases = item["done"]["data"]["test_cases"]
                            break
                else:
                    # Fallback - try to find any list that looks like test cases
                    for key, value in test_plan_data.items():
                        if (
                            isinstance(value, list)
                            and len(value) > 0
                            and isinstance(value[0], dict)
                            and "id" in value[0]
                        ):
                            test_cases = value
                            break
                    else:
                        raise ValueError("Could not find test_cases in the output")

                # Process the test cases
                for tc_data in test_cases:
                    test_case = TestCase(
                        id=tc_data.get("id", ""),
                        description=tc_data.get("description", ""),
                        steps=tc_data.get("steps", []),
                        expected_result=tc_data.get("expected_result", ""),
                    )
                    self.test_plan.add_test_case(test_case)

                return self.test_plan
            except json.JSONDecodeError:
                # If direct JSON parsing fails, try to extract JSON from the text
                import re

                json_match = re.search(r"\{[\s\S]*\}", result_str)
                if json_match:
                    test_plan_data = json.loads(json_match.group(0))
                    if "test_cases" in test_plan_data:
                        test_cases = test_plan_data["test_cases"]
                        for tc_data in test_cases:
                            test_case = TestCase(
                                id=tc_data.get("id", ""),
                                description=tc_data.get("description", ""),
                                steps=tc_data.get("steps", []),
                                expected_result=tc_data.get("expected_result", ""),
                            )
                            self.test_plan.add_test_case(test_case)
                        return self.test_plan

                raise ValueError("Could not extract valid JSON from the output")
        except Exception as e:
            print("Error: Could not parse test plan JSON")
            print(e)
            return None

    async def execute_test_case(self, test_case: TestCase):
        """Execute a single test case and record the results."""
        # Start timing for this test case
        test_id = test_case.id
        self.timing["execution"]["tests"][test_id] = {
            "start": datetime.now().isoformat(),
            "end": None,
            "duration": None,
        }
        start_time = time.time()

        execution_prompt = f"""You are an expert web QA tester with access to a browser.

Your task is to execute a specific test case and determine if it passes or fails.

Website: {self.url}
Test Case ID: {test_case.id}
Description: {test_case.description}

Steps to execute:
{chr(10).join(f"- {step}" for step in test_case.steps)}

Expected Result: {test_case.expected_result}

Execute these steps precisely and report the outcome in this format:
```json
{{
  "actual_result": "Detailed description of what actually happened",
  "status": "PASS/FAIL/ERROR",
  "notes": "Any additional observations or notes about the execution"
}}
```

IMPORTANT: You must output ONLY the JSON result in the exact format shown above. No additional text or explanations.
"""

        # Use standard JSON output
        agent = Agent(task=execution_prompt, llm=self.llm)
        result = await agent.run()

        # Parse the result
        try:
            # End timing for this test case
            self.timing["execution"]["tests"][test_id][
                "end"
            ] = datetime.now().isoformat()
            self.timing["execution"]["tests"][test_id]["duration"] = round(
                time.time() - start_time, 2
            )

            # Get the final result as a string
            result_str = result.final_result()

            # Save the raw output for debugging
            with open(f"autoqa/test_result_{test_case.id}.json", "w") as f:
                f.write(result_str)

            # Try to parse as JSON
            try:
                # First try parsing directly
                execution_data = json.loads(result_str)

                # Handle different possible structures
                if (
                    isinstance(execution_data, dict)
                    and "actual_result" in execution_data
                    and "status" in execution_data
                ):
                    # Direct format
                    test_case.actual_result = execution_data.get("actual_result", "")
                    test_case.status = execution_data.get("status", "ERROR")
                    test_case.notes = execution_data.get("notes", "")
                elif isinstance(execution_data, list) and len(execution_data) > 0:
                    # Nested format
                    for item in execution_data:
                        if (
                            isinstance(item, dict)
                            and "done" in item
                            and "data" in item["done"]
                        ):
                            data = item["done"]["data"]
                            if (
                                isinstance(data, dict)
                                and "actual_result" in data
                                and "status" in data
                            ):
                                test_case.actual_result = data.get("actual_result", "")
                                test_case.status = data.get("status", "ERROR")
                                test_case.notes = data.get("notes", "")
                                break
                        elif (
                            isinstance(item, dict)
                            and "actual_result" in item
                            and "status" in item
                        ):
                            test_case.actual_result = item.get("actual_result", "")
                            test_case.status = item.get("status", "ERROR")
                            test_case.notes = item.get("notes", "")
                            break
                else:
                    # Try to find relevant keys at any level
                    def extract_result(data):
                        if isinstance(data, dict):
                            if "actual_result" in data and "status" in data:
                                return data
                            for key, value in data.items():
                                result = extract_result(value)
                                if result:
                                    return result
                        elif isinstance(data, list):
                            for item in data:
                                result = extract_result(item)
                                if result:
                                    return result
                        return None

                    result_data = extract_result(execution_data)
                    if result_data:
                        test_case.actual_result = result_data.get("actual_result", "")
                        test_case.status = result_data.get("status", "ERROR")
                        test_case.notes = result_data.get("notes", "")
                    else:
                        raise ValueError(
                            "Could not find execution result data in the output"
                        )

            except json.JSONDecodeError:
                # If direct JSON parsing fails, try to extract JSON from the text
                import re

                json_match = re.search(r"\{[\s\S]*\}", result_str)
                if json_match:
                    try:
                        execution_data = json.loads(json_match.group(0))
                        if (
                            "actual_result" in execution_data
                            and "status" in execution_data
                        ):
                            test_case.actual_result = execution_data.get(
                                "actual_result", ""
                            )
                            test_case.status = execution_data.get("status", "ERROR")
                            test_case.notes = execution_data.get("notes", "")
                        else:
                            raise ValueError(
                                "Could not find execution result data in the extracted JSON"
                            )
                    except json.JSONDecodeError:
                        raise ValueError("Could not parse the extracted JSON")
                else:
                    raise ValueError("Could not extract JSON from the output")

            return test_case
        except Exception as e:
            print(
                f"Error: Could not process execution result for test case {test_case.id}"
            )
            print(e)
            test_case.status = "ERROR"
            test_case.notes = f"Error processing execution result: {str(e)}"
            return test_case

    async def execute_all_tests(self):
        """Execute all test cases in the test plan."""
        # Start timing for execution phase
        self.timing["execution"]["start"] = datetime.now().isoformat()
        start_time = time.time()

        for test_case in self.test_plan.test_cases:
            updated_test_case = await self.execute_test_case(test_case)
            self.results.append(updated_test_case)

        # End timing for execution phase
        self.timing["execution"]["end"] = datetime.now().isoformat()
        self.timing["execution"]["duration"] = round(time.time() - start_time, 2)

        return self.results

    def generate_report(self):
        """Generate a summary report of all test results."""
        # End timing for total execution
        self.timing["total"]["end"] = datetime.now().isoformat()
        self.timing["total"]["duration"] = round(
            sum(
                [
                    self.timing["planning"]["duration"] or 0,
                    self.timing["execution"]["duration"] or 0,
                ]
            ),
            2,
        )

        total_tests = len(self.results)
        passed = sum(1 for tc in self.results if tc.status == "PASS")
        failed = sum(1 for tc in self.results if tc.status == "FAIL")
        errors = sum(1 for tc in self.results if tc.status == "ERROR")

        report = {
            "summary": {
                "url": self.url,
                "scenario": self.scenario,
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "pass_rate": (
                    f"{(passed/total_tests)*100:.2f}%" if total_tests > 0 else "0%"
                ),
                "timing": {
                    "planning_seconds": self.timing["planning"]["duration"],
                    "execution_seconds": self.timing["execution"]["duration"],
                    "total_seconds": self.timing["total"]["duration"],
                },
            },
            "test_results": [tc.to_dict() for tc in self.results],
            "timing": self.timing,
        }

        return json.dumps(report, indent=2)
