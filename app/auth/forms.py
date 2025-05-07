from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models.user import User

# 尝试导入Email验证器，如果失败则提供备用验证器
try:
    from wtforms.validators import Email
except ImportError:
    # 如果email_validator未安装，提供一个简单的备用验证器
    import re

    class Email:
        """备用Email验证器"""

        def __init__(self, message=None):
            if message is None:
                message = "Invalid email address."
            self.message = message

        def __call__(self, form, field):
            email_pattern = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            if not email_pattern.match(field.data):
                raise ValidationError(self.message)


class LoginForm(FlaskForm):
    """User login form"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    """User registration form"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    terms = BooleanField(
        "I agree to the Terms and Privacy Policy", 
        validators=[DataRequired()]  # E501: line too long - Shortened
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        """Validate username is not already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username is already taken. Please choose a different one."
            )

    def validate_email(self, email):
        """Validate email is not already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                "Email is already registered. Please use a different one."
            )
