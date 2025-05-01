from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.sharing import bp
from app.models.dataset import Dataset
from app.models.user import User
from app.models.share import Share
from app.extensions import db
from app.sharing.forms import ShareDatasetForm, RevokeShareForm

@bp.route('/', methods=['GET'])
@login_required
def index():
    """Data sharing page route"""
    user_datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    users = User.query.filter(User.id != current_user.id).all()
    
    # Get existing share records to show who already has access
    shares = Share.query.join(Dataset).filter(Dataset.user_id == current_user.id).all()
    
    # Create and initialize share form
    share_form = ShareDatasetForm()
    share_form.dataset_id.choices = [(d.id, d.title) for d in user_datasets]
    share_form.user_id.choices = [(u.id, u.username) for u in users]
    
    # Create a revoke form for each share
    revoke_forms = {share.id: RevokeShareForm() for share in shares}
    
    return render_template(
        'sharing/share.html', 
        share_form=share_form, 
        revoke_forms=revoke_forms, 
        datasets=user_datasets, 
        users=users, 
        shares=shares
    )

@bp.route('/dataset', methods=['POST'])
@login_required
def share_dataset():
    """Process dataset sharing request"""
    # Get user's datasets and other users
    user_datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    users = User.query.filter(User.id != current_user.id).all()
    
    share_form = ShareDatasetForm()
    share_form.dataset_id.choices = [(d.id, d.title) for d in user_datasets]
    share_form.user_id.choices = [(u.id, u.username) for u in users]
    
    if share_form.validate_on_submit():
        dataset_id = share_form.dataset_id.data
        shared_with_id = share_form.user_id.data
        
        # Check dataset ownership
        dataset = Dataset.query.get(dataset_id)
        if not dataset or dataset.user_id != current_user.id:
            flash('You cannot share this dataset', 'danger')
            return redirect(url_for('sharing.index'))
        
        # Check if already shared
        existing_share = Share.query.filter_by(
            dataset_id=dataset_id, 
            shared_with_id=shared_with_id
        ).first()
        
        if existing_share:
            flash('Dataset is already shared with this user', 'warning')
            return redirect(url_for('sharing.index'))
        
        # Create new share record
        new_share = Share(dataset_id=dataset_id, shared_with_id=shared_with_id)
        db.session.add(new_share)
        db.session.commit()
        
        flash('Dataset has been shared successfully!', 'success')
    else:
        # If form validation fails, display errors
        for field, errors in share_form.errors.items():
            for error in errors:
                flash(f'{share_form[field].label.text}: {error}', 'danger')
                
    return redirect(url_for('sharing.index'))

@bp.route('/revoke/<int:share_id>', methods=['POST'])
@login_required
def revoke_share(share_id):
    """Revoke dataset sharing"""
    revoke_form = RevokeShareForm()
    if revoke_form.validate_on_submit():
        # Get share record
        share = Share.query.join(Dataset).filter(
            Share.id == share_id,
            Dataset.user_id == current_user.id
        ).first_or_404()
        
        # Delete share record
        db.session.delete(share)
        db.session.commit()
        
        flash('Dataset sharing has been revoked.', 'info')
    
    return redirect(url_for('sharing.index'))
