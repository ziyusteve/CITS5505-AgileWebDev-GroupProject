from flask import Blueprint

bp = Blueprint("datasets", __name__)

from app.datasets import routes  # noqa: E402,F401
