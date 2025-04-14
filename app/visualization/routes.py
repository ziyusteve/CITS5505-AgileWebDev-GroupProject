from flask import render_template, redirect, url_for, flash, session
from app.visualization import bp
from app.models.dataset import Dataset
from app.models.share import Share
from app.utils import load_dataset

@bp.route('/<int:dataset_id>')
def visualize(dataset_id):
    """数据可视化路由"""
    if 'user_id' not in session:
        flash('请先登录以访问此页面。', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查用户是否拥有数据集或数据集是否与其共享
    is_owner = dataset.user_id == user_id
    is_shared = Share.query.filter_by(dataset_id=dataset_id, shared_with_id=user_id).first() is not None
    
    if not (is_owner or is_shared):
        flash('您无权查看此数据集。', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # 加载数据文件但仅传递最少信息给模板
    # 详细数据将通过API加载
    df, error = load_dataset(dataset.file_path)
    if error:
        flash(f'加载数据集出错: {error}', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # 获取基本元数据用于初始显示
    metadata = {
        "columns": df.columns.tolist(),
        "row_count": len(df)
    }
    
    return render_template('visualization/visualize.html', dataset=dataset, metadata=metadata, is_owner=is_owner)
