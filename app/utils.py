import os
import uuid
import pandas as pd

def allowed_file(filename, allowed_extensions):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    """Generate a unique filename while preserving the original extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    new_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return new_filename

def load_dataset(file_path):
    """Load dataset based on file extension"""
    ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
    try:
        if (ext == 'csv'):
            df = pd.read_csv(file_path)
        elif (ext == 'xlsx'):
            df = pd.read_excel(file_path)
        elif (ext == 'json'):
            df = pd.read_json(file_path)
        elif (ext == 'txt'):
            # Attempt to detect delimiter
            df = pd.read_csv(file_path, sep=None, engine='python')
        else:
            return None, "Unsupported file format"
        return df, None
    except Exception as e:
        return None, f"Error loading dataset: {str(e)}"
