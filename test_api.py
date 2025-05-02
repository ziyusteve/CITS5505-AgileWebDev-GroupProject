import sys
import os
# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.scout_analysis.services import ScoutAnalysisService
import json

app = create_app('development')

def test_scout_analysis_api():
    print("Testing Scout Analysis API connection...")
    # Test text
    test_text = "Testing Gemini API connection. This is an NBA player: Lebron James, an all-star player." # Changed to Gemini
    with app.app_context():
        try:
            # Get API key info
            api_key = app.config.get('GEMINI_API_KEY') # Changed to GEMINI_API_KEY
            if api_key:
                print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
            else:
                print("API Key not found in configuration.")
            print(f"Scout Analysis Enabled: {app.config.get('ENABLE_SCOUT_ANALYSIS', False)}")
            # Call analysis service
            result = ScoutAnalysisService.analyze_report(test_text)
            print(f"Analysis Result: {result}")
            return True
        except Exception as e:
            print(f"Error during test: {e}")
            return False

if __name__ == '__main__':
    success = test_scout_analysis_api()
    print(f"\n测试结果: {'成功' if success else '失败'}") 