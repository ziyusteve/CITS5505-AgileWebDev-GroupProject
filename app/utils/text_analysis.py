from flask import current_app


def analyze_sentiment(text):
    """
    Analyze text sentiment

    Args:
        text (str): Text content to analyze

    Returns:
        dict: Dictionary containing sentiment analysis results
    """
    gemini = current_app.config.get("GEMINI_INSTANCE")
    if not gemini:
        return {"error": "Gemini API instance not initialized"}

    try:
        result = gemini.analyze_text(text)
        # Return API result directly, without using hardcoded default values
        if isinstance(result, dict) and "error" in result:
            return result
        return result
    except Exception as e:
        current_app.logger.error(f"Error analyzing sentiment: {str(e)}")
        return {"error": str(e)}


def extract_keywords(text):
    """
    Extract keywords from text

    Args:
        text (str): Text content to analyze

    Returns:
        dict: Dictionary containing keyword extraction results
    """
    gemini = current_app.config.get("GEMINI_INSTANCE")
    if not gemini:
        return {"error": "Gemini API instance not initialized"}

    try:
        result = gemini.analyze_text(text)
        # Return API result directly, without using hardcoded default values
        if isinstance(result, dict) and "error" in result:
            return result
        return result
    except Exception as e:
        current_app.logger.error(f"Error extracting keywords: {str(e)}")
        return {"error": str(e)}


def summarize_text(text, max_words=50):
    """
    Summarize text

    Args:
        text (str): Text content to summarize
        max_words (int): Maximum word count for the summary

    Returns:
        dict: Dictionary containing text summarization results
    """
    gemini = current_app.config.get("GEMINI_INSTANCE")
    if not gemini:
        return {"error": "Gemini API instance not initialized"}

    try:
        # Include max_words parameter in the request
        prompt = f"Please summarize the following text in no more than {max_words} words:\n\n{text}"
        result = gemini.analyze_text(prompt)
        # Return API result directly, without using hardcoded default values
        if isinstance(result, dict) and "error" in result:
            return result
        return result
    except Exception as e:
        current_app.logger.error(f"Error generating summary: {str(e)}")
        return {"error": str(e)}


def classify_text(text, categories=None):
    """
    Classify text

    Args:
        text (str): Text content to classify
        categories (list): Optional list of classification categories

    Returns:
        dict: Dictionary containing text classification results
    """
    gemini = current_app.config.get("GEMINI_INSTANCE")
    if not gemini:
        return {"error": "Gemini API instance not initialized"}

    try:
        # If categories are provided, include them in the prompt
        prompt = text
        if categories:
            category_list = ", ".join(categories)
            prompt = f"Please classify the following text into one of these categories: {category_list}\n\n{text}"

        result = gemini.analyze_text(prompt)
        # Return API result directly, without using hardcoded default values
        if isinstance(result, dict) and "error" in result:
            return result
        return result
    except Exception as e:
        current_app.logger.error(f"Error classifying text: {str(e)}")
        return {"error": str(e)}
