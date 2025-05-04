from app.models.user import User
from app.models.dataset import Dataset
from app.models.share import Share
from app.extensions import login_manager

# This file allows us to import all models directly from app.models

# Flask-Login 用户加载回调
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
