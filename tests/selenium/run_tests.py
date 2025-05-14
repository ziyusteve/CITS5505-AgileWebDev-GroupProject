#!/usr/bin/env python
"""
Run Selenium tests for the NBA Player Analytics application
"""
import unittest
import sys
import os
import time
import subprocess
from threading import Thread

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Import the tests from test_dashboard.py
from test_dashboard import SeleniumTestCase

if __name__ == '__main__':
    # Start Flask app in a separate process
    print("Starting Flask test server...")
    flask_proc = subprocess.Popen(
        ['python', 'run_testing.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the server to start
    time.sleep(3)
    
    try:
        # Run the tests
        print("Running Selenium tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    finally:
        # Clean up - terminate Flask process
        print("Terminating Flask test server...")
        flask_proc.terminate()
        flask_proc.wait()