from flask import jsonify, session, request, current_app
from app.api import bp
from app.models.dataset import Dataset
from app.models.share import Share
from app.utils import load_dataset
import numpy as np
import pandas as pd

def analyze_dataset(df):
    """对数据集进行分析，生成统计信息和洞察"""
    result = {
        "column_count": len(df.columns),
        "row_count": len(df),
        "preview": df.head(10).to_dict('records')
    }
    
    # 为数值列计算统计信息
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = [col for col in df.columns if col not in numeric_columns]
    
    result["numeric_columns"] = numeric_columns
    result["categorical_columns"] = categorical_columns
    
    if numeric_columns:
        # 计算数值列的基本统计信息
        stats = df[numeric_columns].describe().to_dict()
        result["statistics"] = stats
        
        # 生成洞察
        insights = []
        for col in numeric_columns[:3]:  # 限制为前3个数值列
            max_value = df[col].max()
            min_value = df[col].min()
            mean_value = df[col].mean()
            median_value = df[col].median()
            
            if not pd.isna(max_value) and not pd.isna(min_value):
                insights.append(f"列 {col} 的最大值为 {max_value:.2f}，最小值为 {min_value:.2f}。")
            
            if not pd.isna(mean_value) and not pd.isna(median_value):
                if mean_value > median_value:
                    insights.append(f"列 {col} 的分布呈正偏态（均值 > 中位数）。")
                elif mean_value < median_value:
                    insights.append(f"列 {col} 的分布呈负偏态（均值 < 中位数）。")
        
        result["insights"] = insights
    
    return result

@bp.route('/dataset/<int:dataset_id>/analyze')
def dataset_analyze(dataset_id):
    """数据集分析API端点"""
    if 'user_id' not in session:
        return jsonify({"error": "需要身份验证"}), 401
    
    user_id = session['user_id']
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查用户是否拥有数据集或数据集是否与其共享
    is_owner = dataset.user_id == user_id
    is_shared = Share.query.filter_by(dataset_id=dataset_id, shared_with_id=user_id).first() is not None
    
    if not (is_owner or is_shared):
        return jsonify({"error": "权限被拒绝"}), 403
    
    # 加载并分析数据集
    df, error = load_dataset(dataset.file_path)
    if error:
        return jsonify({"error": error}), 400
    
    # 执行分析
    analysis_result = analyze_dataset(df)
    
    return jsonify(analysis_result)

@bp.route('/dataset/<int:dataset_id>/visualize', methods=['GET'])
def dataset_visualize(dataset_id):
    """数据集可视化API端点"""
    if 'user_id' not in session:
        return jsonify({"error": "需要身份验证"}), 401
    
    user_id = session['user_id']
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # 检查用户是否拥有数据集或数据集是否与其共享
    is_owner = dataset.user_id == user_id
    is_shared = Share.query.filter_by(dataset_id=dataset_id, shared_with_id=user_id).first() is not None
    
    if not (is_owner or is_shared):
        return jsonify({"error": "权限被拒绝"}), 403
    
    # 获取可视化参数
    chart_type = request.args.get('chart_type', 'bar')
    x_column = request.args.get('x_column')
    y_column = request.args.get('y_column')
    
    # 加载数据集
    df, error = load_dataset(dataset.file_path)
    if error:
        return jsonify({"error": error}), 400
    
    if not x_column:
        # 如果未指定，默认使用第一列
        x_column = df.columns[0] if len(df.columns) > 0 else None
    
    if not y_column:
        # 默认使用第二列或第一个数值列（如果有）
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 0:
            y_column = numeric_cols[0]
        elif len(df.columns) > 1:
            y_column = df.columns[1]
        else:
            y_column = df.columns[0] if len(df.columns) > 0 else None
    
    # 生成可视化数据
    try:
        if chart_type == 'pie':
            if x_column and y_column:
                # 对于饼图，我们需要类别和值
                result = {
                    'labels': df[x_column].tolist(),
                    'values': df[y_column].tolist(),
                }
        else:
            # 对于其他图表类型（柱状图、折线图、散点图）
            result = {
                'x': df[x_column].tolist() if x_column else [],
                'y': df[y_column].tolist() if y_column else [],
                'type': chart_type
            }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/scout-analysis/<int:dataset_id>', methods=['GET'])
def get_scout_analysis(dataset_id):
    """API endpoint to get scout report analysis for a dataset"""
    # Check if scout analysis is enabled
    if not current_app.config.get('ENABLE_SCOUT_ANALYSIS', False):
        return jsonify({"error": "Scout analysis feature is not enabled"}), 404
    
    # Check user authentication
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    # Get the dataset
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Check if user has access to the dataset
    if dataset.user_id != session['user_id']:
        # Check if the dataset is shared with the user
        shared = Share.query.filter_by(dataset_id=dataset_id, shared_with=session['user_id']).first()
        if not shared:
            return jsonify({"error": "You don't have access to this dataset"}), 403
    
    # Import the ScoutReportAnalysis model only if scout analysis is enabled
    from app.scout_analysis.models import ScoutReportAnalysis
    
    # Get the analysis for this dataset
    analysis = ScoutReportAnalysis.query.filter_by(dataset_id=dataset_id).first()
    
    if not analysis:
        return jsonify({"error": "No scout analysis found for this dataset"}), 404
    
    # Return the analysis data
    return jsonify({
        "dataset_id": dataset_id,
        "dataset_title": dataset.title,
        "processing_status": analysis.processing_status,
        "analysis_date": analysis.analysis_date.isoformat() if analysis.analysis_date else None,
        "player_info": {
            "name": analysis.player_name,
            "position": analysis.position,
            "team": analysis.team
        },
        "ratings": {
            "offensive": analysis.offensive_rating,
            "defensive": analysis.defensive_rating,
            "physical": analysis.physical_rating,
            "technical": analysis.technical_rating,
            "potential": analysis.potential_rating,
            "overall": analysis.overall_rating
        },
        "full_analysis": analysis.to_dict()["analysis"] if analysis.analysis_result else {}
    })
