from flask import Blueprint

bp = Blueprint('visualization', __name__)

from app.visualization import routes
