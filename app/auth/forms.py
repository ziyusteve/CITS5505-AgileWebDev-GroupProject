from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    """用户登录表单"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    """用户注册表单"""
    username = StringField('用户名', 
                           validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('电子邮箱', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('密码', 
                            validators=[DataRequired(), Length(min=8)])
    terms = BooleanField('我同意服务条款和隐私政策', validators=[DataRequired()])
    submit = SubmitField('创建账户')
    
    def validate_username(self, username):
        """验证用户名是否已存在"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择一个不同的用户名。')
    
    def validate_email(self, email):
        """验证邮箱是否已存在"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用另一个邮箱地址。') 