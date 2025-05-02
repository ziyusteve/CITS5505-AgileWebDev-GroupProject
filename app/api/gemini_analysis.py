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
    # Log the start of the request
    current_app.logger.info("Received Gemini analysis request")
    
    data = request.json
    if not data or 'text' not in data:
        current_app.logger.error("Request is missing the 'text' field")
        return jsonify({"error": "Please provide text for analysis"}), 400
    
    text = data.get('text')
    current_app.logger.info(f"Text to analyze: {text[:50]}...")
    
    analysis_type = data.get('analysis_type', 'sentiment')
    current_app.logger.info(f"Analysis type: {analysis_type}")
    
    options = data.get('options', {})
    current_app.logger.info(f"Analysis options: {options}")
    
    # Check if the Gemini instance exists
    gemini_instance = current_app.config.get('GEMINI_INSTANCE')
    if not gemini_instance:
        current_app.logger.error("GEMINI_INSTANCE not found in app.config!")
    else:
        current_app.logger.info(f"GEMINI_INSTANCE found, API key: {gemini_instance.api_key[:5]}...")
    
    try:
        result = None
        if analysis_type == 'sentiment':
            current_app.logger.info("Calling sentiment analysis...")
            result = analyze_sentiment(text)
        elif analysis_type == 'keywords':
            current_app.logger.info("Calling keyword extraction...")
            result = extract_keywords(text)
        elif analysis_type == 'summary':
            max_words = options.get('max_words', 50)
            current_app.logger.info(f"Calling text summarization, max words: {max_words}...")
            result = summarize_text(text, max_words)
        elif analysis_type == 'classification':
            categories = options.get('categories')
            current_app.logger.info(f"Calling text classification, categories: {categories}...")
            result = classify_text(text, categories)
        else:
            current_app.logger.error(f"Unsupported analysis type: {analysis_type}")
            return jsonify({"error": f"Unsupported analysis type: {analysis_type}"}), 400
        
        current_app.logger.info(f"Analysis completed, result type: {type(result).__name__}")
        
        # Log the returned result
        if isinstance(result, dict):
            # If it's an error message, log the error
            if 'error' in result:
                current_app.logger.error(f"Analysis error: {result['error']}")
            else:
                # Log part of the result content
                keys = list(result.keys())
                current_app.logger.info(f"Returned result contains keys: {keys}")
        
        return jsonify({"success": True, "result": result})
    
    except Exception as e:
        error_msg = f"Exception during analysis: {str(e)}"
        stack_trace = traceback.format_exc()
        current_app.logger.error(f"{error_msg}\n{stack_trace}")
        return jsonify({"error": f"Error during analysis: {str(e)}"}), 500