from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    datasets = db.relationship("Dataset", backref="owner", lazy=True)

    def set_password(self, password):
        """Set password hash for user"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
