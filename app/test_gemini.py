from flask import current_app

from app.extensions import get_gemini_api


def test_gemini_api():
    """Test Gemini API connection"""
    try:
        gemini = get_gemini_api()
        if not gemini.api_key:
            # Try to update API key from current app config
            try:
                api_key = current_app.config.get("GEMINI_API_KEY", "")
                if api_key:
                    gemini.set_api_key(api_key)
            except Exception as e:
                print(f"Error getting API key from config: {e}")

        # Test a simple prompt
        response = gemini.analyze_text(
            "Hello, can you provide a short response for testing?"
        )
        print(f"Test response: {response}")
        return True
    except Exception as e:
        print(f"Gemini API test failed: {e}")
        return False


if __name__ == "__main__":
    test_gemini_api()
