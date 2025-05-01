# filepath: e:\5505\5505_group_project\app\datasets\routes.py
from flask import render_template, redirect, url_for, flash, request, session, current_app
from werkzeug.utils import secure_filename
import os
from app.datasets import bp
from app.models.dataset import Dataset
from app.extensions import db
from app.utils import allowed_file, generate_unique_filename
from app.datasets.forms import DatasetUploadForm

# 这些模块将在需要时在函数内部导入
# from app.scout_analysis.processors import is_scout_report
# from app.scout_analysis.services import ScoutAnalysisService
# from app.scout_analysis.models import ScoutReportAnalysis

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """数据集上传路由"""
    if 'user_id' not in session:
        flash('请先登录以访问此页面。', 'warning')
        return redirect(url_for('auth.login'))
    
    form = DatasetUploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        title = form.title.data
        description = form.description.data or ''
        
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
        
        # 只要是文本文件都自动分析
        if current_app.config.get('ENABLE_SCOUT_ANALYSIS', False):
            from app.scout_analysis.processors import extract_text_from_file
            from app.scout_analysis.services import ScoutAnalysisService
            from app.scout_analysis.models import ScoutReportAnalysis
            # 不再在此处设置API密钥，统一用Flask全局配置
            analysis = ScoutReportAnalysis(
                dataset_id=new_dataset.id,
                processing_status='pending'
            )
            db.session.add(analysis)
            db.session.commit()
            try:
                text_content = extract_text_from_file(file_path)
                current_app.logger.warning(f"[DEBUG] 提取文本内容: {text_content[:200]}")
                if text_content and not text_content.startswith('ERROR') and len(text_content.strip()) > 0:
                    analysis_result = ScoutAnalysisService.analyze_report(
                        text_content,
                        use_deep_analysis=current_app.config.get('ENABLE_SCOUT_DEEP_ANALYSIS', False)
                    )
                    current_app.logger.warning(f"[DEBUG] AI分析结果: {analysis_result}")
                    analysis.update_from_analysis_result(analysis_result)
                    db.session.commit()
                    flash('文件上传成功！已自动分析文本内容。', 'success')
                else:
                    analysis.processing_status = 'failed'
                    analysis.analysis_result = '{"error": "未能提取有效文本内容，无法分析。"}'
                    db.session.commit()
                    flash('文件上传成功！但未能提取有效文本内容，无法分析。', 'warning')
            except Exception as e:
                current_app.logger.error(f"球探报告分析错误: {str(e)}")
                analysis.processing_status = 'failed'
                analysis.analysis_result = f'{{"error": "分析过程中出现错误: {str(e)}"}}'
                db.session.commit()
                flash('文件上传成功！但分析过程中出现错误。', 'warning')
        else:
            flash('文件上传成功！', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('datasets/upload.html', form=form)
