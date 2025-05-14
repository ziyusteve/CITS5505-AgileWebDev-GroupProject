import os
from app import create_app
from app.scout_analysis.services import ScoutAnalysisService
from app.models.dataset import Dataset
from app.models.user import User
from app.extensions import db
from app.config import config_by_name
import json
import unittest
from flask_login import login_user

class TestScoutAnalysisAPI(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Use a file-based SQLite DB for testing
        config_by_name['testing'].SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
        config_by_name['testing'].ENABLE_SCOUT_ANALYSIS = True
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()  # Ensure tables exist

        # Print all registered routes for diagnostics
        print("\nRegistered routes:")
        for rule in self.app.url_map.iter_rules():
            print(rule)

        # Create test user
        self.test_user = User(username='testuser', email='test@example.com')
        self.test_user.set_password('password')
        self.test_user.is_verified = True  # Ensure user is verified
        db.session.add(self.test_user)
        db.session.flush()  # Flush to ensure user is written to DB
        db.session.refresh(self.test_user)  # Refresh to ensure user is up-to-date
        
        # Create test dataset
        self.test_dataset = Dataset(
            title='Test Dataset',
            file_path='/tmp/test.txt',
            user_id=self.test_user.id
        )
        db.session.add(self.test_dataset)
        db.session.flush()  # Flush to ensure dataset is written to DB
        db.session.refresh(self.test_dataset)  # Refresh to ensure dataset is up-to-date
        db.session.commit()  # Commit to finalize changes

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()  # Clean up tables
        self.app_context.pop()
        # Remove the test database file
        if os.path.exists('test.db'):
            os.remove('test.db')

    def test_scout_analysis_api(self):
        """Test the scout analysis API endpoint"""
        # Login the test user using the client
        with self.client as client:
            # First, login through the login route
            response = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'password',
                'remember': False,
                'submit': 'Login'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            # Debug: Print dataset ID and verify it exists
            print(f"\nDebug: Dataset ID: {self.test_dataset.id}")
            dataset = Dataset.query.get(self.test_dataset.id)
            print(f"Debug: Dataset exists: {dataset is not None}")
            if dataset:
                print(f"Debug: Dataset title: {dataset.title}")
                print(f"Debug: Dataset user_id: {dataset.user_id}")
            
            # Test Case 1: No analysis exists
            url = f'/api/scout-analysis/{self.test_dataset.id}'
            print(f"Debug: Making request to: {url}")
            response = client.get(url)
            
            # Debug: Print response details
            print(f"Debug: Response status code: {response.status_code}")
            print(f"Debug: Response data: {response.get_data(as_text=True)}")
            
            # Assert response - expect 404 when no analysis exists
            self.assertEqual(response.status_code, 404)
            data = response.get_json()
            self.assertIn('error', data)
            self.assertIn('processing_status', data)
            self.assertEqual(data['processing_status'], 'not_found')
            self.assertEqual(data['error'], 'No scout analysis report found for this dataset')
            
            # Test Case 2: Create and test with an analysis
            from app.scout_analysis.models import ScoutReportAnalysis
            from datetime import datetime
            
            # Create a test analysis with a complete analysis result
            analysis_result = {
                'player_name': 'Test Player',
                'position': 'Forward',
                'team': 'Test Team',
                'offensive_rating': 85.0,
                'defensive_rating': 80.0,
                'physical_rating': 82.0,
                'technical_rating': 88.0,
                'potential_rating': 90.0,
                'overall_rating': 85.0,
                'summary': 'Test analysis result'
            }
            
            test_analysis = ScoutReportAnalysis(
                dataset_id=self.test_dataset.id,
                processing_status='completed',
                analysis_date=datetime.utcnow(),
                analysis_result=json.dumps(analysis_result)
            )
            db.session.add(test_analysis)
            db.session.commit()
            
            # Make the API request again
            response = client.get(url)
            
            # Debug: Print response details
            print(f"\nDebug: Response status code with analysis: {response.status_code}")
            print(f"Debug: Response data with analysis: {response.get_data(as_text=True)}")
            
            # Assert response - expect 200 when analysis exists
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['processing_status'], 'completed')
            self.assertEqual(data['dataset_id'], self.test_dataset.id)
            self.assertEqual(data['player_name'], 'Test Player')
            self.assertEqual(data['position'], 'Forward')
            self.assertEqual(data['team'], 'Test Team')
            self.assertEqual(data['offensive_rating'], 85.0)
            self.assertEqual(data['defensive_rating'], 80.0)
            self.assertEqual(data['physical_rating'], 82.0)
            self.assertEqual(data['technical_rating'], 88.0)
            self.assertEqual(data['potential_rating'], 90.0)
            self.assertEqual(data['overall_rating'], 85.0)
            self.assertEqual(data['summary'], 'Test analysis result')

if __name__ == "__main__":
    unittest.main()
