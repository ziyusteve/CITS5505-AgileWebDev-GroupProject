from flask import Blueprint

bp = Blueprint('datasets', __name__)

from app.datasets import routes
