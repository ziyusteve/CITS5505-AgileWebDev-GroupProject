from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
import pandas as pd
import numpy as np
import json
import plotly
import plotly.express as px

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'txt', 'xlsx', 'json'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    datasets = db.relationship('Dataset', backref='owner', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shares = db.relationship('Share', backref='dataset', lazy=True, cascade="all, delete")
    
    def __repr__(self):
        return f"Dataset('{self.title}', '{self.date_uploaded}')"

class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_shared = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    shared_with = db.relationship('User', foreign_keys=[shared_with_id])
    
    def __repr__(self):
        return f"Share(Dataset: {self.dataset_id}, Shared with: {self.shared_with_id})"

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_unique_filename(filename):
    """Generate a unique filename while preserving the original extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    new_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return new_filename

def load_dataset(file_path):
    """Load a dataset from a file path based on its extension"""
    ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
    try:
        if ext == 'csv':
            df = pd.read_csv(file_path)
        elif ext == 'xlsx':
            df = pd.read_excel(file_path)
        elif ext == 'json':
            df = pd.read_json(file_path)
        elif ext == 'txt':
            # Attempt to detect delimiter
            df = pd.read_csv(file_path, sep=None, engine='python')
        else:
            return None, "Unsupported file format"
        return df, None
    except Exception as e:
        return None, f"Error loading dataset: {str(e)}"

def analyze_dataset(df):
    """Analyze a dataset and return statistics and visualization data"""
    if df is None or df.empty:
        return {
            "error": "Empty or invalid dataset"
        }
    
    # Get basic info
    result = {
        "column_names": df.columns.tolist(),
        "row_count": len(df),
        "preview": df.head(10).to_dict('records')
    }
    
    # Calculate statistics for numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = [col for col in df.columns if col not in numeric_columns]
    
    result["numeric_columns"] = numeric_columns
    result["categorical_columns"] = categorical_columns
    
    if numeric_columns:
        # Compute basic statistics for numeric columns
        stats = df[numeric_columns].describe().to_dict()
        result["statistics"] = stats
        
        # Generate insights
        insights = []
        for col in numeric_columns[:3]:  # Limit insights to first 3 numeric columns
            max_value = df[col].max()
            min_value = df[col].min()
            mean_value = df[col].mean()
            median_value = df[col].median()
            
            if not pd.isna(max_value) and not pd.isna(min_value):
                insights.append(f"The maximum {col} is {max_value:.2f}, and the minimum is {min_value:.2f}.")
            
            if not pd.isna(mean_value) and not pd.isna(median_value):
                if mean_value > median_value:
                    insights.append(f"The distribution of {col} is positively skewed (mean > median).")
                elif mean_value < median_value:
                    insights.append(f"The distribution of {col} is negatively skewed (mean < median).")
        
        result["insights"] = insights
    
    return result

# Route for home/intro page
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        
        if user_exists:
            flash('Username already taken.', 'danger')
            return redirect(url_for('register'))
        
        if email_exists:
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('login'))
        
        session['user_id'] = user.id
        session['username'] = user.username
        
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_datasets = Dataset.query.filter_by(user_id=user_id).all()
    
    # Get datasets shared with the user
    shared_with_user = db.session.query(Dataset).join(Share).filter(Share.shared_with_id == user_id).all()
    
    return render_template('dashboard.html', 
                           user_datasets=user_datasets, 
                           shared_datasets=shared_with_user)

# Data upload route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        title = request.form.get('title')
        description = request.form.get('description', '')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            new_dataset = Dataset(
                title=title,
                description=description,
                file_path=file_path,
                user_id=session['user_id']
            )
            
            db.session.add(new_dataset)
            db.session.commit()
            
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('File type not allowed', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html')

# Visualization route
@app.route('/visualize/<int:dataset_id>')
def visualize(dataset_id):
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Check if user owns the dataset or it's shared with them
    is_owner = dataset.user_id == user_id
    is_shared = Share.query.filter_by(dataset_id=dataset_id, shared_with_id=user_id).first() is not None
    
    if not (is_owner or is_shared):
        flash('You do not have permission to view this dataset.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Load data file but only pass minimal information to template
    # Detailed data will be loaded via the API
    df, error = load_dataset(dataset.file_path)
    if error:
        flash(f'Error loading dataset: {error}', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get basic metadata for initial display
    metadata = {
        "columns": df.columns.tolist(),
        "row_count": len(df)
    }
    
    return render_template('visualize.html', dataset=dataset, metadata=metadata, is_owner=is_owner)

# API endpoint for dataset analysis
@app.route('/api/dataset/<int:dataset_id>/analyze')
def api_dataset_analyze(dataset_id):
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    user_id = session['user_id']
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Check if user owns the dataset or it's shared with them
    is_owner = dataset.user_id == user_id
    is_shared = Share.query.filter_by(dataset_id=dataset_id, shared_with_id=user_id).first() is not None
    
    if not (is_owner or is_shared):
        return jsonify({"error": "Permission denied"}), 403
    
    # Load and analyze the dataset
    df, error = load_dataset(dataset.file_path)
    if error:
        return jsonify({"error": error}), 400
    
    # Perform analysis
    analysis_result = analyze_dataset(df)
    
    return jsonify(analysis_result)

# API endpoint for generating visualization data
@app.route('/api/dataset/<int:dataset_id>/visualize', methods=['GET'])
def api_dataset_visualize(dataset_id):
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    user_id = session['user_id']
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Check if user owns the dataset or it's shared with them
    is_owner = dataset.user_id == user_id
    is_shared = Share.query.filter_by(dataset_id=dataset_id, shared_with_id=user_id).first() is not None
    
    if not (is_owner or is_shared):
        return jsonify({"error": "Permission denied"}), 403
    
    # Get visualization parameters from request
    chart_type = request.args.get('chart_type', 'bar')
    x_column = request.args.get('x_column')
    y_column = request.args.get('y_column')
    
    # Load the dataset
    df, error = load_dataset(dataset.file_path)
    if error:
        return jsonify({"error": error}), 400
    
    if not x_column:
        # Default to first column if not specified
        x_column = df.columns[0] if len(df.columns) > 0 else None
    
    if not y_column:
        # Default to second column for y-axis, or first numeric column if available
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 0:
            y_column = numeric_cols[0]
        elif len(df.columns) > 1:
            y_column = df.columns[1]
        else:
            y_column = df.columns[0] if len(df.columns) > 0 else None
    
    # Generate visualization data
    try:
        if chart_type == 'pie':
            if x_column and y_column:
                # For pie charts, we need category and values
                result = {
                    'labels': df[x_column].tolist(),
                    'values': df[y_column].tolist(),
                }
        else:
            # For other chart types (bar, line, scatter)
            result = {
                'x': df[x_column].tolist() if x_column else [],
                'y': df[y_column].tolist() if y_column else [],
                'type': chart_type
            }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Sharing routes
@app.route('/share', methods=['GET'])
def share_data():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_datasets = Dataset.query.filter_by(user_id=user_id).all()
    users = User.query.filter(User.id != user_id).all()
    
    # Get existing shares to show who already has access
    shares = Share.query.join(Dataset).filter(Dataset.user_id == user_id).all()
    
    return render_template('share.html', datasets=user_datasets, users=users, shares=shares)

@app.route('/share/dataset', methods=['POST'])
def share_dataset():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    dataset_id = request.form.get('dataset_id')
    shared_with_id = request.form.get('user_id')
    
    # Validate input
    if not dataset_id or not shared_with_id:
        flash('Missing required fields', 'danger')
        return redirect(url_for('share_data'))
    
    # Check dataset ownership
    dataset = Dataset.query.get(dataset_id)
    if not dataset or dataset.user_id != user_id:
        flash('You cannot share this dataset', 'danger')
        return redirect(url_for('share_data'))
    
    # Check if already shared
    existing_share = Share.query.filter_by(
        dataset_id=dataset_id, 
        shared_with_id=shared_with_id
    ).first()
    
    if existing_share:
        flash('Dataset already shared with this user', 'warning')
        return redirect(url_for('share_data'))
    
    # Create new share
    new_share = Share(dataset_id=dataset_id, shared_with_id=shared_with_id)
    db.session.add(new_share)
    db.session.commit()
    
    flash('Dataset shared successfully', 'success')
    return redirect(url_for('share_data'))

@app.route('/share/revoke/<int:share_id>', methods=['POST'])
def revoke_share(share_id):
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    share = Share.query.join(Dataset).filter(Share.id == share_id, Dataset.user_id == user_id).first()
    
    if not share:
        flash('Share not found or you do not have permission to revoke it', 'danger')
        return redirect(url_for('share_data'))
    
    db.session.delete(share)
    db.session.commit()
    
    flash('Access revoked successfully', 'success')
    return redirect(url_for('share_data'))

# Run the application
if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)