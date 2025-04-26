from langchain_openai import ChatOpenAI
from browser_use import Agent, BrowserUseOutput
from dotenv import load_dotenv
import asyncio
import json
from typing import List, Dict, Any, Optional

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

class TestCase:
    def __init__(self, id: str, description: str, steps: List[str], expected_result: str):
        self.id = id
        self.description = description
        self.steps = steps
        self.expected_result = expected_result
        self.actual_result: Optional[str] = None
        self.status: Optional[str] = None  # "PASS", "FAIL", or "ERROR"
        self.notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "steps": self.steps,
            "expected_result": self.expected_result,
            "actual_result": self.actual_result,
            "status": self.status,
            "notes": self.notes
        }

class TestPlan:
    def __init__(self, url: str, scenario: str, test_cases: List[TestCase] = None):
        self.url = url
        self.scenario = scenario
        self.test_cases = test_cases or []

    def add_test_case(self, test_case: TestCase):
        self.test_cases.append(test_case)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "scenario": self.scenario,
            "test_cases": [tc.to_dict() for tc in self.test_cases]
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

class AutoQA:
    def __init__(self, url: str, scenario: str):
        self.url = url
        self.scenario = scenario
        self.test_plan = TestPlan(url, scenario)
        self.results = []

    async def create_test_plan(self):
        """Generate a test plan by exploring the website"""
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

        agent = Agent(
            task=planning_prompt,
            llm=llm,
            output_format=BrowserUseOutput.JSON
        )
        result = await agent.run()
        
        # Parse the JSON result
        try:
            test_plan_data = json.loads(result.final_result())
            for tc_data in test_plan_data.get("test_cases", []):
                test_case = TestCase(
                    id=tc_data.get("id", ""),
                    description=tc_data.get("description", ""),
                    steps=tc_data.get("steps", []),
                    expected_result=tc_data.get("expected_result", "")
                )
                self.test_plan.add_test_case(test_case)
            return self.test_plan
        except json.JSONDecodeError:
            print("Error: Could not parse test plan JSON")
            return None

    async def execute_test_case(self, test_case: TestCase):
        """Execute a single test case and record the results"""
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

        agent = Agent(
            task=execution_prompt,
            llm=llm,
            output_format=BrowserUseOutput.JSON
        )
        result = await agent.run()
        
        # Parse the JSON result
        try:
            execution_result = json.loads(result.final_result())
            test_case.actual_result = execution_result.get("actual_result", "")
            test_case.status = execution_result.get("status", "ERROR")
            test_case.notes = execution_result.get("notes", "")
            return test_case
        except json.JSONDecodeError:
            print(f"Error: Could not parse execution result JSON for test case {test_case.id}")
            test_case.status = "ERROR"
            test_case.notes = "Error parsing execution result"
            return test_case

    async def execute_all_tests(self):
        """Execute all test cases in the test plan"""
        for test_case in self.test_plan.test_cases:
            updated_test_case = await self.execute_test_case(test_case)
            self.results.append(updated_test_case)
        return self.results

    def generate_report(self):
        """Generate a summary report of all test results"""
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
                "pass_rate": f"{(passed/total_tests)*100:.2f}%" if total_tests > 0 else "0%"
            },
            "test_results": [tc.to_dict() for tc in self.results]
        }
        
        return json.dumps(report, indent=2)

async def main():
    # Get user input
    url = input("Enter the URL to test: ")
    scenario = input("Enter the test scenario: ")
    
    # Create and run the AutoQA system
    auto_qa = AutoQA(url, scenario)
    
    print("\n--- PHASE 1: Creating Test Plan ---")
    test_plan = await auto_qa.create_test_plan()
    print("Test Plan Created:")
    print(test_plan.to_json())
    
    print("\n--- PHASE 2: Executing Tests ---")
    await auto_qa.execute_all_tests()
    
    print("\n--- PHASE 3: Test Results Report ---")
    report = auto_qa.generate_report()
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
