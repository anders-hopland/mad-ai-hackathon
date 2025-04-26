#!/usr/bin/env python3
"""Generate a markdown report from an existing test results file."""

import argparse
import os
from autoqa.report import generate_markdown_report

def main():
    parser = argparse.ArgumentParser(description='Generate a markdown report from test results')
    parser.add_argument('--input', '-i', default='data/test_result_1.json',
                      help='Path to the JSON test results file (default: data/test_result_1.json)')
    parser.add_argument('--output', '-o', default=None,
                      help='Path to save the markdown report (default: same name as input with .md extension)')
    
    args = parser.parse_args()
    
    # If output is not specified, use the same name as the input but with .md extension
    if not args.output:
        args.output = os.path.splitext(args.input)[0] + '.md'
    
    print(f"Generating markdown report from {args.input}...")
    markdown = generate_markdown_report(args.input, args.output)
    print(f"Report generated and saved to {args.output}")
    
    # Print a preview of the report
    print("\nReport Preview:")
    print("=" * 50)
    preview_lines = markdown.split('\n')[:15]  # Show first 15 lines
    print('\n'.join(preview_lines))
    print("..." if len(markdown.split('\n')) > 15 else "")
    print("=" * 50)

if __name__ == '__main__':
    main()
