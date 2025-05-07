from flask import Blueprint

bp = Blueprint("dashboard", __name__)

from app.dashboard import routes  # noqa: E402,F401
