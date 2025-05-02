import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'data/uploads'
    ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx', 'json', 'pdf', 'docx'}
    
    # Scout report analysis configuration
    ENABLE_SCOUT_ANALYSIS = True  # Enable scout report analysis feature
    ENABLE_SCOUT_DEEP_ANALYSIS = False  # Enable deep analysis based on Transformer
    SCOUT_REPORT_EXTENSIONS = {'txt', 'pdf', 'docx'}  # Supported file formats for scout reports
    
    # Gemini API Key - Ensure this is set via environment variables in production
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyCETEiGA_fvo5RbEAQid4OHytiU5W2x_ss')
    
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    
class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    # A stronger secret key should be used in production
    # SECRET_KEY = os.environ.get('SECRET_KEY')

# Configuration mapping for selecting different environments
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
