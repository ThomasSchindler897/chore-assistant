#!/usr/bin/env python3
"""
Test Runner for Chore Assistant
Provides easy commands to run specific test suites and scenarios
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}\n")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    commands = {
        '1': {
            'name': 'Run all tests',
            'cmd': 'pytest -v --tb=short',
            'desc': 'Run entire test suite with verbose output'
        },
        '2': {
            'name': 'Run model tests only',
            'cmd': 'pytest test_models.py -v --tb=short',
            'desc': 'Test Chore and Completion models'
        },
        '3': {
            'name': 'Run route tests only',
            'cmd': 'pytest test_routes.py -v --tb=short',
            'desc': 'Test Flask routes and endpoints'
        },
        '4': {
            'name': 'Run daily chore tests',
            'cmd': 'pytest test_models.py::TestDailyChore -v --tb=short',
            'desc': 'Test daily frequency chores'
        },
        '5': {
            'name': 'Run weekly chore tests',
            'cmd': 'pytest test_models.py::TestWeeklyChore -v --tb=short',
            'desc': 'Test weekly frequency chores'
        },
        '6': {
            'name': 'Run monthly chore tests',
            'cmd': 'pytest test_models.py::TestMonthlyChore -v --tb=short',
            'desc': 'Test monthly frequency chores'
        },
        '7': {
            'name': 'Run edge case tests',
            'cmd': 'pytest test_models.py::TestEdgeCases -v --tb=short',
            'desc': 'Test edge cases (leap years, month boundaries)'
        },
        '8': {
            'name': 'Run tests with coverage report',
            'cmd': 'pytest --cov=models --cov=app --cov-report=term-missing',
            'desc': 'Show which lines of code are tested'
        },
        '9': {
            'name': 'Run tests with detailed output',
            'cmd': 'pytest -vv --tb=long',
            'desc': 'Maximum verbosity - useful for debugging'
        },
        '10': {
            'name': 'Run failed tests only',
            'cmd': 'pytest --lf',
            'desc': 'Re-run only tests that failed last time'
        },
        '11': {
            'name': 'Quick smoke test',
            'cmd': 'pytest -x -q',
            'desc': 'Stop on first failure, quiet output'
        },
    }
    
    print("\n" + "="*70)
    print("  CHORE ASSISTANT TEST RUNNER")
    print("="*70)
    print("\nChoose a test command:\n")
    
    for key, info in commands.items():
        print(f"{key:2}. {info['name']:35} - {info['desc']}")
    
    print("\nOr type a custom pytest command (e.g., 'pytest -k daily')")
    print("Type 'exit' to quit\n")
    
    while True:
        choice = input("Enter choice (1-11 or custom command): ").strip()
        
        if choice.lower() == 'exit':
            print("\nGoodbye!")
            break
        
        if choice in commands:
            cmd = commands[choice]['cmd']
            desc = commands[choice]['desc']
        elif choice:
            cmd = choice
            desc = "Custom command"
        else:
            print("Invalid choice. Please try again.")
            continue
        
        success = run_command(cmd, desc)
        
        if not success and choice in ['1', '2', '3']:
            print("\n⚠️  Some tests failed. Review the output above.")
        
        print("\nWant to run another test? (Type 'exit' to quit)\n")

if __name__ == '__main__':
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not installed!")
        print("Install test dependencies with:")
        print("  pip install -r requirements-dev.txt")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
