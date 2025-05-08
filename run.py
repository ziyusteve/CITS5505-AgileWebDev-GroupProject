from dotenv import load_dotenv
import os
import sys

def is_first_run():
    """Check if this appears to be a first run of the application"""
    # Check for key indicators of a fresh clone
    no_env_file = not os.path.exists(".env")
    no_venv = not os.path.exists("venv")
    no_instance_db = not os.path.exists(os.path.join("instance", "site.db"))
    
    return no_env_file or no_instance_db

def suggest_setup():
    """Display setup suggestion for first-time users"""
    print("\n" + "="*80)
    print("\033[1;33mThis appears to be your first time running the application!\033[0m")
    print("\033[1;36mFor an automated setup experience, we recommend running:\033[0m")
    print("\n    \033[1mpython setup.py\033[0m\n")
    print("This will create directories, set up your environment, and install dependencies.")
    print("="*80 + "\n")
    
    choice = input("Would you like to continue anyway? (y/n): ").strip().lower()
    if choice != 'y':
        print("Exiting. Please run setup.py for automatic configuration.")
        sys.exit(0)
    print("\nContinuing with manual setup...\n")

# Try to load environment variables, with user-friendly error handling
try:
    load_dotenv()  # Load environment variables from .env file
    print("Environment variables loaded successfully.")
except Exception as e:
    print(f"Warning: Error loading .env file: {e}")
    print("You can create an .env file by copying env.example")

# Check if this is likely a first run
if is_first_run():
    suggest_setup()

try:
    from app import create_app  # noqa: E402
except ImportError as e:
    print(f"Error importing app: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Check if critical directories exist before even starting the app
instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance")
if not os.path.exists(instance_dir):
    try:
        os.makedirs(instance_dir, exist_ok=True)
        print(f"Created instance directory: {instance_dir}")
    except OSError as e:
        print(f"Warning: Could not create instance directory: {e}")
        print("On Linux/Mac, this may be a permissions issue. Try: chmod -R 755 .")

# This check should ideally happen after create_app if app context is needed for logging etc.
# However, for basic startup, create_app is the main app logic entry point.
try:
    app = create_app("development")  # Explicitly use development configuration
except Exception as e:
    print(f"Fatal error creating app: {e}")
    print("Check the logs for more details.")
    print("Common issues:")
    print("1. Missing dependencies - run: pip install -r requirements.txt")
    print("2. Permission errors - run: chmod -R 755 .")
    print("3. Missing environment variables - copy env.example to .env and fill in values")
    sys.exit(1)

if __name__ == "__main__":
    try:
        # Disable auto-reload to ensure only one process loads the latest code
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        print(f"Error running app: {e}")
        sys.exit(1)
