from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(),
        Length(min=3, message='用户名必须至少包含3个字符')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(),
        Email(message='请输入有效的电子邮件地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=8, message='密码必须至少包含8个字符')
    ])
    terms = BooleanField('我同意服务条款和隐私政策', validators=[
        DataRequired(message='您必须同意服务条款和隐私政策才能继续')
    ])
    submit = SubmitField('创建账户')
    
    # 自定义验证器，用于检查用户名是否已存在
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')
            
    # 自定义验证器，用于检查电子邮件是否已存在
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该电子邮件已注册，请使用其他电子邮件。') 