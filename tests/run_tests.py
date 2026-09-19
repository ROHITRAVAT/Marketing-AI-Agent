#!/usr/bin/env python3
"""
Test runner script.
Executes pytest with specific configurations and generates a summary report.
"""
import subprocess
import sys
import argparse
import os

def run_tests(category=None, coverage=False):
    cmd = ["pytest", "tests/"]
    
    if category:
        cmd.extend(["-m", category])
        
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])
        
    cmd.append("-v")
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print("-" * 80)
    
    # Ensure test environment variables are set
    env = os.environ.copy()
    env["TESTING"] = "true"
    
    result = subprocess.run(cmd, env=env)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="AI Marketing Agent Test Runner")
    parser.add_argument("--category", help="Specific pytest marker to run (e.g., integration, security)")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.all:
        print("Running full test suite...")
        sys.exit(run_tests(coverage=args.coverage))
    elif args.category:
        sys.exit(run_tests(category=args.category, coverage=args.coverage))
    else:
        # Default behavior: run all tests if no arguments provided
        sys.exit(run_tests(coverage=args.coverage))

if __name__ == "__main__":
    main()
