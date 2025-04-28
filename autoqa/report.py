"""Generate markdown reports from test results."""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


def generate_markdown_report(results_file: str, output_file: Optional[str] = None) -> str:
    """
    Generate a markdown report from a test results JSON file.
    
    Args:
        results_file: Path to the JSON file containing test results
        output_file: Optional path to save the markdown report
        
    Returns:
        The markdown report as a string
    """
    # Load the test results
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Extract summary data
    summary = results.get('summary', {})
    url = summary.get('url', 'Unknown')
    scenario = summary.get('scenario', 'Unknown')
    total_tests = summary.get('total_tests', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    errors = summary.get('errors', 0)
    pass_rate = summary.get('pass_rate', '0%')
    
    # Extract timing data
    timing = summary.get('timing', {})
    planning_time = timing.get('planning_seconds', 0)
    execution_time = timing.get('execution_seconds', 0)
    total_time = timing.get('total_seconds', 0)
    
    # Get detailed test timing
    detailed_timing = results.get('timing', {})
    test_timing = detailed_timing.get('execution', {}).get('tests', {})
    
    # Create the markdown report
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Start building the markdown content
    markdown = f"""# Test Results Report

## Summary

{'✅' if failed == 0 and errors == 0 else '❌'} **Overall Result: {'PASS' if failed == 0 and errors == 0 else 'FAIL'}**

- **Website**: {url}
- **Scenario**: {scenario}
- **Date**: {now}
- **Total Tests**: {total_tests}
- **Passed**: {passed}
- **Failed**: {failed}
- **Errors**: {errors}
- **Pass Rate**: {pass_rate}

## Timing

- **Planning Phase**: {planning_time} seconds
- **Execution Phase**: {execution_time} seconds
- **Total Time**: {total_time} seconds

## Test Cases

| ID | Description | Status | Time | Notes |
|---|---|:---:|:---:|---|
"""
    
    # Add each test case to the markdown
    for test in results.get('test_results', []):
        test_id = test.get('id', 'Unknown')
        description = test.get('description', 'Unknown')
        status = test.get('status', 'Unknown')
        notes = test.get('notes', '')
        
        # Add emoji based on status
        status_emoji = '✅' if status == 'PASS' else '❌' if status == 'FAIL' else '⚠️'
        
        # Get test timing if available
        test_time = test_timing.get(test_id, {}).get('duration', '-')
        test_time_str = f"{test_time} s" if test_time != '-' else '-'
        
        # Add row to the table
        markdown += f"| {test_id} | {description} | {status_emoji} {status} | {test_time_str} | {notes[:50]}{'...' if len(notes) > 50 else ''} |\n"
    
    # Add detailed test results section
    markdown += "\n## Detailed Test Results\n\n"
    
    for test in results.get('test_results', []):
        test_id = test.get('id', 'Unknown')
        description = test.get('description', 'Unknown')
        status = test.get('status', 'Unknown')
        steps = test.get('steps', [])
        expected = test.get('expected_result', '')
        actual = test.get('actual_result', '')
        notes = test.get('notes', '')
        
        # Add emoji based on status
        status_emoji = '✅' if status == 'PASS' else '❌' if status == 'FAIL' else '⚠️'
        
        markdown += f"### {test_id}: {description}\n\n"
        markdown += f"**Status**: {status_emoji} {status}\n\n"
        
        # Add test timing if available
        test_time = test_timing.get(test_id, {}).get('duration', '-')
        if test_time != '-':
            markdown += f"**Execution Time**: {test_time} seconds\n\n"
        
        markdown += "**Steps**:\n"
        for i, step in enumerate(steps, 1):
            markdown += f"{i}. {step}\n"
        
        markdown += f"\n**Expected Result**:\n{expected}\n\n"
        markdown += f"**Actual Result**:\n{actual}\n\n"
        
        if notes:
            markdown += f"**Notes**:\n{notes}\n\n"
        
        markdown += "---\n\n"
    
    # Save to file if output_file is provided
    if output_file:
        with open(output_file, 'w') as f:
            f.write(markdown)
    
    return markdown


def main():
    """Command-line interface for generating markdown reports."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate markdown reports from test results')
    parser.add_argument('results_file', help='Path to the JSON file containing test results')
    parser.add_argument('-o', '--output', help='Path to save the markdown report')
    
    args = parser.parse_args()
    
    # If output is not specified, use the same name as the input but with .md extension
    if not args.output:
        args.output = os.path.splitext(args.results_file)[0] + '.md'
    
    markdown = generate_markdown_report(args.results_file, args.output)
    print(f"Report generated and saved to {args.output}")


if __name__ == '__main__':
    main()
