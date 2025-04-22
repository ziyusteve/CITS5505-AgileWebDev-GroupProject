from flask import request, render_template, redirect, flash, session, url_for, current_app
from werkzeug.utils import secure_filename
from textblob import TextBlob
import os
from app.models import Dataset  # adjust import based on your structure
from app.utils import allowed_file, generate_unique_filename  # if custom helpers

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
        player_desc = request.form.get('player_description', '')  # New field

        # Analyze player description
        if player_desc.strip():
            blob = TextBlob(player_desc)
            sentiment = blob.sentiment
            analysis_result = (
                f"球员描述情感分析结果：极性 {sentiment.polarity:.2f}，主观性 {sentiment.subjectivity:.2f}"
            )
            flash(analysis_result, 'info')

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