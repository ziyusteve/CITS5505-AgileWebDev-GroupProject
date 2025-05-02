from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.dashboard import bp
from app.models.dataset import Dataset
from app.models.share import Share
from app.extensions import db

@bp.route('/')
@login_required
def index():
    """User dashboard route"""
    user_datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    
    # Get datasets shared with the user
    shared_with_user = db.session.query(Dataset).join(Share).filter(Share.shared_with_id == current_user.id).all()
    
    return render_template('dashboard/dashboard.html', 
                           user_datasets=user_datasets, 
                           shared_datasets=shared_with_user)
