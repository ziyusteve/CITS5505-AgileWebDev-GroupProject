from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

from app import create_app

app = create_app("development")  # Explicitly use development configuration

if __name__ == "__main__":
    # Disable auto-reload to ensure only one process loads the latest code
    app.run(debug=True, use_reloader=False)
