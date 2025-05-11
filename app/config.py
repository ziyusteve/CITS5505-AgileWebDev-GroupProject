import os
import secrets


class Config:
    """Base configuration class"""

    # Get secret key from environment variable, or generate a strong random key if not available
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(16)

    # Calculate base directory path
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Configure database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(os.path.dirname(basedir), "instance", "site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload configurations
    UPLOAD_FOLDER = os.path.join(os.path.dirname(basedir), "data", "uploads")
    ALLOWED_EXTENSIONS = {"csv", "txt", "json", "xlsx", "xls"}

    # Scout report analysis configuration
    ENABLE_SCOUT_ANALYSIS = True  # Whether to enable scout report analysis
    ENABLE_SCOUT_DEEP_ANALYSIS = (
        False  # Whether to enable transformer-based deep analysis
    )
    SCOUT_REPORT_EXTENSIONS = {
        "txt",
        "pdf",
        "docx",
    }  # Supported file formats for scout reports

    # API key configuration - read from environment variables
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

    @staticmethod
    def validate_config():
        """Validate if critical configurations exist to ensure the app runs properly"""
        missing_configs = []
        if not Config.GEMINI_API_KEY:
            missing_configs.append("GEMINI_API_KEY")
        if not Config.MAIL_USERNAME:
            missing_configs.append("MAIL_USERNAME")
        if not Config.MAIL_PASSWORD:
            missing_configs.append("MAIL_PASSWORD")
        if not Config.MAIL_DEFAULT_SENDER:
            missing_configs.append("MAIL_DEFAULT_SENDER")

        if missing_configs:
            import logging

            logging.warning(
                f"Warning: Missing critical configurations: {', '.join(missing_configs)}. "
                "Some features may not work properly."
            )
            return False
        return True


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Use in-memory database for testing


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False


# Configuration dictionary
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
