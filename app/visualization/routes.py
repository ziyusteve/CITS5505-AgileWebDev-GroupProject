from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.visualization import bp
from app.models.dataset import Dataset
from app.models.share import Share
from app.utils import load_dataset

@bp.route('/<int:dataset_id>')
@login_required
def visualize(dataset_id):
    """Data visualization route"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Check if the user owns the dataset or if it's shared with them
    is_owner = dataset.user_id == current_user.id
    is_shared = Share.query.filter_by(dataset_id=dataset_id, shared_with_id=current_user.id).first() is not None
    
    if not (is_owner or is_shared):
        flash('You do not have permission to view this dataset.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Force all text files to be treated as scout reports to ensure proper visualization
    is_scout_report = True  # Force to True for consistent rendering
    scout_analysis = None
    
    # Check if this dataset has scout report analysis
    if hasattr(Dataset, 'has_scout_analysis') and callable(getattr(Dataset, 'has_scout_analysis')):
        if dataset.has_scout_analysis():
            scout_analysis = dataset.get_scout_analysis()
            current_app.logger.warning(f"[DEBUG] Scout report analysis: {scout_analysis.__dict__ if scout_analysis else None}")
    
    # If no analysis results, create a fallback analysis
    if not scout_analysis:
        # Import models
        try:
            from app.scout_analysis.models import ScoutReportAnalysis
            import json
            
            # Check if there's an existing analysis record
            scout_analysis = ScoutReportAnalysis.query.filter_by(dataset_id=dataset_id).first()
            
            # If no record exists, create an empty one for display
            if not scout_analysis:
                scout_analysis = ScoutReportAnalysis(
                    dataset_id=dataset_id,
                    processing_status='completed',
                    analysis_result=json.dumps({
                        "summary": "This is an uploaded text file. The system couldn't detect detailed analysis results. Please check the original file content."
                    })
                )
            
            # If there's a record but the analysis result is empty, add default content
            if not scout_analysis.analysis_result:
                scout_analysis.analysis_result = json.dumps({
                    "summary": "The system has received your analysis request but couldn't generate detailed analysis. This might be due to incompatible file format or content."
                })
                scout_analysis.processing_status = 'completed'
        except Exception as e:
            current_app.logger.error(f"Failed to create fallback analysis: {str(e)}")
    
    # Render template
    return render_template(
        'visualization/visualize.html', 
        dataset=dataset, 
        is_owner=is_owner,
        is_scout_report=is_scout_report,  # Forced to True
        scout_analysis=scout_analysis
    )
