from app import create_app
from app.scout_analysis.services import ScoutAnalysisService
import json

app = create_app()

def test_scout_analysis_api():
    print("Testing Scout Analysis API connection...")
    # Test text
    test_text = "Testing Gemini API connection. This is an NBA player: Lebron James, he is an All-Star player."
    
    with app.app_context():
        try:
            # Get API key information
            api_key = app.config.get('GEMINI_API_KEY')
            print(f"API key: {api_key[:5]}...{api_key[-5:]}")
            print(f"Scout analysis enabled status: {app.config.get('ENABLE_SCOUT_ANALYSIS', False)}")
            
            # Call analysis service
            result = ScoutAnalysisService.analyze_report(test_text)
            
            # Output results
            print("\nAnalysis results:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"Test failed: {e}")
            return False

if __name__ == "__main__":
    success = test_scout_analysis_api()
    print(f"\nTest result: {'Success' if success else 'Failed'}") 