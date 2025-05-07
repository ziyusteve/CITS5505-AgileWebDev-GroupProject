# Initialize app/utils package
# This file makes the app/utils directory a Python package that can be imported

import os
import uuid
import pandas as pd
import re
from flask import request, abort, flash
from flask_wtf.csrf import validate_csrf


def allowed_file(filename, allowed_extensions=None):
    """Check if the file has an allowed extension"""

    if allowed_extensions is None:
        allowed_extensions = {"csv", "txt", "json", "xlsx", "xls"}
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


def generate_unique_filename(filename):
    """Generate a unique filename while preserving the original extension"""

    if "." in filename:
        name, ext = filename.rsplit(".", 1)
        return f"{name}_{str(uuid.uuid4())}.{ext}"
    return f"{filename}_{str(uuid.uuid4())}"


def sanitize_filename(filename):
    """Remove any potentially dangerous characters from filenames"""

    # Remove any path components (might be dangerous)
    filename = os.path.basename(filename)

    # Replace any unusual characters
    filename = re.sub(r"[^\w\.-]", "_", filename)

    return filename


def validate_csrf_token():
    """验证CSRF令牌，如果无效则中止请求"""

    csrf_token = request.form.get("csrf_token")
    if not csrf_token:
        flash("CSRF token missing", "danger")
        abort(400)

    try:
        validate_csrf(csrf_token)
    except Exception:
        flash("CSRF token validation failed", "danger")
        abort(400)

    return True


def load_dataset(file_path):
    """Load dataset based on file extension"""

    ext = file_path.rsplit(".", 1)[1].lower() if "." in file_path else ""
    try:
        if ext == "csv":
            df = pd.read_csv(file_path)
        elif ext == "xlsx":
            df = pd.read_excel(file_path)
        elif ext == "json":
            df = pd.read_json(file_path)
        elif ext == "txt":
            # Try to detect delimiter
            df = pd.read_csv(file_path, sep=None, engine="python")
        else:
            return None, "Unsupported file format"
        return df, None
    except Exception as e:
        return None, f"Error loading dataset: {str(e)}"
