from flask import render_template
from app.main import bp
from flask_login import current_user

@bp.route('/')
def index():
    """网站主页路由"""
    return render_template('main/index.html')
