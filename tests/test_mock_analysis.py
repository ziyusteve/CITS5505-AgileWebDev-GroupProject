from app import create_app
from app.scout_analysis.services import ScoutAnalysisService
import unittest

class TestMockAnalysis(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_mock_analysis_with_known_player(self):
        """Test mock analysis with a known player (LeBron James)"""
        test_text = "This is a test report about LeBron James, a forward for the Lakers."
        
        # Temporarily disable real API by setting a dummy API key
        original_api_key = self.app.config.get("GEMINI_API_KEY")
        self.app.config["GEMINI_API_KEY"] = "dummy_key"
        
        try:
            result = ScoutAnalysisService.analyze_report(test_text)
            
            # Verify the response structure
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
            
            # Check for required fields
            self.assertIn('processing_status', result)
            self.assertIn('player_info', result)
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
            
            # Verify player info
            player_info = result['player_info']
            self.assertEqual(player_info['name'], 'LeBron James')
            self.assertEqual(player_info['position'], 'Forward')
            
            # Verify data types
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
            
            # Verify rating ranges
            self.assertTrue(0 <= result['offensive_rating'] <= 100)
            self.assertTrue(0 <= result['defensive_rating'] <= 100)
            self.assertTrue(0 <= result['physical_rating'] <= 100)
            self.assertTrue(0 <= result['technical_rating'] <= 100)
            self.assertTrue(0 <= result['potential_rating'] <= 100)
            self.assertTrue(0 <= result['overall_rating'] <= 100)
            
        finally:
            # Restore original API key
            self.app.config["GEMINI_API_KEY"] = original_api_key

    def test_mock_analysis_with_unknown_player(self):
        """Test mock analysis with an unknown player"""
        test_text = "This is a test report about an unknown player."
        
        # Temporarily disable real API by setting a dummy API key
        original_api_key = self.app.config.get("GEMINI_API_KEY")
        self.app.config["GEMINI_API_KEY"] = "dummy_key"
        
        try:
            result = ScoutAnalysisService.analyze_report(test_text)
            
            # Verify the response structure
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
            
            # Check for required fields
            self.assertIn('processing_status', result)
            self.assertIn('player_info', result)
            self.assertIn('strengths', result)
            self.assertIn('weaknesses', result)
            self.assertIn('development_areas', result)
            self.assertIn('summary', result)
            
            # Verify player info
            player_info = result['player_info']
            self.assertEqual(player_info['name'], 'Unknown Player')
            
            # Verify data types and content
            self.assertIsInstance(result['strengths'], list)
            self.assertIsInstance(result['weaknesses'], list)
            self.assertIsInstance(result['development_areas'], list)
            self.assertIsInstance(result['summary'], str)
            
            # Verify that we have some content
            self.assertTrue(len(result['strengths']) > 0)
            self.assertTrue(len(result['weaknesses']) > 0)
            self.assertTrue(len(result['development_areas']) > 0)
            self.assertTrue(len(result['summary']) > 0)
            
        finally:
            # Restore original API key
            self.app.config["GEMINI_API_KEY"] = original_api_key

    def test_mock_analysis_with_empty_text(self):
        """Test mock analysis with empty text input"""
        test_text = ""
        
        # Temporarily disable real API by setting a dummy API key
        original_api_key = self.app.config.get("GEMINI_API_KEY")
        self.app.config["GEMINI_API_KEY"] = "dummy_key"
        
        try:
            result = ScoutAnalysisService.analyze_report(test_text)
            
            # Verify the response structure
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
            
            # Check for required fields
            self.assertIn('processing_status', result)
            self.assertIn('player_info', result)
            self.assertIn('strengths', result)
            self.assertIn('weaknesses', result)
            self.assertIn('development_areas', result)
            self.assertIn('summary', result)
            
            # Verify player info defaults
            player_info = result['player_info']
            self.assertEqual(player_info['name'], 'Unknown Player')
            self.assertEqual(player_info['position'], 'Forward')
            
            # Verify data types and content
            self.assertIsInstance(result['strengths'], list)
            self.assertIsInstance(result['weaknesses'], list)
            self.assertIsInstance(result['development_areas'], list)
            self.assertIsInstance(result['summary'], str)
            
            # Verify that we have some content
            self.assertTrue(len(result['strengths']) > 0)
            self.assertTrue(len(result['weaknesses']) > 0)
            self.assertTrue(len(result['development_areas']) > 0)
            self.assertTrue(len(result['summary']) > 0)
            
            # Verify summary mentions unknown player
            self.assertIn('unknown player', result['summary'].lower())
            
        finally:
            # Restore original API key
            self.app.config["GEMINI_API_KEY"] = original_api_key

if __name__ == '__main__':
    unittest.main() 