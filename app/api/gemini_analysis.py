from flask import Blueprint, request, jsonify, current_app
from app.utils.text_analysis import (
    analyze_sentiment, 
    extract_keywords, 
    summarize_text,
    classify_text
)
import traceback

gemini_analysis_bp = Blueprint('gemini_analysis', __name__)

@gemini_analysis_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Text Analysis API Endpoint
    
    Request Body Format:
    {
        "text": "Text to analyze",
        "analysis_type": "sentiment|keywords|summary|classification",
        "options": {
            // Optional analysis parameters
            "max_words": 50,  // For summary
            "categories": []  // For classification
        }
    }
    """
    # 记录请求开始
    current_app.logger.info("收到Gemini分析请求")
    
    data = request.json
    if not data or 'text' not in data:
        current_app.logger.error("请求缺少text字段")
        return jsonify({"error": "Please provide text for analysis"}), 400
    
    text = data.get('text')
    current_app.logger.info(f"分析文本: {text[:50]}...")
    
    analysis_type = data.get('analysis_type', 'sentiment')
    current_app.logger.info(f"分析类型: {analysis_type}")
    
    options = data.get('options', {})
    current_app.logger.info(f"分析选项: {options}")
    
    # 检查Gemini实例是否存在
    gemini_instance = current_app.config.get('GEMINI_INSTANCE')
    if not gemini_instance:
        current_app.logger.error("GEMINI_INSTANCE未在app.config中找到!")
    else:
        current_app.logger.info(f"找到GEMINI_INSTANCE，API密钥: {gemini_instance.api_key[:5]}...")
    
    try:
        result = None
        if analysis_type == 'sentiment':
            current_app.logger.info("调用情感分析...")
            result = analyze_sentiment(text)
        elif analysis_type == 'keywords':
            current_app.logger.info("调用关键词提取...")
            result = extract_keywords(text)
        elif analysis_type == 'summary':
            max_words = options.get('max_words', 50)
            current_app.logger.info(f"调用文本摘要，最大字数: {max_words}...")
            result = summarize_text(text, max_words)
        elif analysis_type == 'classification':
            categories = options.get('categories')
            current_app.logger.info(f"调用文本分类，类别: {categories}...")
            result = classify_text(text, categories)
        else:
            current_app.logger.error(f"不支持的分析类型: {analysis_type}")
            return jsonify({"error": f"Unsupported analysis type: {analysis_type}"}), 400
        
        current_app.logger.info(f"分析完成，结果类型: {type(result).__name__}")
        
        # 记录返回结果
        if isinstance(result, dict):
            # 如果是错误信息，记录错误
            if 'error' in result:
                current_app.logger.error(f"分析出错: {result['error']}")
            else:
                # 记录部分结果内容
                keys = list(result.keys())
                current_app.logger.info(f"返回结果包含键: {keys}")
        
        return jsonify({"success": True, "result": result})
    
    except Exception as e:
        error_msg = f"分析过程异常: {str(e)}"
        stack_trace = traceback.format_exc()
        current_app.logger.error(f"{error_msg}\n{stack_trace}")
        return jsonify({"error": f"Error during analysis: {str(e)}"}), 500 