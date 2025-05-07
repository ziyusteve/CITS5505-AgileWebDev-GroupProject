from flask import Blueprint, request, current_app, jsonify

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/analyze", methods=["POST"])
def analyze_text():
    """
    Analyze text using Gemini API

    Expected JSON body:
    {
        "text": "Your text to analyze",
        "analysis_type": "sentiment|keywords|summary|classification",
        "options": {
            // Optional parameters specific to the analysis type
            "max_words": 100,  // For summary
            "categories": ["sports", "politics"]  // For classification
        }
    }

    Returns:
        JSON with analysis results
    """
    try:
        data = request.get_json()

        # Log request start
        current_app.logger.info("Received Gemini analysis request")

        # Validate input
        if "text" not in data:
            current_app.logger.error("Request missing text field")
            return jsonify({"error": "Text field is required"}), 400

        text = data["text"]
        current_app.logger.info(f"Analyzing text: {text[:50]}...")

        analysis_type = data.get("analysis_type", "sentiment")
        current_app.logger.info(f"Analysis type: {analysis_type}")

        options = data.get("options", {})
        current_app.logger.info(f"Analysis options: {options}")

        # Check if Gemini instance exists
        gemini_instance = current_app.config.get("GEMINI_INSTANCE")
        if not gemini_instance:
            current_app.logger.error("GEMINI_INSTANCE not found in app.config!")
            return jsonify({"error": "Gemini API not configured"}), 500

        current_app.logger.info(
            f"Found GEMINI_INSTANCE, API key: {gemini_instance.api_key[:5]}..."
        )

        # Perform the requested analysis
        result = None

        if analysis_type == "sentiment":
            current_app.logger.info("Calling sentiment analysis...")
            result = gemini_instance.analyze_sentiment(text)
        elif analysis_type == "keywords":
            current_app.logger.info("Calling keyword extraction...")
            result = gemini_instance.extract_keywords(text)
        elif analysis_type == "summary":
            max_words = options.get("max_words", 100)
            current_app.logger.info(
                f"Calling text summarization, max words: {max_words}..."
            )
            result = gemini_instance.summarize(text, max_words=max_words)
        elif analysis_type == "classification":
            categories = options.get("categories", [])
            current_app.logger.info(
                f"Calling text classification, categories: {categories}..."
            )
            result = gemini_instance.classify(text, categories=categories)
        else:
            current_app.logger.error(f"Unsupported analysis type: {analysis_type}")
            return (
                jsonify({"error": f"Unsupported analysis type: {analysis_type}"}),
                400,
            )

        current_app.logger.info(
            f"Analysis complete, result type: {type(result).__name__}"
        )

        # Log response
        response = {"result": result}
        return jsonify(response)

    except Exception as e:
        current_app.logger.error(f"Error in analyze_text: {str(e)}")
        return jsonify({"error": str(e)}), 500
