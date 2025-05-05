from flask import render_template, redirect, url_for, flash
from app.dashboard import bp
from app.models.dataset import Dataset
from app.models.share import Share
from app.extensions import db
from flask_login import login_required, current_user


@bp.route("/")
@login_required
def index():
    """User dashboard routes"""

    user_id = current_user.id
    user_datasets = Dataset.query.filter_by(user_id=user_id).all()

    # Get datasets shared with the user
    shared_with_user = (
        db.session.query(Dataset)
        .join(Share)
        .filter(Share.shared_with_id == user_id)
        .all()
    )

    return render_template(
        "dashboard/dashboard.html",
        user_datasets=user_datasets,
        shared_datasets=shared_with_user,
    )
