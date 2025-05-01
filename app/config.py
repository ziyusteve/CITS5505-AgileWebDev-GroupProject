import os

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'data/uploads'
    ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx', 'json', 'pdf', 'docx'}
    
    # 球探报告分析配置
    ENABLE_SCOUT_ANALYSIS = True  # 是否启用球探报告分析功能
    ENABLE_SCOUT_DEEP_ANALYSIS = False  # 是否启用基于Transformer的深度分析
    SCOUT_REPORT_EXTENSIONS = {'txt', 'pdf', 'docx'}  # 球探报告支持的文件格式
    
    # Gemini API Key - Ensure this is set via environment variables in production
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyCETEiGA_fvo5RbEAQid4OHytiU5W2x_ss')
    
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 在生产环境中应使用更强的密钥
    # SECRET_KEY = os.environ.get('SECRET_KEY')

# 配置映射，用于选择不同环境
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
