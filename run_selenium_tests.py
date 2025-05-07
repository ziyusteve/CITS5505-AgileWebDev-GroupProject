import unittest
import sys
import os
import time
from run_selenium_tests import SeleniumTestCase

if __name__ == '__main__':
    # Start Flask app in a separate process
    import subprocess
    from threading import Thread
    
    # Start Flask app in testing mode
    flask_proc = subprocess.Popen(
        ['python', 'run_testing.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the server to start
    print("Starting Flask test server...")
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