from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

from app import create_app  # noqa: E402

# This check should ideally happen after create_app if app context is needed for logging etc.
# However, for basic startup, create_app is the main app logic entry point.
app = create_app("development")  # Explicitly use development configuration

if __name__ == "__main__":
    # Disable auto-reload to ensure only one process loads the latest code
    app.run(debug=True, use_reloader=False)
