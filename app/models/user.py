from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    datasets = db.relationship("Dataset", backref="owner", lazy=True)

    def set_password(self, password):
        """Set password hash for user"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password, password)

    def generate_verification_token(self, expiration=3600):
        """Generate a verification token for the user"""
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt='email-verification-salt')

    def verify_token(self, token, expiration=3600):
        """Verify the token for the user"""
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt='email-verification-salt',
                max_age=expiration
            )
        except:
            return False
        return email == self.email

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
