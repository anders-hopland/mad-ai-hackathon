# AutoQA - Automated Web Testing System

This project was created for the Mad AI Hackathon. AutoQA is an automated web testing system that uses BrowserUse to explore websites, create test plans, and execute tests without manual intervention.

## Features

- **Automated Website Exploration**: AutoQA explores websites to understand how features work
- **Structured Test Plan Generation**: Creates detailed test plans with test cases based on observations
- **Automated Test Execution**: Executes test cases and records results
- **Comprehensive Reporting**: Generates detailed reports of test results

## How It Works

AutoQA works in three phases:

1. **Planning Phase**: The system explores the website and creates a structured test plan
2. **Execution Phase**: Each test case is executed and results are recorded
3. **Reporting Phase**: A comprehensive report is generated with test results

## Requirements

- Python 3.8+
- uv (fast Python package installer)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd mad-ai-hackathon

# Install uv if you don't have it already
curl -sSf https://install.ultraviolet.rs | sh

# Install dependencies using uv
uv pip install -e .
```

## Usage

```bash
python agent.py
```

When prompted:
1. Enter the URL of the website you want to test
2. Enter the test scenario (e.g., "Test the add to cart functionality")

The system will then:
1. Explore the website and create a test plan
2. Execute each test case
3. Generate a comprehensive report

## Example

```
Enter the URL to test: https://amazon.com
Enter the test scenario: Test the add to cart functionality
```

The system will explore Amazon's website, understand how the add to cart feature works, create test cases (like adding items, changing quantities, testing edge cases), execute those tests, and provide a detailed report.

## Output Format

The test plan and results are output in JSON format for easy parsing and integration with other systems.
