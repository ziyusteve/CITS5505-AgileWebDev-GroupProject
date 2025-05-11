import unittest
from flask import current_app
from app import create_app
from app.extensions import db
from app.models.user import User
from app.extensions import mail
from flask_mail import Message
import json
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import time
from flask_login import login_user

class TestEmailVerification(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app('testing')
        # Configure test email settings and disable CSRF
        self.app.config.update(
            MAIL_SERVER='smtp.office365.com',
            MAIL_PORT=587,
            MAIL_USE_TLS=True,
            MAIL_USERNAME='wangziyusteve@outlook.com',
            MAIL_PASSWORD='rzrrcsvnkwjhdhpf',
            MAIL_DEFAULT_SENDER='wangziyusteve@outlook.com',
            BASE_URL='http://localhost:5000',
            WTF_CSRF_ENABLED=False
        )
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_verification_email_sent(self):
        """Test that verification email is sent during registration"""
        with mail.record_messages() as outbox:
            response = self.client.post('/auth/register', data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'confirm_password': 'testpass123',
                'terms': True
            }, follow_redirects=True)

            # Check if user was created
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
            self.assertFalse(user.is_verified)

            # Check if verification email was sent
            self.assertEqual(len(outbox), 1)
            self.assertEqual(outbox[0].subject, 'Verify Your Email')
            self.assertIn('test@example.com', outbox[0].recipients)
            self.assertIn('verify', outbox[0].body.lower())

    def test_verification_token(self):
        """Test email verification token generation and validation"""
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()

        # Generate verification token
        token = user.generate_verification_token()
        self.assertIsNotNone(token)

        # Verify the token
        self.assertTrue(user.verify_token(token))

        # Test invalid token
        self.assertFalse(user.verify_token('invalid-token'))

        # Test expired token
        with self.app.app_context():
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            expired_token = serializer.dumps(
                user.email,
                salt='email-verification-salt'
            )
            # Simulate token expiration by waiting
            time.sleep(2)
            self.assertFalse(user.verify_token(expired_token, expiration=1))

    def test_verification_endpoint(self):
        """Test the email verification endpoint"""
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()

        # Generate verification token
        token = user.generate_verification_token()

        # Test verification endpoint
        response = self.client.get(f'/auth/verify/{token}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check if user is now verified
        user = User.query.filter_by(email='test@example.com').first()
        self.assertTrue(user.is_verified)

        # Test verifying already verified user
        response = self.client.get(f'/auth/verify/{token}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your email is already verified', response.data)

        # Test invalid token
        response = self.client.get('/auth/verify/invalid-token', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The verification link is invalid or has expired', response.data)

    def test_resend_verification(self):
        """Test resending verification email"""
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()

        with self.client as c:
            # Simulate login by setting user ID in session
            with c.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

            with mail.record_messages() as outbox:
                # Request new verification email
                response = c.get('/auth/resend-verification', follow_redirects=True)
                print('RESEND RESPONSE:', response.data.decode('utf-8'))
                self.assertEqual(response.status_code, 200)

                # Check if new verification email was sent
                self.assertEqual(len(outbox), 1)
                self.assertEqual(outbox[0].subject, 'Verify Your Email')
                self.assertIn('test@example.com', outbox[0].recipients)

    def test_verification_required_for_login(self):
        """Test that unverified users cannot log in"""
        # Create an unverified user
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()

        # Try to login
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        self.assertIn(b'Please verify your email before logging in', response.data)

    def test_verification_email_content(self):
        """Test the content of verification email"""
        with mail.record_messages() as outbox:
            # Register a new user
            self.client.post('/auth/register', data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'confirm_password': 'testpass123',
                'terms': True
            }, follow_redirects=True)

            # Check email content
            self.assertEqual(len(outbox), 1)
            email = outbox[0]
            self.assertIn('Verify Your Email', email.subject)
            self.assertIn('test@example.com', email.recipients)
            self.assertIn('verify', email.body.lower())
            self.assertIn('http://localhost:5000/auth/verify/', email.body)

    def test_verification_token_security(self):
        """Test security aspects of verification tokens"""
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()

        # Generate token
        token = user.generate_verification_token()

        # Test token cannot be used for another user
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('testpass123')
        db.session.add(other_user)
        db.session.commit()

        self.assertFalse(other_user.verify_token(token))

if __name__ == '__main__':
    unittest.main() 