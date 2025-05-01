# filepath: e:\5505\5505_group_project\app\datasets\routes.py
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.datasets import bp
from app.models.dataset import Dataset
from app.extensions import db
from app.utils import allowed_file, generate_unique_filename
from app.datasets.forms import DatasetUploadForm

# These modules will be imported within functions as needed
# from app.scout_analysis.processors import is_scout_report
# from app.scout_analysis.services import ScoutAnalysisService
# from app.scout_analysis.models import ScoutReportAnalysis

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Dataset upload route"""
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
            user_id=current_user.id
        )
        db.session.add(new_dataset)
        db.session.commit()
        
        # Automatically analyze all text files
        if current_app.config.get('ENABLE_SCOUT_ANALYSIS', False):
            from app.scout_analysis.processors import extract_text_from_file
            from app.scout_analysis.services import ScoutAnalysisService
            from app.scout_analysis.models import ScoutReportAnalysis
            # Use the global Flask configuration for API keys instead of setting them here
            analysis = ScoutReportAnalysis(
                dataset_id=new_dataset.id,
                processing_status='pending'
            )
            db.session.add(analysis)
            db.session.commit()
            try:
                text_content = extract_text_from_file(file_path)
                current_app.logger.warning(f"[DEBUG] Extracted text content: {text_content[:200]}")
                if text_content and not text_content.startswith('ERROR') and len(text_content.strip()) > 0:
                    analysis_result = ScoutAnalysisService.analyze_report(
                        text_content,
                        use_deep_analysis=current_app.config.get('ENABLE_SCOUT_DEEP_ANALYSIS', False)
                    )
                    current_app.logger.warning(f"[DEBUG] AI analysis result: {analysis_result}")
                    analysis.update_from_analysis_result(analysis_result)
                    db.session.commit()
                    flash('File uploaded successfully! Text content has been automatically analyzed.', 'success')
                else:
                    analysis.processing_status = 'failed'
                    analysis.analysis_result = '{"error": "Could not extract valid text content for analysis."}'
                    db.session.commit()
                    flash('File uploaded successfully! But could not extract valid text content for analysis.', 'warning')
            except Exception as e:
                current_app.logger.error(f"Scout report analysis error: {str(e)}")
                analysis.processing_status = 'failed'
                analysis.analysis_result = f'{{"error": "Error occurred during analysis: {str(e)}"}}'
                db.session.commit()
                flash('File uploaded successfully! But an error occurred during analysis.', 'warning')
        else:
            flash('File uploaded successfully!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('datasets/upload.html', form=form)
