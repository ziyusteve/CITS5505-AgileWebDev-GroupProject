from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create extension instances not bound to a specific application
db = SQLAlchemy()

# Create LoginManager instance
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please login to access this page."
login_manager.login_message_category = "info"
