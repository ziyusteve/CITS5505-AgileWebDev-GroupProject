from app import create_app
from app.scout_analysis.services import ScoutAnalysisService
import json
import unittest

app = create_app()

class TestScoutAnalysisAPI(unittest.TestCase):
    def test_scout_analysis_api(self):
        print("Testing Scout Analysis API connection...")
        # Test text
        test_text = (
            "Testing Gemini API connection. This is an NBA player: Lebron James, "
            "he is an All-Star player."
        )

        with app.app_context():
            try:
                # Get API key information
                api_key = app.config.get("GEMINI_API_KEY")
                print(f"API key: {api_key[:5]}...{api_key[-5:]}")
                print(
                    f"Scout analysis enabled status: "
                    f"{app.config.get('ENABLE_SCOUT_ANALYSIS', False)}"
                )

                # Call analysis service
                result = ScoutAnalysisService.analyze_report(test_text)

                # Output results
                print("\nAnalysis results:")
                print(json.dumps(result, indent=2, ensure_ascii=False))

                # Assert the result is not None or empty
                self.assertIsNotNone(result)
                self.assertIsInstance(result, dict)
                
                # Check for required fields in the response
                self.assertIn('player_name', result)
                self.assertIn('position', result)
                self.assertIn('strengths', result)
                self.assertIn('weaknesses', result)
                self.assertIn('development_areas', result)
                self.assertIn('summary', result)
                self.assertIn('offensive_rating', result)
                self.assertIn('defensive_rating', result)
                self.assertIn('physical_rating', result)
                self.assertIn('technical_rating', result)
                self.assertIn('potential_rating', result)
                self.assertIn('overall_rating', result)
                
                # Verify data types
                self.assertIsInstance(result['player_name'], str)
                self.assertIsInstance(result['position'], str)
                self.assertIsInstance(result['strengths'], list)
                self.assertIsInstance(result['weaknesses'], list)
                self.assertIsInstance(result['development_areas'], list)
                self.assertIsInstance(result['summary'], str)
                self.assertIsInstance(result['offensive_rating'], (int, float))
                self.assertIsInstance(result['defensive_rating'], (int, float))
                self.assertIsInstance(result['physical_rating'], (int, float))
                self.assertIsInstance(result['technical_rating'], (int, float))
                self.assertIsInstance(result['potential_rating'], (int, float))
                self.assertIsInstance(result['overall_rating'], (int, float))
                
                return True
            except Exception as e:
                print(f"Test failed: {e}")
                self.fail(f"Test failed: {e}")

if __name__ == "__main__":
    unittest.main()
