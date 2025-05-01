from flask import render_template, redirect, url_for, flash, request, session
from app.sharing import bp
from app.models.dataset import Dataset
from app.models.user import User
from app.models.share import Share
from app.extensions import db
from app.sharing.forms import ShareDatasetForm, RevokeShareForm

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
    
    # 创建并初始化共享表单
    share_form = ShareDatasetForm()
    share_form.dataset_id.choices = [(d.id, d.title) for d in user_datasets]
    share_form.user_id.choices = [(u.id, u.username) for u in users]
    
    # 为每个共享创建一个撤销表单
    revoke_forms = {share.id: RevokeShareForm() for share in shares}
    
    return render_template(
        'sharing/share.html', 
        share_form=share_form, 
        revoke_forms=revoke_forms, 
        datasets=user_datasets, 
        users=users, 
        shares=shares
    )

@bp.route('/dataset', methods=['POST'])
def share_dataset():
    """处理数据集共享请求"""
    if 'user_id' not in session:
        flash('请先登录以访问此页面。', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # 获取用户的数据集和其他用户
    user_datasets = Dataset.query.filter_by(user_id=user_id).all()
    users = User.query.filter(User.id != user_id).all()
    
    share_form = ShareDatasetForm()
    share_form.dataset_id.choices = [(d.id, d.title) for d in user_datasets]
    share_form.user_id.choices = [(u.id, u.username) for u in users]
    
    if share_form.validate_on_submit():
        dataset_id = share_form.dataset_id.data
        shared_with_id = share_form.user_id.data
        
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
    else:
        # 如果表单验证失败，显示错误
        for field, errors in share_form.errors.items():
            for error in errors:
                flash(f'{share_form[field].label.text}: {error}', 'danger')
                
    return redirect(url_for('sharing.index'))

@bp.route('/revoke/<int:share_id>', methods=['POST'])
def revoke_share(share_id):
    """撤销数据集共享"""
    if 'user_id' not in session:
        flash('请先登录以访问此页面。', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    revoke_form = RevokeShareForm()
    if revoke_form.validate_on_submit():
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
