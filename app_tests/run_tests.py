import os
import sys
import subprocess

def run_tests():
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Run the populate script first
    print("Populating test database...")
    subprocess.run([sys.executable, "app_tests/populate_test_data.py"], check=True)
    
    # Run the tests
    print("\nRunning tests...")
    result = subprocess.run(["pytest", "app_tests/app_test.py", "-v"], check=False)
    
    # Return the test result
    return result.returncode

if __name__ == '__main__':
    sys.exit(run_tests()) 