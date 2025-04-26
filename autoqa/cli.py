"""Command-line interface for the AutoQA system."""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from autoqa.core import AutoQA
from autoqa.report import generate_markdown_report


async def main():
    """Main entry point for the AutoQA CLI."""
    # Load environment variables
    load_dotenv()
    
    # Initialize the Gemini Flash LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")
    
    # Get user input
    url = input("Enter the URL to test: ")
    scenario = input("Enter the test scenario: ")
    
    # Create and run the AutoQA system
    auto_qa = AutoQA(url, scenario, llm=llm)
    
    print("\n--- PHASE 1: Creating Test Plan ---")
    test_plan = await auto_qa.create_test_plan()
    print("Test Plan Created:")
    print(test_plan.to_json())
    
    print("\n--- PHASE 2: Executing Tests ---")
    await auto_qa.execute_all_tests()
    
    print("\n--- PHASE 3: Test Results Report ---")
    report = auto_qa.generate_report()
    print(report)
    
    # Save the JSON report to a file
    os.makedirs('data', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_report_path = f'data/test_result_{timestamp}.json'
    with open(json_report_path, 'w') as f:
        f.write(report)
    print(f"\nJSON report saved to {json_report_path}")
    
    # Generate and save the markdown report
    md_report_path = f'data/test_result_{timestamp}.md'
    markdown_report = generate_markdown_report(json_report_path, md_report_path)
    print(f"Markdown report saved to {md_report_path}")


if __name__ == "__main__":
    asyncio.run(main())
