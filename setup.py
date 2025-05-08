#!/usr/bin/env python
"""
Setup script for 5505 Group Project
This script helps set up the project for first-time users with minimal effort
"""
import os
import sys
import shutil
import secrets
import subprocess
from pathlib import Path

def print_step(message):
    """Print a formatted step message"""
    print(f"\n\033[1;34m>>> {message}\033[0m")

def print_success(message):
    """Print a formatted success message"""
    print(f"\033[1;32m✓ {message}\033[0m")

def print_error(message):
    """Print a formatted error message"""
    print(f"\033[1;31m✗ {message}\033[0m")

def print_warning(message):
    """Print a formatted warning message"""
    print(f"\033[1;33m! {message}\033[0m")

def ensure_directory(directory):
    """Ensure directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print_success(f"Created directory: {directory}")
    return True

def copy_env_file():
    """Create a .env file from env.example if it doesn't exist"""
    if os.path.exists(".env"):
        print_warning(".env file already exists, skipping")
        return

    try:
        if os.path.exists("env.example"):
            shutil.copy("env.example", ".env")
            # Generate a random secret key
            secret_key = secrets.token_hex(16)
            
            # Read the .env file
            with open(".env", "r") as f:
                env_content = f.read()
            
            # Replace placeholder with actual secret key
            env_content = env_content.replace("your-secret-key-here", secret_key)
            
            # Write back to .env
            with open(".env", "w") as f:
                f.write(env_content)
                
            print_success("Created .env file with secure random SECRET_KEY")
        else:
            print_error("env.example file not found")
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")

def setup_virtual_env():
    """Setup virtual environment if not exists"""
    if os.path.exists("venv"):
        print_warning("Virtual environment already exists, skipping")
        return True
    
    print_step("Creating virtual environment")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_success("Created virtual environment")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install project dependencies"""
    print_step("Installing dependencies")
    
    # Determine the pip path based on the OS
    if sys.platform.startswith('win'):
        pip = os.path.join("venv", "Scripts", "pip")
    else:
        pip = os.path.join("venv", "bin", "pip")
    
    try:
        subprocess.run([pip, "install", "-r", "requirements.txt"], check=True)
        print_success("Installed core dependencies")
        
        if os.path.exists("requirements/dev.txt"):
            subprocess.run([pip, "install", "-r", "requirements/dev.txt"], check=True)
            print_success("Installed development dependencies")
            
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def setup_database():
    """Setup the database"""
    print_step("Setting up database")
    
    # Ensure instance directory exists
    ensure_directory("instance")
    
    # Set correct permissions for directories
    if not sys.platform.startswith('win'):
        try:
            subprocess.run(["chmod", "-R", "755", "instance"], check=True)
            subprocess.run(["chmod", "-R", "755", "data"], check=True)
            subprocess.run(["chmod", "-R", "755", "logs"], check=True)
            print_success("Set directory permissions")
        except subprocess.CalledProcessError as e:
            print_warning(f"Failed to set permissions: {e}")
    
    return True

def create_starter_data():
    """Create starter data directory and files"""
    ensure_directory("data")
    ensure_directory(os.path.join("data", "uploads"))
    ensure_directory("logs")
    
    print_success("Created data directories")
    return True

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*80)
    print("\033[1;36mSetup Complete! Next steps:\033[0m")
    
    if sys.platform.startswith('win'):
        activate_cmd = ".\\venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"""
1. Activate the virtual environment:
   \033[1m{activate_cmd}\033[0m

2. Run the application:
   \033[1mpython run.py\033[0m

3. Access the application in your browser:
   \033[1mhttp://localhost:5000\033[0m
   
Note: Some features may require API keys. Edit the .env file to add them.
""")
    print("="*80)

def main():
    """Main setup function"""
    print("\033[1;35m")
    print("="*80)
    print(f"5505 Group Project - Automated Setup")
    print("="*80)
    print("\033[0m")
    
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Create necessary directories
    create_starter_data()
    
    # Setup the database
    setup_database()
    
    # Copy the .env file
    copy_env_file()
    
    # Setup virtual environment
    if setup_virtual_env():
        # Install dependencies
        install_dependencies()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main() 