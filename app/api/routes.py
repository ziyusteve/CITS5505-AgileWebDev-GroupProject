from flask import jsonify, session, request, current_app
from app.api import bp
from app.models.dataset import Dataset
from app.models.share import Share
from app.utils import load_dataset
import numpy as np
import pandas as pd

def analyze_dataset(df):
    """Analyze the dataset, generate statistics and insights"""
    result = {
        "column_count": len(df.columns),
        "row_count": len(df),
        "preview": df.head(10).to_dict('records')
    }
    
    # Calculate statistics for numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = [col for col in df.columns if col not in numeric_columns]
    
    result["numeric_columns"] = numeric_columns
    result["categorical_columns"] = categorical_columns
    
    if numeric_columns:
        # Calculate basic statistics for numeric columns
        stats = df[numeric_columns].describe().to_dict()
        result["statistics"] = stats
        
        # Generate insights
        insights = []
        for col in numeric_columns[:3]:  # Limit to first 3 numeric columns
            max_value = df[col].max()
            min_value = df[col].min()
            mean_value = df[col].mean()
            median_value = df[col].median()
            
            if not pd.isna(max_value) and not pd.isna(min_value):
                insights.append(f"Column {col} has a maximum value of {max_value:.2f} and a minimum value of {min_value:.2f}.")
            
            if not pd.isna(mean_value) and not pd.isna(median_value):
                if mean_value > median_value:
                    insights.append(f"Column {col} has a positively skewed distribution (mean > median).")
                elif mean_value < median_value:
                    insights.append(f"Column {col} has a negatively skewed distribution (mean < median).")
        
        result["insights"] = insights
    
    return result

@bp.route('/dataset/<int:dataset_id>/analyze')
def dataset_analyze(dataset_id):
    """Dataset analysis API endpoint"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    user_id = session['user_id']
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Check if the user owns the dataset or the dataset is shared with them
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

@bp.route('/dataset/<int:dataset_id>/visualize', methods=['GET'])
def dataset_visualize(dataset_id):
    """Dataset visualization API endpoint"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    user_id = session['user_id']
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Check if the user owns the dataset or the dataset is shared with them
    is_owner = dataset.user_id == user_id
    is_shared = Share.query.filter_by(dataset_id=dataset_id, shared_with_id=user_id).first() is not None
    
    if not (is_owner or is_shared):
        return jsonify({"error": "Permission denied"}), 403
    
    # Get visualization parameters
    chart_type = request.args.get('chart_type', 'bar')
    x_column = request.args.get('x_column')
    y_column = request.args.get('y_column')
    
    # Load the dataset
    df, error = load_dataset(dataset.file_path)
    if error:
        return jsonify({"error": error}), 400
    
    if not x_column:
        # If not specified, default to the first column
        x_column = df.columns[0] if len(df.columns) > 0 else None
    
    if not y_column:
        # Default to the second column or the first numeric column (if any)
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
                # For pie charts, we need categories and values
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

@bp.route('/scout-analysis/<int:dataset_id>')
def scout_analysis(dataset_id):
    """Scout report analysis API endpoint"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required", "processing_status": "failed"}), 401
    
    user_id = session['user_id']
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Check if the user owns the dataset or the dataset is shared with them
    is_owner = dataset.user_id == user_id
    is_shared = Share.query.filter_by(dataset_id=dataset_id, shared_with_id=user_id).first() is not None
    
    if not (is_owner or is_shared):
        return jsonify({"error": "You do not have access to this dataset", "processing_status": "failed"}), 403
    
    # Retrieve the scout report analysis
    try:
        from app.scout_analysis.models import ScoutReportAnalysis
        analysis = ScoutReportAnalysis.query.filter_by(dataset_id=dataset_id).first()
        
        if not analysis:
            # If no analysis record exists, return a specific response
            return jsonify({
                "processing_status": "not_found",
                "error": "No scout analysis report found for this dataset"
            }), 404
        
        # If the analysis is still in progress
        if analysis.processing_status == 'pending':
            return jsonify({
                "processing_status": "pending",
                "dataset_id": dataset_id,
                "message": "Analysis is in progress"
            })
            
        # If the analysis failed
        if analysis.processing_status == 'failed':
            return jsonify({
                "processing_status": "failed",
                "dataset_id": dataset_id,
                "error": "Analysis process failed"
            })
            
        # If the analysis completed successfully
        if analysis.analysis_result:
            try:
                import json
                analysis_data = json.loads(analysis.analysis_result)
                # Add additional information
                analysis_data['processing_status'] = 'completed'
                analysis_data['dataset_id'] = dataset_id
                return jsonify(analysis_data)
            except Exception as e:
                current_app.logger.error(f"Error parsing analysis result JSON: {str(e)}")
                # If JSON parsing fails, return the original string as a summary
                return jsonify({
                    "processing_status": "completed",
                    "dataset_id": dataset_id,
                    "summary": analysis.analysis_result,
                    "error": "Result format parsing error"
                })
        else:
            # If there are no analysis results
            return jsonify({
                "processing_status": "completed",
                "dataset_id": dataset_id,
                "summary": "Analysis completed but no results returned",
                "error": "No analysis data available"
            })
            
    except Exception as e:
        current_app.logger.error(f"Error getting scout analysis data: {str(e)}")
        return jsonify({
            "processing_status": "error",
            "error": f"Error retrieving analysis data: {str(e)}"
        }), 500

@bp.route('/test-api')
def test_api():
    """Test API connection endpoint, no authentication required"""
    try:
        # Import scout analysis service
        from app.scout_analysis.services import ScoutAnalysisService

        # Get API key and version
        api_key = current_app.config.get('DEEPSEEK_API_KEY')
        api_key_masked = f"{api_key[:5]}...{api_key[-5:]}" if api_key else "Not set"
        
        # Generate a short test text
        test_text = "Testing DeepSeek API connection. This is an NBA player: Lebron James, an all-star player."
        
        # Try to call the API for simple analysis
        result = ScoutAnalysisService.analyze_report(test_text)
        
        # Return test results
        return jsonify({
            "status": "success",
            "api_key_masked": api_key_masked,
            "config_enabled": current_app.config.get('ENABLE_SCOUT_ANALYSIS', False),
            "test_result": result,
            "message": "API connection test successful"
        })
    except Exception as e:
        current_app.logger.error(f"API test failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"API test failed: {str(e)}",
            "api_key_masked": api_key_masked if 'api_key_masked' in locals() else "Unknown"
        }), 500
