from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 创建不与特定应用绑定的扩展实例
db = SQLAlchemy()

# 创建LoginManager实例
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面。'
login_manager.login_message_category = 'info'
