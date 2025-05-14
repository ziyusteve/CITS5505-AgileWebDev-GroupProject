from app.models.user import User
from app.extensions import login_manager
from flask_sqlalchemy import SQLAlchemy

# This file allows us to import all models directly from app.models

db = SQLAlchemy()

# Flask-Login user loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_by_id(user_id):
    """Get user by ID using SQLAlchemy 2.0 style"""
    return db.session.get(User, int(user_id))
