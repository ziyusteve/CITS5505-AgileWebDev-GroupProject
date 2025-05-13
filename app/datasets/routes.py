# filepath: e:\5505\5505_group_project\app\datasets\routes.py
from flask import render_template, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
from app.datasets import bp
from app.models.dataset import Dataset
from app.extensions import db
from app.utils import generate_unique_filename, sanitize_filename
from app.datasets.forms import UploadDatasetForm
from flask_login import login_required, current_user

# These modules will be imported inside functions when needed
# from app.scout_analysis.processors import is_scout_report
# from app.scout_analysis.services import ScoutAnalysisService
# from app.scout_analysis.models import ScoutReportAnalysis


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Dataset upload routes"""

    form = UploadDatasetForm()

    if form.validate_on_submit():
        file = form.file.data
        title = form.title.data

        # Enhance filename security
        filename = secure_filename(file.filename)
        filename = sanitize_filename(filename)

        # Generate a unique filename
        unique_filename = generate_unique_filename(filename)

        # Ensure the upload directory exists
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        # Save the file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # Create dataset record
        new_dataset = Dataset(
            user_id=current_user.id,
            title=title or filename,  
            file_path=file_path,
            description="",  
        )
        db.session.add(new_dataset)
        db.session.commit()

        # Automatically analyze any text file
        if current_app.config.get("ENABLE_SCOUT_ANALYSIS", False):
            from app.scout_analysis.processors import extract_text_from_file
            from app.scout_analysis.services import ScoutAnalysisService
            from app.scout_analysis.models import ScoutReportAnalysis

            # No longer setting API key here, using Flask global config uniformly
            analysis = ScoutReportAnalysis(
                dataset_id=new_dataset.id, processing_status="pending"
            )
            db.session.add(analysis)
            db.session.commit()
            try:
                text_content = extract_text_from_file(file_path)
                current_app.logger.warning(
                    f"[DEBUG] Extracted text content: {text_content[:200]}"
                )
                if (
                    text_content
                    and not text_content.startswith("ERROR")
                    and len(text_content.strip()) > 0
                ):
                    analysis_result = ScoutAnalysisService.analyze_report(
                        text_content,
                        use_deep_analysis=current_app.config.get(
                            "ENABLE_SCOUT_DEEP_ANALYSIS", False
                        ),
                    )
                    current_app.logger.warning(
                        f"[DEBUG] AI analysis result: {analysis_result}"
                    )
                    analysis.update_from_analysis_result(analysis_result)
                    db.session.commit()
                    flash(
                        "File uploaded successfully! Text content has been automatically analyzed.",
                        "success",
                    )
                else:
                    analysis.processing_status = "failed"
                    analysis.analysis_result = '{"error": "Unable to extract valid text content, unable to analyze."}'
                    db.session.commit()
                    flash(
                        "File uploaded successfully! But unable to extract valid text content, unable to analyze.",
                        "warning",
                    )
            except Exception as e:
                current_app.logger.error(f"Scout report analysis error: {str(e)}")
                analysis.processing_status = "failed"
                analysis.analysis_result = f'{{"error": "Analysis error: {str(e)}"}}'
                db.session.commit()
                flash(
                    "File uploaded successfully! But analysis error occurred.",
                    "warning",
                )
        else:
            flash("File uploaded successfully!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("datasets/upload.html", form=form)

@bp.route("/delete/<int:dataset_id>", methods=["POST"])
@login_required
def delete(dataset_id):
    """Delete a dataset by its owner"""
    from app.utils import validate_csrf_token
    validate_csrf_token()
    dataset = Dataset.query.get_or_404(dataset_id)
    if dataset.user_id != current_user.id:
        flash("You do not have permission to delete this dataset.", "danger")
        return redirect(url_for("dashboard.index"))
    # Delete the file from disk if it exists
    try:
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)
    except Exception as e:
        current_app.logger.warning(f"Failed to delete file: {e}")
    # Delete related scout analyses (for safety, without using backref)
    from app.scout_analysis.models import ScoutReportAnalysis
    analyses = ScoutReportAnalysis.query.filter_by(dataset_id=dataset.id).all()
    for analysis in analyses:
        db.session.delete(analysis)
    # Delete the dataset record
    db.session.delete(dataset)
    db.session.commit()
    flash("Dataset deleted successfully.", "success")
    return redirect(url_for("dashboard.index"))
