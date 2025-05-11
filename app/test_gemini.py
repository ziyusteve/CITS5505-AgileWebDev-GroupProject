from flask import current_app
from app.extensions import get_gemini_api
import unittest
from app import create_app

class TestGeminiAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_gemini_api_connection(self):
        """Test Gemini API connection and basic functionality"""
        try:
            gemini = get_gemini_api()
            if not gemini.api_key:
                # Try to update API key from current app config
                try:
                    api_key = current_app.config.get("GEMINI_API_KEY", "")
                    if api_key:
                        gemini.set_api_key(api_key)
                except Exception as e:
                    self.fail(f"Error getting API key from config: {e}")

            # Test a simple prompt
            response = gemini.analyze_text(
                "Hello, can you provide a short response for testing?"
            )
            
            # Assert that we got a response
            self.assertIsNotNone(response)
            self.assertIsInstance(response, dict)
            self.assertIn('result', response)
            self.assertIsInstance(response['result'], str)
            self.assertTrue(len(response['result']) > 0)
            
        except Exception as e:
            self.fail(f"Gemini API test failed: {e}")

if __name__ == "__main__":
    unittest.main()
