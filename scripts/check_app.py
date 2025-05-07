"""
Simple script to check if the application loads correctly after project restructuring.
"""
import sys
import os

# Add the parent directory to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

from app import create_app  # noqa: E402


def check_app():
    """Check if the application can be created and configured correctly."""
    try:
        app = create_app()
        print("✅ Application loaded successfully!")
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        return True
    except Exception as e:
        print(f"❌ Error loading application: {e}")
        return False


if __name__ == "__main__":
    success = check_app()
    exit(0 if success else 1)
