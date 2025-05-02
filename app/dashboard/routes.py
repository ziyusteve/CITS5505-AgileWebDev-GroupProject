from flask import render_template, redirect, url_for, flash, session
from app.dashboard import bp
from app.models.dataset import Dataset
from app.models.share import Share
from app.extensions import db

@bp.route('/')
def index():
    """用户仪表板路由"""
    if 'user_id' not in session:
        flash('请先登录以访问此页面。', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user_datasets = Dataset.query.filter_by(user_id=user_id).all()
    
    # 获取与用户共享的数据集
    shared_with_user = db.session.query(Dataset).join(Share).filter(Share.shared_with_id == user_id).all()
    
    return render_template('dashboard/dashboard.html', 
                           user_datasets=user_datasets, 
                           shared_datasets=shared_with_user)
