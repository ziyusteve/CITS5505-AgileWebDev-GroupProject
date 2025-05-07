from flask import render_template
from app.main import bp


@bp.route('/')
def index():
    """Website homepage route"""
    return render_template('main/index.html')
