from flask import render_template, redirect, url_for, flash, request
from app.sharing import bp
from app.models.dataset import Dataset
from app.models.user import User
from app.models.share import Share
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import validate_csrf_token


@bp.route("/", methods=["GET"])
@login_required
def index():
    """Data sharing page routes"""

    user_id = current_user.id
    user_datasets = Dataset.query.filter_by(user_id=user_id).all()
    users = User.query.filter(User.id != user_id).all()

    # Get existing share records to show who already has access
    shares = Share.query.join(Dataset).filter(
        Dataset.user_id == user_id
    ).all()

    return render_template(
        "sharing/share.html",
        datasets=user_datasets,
        users=users,
        shares=shares,
    )


@bp.route("/share", methods=["POST"])
@login_required
def handle_share():
    """Process dataset sharing request"""

    # 验证CSRF令牌
    validate_csrf_token()

    user_id = current_user.id
    dataset_id = request.form.get("dataset_id")
    shared_with_id = request.form.get("user_id")

    # Validate input
    if not dataset_id or not shared_with_id:
        flash("Missing required fields", "danger")
        return redirect(url_for("sharing.index"))

    # Convert to integers
    try:
        dataset_id = int(dataset_id)
        shared_with_id = int(shared_with_id)
    except ValueError:
        flash("Invalid input data", "danger")
        return redirect(url_for("sharing.index"))

    # Check dataset ownership
    dataset = Dataset.query.get(dataset_id)
    if not dataset or dataset.user_id != user_id:
        flash("You cannot share this dataset", "danger")
        return redirect(url_for("sharing.index"))

    # Check if already shared
    existing_share = Share.query.filter_by(
        dataset_id=dataset_id,
        shared_with_id=shared_with_id,
    ).first()

    if existing_share:
        flash("Dataset already shared with this user", "warning")
        return redirect(url_for("sharing.index"))

    # Create new share record
    new_share = Share(dataset_id=dataset_id, shared_with_id=shared_with_id)
    db.session.add(new_share)
    db.session.commit()

    flash("Dataset shared successfully!", "success")
    return redirect(url_for("sharing.index"))


@bp.route("/revoke/<int:share_id>", methods=["POST"])
@login_required
def revoke_share(share_id):
    """Revoke dataset sharing"""

    # 验证CSRF令牌
    validate_csrf_token()

    user_id = current_user.id

    # Get share record
    share = (
        Share.query.join(Dataset)
        .filter(
            Share.id == share_id,
            Dataset.user_id == user_id,
        )
        .first_or_404()
    )

    # Delete share record
    db.session.delete(share)
    db.session.commit()

    flash("Dataset sharing revoked.", "info")
    return redirect(url_for("sharing.index"))
