from flask import render_template
from app.main import bp

@bp.route('/')
def index():
    """网站主页路由"""
    return render_template('main/index.html')
