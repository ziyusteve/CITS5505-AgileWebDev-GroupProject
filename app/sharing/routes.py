from flask import render_template, redirect, url_for, flash, request, session
from app.sharing import bp
from app.models.dataset import Dataset
from app.models.user import User
from app.models.share import Share
from app.extensions import db

@bp.route('/', methods=['GET'])
def index():
    """数据共享页面路由"""
    if 'user_id' not in session:
        flash('请先登录以访问此页面。', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user_datasets = Dataset.query.filter_by(user_id=user_id).all()
    users = User.query.filter(User.id != user_id).all()
    
    # 获取现有共享记录以显示谁已经有访问权限
    shares = Share.query.join(Dataset).filter(Dataset.user_id == user_id).all()
    
    return render_template('sharing/share.html', datasets=user_datasets, users=users, shares=shares)

@bp.route('/dataset', methods=['POST'])
def share_dataset():
    """处理数据集共享请求"""
    if 'user_id' not in session:
        flash('请先登录以访问此页面。', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    dataset_id = request.form.get('dataset_id')
    shared_with_id = request.form.get('user_id')
    
    # 验证输入
    if not dataset_id or not shared_with_id:
        flash('缺少必填字段', 'danger')
        return redirect(url_for('sharing.index'))
    
    # 检查数据集所有权
    dataset = Dataset.query.get(dataset_id)
    if not dataset or dataset.user_id != user_id:
        flash('您无法共享此数据集', 'danger')
        return redirect(url_for('sharing.index'))
    
    # 检查是否已共享
    existing_share = Share.query.filter_by(
        dataset_id=dataset_id, 
        shared_with_id=shared_with_id
    ).first()
    
    if existing_share:
        flash('数据集已经与该用户共享', 'warning')
        return redirect(url_for('sharing.index'))
    
    # 创建新的共享记录
    new_share = Share(dataset_id=dataset_id, shared_with_id=shared_with_id)
    db.session.add(new_share)
    db.session.commit()
    
    flash('数据集已成功共享！', 'success')
    return redirect(url_for('sharing.index'))

@bp.route('/revoke/<int:share_id>', methods=['POST'])
def revoke_share(share_id):
    """撤销数据集共享"""
    if 'user_id' not in session:
        flash('请先登录以访问此页面。', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # 获取共享记录
    share = Share.query.join(Dataset).filter(
        Share.id == share_id,
        Dataset.user_id == user_id
    ).first_or_404()
    
    # 删除共享记录
    db.session.delete(share)
    db.session.commit()
    
    flash('数据集共享已撤销。', 'info')
    return redirect(url_for('sharing.index'))
