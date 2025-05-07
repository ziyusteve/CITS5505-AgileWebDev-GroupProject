from flask import Blueprint

# Create blueprint without adding any routes, providing only service layer functionality
scout_bp = Blueprint(
    'scout', __name__
)

# Avoid circular imports, don't import models and services modules here
# These modules will be imported when needed in functions
