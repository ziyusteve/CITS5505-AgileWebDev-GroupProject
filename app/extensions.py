from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Create extension instances not bound to a specific application
db = SQLAlchemy()

# Create LoginManager instance
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please login to access this page."
login_manager.login_message_category = "info"

# Create Mail instance
mail = Mail()

# Gemini API singleton instance
_gemini_api_instance = None

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

def get_gemini_api():
    """
    Returns the Gemini API singleton instance.

    Returns:
        object: Gemini API client instance
    """
    global _gemini_api_instance
    if _gemini_api_instance is None:
        from flask import current_app

        api_key = current_app.config.get("GEMINI_API_KEY", "")
        # Initialize your Gemini API client here
        # This is a placeholder implementation
        _gemini_api_instance = GeminiAPI(api_key)
    return _gemini_api_instance


class GeminiAPI:
    """Simple wrapper for Gemini API interactions"""

    def __init__(self, api_key=None):
        """Initialize the Gemini API client with an API key"""
        self.api_key = api_key

    def set_api_key(self, api_key):
        """Set or update the API key"""
        self.api_key = api_key

    def analyze_text(self, text):
        """
        Analyze text using Gemini API

        Args:
            text (str): Text to analyze

        Returns:
            dict: Analysis results
        """
        if not self.api_key:
            return {"error": "API key not set"}

        # This is a placeholder. In a real implementation,
        # you would call the actual Gemini API here
        return {"result": f"Analysis of: {text[:30]}..."}
