from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.utils import secure_filename
import os
from app.datasets import bp
from app.models.dataset import Dataset
from app.extensions import db
from app.utils import allowed_file, generate_unique_filename
from flask import current_app

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """数据集上传路由"""
    if 'user_id' not in session:
        flash('请先登录以访问此页面。', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('没有文件部分', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('未选择文件', 'danger')
            return redirect(request.url)
        
        title = request.form.get('title')
        description = request.form.get('description', '')
        
        if file and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            new_dataset = Dataset(
                title=title,
                description=description,
                file_path=file_path,
                user_id=session['user_id']
            )
            
            db.session.add(new_dataset)
            db.session.commit()
            
            flash('文件上传成功！', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('不允许的文件类型', 'danger')
            return redirect(request.url)
    
    return render_template('datasets/upload.html')
